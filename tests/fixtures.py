"""PDF uji sintetis (tanpa data wajib pajak asli) untuk tes engine dan aplikasi.

    python tests/fixtures.py <folder>   -> bppu.pdf, bpbs.pdf, faktur.pdf, rekening.pdf, cimb.pdf
"""

import sys
from pathlib import Path

BPPU_LINES = [
    "BUKTI PEMOTONGAN DAN/ATAU PEMUNGUTAN PPh UNIFIKASI",
    "25004WOBY 01-2025 TIDAK FINAL NORMAL",
    "A.1 NPWP / NIK : 0436117337418000",
    "A.2 NAMA : MITRACOLL SARANA JAYA",
    "A.3 NOMOR IDENTITAS : 0436117337418000000000",
    "B.1 Jenis Fasilitas : Tanpa Fasilitas",
    "B.2 Jenis PPh : Pasal 23",
    "B.3 B.4 B.5 B.6 B.7",
    "24-104-18 Jasa Perantara dan/atau Keagenan 3.700.000 2 74.000",
    "B.8 Dokumen Dasar Bukti Jenis Dokumen : Surat Tagihan Tanggal : 31 Januari 2025",
    "B.9 Nomor Dokumen : 10006302",
    "B.10 Untuk Instansi Pemerintah",
    "C.1 NPWP / NIK : 0013464946091000",
    "C.3 NAMA PEMOTONG DAN/ATAU PEMUNGUT : ADIRA DINAMIKA MULTI FINANCE TBK.",
    "PPh",
    "C.4 TANGGAL : 31 Januari 2025",
    "C.5 NAMA PENANDATANGAN : I DEWA MADE SUSILA",
]
BPPU_NAME = "ADIRA DINAMIKA MULTI FINANCE TBK - 25004WOBY - 01-2025 - TIDAK FINAL - NORMAL.pdf"
BPPU_A2_NAME = "MITRACOLL SARANA JAYA - 25004WOBY - 01-2025 - TIDAK FINAL - NORMAL.pdf"

BPBS_LINES = [
    "FORMULIR BPBS",
    "H.1 NOMOR : 2 0 0 0 0 0 0 0 0 1 H.4 PPh Final",
    "H.2 Pembetulan Ke- 0 H.3 Pembatalan H.5 X PPh Tidak Final",
    "A.1 NPWP : 4 3 6 1 1 7 3 3 7 4 1 8 0 0 0",
    "A.2 NIK :",
    "A.3 Nama : MITRACOLL SARANA JAYA",
    "B. PAJAK PENGHASILAN YANG DIPOTONG/DIPUNGUT",
    "B.1 B.2 B.3 B.4 B.5 B.6",
    "1-2024 24-104-18 1.300.000,00 2.00 26.000,00",
    "Keterangan Kode Objek Pajak : Jasa Perantara dan/atau Keagenan",
    "B.7 Dokumen Referensi : Nomor Dokumen 1.3-01.24-0000407",
    "Nama Dokumen Surat Perjanjian Tanggal 3 1 dd 0 1 mm 2 0 2 4 yyyy",
    "C.1 NPWP : 0 1 3 1 6 1 1 1 2 5 0 1 0 0 1",
    "C.2 Nama Wajib Pajak : BFI FINANCE INDONESIA TBK.",
    "C.3 Tanggal : 3 1 dd 0 1 mm 2 0 2 4 yyyy",
    "C.4 Nama Penandatangan : ARIEF LUTHFI BACHTIAR",
    "C.5 Pernyataan Wajib Pajak : Dengan ini saya menyatakan",
    # Kode verifikasi di kaki formulir asli; tidak boleh terbaca sebagai nomor bukti.
    "9PT5ZJ6S dinyatakan sah dan tidak diperlukan tanda tangan basah",
]
# Nama hasil Penamaan Bupot untuk BPBS: pemotong C.2 dan wajib pajak yang dipotong A.3.
BPBS_NAME = "BFI FINANCE INDONESIA TBK - 2000000001 - 01-2024 - TIDAK FINAL - NORMAL.pdf"
BPBS_A3_NAME = "MITRACOLL SARANA JAYA - 2000000001 - 01-2024 - TIDAK FINAL - NORMAL.pdf"

