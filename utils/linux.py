import platform

def get_distro() -> str:
    if platform.system() == "Linux":
        try:
            return platform.freedesktop_os_release().get("ID", "linux")
        except AttributeError:
            return "linux"
    return ""
