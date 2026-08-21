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

    # Label "PEMUNGUT PPh" terpotong baris — sisa "PPh" tidak boleh ikut nama.
    wrapped = """25004WOBY 01-2025 TIDAK FINAL NORMAL
C.3 NAMA PEMOTONG DAN/ATAU PEMUNGUT : ADIRA DINAMIKA MULTI FINANCE TBK.
PPh
C.4 TANGGAL : 31 Januari 2025"""
    assert ExpCore._extract_rename_bupot_data(wrapped)["NAMA_PEMOTONG"] == \
        "ADIRA DINAMIKA MULTI FINANCE TBK."

    bupot = """25004WOBY 01-2025 TIDAK FINAL NORMAL
A.1 NPWP / NIK : 0436117337418000
A.2 NAMA : MITRACOLL SARANA JAYA
A.3 NOMOR IDENTITAS : 0436117337418000000000
B.1 Jenis Fasilitas : Tanpa Fasilitas
B.2 Jenis PPh : Pasal 23
B.3 B.4 B.5 B.6 B.7
24-104-18 Jasa Perantara dan/atau Keagenan 3.700.000 2 74.000
B.8 Dokumen Dasar Bukti Jenis Dokumen : Surat Tagihan Tanggal : 31 Januari 2025
Pemotongan dan/atau Pemungutan PPh Unifikasi
B.9 Nomor Dokumen : 10006302
B.10 Untuk Instansi Pemerintah
C.1 NPWP / NIK : 0013464946091000
C.3 NAMA PEMOTONG DAN/ATAU PEMUNGUT : ADIRA DINAMIKA MULTI FINANCE TBK.
PPh
C.4 TANGGAL : 31 Januari 2025
C.5 NAMA PENANDATANGAN : I DEWA MADE SUSILA"""
    rows = ExpCore._extract_bupot_rows(bupot)
    assert len(rows) == 1, rows
    assert rows[0] == {
        "Nomor Dokumen": "25004WOBY", "Masa Pajak": "01-2025",
        "NPWP/NIK": "0436117337418000", "Nama": "MITRACOLL SARANA JAYA",
        "Status Bukti": "NORMAL", "Jenis Fasilitas": "Tanpa Fasilitas",
        "Jenis PPh": "Pasal 23", "Kode Objek Pajak": "24-104-18",
        "Objek Pajak": "Jasa Perantara dan/atau Keagenan",
        "DPP (Rp)": 3700000.0, "Tarif (%)": 2.0, "Pajak Penghasilan (Rp)": 74000.0,
        "Jenis Dokumen": "Surat Tagihan", "Nomor Dokumen Dasar": "10006302",
        "Tanggal Dokumen": "31 Januari 2025",
        "NPWP/NIK Pemotong": "0013464946091000",
        "Nama Pemotong": "ADIRA DINAMIKA MULTI FINANCE TBK.",
        "Tanggal Bukti Potong": "31 Januari 2025",
    }

    print("Rekap Bukti Potong: ok")


if __name__ == "__main__":
    main()
