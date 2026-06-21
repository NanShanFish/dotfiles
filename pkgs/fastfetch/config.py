from utils import Context, LinkItem, PackageConfig, Template_Item, has_cmd, installer

def get_config(ctx: Context) -> PackageConfig:
    tar_dir = ctx["config_home"]

    files: list[ str | LinkItem ] = [
            "./fastfetch/"
        ]
    template_files: list[str | Template_Item ] = [
        ]

    def pre_processing():
        if not has_cmd("fastfetch"):
            installer("fastfetch")

    return {
        "name": "fastfetch",
        "deps": [ ],
        "files": files,
        "template_files": template_files,
        "tar_dir": tar_dir,
        "pre_process": pre_processing,
    }
