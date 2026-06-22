import hashlib
from pathlib import Path
from typing import IO

def _compute_hash(data: str | Path | IO[bytes] | bytes) -> str:
    """计算任意输入的 MD5 哈希：文件路径、字符串、字节、IO 对象"""
    if isinstance(data, bytes):
        return hashlib.md5(data).hexdigest()

    hasher = hashlib.md5()
    if isinstance(data, Path):
        with open(data, "rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()

    elif isinstance(data, str):
        return hashlib.md5(data.encode('utf-8')).hexdigest()

    # IO 对象
    try:
        pos = data.tell()
        data.seek(0)
    except (AttributeError, OSError):
        pos = None
    while chunk := data.read(8192):
        if isinstance(chunk, str):
            chunk = chunk.encode('utf-8')
        hasher.update(chunk)
    if pos is not None:
        try:
            data.seek(pos)
        except OSError:
            pass
    return hasher.hexdigest()

def compare_content(
    target1: str | Path | IO[bytes] | bytes,
    target2: str | Path | IO[bytes] | bytes,
) -> bool:
    """比较两个任意来源的内容是否一致（文件、字符串、字节等）"""
    return _compute_hash(target1) == _compute_hash(target2)
