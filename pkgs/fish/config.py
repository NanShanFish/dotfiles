from pathlib import Path
from utils import Context, LinkItem, PackageConfig, Template_Item, has_cmd, installer

def get_config(ctx: Context) -> PackageConfig:
    tar_dir = ctx["config_home"]

    files: list[ str | LinkItem ] = [
            "./fish/"
            ]
    template_files = [
            { "src": "./config.fish", "dst": tar_dir / "fish/config.fish" }
            ]

    return {
        "name": "fish",
        "deps": [],
        "files": files,
        "template_files": template_files,
        "tar_dir": tar_dir,
    }
