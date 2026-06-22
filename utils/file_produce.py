from functools import partial
from pathlib import Path
from .model import LinkItem, Context
from typing import Callable
from .sim_func import file_exists, confirm, dot_replace
from .template import compare_content, diff_file, generate_new_content, resolve_template_conflict
import shutil

def copy(src: Path, dst: Path, follow_symlink: bool):
    if src.is_dir():
        shutil.copytree(
                src,
                dst,
                symlinks=not follow_symlink,
                ignore=shutil.ignore_patterns("node_modules", "__pycache__", "*.pyc"),
                dirs_exist_ok=True
                )
    else:
        shutil.copy2(src, dst)



def dotify_relative_path(p: Path) -> Path:
    """将路径中所有隐藏组件（以.开头，除.和..）转为dot-形式"""
    new_parts = []
    for part in p.parts:
        if part not in (".", "..") and part.startswith("."):
            new_parts.append("dot-" + part[1:])
        else:
            new_parts.append(part)
    return Path(*new_parts)


def rename_dot_prefix_dir(root_dir: Path, reverse: bool = False) -> Path:
    old_prefix, new_prefix = (".", "dot-") if reverse else ("dot-", ".")

    targets = [p for p in root_dir.rglob("*") if p.name.startswith(old_prefix)]
    targets.sort(key=lambda p: len(p.parts), reverse=True)

    # 2. 逐个重命名内部条目
    for p in targets:
        new_name = new_prefix + p.name[len(old_prefix):]
        new_path = p.with_name(new_name)
        if new_path.exists():
            raise FileExistsError(f"{new_path} already exists")
        p.rename(new_path)

    # 3. 最后检查根目录本身
    if root_dir.name.startswith(old_prefix):
        new_root = root_dir.with_name(new_prefix + root_dir.name[len(old_prefix):])
        if new_root.exists():
            raise FileExistsError(f"{new_root} already exists")
        root_dir.rename(new_root)
        return new_root

    return root_dir

def rename_dot_prefix(root: Path, reverse:bool):
    if root.is_dir():
        rename_dot_prefix_dir(root, reverse)
        return
    new_path = dot_replace(root, reverse)
    if new_path != root:
        root.rename(new_path)

def delete(src: Path):
    if src.is_dir():
        shutil.rmtree(src)
    else:
        src.unlink()

def link_items(item_list: list[LinkItem]):
    for item in item_list:
        item['dst'].parent.mkdir(parents=True, exist_ok=True)
        item['dst'].symlink_to(item['src'])
        print(f"    [link] {item['src']} -> {item['dst']}")

def longest_parent_entry(mapping: dict[str, str], target: Path) -> str | None:
    target = target.resolve()
    best_key, best_path = None, None
    best_depth = 0

    for key, p in mapping.items():
        p = Path(p)
        if p != target and target.is_relative_to(p):
            depth = len(p.parts)
            if depth > best_depth:
                best_depth = depth
                best_key = key
    if best_key is not None:
        return best_key
    return None

def get_predef_folder_under_pkg(
        pkg_name: str,
        dot_base_dir: Path,
        ctx: Context,
        ):
    pkg_dir = dot_base_dir / "pkgs" / pkg_name
    if not pkg_dir.exists():
        raise ValueError(f"path {pkg_dir} not exists")

    tmp_list: list[LinkItem] = []
    for dir in pkg_dir.iterdir():
        if not dir.is_dir():
            continue

        if dir.name not in ctx["paths"]:
            print(f"{dir.name} not defined, skip")
            continue

        tmp_list.append({
            "src": dir,
            "dst": ctx["paths"][dir.name]
            })

    return tmp_list

def collect_files(
        source_dir: Path,
        target_dir: Path,
        pre_process: Callable[[Path], Path],
        produce_file: Callable[[Path, Path], None | LinkItem]
        ) -> list[LinkItem]:
    res: list[LinkItem] = []

    for src in source_dir.rglob("*"):
        if src.is_dir():
            continue
        relative = src.relative_to(source_dir)
        tmp_dst = pre_process( target_dir / relative )

        back = produce_file(src, tmp_dst)
        if back: res.append(back)
    return res