FAKTUR_LINES = [
    "Faktur Pajak",
    "Kode dan Nomor Seri Faktur Pajak : 04002500000000001",
    "Pengusaha Kena Pajak:",
    "Nama : PT PENJUAL UJI",
    "NPWP : 0987654321098765",
    "Pembeli Barang Kena Pajak / Penerima Jasa Kena Pajak:",
    "Nama : PT PEMBELI UJI",
    "NPWP : 0012345678901234",
]
FAKTUR_TABLE = [
    ["No.", "Kode Barang/Jasa", ["Nama Barang Kena Pajak /", "Jasa Kena Pajak"], "Harga Jual (Rp)"],
    ["1", "000000", ["Jasa Konsultasi Pajak", "Rp 1.500.000,00 x 2,00 Jasa",
                     "Potongan Harga = Rp 0,00", "PPnBM (0,00%) = Rp 0,00"], "3.000.000,00"],
]


# e-Statement BCA sintetis: (tanggal, keterangan, keterangan lanjutan, CBG, mutasi, DB/CR, saldo).
# Baris tanpa tanggal melanjutkan keterangan transaksi sebelumnya; None = pindah halaman, sehingga
# keterangan transaksi 03/01 berlanjut ke halaman 2. Ringkasan cocok dengan transaksi.
REKENING_LINES = [
    ("01/01", "SALDO AWAL", "", "", "", "", "1,000,000.00"),
    ("02/01", "SETORAN TUNAI", "", "0473", "2,500,000.00", "", ""),
    ("02/01", "TRSF E-BANKING DB", "0201/FTSCY/WS95051", "", "750,000.00", "DB", "2,750,000.00"),
    ("", "", "750000.00", "", "", "", ""),
    ("", "", "BUDI SANTOSO", "", "", "", ""),
    ("03/01", "TRSF E-BANKING CR", "0301/FTSCY/WS95031", "", "1,234,567.89", "", "3,984,567.89"),
    ("", "", "1234567.89", "", "", "", ""),
    None,
    ("", "", "PT MITRA UJI", "", "", "", ""),
    ("31/01", "BUNGA", "", "", "1,857.12", "", ""),
    ("31/01", "PAJAK BUNGA", "", "", "371.42", "DB", "3,986,053.59"),
]
REKENING_SUMMARY = [
    ("SALDO AWAL", "1,000,000.00", ""), ("MUTASI CR", "3,736,425.01", "3"),
    ("MUTASI DB", "750,371.42", "2"), ("SALDO AKHIR", "3,986,053.59", ""),
]


