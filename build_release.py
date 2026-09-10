"""Build the Windows application using the invoking virtual environment."""

from pathlib import Path
import subprocess
import sys

from expcore_updates import APP_VERSION, version_tuple


def main():
    root = Path(__file__).resolve().parent
    if len(APP_VERSION.split(".")) != 3 or APP_VERSION.startswith("v") or any(n > 65535 for n in version_tuple(APP_VERSION)):
        raise ValueError("VERSION harus MAJOR.MINOR.PATCH, setiap angka 0–65535.")
    # Import failures must stop the build, not produce a broken distributable.
    subprocess.run([sys.executable, "-c", "import customtkinter, pdfplumber, pandas, openpyxl, nuitka"], check=True)
    subprocess.run([
        sys.executable, "-m", "nuitka", "--mode=standalone", "--windows-console-mode=disable",
        "--assume-yes-for-downloads",
        "--enable-plugin=tk-inter", "--include-data-files=icon.ico=icon.ico",
        "--include-data-files=icon.png=icon.png", "--include-data-files=VERSION=VERSION",
        "--windows-icon-from-ico=icon.ico", f"--product-version={APP_VERSION}",
        f"--file-version={APP_VERSION}", "ExpCore.py",
    ], cwd=root, check=True)
    bundled_version = (root / "ExpCore.dist" / "VERSION").read_text(encoding="utf-8").strip()
    if bundled_version != APP_VERSION:
        raise RuntimeError("Versi yang dibundel tidak sesuai.")
    print(f"ExpCore {APP_VERSION} siap dibuat installer dengan ExpCore.iss.")


if __name__ == "__main__":
    main()
