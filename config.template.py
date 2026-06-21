from utils import Context, LinkItem, PackageConfig, Template_Item, has_cmd, installer

def get_config(ctx: Context) -> PackageConfig:
    tar_dir = "<++>"

    files: list[ str | LinkItem ] = [
        ]
    template_files: list[str | Template_Item ] = [
        ]

    return {
        "name": "<++>",
        "deps": [ ],
        "files": files,
        "template_files": template_files,
        "tar_dir": tar_dir,
    }
