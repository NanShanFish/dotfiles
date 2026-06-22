import re
import os
import subprocess
import shutil
from .hash import compare_content
from .sim_func import file_exists, confirm
from pathlib import Path


substitute_pattern = re.compile(r"@@(\S+?)@@")
def generate_new_content(template_file: Path, ctx: dict[str, str]) -> str:
    def replace_match(match):
        var_name = match.group(1)
        return str(ctx.get(var_name, match.group(0)))

    content = template_file.read_text(encoding='utf-8')
    return substitute_pattern.sub(replace_match, content)

def fill_template(tmpl: Path, dst: Path, ctx: dict[str, str]) -> None:
    new_content = generate_new_content(tmpl, ctx)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(new_content, encoding='utf-8')
    shutil.copymode(tmpl, dst)

def diff_file(src: Path, dst: Path):
    editor = os.environ.get("EDITOR") or "vim"
    if os.path.basename(editor) in { "vim", "nvim", "gvim" }:
        subprocess.run([editor, "-d", src, dst], check=True)
    else:
        subprocess.run([editor, src, dst], check=True)

def resolve_template_conflict(
        src: Path,
        dst: Path,
        ctx: dict[str, str],
        ) -> None:
    if not file_exists(dst):
        fill_template(src, dst, ctx)
        print(f"    [fill] {src} -> {dst}")
        return

    if dst.is_symlink() and not dst.exists():
        dst.unlink()
        resolve_template_conflict(src, dst, ctx)
        return

    new_content = generate_new_content(src, ctx)
    if compare_content(new_content, dst):
        return

    diff_file(src, dst)

    choice = confirm(f"fill {src} to {dst}")
    if choice == 'n':
        return

    dst.write_text(new_content, encoding='utf-8')
    print(f"    [fill] {src} -> {dst}")
    shutil.copymode(src, dst)
