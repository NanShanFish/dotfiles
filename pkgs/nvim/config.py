from utils import Context, LinkItem, PackageConfig, Template_Item, has_cmd, installer
import subprocess
import os

def get_config(ctx: Context) -> PackageConfig:
    tar_dir = ctx["config_home"]
    nvim_repo = "https://github.com/nanshanfish/nvim"
    clone_to = ctx["dot_path"] / "pkgs/nvim/nvim"

    files: list[ str | LinkItem ] = [
            "./nvim"
        ]
    template_files: list[str | Template_Item ] = [
        ]

    def pre_process():
        if not os.path.lexists(str(tar_dir / "nvim")) and not os.path.lexists(str(clone_to)):
            subprocess.run(["git", "clone", nvim_repo, str(clone_to) ], check=True)

    return {
        "name": "nvim",
        "deps": [ ],
        "files": files,
        "template_files": template_files,
        "tar_dir": tar_dir,
        "pre_process": pre_process
    }