# Combine Statement Portfolio CIMB Niaga sintetis (lihat write_cimb). Satu sel tabel = daftar baris
# (tanggal, valuta, uraian, no cek/BG, debit, kredit, saldo); tanggal dan nominal di baris tengah sel
# seperti aslinya. None = pindah halaman, judul tabel diulang. Laporan Januari: 31/12 milik 2024.
CIMB_MUTASI = [
    [("", "", "SALDO AWAL", "", "", "", "1,000.00")],
    [("", "", "SETORAN TUNAI", "", "", "", ""),
     ("31/12", "31/12", "CABANG CONTOH", "", "", "500.00", "1,500.00"),
     ("", "", "REF0001", "", "", "", "")],
    None,
    [("05/01", "06/01", "TARIK TUNAI", "CK001", "265.50", "", "1,234.50")],
    [("Total", "", "", "", "265.50", "500.00", "")],
    [("", "", "SALDO AKHIR", "", "", "", "1,234.50")],
]
CIMB_VALAS = [  # Tanpa transaksi bulan ini.
    [("", "", "SALDO AWAL", "", "", "", "10.00")],
    [("Total", "", "", "", "", "", "")],
    [("", "", "SALDO AKHIR", "", "", "", "10.00")],
]
CIMB_BERJANGKA = [
    [("", "", "SALDO AWAL", "", "", "", "100.00")],
    [("", "", "DIRECT DEBIT CR", "", "", "", ""),
     ("10/01", "10/01", "Deposit TRF CONTOH", "", "", "5.25", "105.25"),
     ("", "", "250110VDEP000001", "", "", "", "")],
    [("", "", "WITHHOLDING TAX", "", "", "", ""),
     ("31/01", "31/01", "DD0000000000001", "", "0.25", "", "105.00")],
    [("Total", "", "", "", "0.25", "5.25", "")],
    [("", "", "SALDO AKHIR", "", "", "", "105.00")],
]
CIMB_JATUH_TEMPO = [  # Rekening jatuh tempo: saldo di daftar aset ditulis "-".
    [("", "", "SALDO AWAL", "", "", "", "50.00")],
    [("15/01", "15/01", "PENCAIRAN", "", "50.00", "", "0.00")],
    [("Total", "", "", "", "50.00", "", "")],
    [("", "", "SALDO AKHIR", "", "", "", "0.00")],
]
# Daftar RINCIAN ASET: (nomor, produk, mata uang, saldo asal, saldo Ekuivalen IDR); kurs USD 16.000.
CIMB_DAFTAR_GIRO = [("1111222233", "TAPLUS CONTOH", "IDR", "1,234.50", "1,234.50"),
                    ("4444555566", "VALAS CONTOH USD", "USD", "10.00", "160,000.00")]
CIMB_TOTAL_GIRO = "161,234.50"
CIMB_TABEL = (43.2, 85.0, 121.0, 259.3, 332.2, 418.6, 494.1, 586.1)  # tepi kolom tabel mutasi seperti aslinya
CIMB_JUDUL_TABEL = [("Tanggal", "Tanggal", "", "", "", "", ""),
                    ("Transaksi/", "Valuta/", "Uraian Transaksi/", "No Cek/BG", "Debit/", "Kredit/", "Saldo/"),
                    ("Date", "Date", "", "", "", "", "")]


def _text(x, y, text, size=9):
    escaped = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    return f"BT /F1 {size} Tf {x} {y} Td ({escaped}) Tj ET"


def write_pdf(path, lines, table=None):
    """PDF satu halaman A4, Helvetica (metrik bawaan pdfminer), opsional tabel bergaris."""
    ops = [_text(40, 800 - 14 * index, line) for index, line in enumerate(lines)]
    if table:
        widths, row_height = (40, 110, 230, 120), 64
        top = 800 - 14 * len(lines) - 20
        for row_index, row in enumerate(table):
            x, y = 40, top - row_height * (row_index + 1)
            for width, cell in zip(widths, row):
                ops.append(f"{x} {y} {width} {row_height} re S")
                for line_index, line in enumerate(cell if isinstance(cell, list) else [cell]):
                    ops.append(_text(x + 4, y + row_height - 12 - 11 * line_index, line))
                x += width
    _write_pages(path, ["\n".join(ops)])


