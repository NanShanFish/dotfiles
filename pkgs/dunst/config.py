from pathlib import Path
from utils import Context, LinkItem, PackageConfig, Template_Item, has_cmd, installer

def get_config(ctx: Context) -> PackageConfig:
    tar_dir = ctx["config_home"]

    files: list[ str | LinkItem ] = [
            "./dunst/"
            ]

    return {
        "name": "dunst",
        "deps": [],
        "files": files,
        "tar_dir": tar_dir,
    }
