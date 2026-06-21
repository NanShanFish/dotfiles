import shutil
import subprocess
import platform
import sys
from typing import Callable, TypedDict
from pathlib import Path
import re
import os
import hashlib
from typing import IO

class Context(TypedDict):
    home_dir: Path
    config_home: Path
    os_type: str
    distro: str
    offset_dir: str

class Template_Item(TypedDict):
    template: str
    src: str
    dst: str

class LinkItem(TypedDict):
    src: str
    dst: str

class PackageConfig(TypedDict, total=False):
    name: str
    deps: list[str]
    tar_dir: Path | None
    files: list[str | LinkItem] | None
    template_files: list[str | LinkItem] | None
    pre_check: Callable[[], bool] | None
    pre_process: Callable[[], None] | None
    post_process: Callable[[], None] | None

def has_cmd(cmd: str) -> bool:
    res = subprocess.run(["which", cmd], capture_output=True, text=True, check=False)
    return res.returncode == 0

def get_distro() -> str:
    if platform.system() == "Linux":
        try:
            return platform.freedesktop_os_release().get("ID", "linux")
        except AttributeError:
            return "linux"
    return ""


def arch_installer(pkglist: list[str]) -> None:
    print(f"   -> installing {pkglist} via pacman...")
    subprocess.run(["sudo", "pacman", "-S", "--noconfirm", *pkglist], check=True)

def mac_installer(pkglist: list[str]) -> None:
    print(f"   -> installing {pkglist} via homebrew...")
    subprocess.run(["brew", "install", *pkglist], check=True)

def check_links(links: list[LinkItem]) -> bool:
    all_ok = True
    for item in links:
        src = Path(item["src"])
        dst = Path(item["dst"])

        if dst.exists() and not dst.is_symlink():
            print(f"   [error] {dst} already exists and is not a link.")
            all_ok = False
            continue
        if dst.is_symlink():
            try:
                current_target = dst.readlink().resolve()
                actual_src = src.resolve()

                if current_target != actual_src:
                    print(f"   [warning] {dst} is a symlink but points to {current_target} instead of {actual_src}.")
                    all_ok = False
            except Exception as e:
                print(f"   [error] Failed to read symlink {dst}: {e}")
                all_ok = False
            continue
    return all_ok

