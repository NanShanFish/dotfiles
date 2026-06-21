from pathlib import Path
from utils import Context, LinkItem, PackageConfig, Template_Item, has_cmd, installer

def get_config(ctx: Context) -> PackageConfig:
    tar_dir = ctx["home_dir"] / ".local" / "bin"

    files: list[ str | LinkItem ] = [ "v" ]
    template_files = [
        "jy", "td"
            ]

    return {
        "name": "bin",
        "deps": [],
        "files": files,
        "template_files": template_files,
        "tar_dir": tar_dir,
    }