def write_rekening(path, lines=REKENING_LINES, summary=REKENING_SUMMARY, title="REKENING GIRO",
                   periode="JANUARI 2025", total_pages=None):
    """e-Statement BCA sintetis dengan kolom pada posisi x seperti aslinya (lihat REKENING_LINES)."""
    chunks = [[]]
    for line in lines:
        if line is None:
            chunks.append([])
        else:
            chunks[-1].append(line)
    pages = []
    for number, chunk in enumerate(chunks, 1):
        ops = [(208, 800, title), (30, 770, "PT CONTOH SEJAHTERA"), (326, 770, "NO. REKENING : 1234567890"),
               (326, 755, f"HALAMAN : {number} / {total_pages or len(chunks)}"), (326, 740, f"PERIODE : {periode}"),
               (326, 725, "MATA UANG : IDR"), (34, 690, "TANGGAL"), (163, 690, "KETERANGAN"), (309, 690, "CBG"),
               (385, 690, "MUTASI"), (504, 690, "SALDO")]
        y = 672
        for line in chunk:
            ops += [(x, y, text) for x, text in zip((46, 92, 195, 306, 380, 448, 505), line) if text]
            y -= 12
        if number < len(chunks):
            ops.append((378, y - 10, "Bersambung ke Halaman berikut"))
        else:
            for label, nilai, jumlah in summary:
                y -= 12
                ops += [(180, y - 18, f"{label} :"), (293, y - 18, nilai)] + ([(405, y - 18, jumlah)] if jumlah else [])
        pages.append("\n".join(_text(x, y, text) for x, y, text in ops))
    _write_pages(path, pages)


def write_cimb(path, mutasi=CIMB_MUTASI, daftar_giro=CIMB_DAFTAR_GIRO, total_giro=CIMB_TOTAL_GIRO,
               judul_tabel=CIMB_JUDUL_TABEL, total_pages=None, tanggal="31 January 2025"):
    """Combine Statement Portfolio CIMB Niaga sintetis: sampul, kotak kepala tiap halaman, daftar aset dan
    tabel mutasi bergaris pada posisi kolom seperti aslinya, plus deposito dan Poin Xtra yang harus diabaikan.
    Semua rekening di sini seimbang: setiap cek parser menghasilkan SESUAI."""

    def akun(norek, mata_uang, produk, rows):
        flow, chunk = [("teks", f"Nomor Rekening - Mata Uang /Account Number - Currency : {norek} - {mata_uang}"),
                       ("teks", f"Nama Produk /Product Name : {produk}")], []
        for row in [*rows, None]:
            if row is None:
                flow += [("tabel", CIMB_TABEL, [judul_tabel, *chunk]), None]
                chunk = []
            else:
                chunk.append(row)
        return flow[:-1]

    giro = (43.2, 117.2, 262.4, 338.0, 472.5, 586.1)
    berjangka = (43.2, 117.2, 145.0, 175.0, 205.0, 260.0, 310.0, 350.0, 410.0, 480.0, 586.1)
    flow = [
        ("teks", "Nasabah CIMB Preferred Yang Terhormat/ LAPORAN KONSOLIDASI PORTFOLIO /"),
        ("teks", "COMBINE STATEMENT PORTFOLIO"),
        ("teks", "Bapak/Ibu/Sir/Madam"),
        ("teks", "BUDI CONTOH"),
        ("teks", f"Tanggal Laporan : {tanggal}"),
        None,
        ("teks", "RINCIAN ASET /ASSET DETAIL"),
        ("teks", "Tabungan/Giro/Savings/Current Account"),
        ("tabel", giro, [[("Nomor Rekening /", "Nama Produk /", "Mata Uang /", "Saldo Asal /", "Saldo IDR /")],
                         *([row] for row in daftar_giro)]),
        ("teks", f"Total Tabungan / Giro / Total Saving / Current Account {total_giro}"),
        *akun("1111222233", "IDR", "TAPLUS CONTOH", mutasi),
        *akun("4444555566", "USD", "VALAS CONTOH USD", CIMB_VALAS),
        None,
        ("teks", "Tabungan Berjangka /Installment Saving"),
        ("tabel", berjangka, [
            [("Nomor Rekening /", "Mata", "Bunga", "Tenor", "Setoran Awal", "Rutin", "Tunggakan", "", "Saldo Asal",
              "Saldo IDR")],
            [("7777888899",), ("RENCANA", "USD", "5%", "3M", "100.00", "1,000", "-", "", "105.00", "1,680,000.00"),
             ("CONTOH USD",)],
            [("7777000011",), ("RENCANA", "USD", "5%", "3M", "50.00", "1,000", "-", "", "-", "-"), ("CONTOH USD",)],
        ]),
        ("teks", "TOTAL TABUNGAN BERJANGKA/TOTAL INSTALLMENT SAVINGS 1,680,000.00"),
        *akun("7777888899", "USD", "RENCANA CONTOH USD", CIMB_BERJANGKA),
        *akun("7777000011", "USD", "RENCANA CONTOH USD", CIMB_JATUH_TEMPO),
        None,
        ("teks", "Deposito /Time Deposit"),
        *akun("9999000011", "IDR", "DEPOSITO CONTOH", [[("", "", "SALDO AWAL", "", "", "", "5,000.00")]]),
        ("teks", "RINCIAN POIN XTRA /POIN XTRA DETAILS"),
        ("teks", "28 Desember CASA Pengkreditan Poin 0.00 1,000.00 17,000.00"),
    ]
    pages = [[]]
    for item in flow:
        if item is None:
            pages.append([])
        else:
            pages[-1].append(item)
    contents = []
    for number, items in enumerate(pages, 1):
        ops, y = [], 100.0  # y diukur dari atas halaman
        if number > 1:  # kotak kepala; baris tanggal laporan + CIF menutupnya
            ops += [_text(44, 792, "Tanggal Laporan Nomor CIF Profil Resiko Halaman /Page", 7),
                    _text(44, 782, "Statement Date CIF Number Risk Profile", 7),
                    _text(513, 774, f"{number}/{total_pages or len(pages)}", 7),
                    _text(44, 766, f"{tanggal} 11223344556677 Moderate", 7)]
        for kind, *data in items:
            if kind == "teks":
                ops.append(_text(44, 842 - y, data[0], 7))
                y += 14
                continue
            edges, rows = data
            garis = lambda top: [f"{a} {842 - top - 0.4:.1f} {b - a:.1f} 0.4 re f" for a, b in zip(edges, edges[1:])]
            for row in rows:
                ops += garis(y)
                y += 3
                for line in row:
                    y += 9.4
                    ops += [_text(left + 3, round(842 - y, 1), text, 7) for left, text in zip(edges, line) if text]
                y += 4
            ops += garis(y)
            y += 14
        ops.append(_text(520, 22, "123456789", 7))  # nomor dokumen di kaki halaman
        contents.append("\n".join(ops))
    _write_pages(path, contents)


