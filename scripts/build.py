"""Build script for HuG.

Cross-platform: run this from an activated venv on the target OS
(Linux, Windows, or macOS). It builds a native executable for whatever
platform it's run on -- PyInstaller does not cross-compile, so a
Windows build must be produced on Windows, a Linux build on Linux, etc.
See dev-docs for the full per-platform build notes.
"""
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / "build"
SPEC_FILE = PROJECT_ROOT / "package" / "hug.spec"

PLATFORM_TAGS = {
    "Linux": "linux",
    "Windows": "windows",
    "Darwin": "macos",
}
PLATFORM_TAG = PLATFORM_TAGS.get(platform.system(), platform.system().lower())
EXE_NAME = "hug.exe" if platform.system() == "Windows" else "hug"

def _rmtree_retry(path: Path, attempts: int = 5, delay: float = 2.0) -> None:
    """Remove a directory tree, retrying on transient file locks.

    If this project lives inside a cloud-sync folder (Dropbox, OneDrive,
    etc.), the sync client can briefly hold a lock on files it's actively
    scanning/uploading, which turns into a PermissionError here.
    """
    for attempt in range(1, attempts + 1):
        try:
            shutil.rmtree(path)
            return
        except PermissionError as e:
            if attempt == attempts:
                print(f"Could not remove {path}: {e}")
                print(
                    "This is likely a cloud-sync client (Dropbox/OneDrive/etc.) "
                    "locking files while it syncs the build output. Pause syncing "
                    "for this folder, or move the project out of the synced "
                    "directory, then retry."
                )
                sys.exit(1)
            print(f"{path} is locked (attempt {attempt}/{attempts}), retrying...")
            time.sleep(delay)

def clean():
    """Remove previous build artifacts."""
    print("Cleaning build directories...")
    if DIST_DIR.exists():
        _rmtree_retry(DIST_DIR)
    if BUILD_DIR.exists():
        _rmtree_retry(BUILD_DIR)

def check_pyinstaller():
    """Verify PyInstaller is importable in the active environment."""
    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        print("PyInstaller is not installed in this environment.")
        print("Install dev dependencies first, e.g.:")
        print("  pip install -r requirements-dev.txt")
        sys.exit(1)

def build():
    """Run PyInstaller for the current platform."""
    check_pyinstaller()

    print(f"Running PyInstaller ({PLATFORM_TAG})...")
    # Invoke via "python -m PyInstaller" (not the "pyinstaller" console
    # script) so this always uses the active venv's interpreter,
    # regardless of whether its Scripts/bin dir is on PATH.
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--clean",
        "--distpath", str(DIST_DIR),
        "--workpath", str(BUILD_DIR),
        str(SPEC_FILE)
    ]

    result = subprocess.run(cmd)
    if result.returncode != 0:
        print("Build failed!")
        sys.exit(1)

    exe_path = DIST_DIR / "hug" / EXE_NAME
    print(f"Build successful! Executable is at {exe_path}")

    # Create Zip Archive
    print("Creating release archive...")
    archive_name = DIST_DIR / f"hug-{PLATFORM_TAG}"
    shutil.make_archive(str(archive_name), 'zip', DIST_DIR / "hug")
    print(f"Release archive created: {archive_name}.zip")

if __name__ == "__main__":
    clean()
    build()