def _compute_hash(data: str | Path | IO[bytes] | bytes) -> str:
    """计算任意输入的 MD5 哈希：文件路径、字符串、字节、IO 对象"""
    if isinstance(data, bytes):
        return hashlib.md5(data).hexdigest()

    hasher = hashlib.md5()
    if isinstance(data, Path):
        with open(data, "rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()

    elif isinstance(data, str):
        return hashlib.md5(data.encode('utf-8')).hexdigest()

    # IO 对象
    try:
        pos = data.tell()
        data.seek(0)
    except (AttributeError, OSError):
        pos = None
    while chunk := data.read(8192):
        if isinstance(chunk, str):
            chunk = chunk.encode('utf-8')
        hasher.update(chunk)
    if pos is not None:
        try:
            data.seek(pos)
        except OSError:
            pass
    return hasher.hexdigest()


def compare_content(
    target1: str | Path | IO[bytes] | bytes,
    target2: str | Path | IO[bytes] | bytes,
) -> bool:
    """比较两个任意来源的内容是否一致（文件、字符串、字节等）"""
    return _compute_hash(target1) == _compute_hash(target2)

def confirm_remove(path: Path) -> str:
    """返回 'y', 'n', 'q'"""
    prompt = f"   [force] Delete {path}? [y/N/q] "
    while True:
        choice = input(prompt).strip().lower()
        if choice in ('y', 'yes'):
            return 'y'
        elif choice in ('n', 'no', ''):
            return 'n'
        elif choice in ('q', 'quit'):
            return 'q'
        else:
            print("   Please answer y, n, or q.")

substitute_pattern = re.compile(r"@@(\S+?)@@")

def generate_new_content(template_file: Path, ctx: dict[str, str]) -> str:
    def replace_match(match):
        var_name = match.group(1)
        return str(ctx.get(var_name, match.group(0)))

    content = template_file.read_text(encoding='utf-8')
    return substitute_pattern.sub(replace_match, content)

def fill_template_list(temp_list: list[dict[str, Path]], ctx: dict[str, str]) -> None:
    for item in temp_list:
        new_content = generate_new_content(item['template'], ctx)
        item['src'].parent.mkdir(parents=True, exist_ok=True)
        item['src'].write_text(new_content, encoding='utf-8')
        # 将模板文件的权限（如可执行位）复制到生成的目标文件
        shutil.copymode(item['template'], item['src'])

def _resolve_existing_dst(
    dst: Path,
    expected_src: Path,          # 期望的源路径（调用方决定是否 resolve）
    delete_when_exists: bool,
    delete_when_symlink: bool,
    desc: str = "destination",   # 用于错误信息，如 "file" / "template"
) -> bool:
    """
    处理已存在的目标路径冲突。
    
    返回:
        True  - 应跳过该项（用户选择不删除）
        False - 已成功清除冲突，可继续创建链接
    """
    if not dst.is_symlink():
        # 目标为普通文件或目录
        if delete_when_exists:
            choice = confirm_remove(dst)
            if choice == 'y':
                # 目录用 rmtree，文件/其它用 unlink
                if dst.is_dir():
                    shutil.rmtree(dst)
                else:
                    dst.unlink()
            elif choice == 'n':
                print(f"   [skip] {dst}")
                return True   # 跳过
            else:  # 'q'
                print("Aborted by user.")
                sys.exit(0)
        else:
            raise ValueError(f"{desc} already exists and is not a symlink: {dst}")
    else:

        try:
            current_target = dst.readlink().resolve()
        except Exception:
            # 损坏的符号链接
            if delete_when_symlink:
                dst.unlink()
                print(f"   [removed] broken symlink {dst}")
            else:
                raise ValueError(f"failed to read symlink {dst}: broken link")
        else:
            if current_target != expected_src:
                if delete_when_symlink:
                    dst.unlink()
                    print(f"   [removed] outdated symlink {dst}")
                else:
                    raise ValueError(
                        f"{desc} symlink points to {current_target} instead of {expected_src}"
                    )
            elif delete_when_exists:
                dst.unlink()
    return False

def generate_and_check_files_list(
    lst: list[str | LinkItem],
    base_dir: Path,
    tar_dir: Path | None,
    delete_when_symlink: bool = False,
    delete_when_exists: bool = False,
) -> list[dict[str, Path]]:
    if delete_when_exists:
        delete_when_symlink = True

    res: list[dict[str, Path]] = []

    for item in lst:
        if isinstance(item, str):
            src_rel = Path(item)
            dst_rel = Path(item)
        else:
            src_rel = Path(item["src"])
            dst_rel = Path(item["dst"])

        if src_rel.is_absolute():
            raise ValueError("files src must be a relative path")

        if not dst_rel.is_absolute():
            if tar_dir is None:
                raise ValueError("tar_dir must be set when dst is relative")
            dst = tar_dir / dst_rel
        else:
            dst = dst_rel

        src = base_dir / src_rel
        if not os.path.lexists(str(src)):
            raise ValueError(f"source file not found: {src}")

        # 处理目标冲突
        if os.path.lexists(str(dst)):
            expected = src.resolve()   # files 类型 resolve 后比较
            skip = _resolve_existing_dst(
                dst, expected,
                delete_when_exists, delete_when_symlink,
                desc="file"
            )
            if skip:
                continue

        res.append({"src": src, "dst": dst})
    return res

def generate_and_check_template_files_list(
    lst: list[str | LinkItem],
    base_dir: Path,
    tar_dir: Path | None,
    offset_dir: str,
    delete_when_symlink: bool = False,
    delete_when_exists: bool = False,
) -> list[dict[str, Path]]:
    if delete_when_exists:
        delete_when_symlink = True

    res: list[dict[str, Path]] = []

    for item in lst:
        if isinstance(item, str):
            src_rel = Path(item)
            dst_rel = Path(item)
        else:
            src_rel = Path(item["src"])
            dst_rel = Path(item["dst"])

        if src_rel.is_absolute():
            raise ValueError("template files src must be a relative path")

        if not dst_rel.is_absolute():
            if tar_dir is None:
                raise ValueError("tar_dir must be set when dst is relative")
            dst = tar_dir / dst_rel
        else:
            dst = dst_rel

        template = base_dir / src_rel
        src = base_dir / offset_dir / src_rel

        if not template.exists():
            raise ValueError(f"template file not found: {template}")

        if os.path.lexists(str(dst)):
            skip = _resolve_existing_dst(
                dst, src,
                delete_when_exists, delete_when_symlink,
                desc="template"
            )
            if skip:
                continue

        res.append({"src": src, "template": template, "dst": dst})
    return res

def check_content(temp_list: list[dict[str, Path]], ctx: Context):
    for item in temp_list:
        if not item["src"].exists():
            print(f"{item['template']} has not been generated")
            continue

        rendered = generate_new_content(item["template"], ctx)
        if not compare_content(rendered, item["dst"]):
            print(f"{item['dst']} has been edited, need diff? Y/N, q to quit")
            choice = input().strip().lower()
            if choice == 'y':
                editor = os.environ.get("EDITOR", "vim")
                editor_path = Path(editor)
                if editor_path.name in ("vim", "nvim"):
                    subprocess.run([editor, "-d", str(item['template']), str(item["dst"])])
                else:
                    subprocess.run([editor, str(item['template']), str(item["dst"])])
            elif choice == 'q':
                return

def get_destination_paths(
    lst: list[str | LinkItem],
    base_dir: Path,
    tar_dir: Path | None,
    offset_dir: str | None = None,
) -> list[dict[str, Path]]:
    """
    仅解析文件/模板列表，返回每个目标的 src 和 dst 路径。
    对于模板文件，offset_dir 用于确定 src（渲染后位置），否则为普通文件。
    """
    res: list[dict[str, Path]] = []
    for item in lst:
        if isinstance(item, str):
            src_rel = Path(item)
            dst_rel = Path(item)
        else:
            src_rel = Path(item["src"])
            dst_rel = Path(item["dst"])

        # 计算 src 和 dst（与生成函数逻辑一致）
        if not dst_rel.is_absolute():
            if tar_dir is None:
                continue  # 无法确定目标，跳过
            dst = tar_dir / dst_rel
        else:
            dst = dst_rel

        if offset_dir is not None:
            # 模板文件：src 在 base_dir/offset_dir/src_rel
            src = base_dir / offset_dir / src_rel
        else:
            src = base_dir / src_rel

        res.append({"src": src, "dst": dst})
    return res
def run_remove(pkg_meta: PackageConfig, base_dir: Path, ctx: Context,
               force_all: bool = False, force_link: bool = False) -> None:
    """卸载指定的包：删除所有创建的文件/符号链接。"""
    print(f":: removing {pkg_meta['name']}...")

    tar_dir = pkg_meta.get("tar_dir")
    offset_dir = ctx["offset_dir"]

    # 获取所有目标路径（普通文件和模板文件）
    files_dst = get_destination_paths(
        pkg_meta.get("files", []), base_dir, tar_dir
    )
    template_dst = get_destination_paths(
        pkg_meta.get("template_files", []), base_dir, tar_dir, offset_dir
    )
    all_targets = files_dst + template_dst

    for entry in all_targets:
        dst = entry["dst"]
        src = entry["src"]   # 仅用于显示

        # 如果目标根本不存在，直接跳过
        if not dst.exists() and not dst.is_symlink():
            print(f"   [skip] {dst} (not found)")
            continue

        # 决定是否删除
        if dst.is_symlink():
            # 是符号链接（无论是否断开）
            if force_all or force_link:
                do_delete = True
            else:
                # 默认也删除符号链接，但询问一次（可省略询问，此处提供 -f 静默删除）
                # 为了安全，默认也询问
                choice = confirm_remove(dst)
                do_delete = (choice == 'y')
                if choice == 'q':
                    print("Aborted by user.")
                    sys.exit(0)
        else:
            # 目标不是符号链接（普通文件或目录）
            if force_all:
                choice = confirm_remove(dst)
                do_delete = (choice == 'y')
                if choice == 'q':
                    print("Aborted by user.")
                    sys.exit(0)
            else:
                print(f"   [skip] {dst} (not a symlink, use -F to force delete)")
                continue

        if do_delete:
            if dst.is_dir() and not dst.is_symlink():
                shutil.rmtree(dst)
                print(f"   [removed] directory {dst}")
            else:
                dst.unlink()
                print(f"   [removed] {dst}")
        else:
            print(f"   [skip] {dst}")

    # 可选：清理模板生成的文件（src），这些是包内部的中间文件，可根据需要决定
    # 通常保留，这里暂不删除

os_type = platform.system()
distro = get_distro()

installer = lambda _: sys.stderr.write("Unkown platfrom\n")
if distro == "arch":
    installer = arch_installer
elif os_type == "Darwin":
    installer = mac_installer
