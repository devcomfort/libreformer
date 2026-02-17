from invoke import run
import logging
import shutil
import shutil
from loguru import logger


def check_install() -> bool:
    """Check whether LibreOffice is available on the system using shutil.which."""
    try:
        return shutil.which("libreoffice") is not None
    except Exception as e:
        logger.error(f"[check_install] Error while checking LibreOffice: {e}")
        return False


def get_path() -> str | None:
    """Check whether LibreOffice is available on the system using shutil.which."""
    return shutil.which("libreoffice")


def install() -> bool:
    """Install LibreOffice using `apt`.

    The command updates the package index first and then installs the package
    in a non‑interactive way (`-y`). It returns `True` on success.
    """
    try:
        cmd = "sudo apt update -y && sudo apt install -y libreoffice"
        result = run(cmd, hide=True, warn=True)
        if result.ok:
            logger.info("[install] LibreOffice installed successfully.")
        else:
            logger.error(
                f"[install] Installation failed with exit code {result.exited}."
            )
        return result.ok
    except Exception as e:
        logger.error(f"[install] Exception during installation: {e}", exc_info=True)
        return False


def uninstall() -> bool:
    """Remove LibreOffice from the system."""
    try:
        cmd = "sudo apt remove -y libreoffice"
        result = run(cmd, hide=True, warn=True)
        if result.ok:
            logger.info("[uninstall] LibreOffice removed successfully.")
        else:
            logger.error(f"[uninstall] Removal failed with exit code {result.exited}.")
        return result.ok
    except Exception as e:
        logger.error(f"[uninstall] Exception during removal: {e}")
        return False


if __name__ == "__main__":
    result = check_install()
    if result:
        print("LibreOffice is installed and reachable.")
    else:
        print("LibreOffice is NOT installed or not found in PATH.")
