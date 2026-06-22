from functools import partial
import shutil
from typing import Callable, TypedDict
from pathlib import Path

class PreDefVar(TypedDict):
    home: str
    config_home: str
    doc_dir: str
    dot_path: str

class Context(TypedDict):
    os_type: str
    distro: str
    paths: PreDefVar

class LinkItem(TypedDict):
    src: Path
    dst: Path



class PackageConfig(TypedDict, total=False):
    deps: list[str]
    pre_check: Callable[[], bool] | None
    pre_process: Callable[[], None] | None
    post_process: Callable[[], None] | None
