from utils import Context, LinkItem, PackageConfig, Template_Item, has_cmd, installer

def get_config(ctx: Context) -> PackageConfig:
    tar_dir = ctx["config_home"] / "yazi"

    files: list[ str | LinkItem ] = [
        "./yazi.toml",
        "./package.toml",
        "./theme.toml",
        "./init.lua",
        ]
    template_files: list[str | Template_Item ] = [
            "./keymap.toml"
        ]

    def pre_process():
        if not has_cmd("yazi"):
            installer(["yazi"])
    return {
        "name": "yazi",
        "deps": [ ],
        "files": files,
        "template_files": template_files,
        "tar_dir": tar_dir,
        "pre_process": pre_process,
    }
