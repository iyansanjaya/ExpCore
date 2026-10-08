"""Build installer Windows: engine Python (Nuitka) lalu aplikasi Electron (electron-builder).

Jalankan dengan interpreter venv proyek:  ./.venv/Scripts/python.exe build_release.py
Versi aplikasi, metadata exe, dan installer bersumber dari "version" di package.json.
"""

import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ENGINE_DIST = ROOT / "expcore_engine.dist"
ELECTRON_BUILDER = ROOT / "node_modules" / "electron-builder" / "cli.js"
EXPORTS = {
    "bupot": "!Hasil_Rekap_Bupot.xlsx",
    "bupot2024": "!Hasil_Rekap_Bupot_2024.xlsx",
    "pm": "Hasil_Pajak_Masukan.xlsx",
}


def app_version():
    version = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))["version"]
    # Versi file Windows: tepat tiga angka, masing-masing 0–65535.
    if not re.fullmatch(r"(0|[1-9]\d{0,4})\.(0|[1-9]\d{0,4})\.(0|[1-9]\d{0,4})", version) \
            or any(int(part) > 65535 for part in version.split(".")):
        raise ValueError(f"version di package.json harus MAJOR.MINOR.PATCH (0–65535), bukan {version!r}.")
    return version


def run_engine(engine, *args):
    result = subprocess.run([str(engine), *args], capture_output=True, timeout=300)
    events = [json.loads(line) for line in result.stdout.decode("ascii").splitlines()]
    if result.returncode != 0 or not events or events[-1]["event"] != "done":
        raise RuntimeError(f"Engine gagal: {args}\n{events}\n{result.stderr.decode('utf-8', 'replace')}")
    return events[-1]


def check_engine(engine):
    """Keempat pekerjaan pada PDF sintetis: import lazy (mis. writer Excel) ikut teruji."""
    from tests.fixtures import BPPU_NAME, write_all

    with tempfile.TemporaryDirectory() as temp:
        folder = Path(temp) / "uji build"
        write_all(folder)
        for job, output in EXPORTS.items():
            done = run_engine(engine, job, str(folder))
            if done["path"] != str(folder / output) or done["summary"] != "Selesai — 1 baris, 2 PDF dilewati.":
                raise RuntimeError(f"Hasil {job} tidak sesuai: {done}")
        run_engine(engine, "rename", str(folder))
        run_engine(engine, "rename", str(folder), "--apply")
        if not (folder / BPPU_NAME).is_file():
            raise RuntimeError("Penamaan pada engine hasil build tidak berjalan.")


def build_engine(version):
    # Import yang gagal harus menghentikan build, bukan menghasilkan engine yang rusak.
    subprocess.run([sys.executable, "-c", "import pdfplumber, pandas, openpyxl, nuitka"], check=True)
    shutil.rmtree(ENGINE_DIST, ignore_errors=True)
    subprocess.run([
        sys.executable, "-m", "nuitka", "--mode=standalone", "--assume-yes-for-downloads",
        # Konsol tetap tersembunyi: Electron menjalankan engine dengan windowsHide.
        "--windows-console-mode=force", "--windows-icon-from-ico=icon.ico",
        "--company-name=Iyan App", "--product-name=ExpCore", "--file-description=ExpCore PDF engine",
        f"--product-version={version}", f"--file-version={version}",
        "--copyright=Copyright (c) 2026 Iyan Sanjaya", "expcore_engine.py",
    ], cwd=ROOT, check=True)
    check_engine(ENGINE_DIST / "expcore_engine.exe")


def build_app(version):
    node, npm = shutil.which("node"), shutil.which("npm")
    if not node or not npm or not ELECTRON_BUILDER.is_file():
        raise RuntimeError("Node.js dan dependency npm belum tersedia. Jalankan: npm ci")
    # Renderer (Tailwind + esbuild) dibangun ulang agar paket tidak memuat CSS/JS lama.
    subprocess.run([npm, "run", "build:renderer"], cwd=ROOT, check=True)
    subprocess.run([node, str(ELECTRON_BUILDER), "--win", "--x64", "--publish", "never"], cwd=ROOT, check=True)
    dist = ROOT / "dist"
    asar = subprocess.run([node, "-e", "console.log(JSON.stringify(require('@electron/asar').listPackage(process.argv[1])))",
                           str(dist / "win-unpacked" / "resources" / "app.asar")], cwd=ROOT, check=True,
                          capture_output=True, text=True)
    packed = {path.replace("\\", "/") for path in json.loads(asar.stdout)}
    missing = {"/app/renderer/dist/app.js", "/app/renderer/dist/styles.css", "/app/renderer/index.html"} - packed
    if missing or any(path.startswith("/app/renderer/src") for path in packed):
        raise RuntimeError(f"Isi app.asar tidak sesuai: hilang {sorted(missing)}, atau sumber renderer ikut terbawa.")
    installer = dist / f"ExpCore-Setup-{version}.exe"
    for path in (dist / "win-unpacked" / "ExpCore.exe", dist / "win-unpacked" / "resources" / "engine" / "expcore_engine.exe",
                 installer, dist / f"{installer.name}.blockmap"):
        if not path.is_file():
            raise RuntimeError(f"Artefak build tidak ditemukan: {path}")
    latest = (dist / "latest.yml").read_text(encoding="utf-8")
    if f"version: {version}\n" not in latest or f"path: {installer.name}\n" not in latest:
        raise RuntimeError("latest.yml tidak sesuai dengan versi build.")
    return installer


def main():
    version = app_version()
    if "--app-only" not in sys.argv:
        build_engine(version)
    elif not (ENGINE_DIST / "expcore_engine.exe").is_file():
        raise RuntimeError("--app-only memerlukan expcore_engine.dist dari build sebelumnya.")
    installer = build_app(version)
    print(f"\nExpCore {version} siap dirilis. Unggah ketiga file ini ke GitHub Release v{version}:")
    for name in (installer.name, f"{installer.name}.blockmap", "latest.yml"):
        print(f"  dist/{name}")


if __name__ == "__main__":
    main()
