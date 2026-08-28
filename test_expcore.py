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

    bupot2024 = """a r e a s t a p l e s
BUKTI PEMOTONGAN/PEMUNGUTAN
FORMULIR BPBS
PPh PASAL 4 AYAT (2), PASAL 15, PASAL 22, DAN PASAL 23
H.1 NOMOR : 2 0 0 0 0 0 0 0 0 1 H.4 PPh Final
KEMENTERIAN KEUANGAN RI
DIREKTORAT JENDERAL PAJAK H.2 Pembetulan Ke- 0 H.3 Pembatalan H.5 X PPh Tidak Final
A. IDENTITAS WAJIB PAJAK YANG DIPOTONG/DIPUNGUT
A.1 NPWP : 4 3 6 1 1 7 3 3 7 4 1 8 0 0 0
A.2 NIK :
A.3 Nama : MITRACOLL SARANA JAYA
B. PAJAK PENGHASILAN YANG DIPOTONG/DIPUNGUT
Masa Pajak Dikenakan Tarif Lebih PPh yang Dipotong/
(mm-yyyy) Kode Objek Pajak Dasar Pengenaan Pajak (Rp) m Ti e n m g i g li i k ( i T N id P a W k P) Tarif (%) Dipungut/DTP (Rp)
B.1 B.2 B.3 B.4 B.5 B.6
1-2024 24-104-18 1.300.000,00 2.00 26.000,00
Keterangan Kode Objek Pajak : Jasa Perantara dan/atau Keagenan
B.7 Dokumen Referensi : Nomor Dokumen 1.3-01.24-0000407
Nama Dokumen Surat Perjanjian Tanggal 3 1 dd 0 1 mm 2 0 2 4 yyyy
B.8 Dokumen Referensi untuk Faktur Pajak, apabila ada :
Nomor Faktur Pajak : Tanggal dd mm yyyy
B.9 PPh dibebankan berdasarkan Surat Keterangan Bebas (SKB).
Nomor : Tanggal dd mm yyyy
B.10 PPh yang ditanggung oleh Pemerintah (DTP) berdasarkan :
B.11 PPh dalam hal transaksi menggunakan Surat Keterangan berdasarkan PP Nomor 23 Tahun 2018 dengan Nomor :
B.12 PPh yang dipotong/dipungut yang diberikan fasilitas PPh berdasarkan:
C. IDENTITAS PEMOTONG/PEMUNGUT
C.1 NPWP : 0 1 3 1 6 1 1 1 2 5 0 1 0 0 1
C.2 Nama Wajib Pajak : BFI FINANCE INDONESIA TBK.
C.3 Tanggal : 3 1 dd 0 1 mm 2 0 2 4 yyyy
C.4 Nama Penandatangan : ARIEF LUTHFI BACHTIAR
C.5 Pernyataan Wajib Pajak : Dengan ini saya menyatakan bahwa bukti Pemotongan/Pemungutan Unifikasi telah saya isi dengan benar dan telah saya tandatangani secara
elektronik
Apabila terdapat kesalahan/pembatalan dalam pembuatan Bukti Pemotongan/Pemungutan Unifikasi yang menyebabkan kelebihan
pemotongan/pemungutan PPh atau pembayaran, atas kelebihan tersebut akan diajukan:
Pengembalian atas kelebihan pembayaran pajak yang tidak seharusnya terutang oleh Pemotong dan/atau Pemungut PPh
V Pemindahbukuan oleh Pemotong dan/atau Pemungut PPh
Sesuai dengan ketentuan yang berlaku di, Direktorat Jenderal pajak mengatur bahwa Bukti Pemotongan/Pemungutan PPh Unifikasi ini
9PT5ZJ6S dinyatakan sah dan tidak diperlukan tanda tangan basah pada Bukti Pemotongan ini."""
    rows2024 = ExpCore._extract_bupot2024_rows(bupot2024)
    assert len(rows2024) == 1, rows2024
    assert rows2024[0] == {
        "Nomor Bukti Potong": "2000000001",
        "Pembetulan Ke": 0,
        "Status Bukti": "NORMAL",
        "Sifat": "TIDAK FINAL",
        "NPWP": "436117337418000",
        "NIK": "-",
        "Nama": "MITRACOLL SARANA JAYA",
        "Masa Pajak": "01-2024",
        "Kode Objek Pajak": "24-104-18",
        "Objek Pajak": "Jasa Perantara dan/atau Keagenan",
        "DPP (Rp)": 1300000.0,
        "Tarif Lebih Tinggi": "Tidak",
        "Tarif (%)": 2.0,
        "Pajak Penghasilan (Rp)": 26000.0,
        "Nomor Dokumen Referensi": "1.3-01.24-0000407",
        "Nama Dokumen": "Surat Perjanjian",
        "Tanggal Dokumen": "31-01-2024",
        "NPWP Pemotong": "013161112501001",
        "Nama Pemotong": "BFI FINANCE INDONESIA TBK.",
        "Tanggal Bukti Potong": "31-01-2024",
        "Nama Penandatangan": "ARIEF LUTHFI BACHTIAR",
    }

    # Formulir Coretax (BPPU) tidak boleh ikut terbaca oleh parser BPBS.
    assert ExpCore._extract_bupot2024_rows(bupot) == []
    # Tanggal dengan kotak kosong menghasilkan string kosong, bukan crash.
    assert ExpCore._form_date("Tanggal dd mm yyyy") == ""
    assert ExpCore._form_date("3 1 dd 0 1 mm 2 0 2 4 yyyy") == "31-01-2024"

    print("Rekap Bukti Potong 2024: ok")


if __name__ == "__main__":
    main()
