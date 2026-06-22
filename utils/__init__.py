import subprocess
import sys

def arch_installer(pkglist: list[str]) -> None:
    print(f"   -> installing {pkglist} via pacman...")
    subprocess.run(["sudo", "pacman", "-S", "--noconfirm", *pkglist], check=True)

def mac_installer(pkglist: list[str]) -> None:
    print(f"   -> installing {pkglist} via homebrew...")
    subprocess.run(["brew", "install", *pkglist], check=True)

installer = lambda _: sys.stderr.write("Unkown platfrom\n")

from .sim_func import get_system
os_type = get_system()
distro = ''
if os_type == 'Linux':
    from .linux import get_distro
    distro = get_distro()
    if distro == "arch":
        installer = arch_installer
elif os_type == "Darwin":
    installer = mac_installer
