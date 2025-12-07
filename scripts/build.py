"""Build script for HuG."""
import os
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / "build"
SPEC_FILE = PROJECT_ROOT / "package" / "hug.spec"

def clean():
    """Remove previous build artifacts."""
    print("Cleaning build directories...")
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)

def build():
    """Run PyInstaller."""
    print("Running PyInstaller...")
    cmd = [
        "pyinstaller",
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
        
    print(f"Build successful! Executable is in {DIST_DIR / 'hug'}")

    # Create Zip Archive
    print("Creating release archive...")
    archive_name = DIST_DIR / "hug-linux"
    shutil.make_archive(str(archive_name), 'zip', DIST_DIR / "hug")
    print(f"Release archive created: {archive_name}.zip")

if __name__ == "__main__":
    clean()
    build()
