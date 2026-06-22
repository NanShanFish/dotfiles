import subprocess
from pathlib import Path
import os

def confirm(prompt: str) -> str:
    """返回 'y', 'n', 'q'"""
    prompt = f"   {prompt}? [y/N/q] "
    while True:
        choice = input(prompt).strip().lower()
        if choice in ('y', 'yes'):
            return 'y'
        elif choice in ('n', 'no', ''):
            return 'n'
        elif choice in ('q', 'quit'):
            exit(0)
        else:
            print("   Please answer y, n, or q.")

def has_cmd(cmd: str) -> bool:
    res = subprocess.run(["which", cmd], capture_output=True, text=True, check=False)
    return res.returncode == 0

def file_exists(path: Path):
    return os.path.lexists(str(path))

def get_system():
    import platform
    return platform.system()

def dot_replace(file: Path, reverse: bool = False) -> Path:
    pats =   [ '.', 'dot-' ] if reverse else [ 'dot-', '.' ]
    parts = file.parts
    new_parts = []
    for part in parts:
        if part.startswith(pats[0]):
            new_parts.append(pats[1] + part[len(pats[0]):])  # 将前4个字符 dot- 替换为 .
        else:
            new_parts.append(part)
    res = Path(*new_parts)
    return res

