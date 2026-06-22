#!/usr/bin/env python
# {{{

import argparse
import sys
from functools import partial
from pathlib import Path
import importlib.util

from utils import (
    os_type,
    distro,
)
from utils.model import Context, PackageConfig
from utils.file_produce import link_items, pre_check, stow, func, unstow_check, unstow_post_processing, unstow_template
# }}}

global_ctx: Context = {
    "os_type": os_type,
    "distro": distro,
    "offset_dir": "dist",
    "paths": {
        "home": str(Path.home()),
        "config_home": str(Path.home() / ".config"),
        "doc_dir": "/mnt/a/doc",
        "dot_dir": str(Path.home / "dot"),
        "dls_dir": str(Path.home() / "dls"),
        "root": "/"
    }
}

def discover_packages(pkgs_dir: Path) -> set[str]:# {{{
    """扫描 pkgs_dir 下所有包含 config.py 的子目录，返回包名列表"""
    packages = set()
    if pkgs_dir.is_dir():
        for child in pkgs_dir.iterdir():
            if child.is_dir():
                packages.add(child.name)
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
            continue

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
    return resolved# }}}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Deploy and manage dotfiles/templates."
    )

    # 位置参数：通用目标列表（创建/检查/删除时为包名，添加时为路径）
    parser.add_argument(
        "pkgs", nargs="*", metavar="TARGET",
        help="Package names (or paths when -a is used)"
    )

    # 互斥模式选择（不再带参数）
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "-c", "--check", action="store_true",
        help="Check templates for specified packages"
    )
    mode.add_argument(
        "-a", "--add", action="store_true",
        help="Add specified paths (stow)"
    )
    mode.add_argument(
        "-d", "--delete", action="store_true",
        help="Delete (unstow) specified packages"
    )

    # 全局选项
    parser.add_argument(
        "--all", action="store_true",
        help="Apply to all packages/paths (ignores explicit list)"
    )

    # 创建模式专属的文件存在行为（互斥）
    create_group = parser.add_argument_group("Create mode options (default)")
    create_ex = create_group.add_mutually_exclusive_group()
    create_ex.add_argument(
        "-i", "--ignore-exists", action="store_true",
        help="Skip if destination already exists"
    )
    create_ex.add_argument(
        "-f", "--force-link", action="store_true",
        help="Update symlink if destination is a link"
    )
    create_ex.add_argument(
        "-F", "--force-delete", action="store_true",
        help="Prompt to delete existing file before creating"
    )

    return parser.parse_args()


from utils.file_produce import get_predef_folder_under_pkg, collect_files
from utils.sim_func import dot_replace, file_exists
def create(
        pkg_list: list[str],
        ctx: Context,
        dot_dir: Path,
        level: int,
        ):
    f_ = partial(func, ctx=ctx, level=level, check=pre_check)
    for pkg in pkg_list:
        print(f":: processing {pkg}...")
        lst = get_predef_folder_under_pkg(pkg, dot_dir, ctx)
        for item in lst:
            src = item['src']
            dst = item['dst']
            neo_lst = collect_files(src, dst, dot_replace, f_ )
            link_items(neo_lst)

def check(
        pkg_list: list[str],
        ctx: Context,
        dot_dir: Path
        ):
    f_ = partial(func, ctx=ctx, level=0, check=lambda p,p2,i: False)
    for pkg in pkg_list:
        lst = get_predef_folder_under_pkg(pkg, dot_dir, ctx)
        for item in lst:
            src = item['src']
            dst = item['dst']
            _ = collect_files(src, dst, dot_replace, f_ )

def unstow(
        pkg_list: list[str],
        ctx: Context,
        dot_dir: Path,
        ):
    f_ = partial(func, ctx=ctx, level=0, check=unstow_check, template_callback=unstow_template)
    for pkg in pkg_list:
        lst = get_predef_folder_under_pkg(pkg, dot_dir, ctx)
        for item in lst:
            src = item['src']
            dst = item['dst']
            _ = collect_files(src, dst, dot_replace, f_ )
            unstow_post_processing(src, dst)


def main():
    # 检查预定义路径是否存在
    for key, value in global_ctx["paths"].items():
        if not file_exists(Path(value)):
            raise ValueError(f"{key}:{value} defined in paths does not exist")

    args = parse_args()
    dot_path = Path(global_ctx["paths"]["dot_dir"])
    pkgs_path = dot_path / "pkgs"

    # 添加模式：目标列表是路径
    if args.add:
        paths = [Path(s) for s in args.pkgs]
        for p in paths:
            if not p.exists():
                raise ValueError(f"Path does not exist: {p}")
        stow(paths, global_ctx, dot_path)
        return

    # 确定模式与包名列表
    if args.check:
        mode = 'check'
    elif args.delete:
        mode = 'delete'
    else:
        mode = 'create'

    raw_targets = args.pkgs
    all_packages = discover_packages(pkgs_path)

    if args.all:
        raw_targets = list(all_packages)
    elif not raw_targets:
        print("Error: No targets specified. Use packages or --all.", file=sys.stderr)
        sys.exit(1)

    graph = load_packages_with_deps(raw_targets, global_ctx)
    exec_order = compute_execution_order(graph, raw_targets)
    missing = set(exec_order) - all_packages
    if missing:
        print(f"Info: packages not found, skipped: {', '.join(sorted(missing))}")

    if mode == 'create':
        level = 0
        if args.ignore_exists:
            level = 1
        elif args.force_link:
            level = 2
        elif args.force_delete:
            level = 3
        create(exec_order, global_ctx, dot_path, level)
    elif mode == 'check':
        check(exec_order, global_ctx, dot_path)
    elif mode == 'delete':
        unstow(exec_order, global_ctx, dot_path)

if __name__ == "__main__":
    try:
        main()
    except ValueError as e:
        print(str(e))