def _write_pages(path, contents):
    """PDF A4 dengan satu content stream per halaman, font Helvetica sebagai /F1."""
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        None,  # /Pages, diisi setelah nomor objek halaman diketahui.
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>",
    ]
    kids = []
    for content in contents:
        stream = content.encode("latin-1")
        kids.append(b"%d 0 R" % (len(objects) + 1))
        objects.append(b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
                       b"/Resources << /Font << /F1 3 0 R >> >> /Contents %d 0 R >>" % (len(objects) + 2))
        objects.append(b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream")
    objects[1] = b"<< /Type /Pages /Kids [%s] /Count %d >>" % (b" ".join(kids), len(contents))
    data = bytearray(b"%PDF-1.4\n")
    offsets = []
    for number, obj in enumerate(objects, 1):
        offsets.append(len(data))
        data += b"%d 0 obj\n" % number + obj + b"\nendobj\n"
    xref = len(data)
    data += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objects) + 1)
    data += b"".join(b"%010d 00000 n \n" % offset for offset in offsets)
    data += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objects) + 1, xref)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_bytes(data)


def write_all(folder):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    write_pdf(folder / "bppu.pdf", BPPU_LINES)
    write_pdf(folder / "bpbs.pdf", BPBS_LINES)
    write_pdf(folder / "faktur.pdf", FAKTUR_LINES, FAKTUR_TABLE)
    write_rekening(folder / "rekening.pdf")
    write_cimb(folder / "cimb.pdf")


if __name__ == "__main__":
    write_all(sys.argv[1])
