from pathlib import Path
from utils import Context, LinkItem, PackageConfig, Template_Item, has_cmd, installer

def get_config(ctx: Context) -> PackageConfig:
    tar_dir = ctx["config_home"] / "alacritty"

    files: list[ str | LinkItem ] = [
            "./alacritty.toml",
            "./catppuccin.toml",
            "./tokyonight.toml",
            "./theme.toml",
            ]
    template_files = [
            "./theme.toml"
            ]

    return {
        "name": "alacritty",
        "deps": [],
        "files": files,
        "template_files": template_files,
        "tar_dir": tar_dir,
    }