def unstow_post_processing(
        source_dir: Path,
        target_dir: Path,
        ):
    all_dir: list[Path] = []
    for src in source_dir.rglob("*"):
        if not src.is_dir():
            continue
        relative = src.relative_to(source_dir)

        realative_dst = dotify_relative_path(relative)
        dst = target_dir / realative_dst

        all_dir.append(dst)

    all_dir.sort(reverse=True)
    for path in all_dir:
        if path.exists() and not any(path.iterdir()):
            delete(path)
            print(f"    [unstow] remove empty dir {path}")

def unstow_check(
    src: Path,
    dst: Path,
    _: int,
    ) -> bool:
    if not file_exists(dst):
        return False
    if dst.is_symlink():
        if not dst.exists():
            dst.unlink()
            print(f"    [clean] bad link {dst}")
        if dst.resolve() == src.resolve():
            dst.unlink()
            print(f"    [unstow] unlink {src} -> {dst}")
    else:
        print(f"    [info] {dst} not manage by stow, skip")
    return False

def unstow_template(
        src: Path,
        dst: Path,
        ctx: dict[str, str]
        ):
    if not dst.exists():
        if dst.is_symlink():
            dst.unlink()
        return

    new_content = generate_new_content(src, ctx)
    if not compare_content(new_content, dst):
        diff_file(src, dst)
        choice = confirm(f'delete {dst}')
        if choice != 'y':
            return
    delete(dst)

def pre_check(
        src: Path,
        dst: Path,
        level: int,
        ) -> bool:
    if not file_exists(dst):
        return True
    if level == 1:
        return False

    if dst.is_symlink():
        if dst.resolve() == src:
            return False
        elif level >= 2:
            dst.unlink()
            return True
        else:
            raise ValueError(f"{dst} exists but link to {dst.resolve()}")

    if level == 3:
        if 'y' == confirm(f"[force] delete {dst}"):
            delete(dst)
            return True
        else:
            return False

    raise ValueError(f"File {dst} exists")

def func(
        src: Path,
        dst: Path,
        ctx: Context,
        check: Callable[[Path, Path, int], bool],
        level: int,
        template_callback: Callable[[Path, Path, dict[str, str]], None] = resolve_template_conflict
        ) -> None | LinkItem:
    tmpl_str = ".tmpl"
    idx = dst.name.rfind(tmpl_str)
    if idx != -1:
        neo_dst = dst.parent / (dst.name[:idx] + dst.name[idx + len(tmpl_str):])
        template_callback(src, neo_dst, ctx["paths"])
        return

    if check(src, dst, level):
        return { "src": src, "dst": dst }


def stow(
        tar_list: list[Path],
        ctx: Context,
        dot_base_dir: Path,
        follow_symlink: bool = False,
):
    pkg_name = input("input pkgname: ")
    pkg_dir = dot_base_dir / "pkgs" / pkg_name

    for tar in tar_list:
        # 安全检查
        if pkg_dir.is_relative_to(tar):
            raise ValueError(f"can't add {tar} into itself")

        longest_parent = longest_parent_entry(ctx["paths"], tar)
        if not longest_parent:
            raise ValueError("not found longest parent")

        lp_path = Path(ctx["paths"][longest_parent])
        relative = tar.relative_to(lp_path)

        # 将 relative 路径中的隐藏部分转为 dot- 形式（包括文件名）
        dot_relative = dotify_relative_path(relative)

        stow_to = pkg_dir / longest_parent / dot_relative
        if file_exists(stow_to):
            if 'n' == confirm(f"{stow_to} already exists, cover anyway"):
                return

        stow_to.parent.mkdir(parents=True, exist_ok=True)

        copy(tar, stow_to, follow_symlink)
        delete(tar)
        if stow_to.is_dir():
            stow_to = rename_dot_prefix_dir(stow_to, reverse=True)

            lst = collect_files(
                    stow_to.parent,
                    tar.parent,
                    dot_replace,
                    partial(func, ctx=ctx, check=pre_check, level=0)
                    )
        else:
            lst = [ {"src": stow_to, "dst": tar }]
        link_items(lst)


# if __name__ == "__main__":
# #     collect_files("tmux", Path("/home/shan/dot_new/"), {"paths": {"config_home": "/home/shan/.config"}})
#     func(
#             Path("dot/tmux/home/tmux.tmpl.conf"),
#             Path("/home/shan/.config/tmux.tmpl.conf")
#             )
