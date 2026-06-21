from pathlib import Path
from utils import Context, LinkItem, PackageConfig, Template_Item, has_cmd, installer

def get_config(ctx: Context) -> PackageConfig:
    tar_dir = ctx["config_home"] / "tmux"

    files: list[ str | LinkItem ] = [ ]
    template_files: list[str | Template_Item ] = [
            "./tmux.conf"
        ]

    def pre_process():
        if not has_cmd("tmux"):
            installer(["tmux"])
    return {
        "name": "tmux",
        "deps": [ "bin" ],
        "files": files,
        "template_files": template_files,
        "tar_dir": tar_dir,
        "pre_process": pre_process,
    }
