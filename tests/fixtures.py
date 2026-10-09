"""PDF uji sintetis (tanpa data wajib pajak asli) untuk tes engine dan aplikasi.

    python tests/fixtures.py <folder>   -> bppu.pdf, bpbs.pdf, faktur.pdf, rekening.pdf
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
]

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


def _text(x, y, text):
    escaped = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    return f"BT /F1 9 Tf {x} {y} Td ({escaped}) Tj ET"


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


if __name__ == "__main__":
    write_all(sys.argv[1])
