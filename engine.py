#!/usr/bin/env python# {{{

import argparse
import sys
from pathlib import Path
import importlib.util

from utils import (
    fill_template_list,
    generate_and_check_files_list,
    generate_and_check_template_files_list,
    check_content,
    os_type,
    distro,
    Context,
    PackageConfig,
    run_remove,
)
# }}}
global_ctx: Context = {
    "home_dir": Path.home(),
    "config_home": Path.home() / ".config",
    "os_type": os_type,
    "distro": distro,
    "offset_dir": "dist",
    "doc_path": Path("/mnt/a/doc"),
    "dot_path": Path(__file__).resolve().parent,
    "dls_path": Path.home() / "dls",
}

def discover_packages(pkgs_dir: Path) -> list[str]:
    """扫描 pkgs_dir 下所有包含 config.py 的子目录，返回包名列表"""
    packages = []
    if pkgs_dir.is_dir():
        for child in pkgs_dir.iterdir():
            if child.is_dir() and (child / "config.py").exists():
                packages.append(child.name)
    return packages

def load_packages_with_deps(package_names: list[str], ctx: Context) -> dict[str, PackageConfig]:
    """递归加载所有需要的包（包括间接依赖），返回包名到配置的映射。"""
    graph: dict[str, PackageConfig] = {}
    to_load = set(package_names)

    while to_load:
        pkg = to_load.pop()
        if pkg in graph:          # 已加载过，跳过
            continue

        script_path = Path(f"pkgs/{pkg}/config.py")
        if not script_path.exists():
            print(f":: error: required package '{pkg}' not found in pkgs/")
            sys.exit(1)

        # 动态导入模块
        spec = importlib.util.spec_from_file_location("pkg_config", script_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        config = module.get_config(ctx)
        graph[pkg] = config

        # 将依赖加入待加载队列
        for dep in config.get("deps", []):
            if dep not in graph:
                to_load.add(dep)

    return graph

def topo_sort(resolved: list, graph: dict, node: str):
    """拓扑排序辅助递归函数"""
    deps = graph.get(node, {}).get("deps", [])
    for dep in deps:
        if dep not in resolved:
            topo_sort(resolved, graph, dep)
    if node not in resolved:
        resolved.append(node)

def compute_execution_order(graph: dict, targets: list[str]) -> list[str]:
    """根据依赖关系计算执行顺序"""
    resolved = []
    for target in targets:
        topo_sort(resolved, graph, target)
    return resolved

def run_lifecycle(pkg_meta: PackageConfig, base_dir: Path, ctx: Context,
                  force_all: bool = False, force_link: bool = False) -> None:
    print(f":: processing {pkg_meta['name']}...")

    if pkg_meta.get("pre_check") and not pkg_meta["pre_check"]():
        return

    if pkg_meta.get("pre_process"):
        pkg_meta["pre_process"]()

    tar_dir = pkg_meta.get("tar_dir")
    offset_dir = ctx["offset_dir"]

    file_list = generate_and_check_files_list(
        pkg_meta.get("files", []), base_dir, tar_dir,
        delete_when_exists=force_all,
        delete_when_symlink=force_link or force_all   # -F 自动包含 -f
    )
    temp_list = generate_and_check_template_files_list(
        pkg_meta.get("template_files", []), base_dir, tar_dir, offset_dir,
        delete_when_exists=force_all,
        delete_when_symlink=force_link or force_all
    )

    fill_template_list(temp_list, ctx)

    # 此时所有冲突已在生成函数中处理完毕，直接创建符号链接
    for lst in [file_list, temp_list]:
        for l in lst:
            l["dst"].parent.mkdir(parents=True, exist_ok=True)
            if l["dst"].exists():
                continue
            print(f"   [link] {l['src']} -> {l['dst']}")
            l["dst"].symlink_to(l["src"])

    if pkg_meta.get("post_process"):
        pkg_meta["post_process"]()

def run_check(pkg_meta: PackageConfig, base_dir: Path, ctx: Context) -> None:
    """仅执行检查：生成文件列表（不安装），然后调用 check_content 交互式比对模板"""
    print(f":: checking {pkg_meta['name']}...")

    tar_dir = pkg_meta.get("tar_dir")
    offset_dir = ctx["offset_dir"]

    # 只生成模板文件列表用于检查
    temp_list = generate_and_check_template_files_list(
        pkg_meta.get("template_files", []), base_dir, tar_dir, offset_dir
    )

    # file_list = generate_and_check_files_list(
    #     pkg_meta.get("files", []), base_dir, tar_dir
    # )

    check_content(temp_list, ctx)   # check_content 在 utils 中实现


def parse_args():
    parser = argparse.ArgumentParser(description="Dotfiles package manager")
    parser.add_argument("-c", "--check", action="store_true",
                        help="Check installed files for modifications instead of installing")
    parser.add_argument("-d", "--remove", action="store_true",
                        help="Remove installed packages (delete symlinks and generated files)")
    parser.add_argument("--all", action="store_true",
                        help="Process all packages found in pkgs/")
    parser.add_argument("-F", "--force-all", action="store_true",
                        help="Force overwrite/delete ANY existing files, directories or symlinks (with confirmation)")
    parser.add_argument("-f", "--force-link", action="store_true",
                        help="Force overwrite/delete existing symlinks only")
    parser.add_argument("packages", nargs="*",
                        help="Specific packages to process (ignored if --all is given)")
    return parser.parse_args()



def main():
    args = parse_args()
    all_packages = set(discover_packages(Path("pkgs")))

    if args.all:
        packages = discover_packages(Path("pkgs"))
        if not packages:
            print("No packages found in pkgs/ directory.")
            sys.exit(1)
    else:
        packages = [Path(pkg).name for pkg in args.packages]
        if not packages:
            print("No packages specified. Use positional arguments or --all.")
            sys.exit(1)

    # ---------- 移除包的分支 ----------
    if args.remove:
        for pkg_name in packages:
            try:
                pkg_graph = load_packages_with_deps([pkg_name], global_ctx)
                pkg_meta = pkg_graph.get(pkg_name)
                if not pkg_meta:
                    print(f":: error: package '{pkg_name}' not found")
                    continue
                base_dir = global_ctx['dot_path'] / f"pkgs/{pkg_name}"
                run_remove(pkg_meta, base_dir, global_ctx,
                           force_all=args.force_all,
                           force_link=args.force_link)
            except ValueError as e:
                print(str(e))
        sys.exit(0)

    # ---------- 正常安装/检查 ----------
    pkg_graph = load_packages_with_deps(packages, global_ctx)
    exec_order = compute_execution_order(pkg_graph, packages)

    missing_packages = set(exec_order) - all_packages
    if missing_packages:
        print(f":: error: missing packages: {missing_packages}")
        sys.exit(1)

    for pkg_name in exec_order:
        base_dir = global_ctx['dot_path'] / f"pkgs/{pkg_name}"
        pkg_meta = pkg_graph[pkg_name]

        try:
            if args.check:
                run_check(pkg_meta, base_dir, global_ctx)
            else:
                run_lifecycle(pkg_meta, base_dir, global_ctx,
                              force_all=args.force_all,
                              force_link=args.force_link)
        except ValueError as e:
            print(str(e))

if __name__ == "__main__":
    main()
