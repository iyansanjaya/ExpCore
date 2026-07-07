import os
import tempfile

from ExpCore import ExpCore


def main():
    text = """2505Z0UR6 10-2025 TIDAK FINAL PEMBETULAN KE-2
C.3 NAMA PEMOTONG : PT CONTOH: ABADI
C.4 TANGGAL : 7 Juli 2026"""
    assert ExpCore._extract_rename_bupot_data(text) == {
        "NAMA_PEMOTONG": "PT CONTOH: ABADI",
        "NOMOR_BUKTI": "2505Z0UR6",
        "MASA_PAJAK": "10-2025",
        "SIFAT": "TIDAK FINAL",
        "STATUS": "PEMBETULAN KE-2",
    }
    assert ExpCore._safe_filename("PT: CONTOH?") == "PT CONTOH"

    fallback = """ABC12345
11-2025
FINAL
DIBATALKAN
C.3 NAMA PEMOTONG : CV FALLBACK
C.4 TANGGAL : 7 Juli 2026"""
    assert ExpCore._extract_rename_bupot_data(fallback) == {
        "NAMA_PEMOTONG": "CV FALLBACK",
        "NOMOR_BUKTI": "ABC12345",
        "MASA_PAJAK": "11-2025",
        "SIFAT": "FINAL",
        "STATUS": "DIBATALKAN",
    }

    with tempfile.TemporaryDirectory() as folder:
        path = os.path.join(folder, "Bupot.pdf")
        open(path, "w").close()
        assert ExpCore._unique_filename(path).endswith("Bupot (2).pdf")

    print("Penamaan Otomatis Bupot: ok")


if __name__ == "__main__":
    main()
