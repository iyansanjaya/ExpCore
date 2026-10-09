import csv
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, Mock, patch

import pdfplumber
from openpyxl import load_workbook

from ExpCore import ExpCore
from tests.fixtures import BPPU_NAME, write_all

ROOT = Path(__file__).resolve().parent


def run_engine(*args):
    result = subprocess.run([sys.executable, str(ROOT / "expcore_engine.py"), *args],
                            capture_output=True, timeout=120)
    # Protokol wajib ASCII murni; decode("ascii") gagal bila ada keluaran liar.
    events = [json.loads(line) for line in result.stdout.decode("ascii").splitlines()]
    return result.returncode, events, result.stderr.decode("utf-8", "replace")


def sheet_row(path):
    book = load_workbook(path)
    try:
        sheet = book.active
        assert sheet.max_row == 2, sheet.max_row
        return dict(zip((c.value for c in sheet[1]), (c.value for c in sheet[2])))
    finally:
        book.close()


def test_engine_protocol():
    """Engine JSON: tiga ekspor + penamaan pada PDF sintetis, folder Unicode, PDF rusak, argumen."""
    with tempfile.TemporaryDirectory() as temp:
        folder = Path(temp) / "Bupot Ünïcode — 2026 (uji)"
        write_all(folder / "sub")
        (folder / "rusak.pdf").write_bytes(b"corrupt")
        single = "Selesai — 1 baris, 4 PDF dilewati."
        exports = {
            "bupot": ("!Hasil_Rekap_Bupot.xlsx", single, {"Nomor Dokumen": "25004WOBY", "DPP (Rp)": 3700000}),
            "bupot2024": ("!Hasil_Rekap_Bupot_2024.xlsx", single, {"Nomor Bukti Potong": "2000000001", "Tarif (%)": 2}),
            "pm": ("Hasil_Pajak_Masukan.xlsx", single,
                   {"NPWP Pembeli": "0012345678901234", "DPP": 3000000, "PPN": 360000}),
            "rekening": ("!Hasil_Rekap_Rekening_Koran.xlsx",
                         "Selesai — 1 rekening koran, 5 transaksi, 0 perlu dicek, 4 PDF dilewati.",
                         {"No. Rekening": "1234567890", "Mutasi CR": 3736425.01, "Hasil Cek": "SESUAI"}),
        }
        for job, (output, summary, expected) in exports.items():
            code, events, stderr = run_engine(job, str(folder))
            assert code == 0, (job, events, stderr)
            assert events[0] == {"event": "log", "message": "Memproses 5 file …"}, events[0]
            progress = [e for e in events if e["event"] == "progress"]
            assert progress == [{"event": "progress", "done": i, "total": 5} for i in range(5)], progress
            assert sum(e["event"] in ("done", "error") for e in events) == 1, events
            assert events[-1]["event"] == "done" and events[-1]["path"] == str(folder / output), events[-1]
            assert events[-1]["summary"] == summary, events[-1]
            values = sheet_row(events[-1]["path"])
            assert values["Folder Sumber"] == "sub", values
            for column, value in expected.items():
                assert values[column] == value, (job, column, values[column])

        code, events, _ = run_engine("rename", str(folder))
        assert code == 0 and events[-1]["summary"] == (
            "Pratinjau selesai — 1 siap/berhasil, 0 sudah sesuai, 3 perlu diperiksa, 1 gagal."), events[-1]
        assert events[0]["message"] == "Pratinjau: memeriksa 5 PDF … (nama dari Identitas Pemotong (C.3))", events[0]
        assert (folder / "sub" / "bppu.pdf").exists(), "Pratinjau tidak boleh mengubah nama file"
        code, events, _ = run_engine("rename", str(folder), "--apply")
        assert code == 0 and events[-1]["summary"].startswith("Penerapan selesai — 1 siap/berhasil"), events[-1]
        assert (folder / "sub" / BPPU_NAME).exists() and not (folder / "sub" / "bppu.pdf").exists()
        assert Path(events[-1]["path"]).name.startswith("Log_Penamaan_Bupot_Penerapan_")
        code, events, _ = run_engine("rename", str(folder))
        assert "0 siap/berhasil, 1 sudah sesuai" in events[-1]["summary"], events[-1]
        # Sumber nama A.2: pratinjau memakai nama wajib pajak yang dipotong, file tidak berubah.
        code, events, _ = run_engine("rename", str(folder), "--nama", "penerima")
        assert code == 0 and "1 siap/berhasil, 0 sudah sesuai" in events[-1]["summary"], events[-1]
        with open(events[-1]["path"], encoding="utf-8-sig", newline="") as log:
            ready = [row for row in csv.DictReader(log) if row["status"] == "SIAP"]
        assert [(row["nama_baru"], row["sumber_nama"]) for row in ready] == [
            ("MITRACOLL SARANA JAYA - 25004WOBY - 01-2025 - TIDAK FINAL - NORMAL.pdf", "Wajib Pajak yang Dipotong (A.2)")]
        assert (folder / "sub" / BPPU_NAME).exists()

        # Kegagalan menulis hasil menjadi event error, bukan crash diam-diam.
        (folder / "!Hasil_Rekap_Bupot.xlsx").unlink()
        (folder / "!Hasil_Rekap_Bupot.xlsx").mkdir()
        code, events, stderr = run_engine("bupot", str(folder))
        assert code == 1 and events[-1]["event"] == "error" and "Traceback" in stderr, (events, stderr)
        assert events[-2]["message"].startswith("Error: "), events[-2]

        empty = Path(temp) / "kosong"
        empty.mkdir()
        for path, message in ((empty, "Tidak ada PDF di folder atau subfolder ini. Pilih folder lain."),
                              (Path(temp) / "tidak-ada", "Folder tidak ditemukan. Pilih folder yang tersedia.")):
            assert run_engine("pm", str(path))[:2] == (1, [{"event": "error", "message": message}])
        for args in (("bupot", str(folder), "--apply"), ("lainnya", str(folder)), ("bupot",),
                     ("rekening", str(folder), "--nama", "penerima"), ("rename", str(folder), "--nama", "C.3")):
            code, events, stderr = run_engine(*args)
            assert (code, events) == (2, []) and "usage" in stderr, (args, code, events)
    print("Engine: protokol JSON, empat ekspor, penamaan (C.3/A.2), Unicode, PDF rusak dan argumen OK")


def test_batch_exports():
    """All three workers export valid PDFs despite a corrupt sibling PDF."""
    for method, parser in (
        ("process_bupot", "_extract_bupot_rows"),
        ("process_bupot_2024", "_extract_bupot2024_rows"),
        ("process_pm", None),
    ):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder)
            (source / "sub").mkdir()
            (source / "broken.pdf").write_bytes(b"corrupt")
            (source / "sub" / "valid.pdf").write_bytes(b"fixture")
            page = SimpleNamespace(
                extract_text=lambda: "Pembeli Barang Kena Pajak\nNama : PT UJI\nNPWP : 0012345678901234\n"
                                     "Kode dan Nomor Seri Faktur Pajak : 0100000000000001",
                extract_tables=lambda: [[["1", "123456", "Jasa Uji Rp 1.000,00 x 2 Unit"]]],
            )
            worker = SimpleNamespace(progress=Mock(), log=Mock(), _write_excel=ExpCore._write_excel)
            if parser:
                setattr(worker, parser, lambda text: [{"NPWP": "0012345678901234", "DPP (Rp)": 2000.0}])
            good_pdf = MagicMock()
            good_pdf.__enter__.return_value = SimpleNamespace(pages=[page])
            with patch("ExpCore.pdfplumber.open", side_effect=[ValueError("corrupt PDF"), good_pdf]):
                output, summary = getattr(ExpCore, method)(worker, folder)
            assert "1 baris, 1 PDF dilewati" in summary, summary
            book = load_workbook(output)
            sheet = book.active
            assert sheet.max_row == 2
            values = dict(zip((c.value for c in sheet[1]), (c.value for c in sheet[2])))
            assert values["Folder Sumber"] == "sub"
            if method == "process_pm":
                assert values["NPWP Pembeli"] == "0012345678901234"
                assert values["DPP"] == 2000 and values["PPN"] == 240
            else:
                assert values["NPWP"] == "0012345678901234"
            book.close()
            assert (source / "broken.pdf").read_bytes() == b"corrupt"
            assert (source / "sub" / "valid.pdf").read_bytes() == b"fixture"
            assert worker.progress.call_count == 2
    print("Batch workers: corrupted PDF recovery, subfolders and three Excel exports OK")


def test_rename_pemotong():
    # Teks berdasarkan contoh BPPU: nama A.2 berbeda dari pemotong C.3.
    text = """26007GORO 01-2026 FINAL NORMAL
A.1 NPWP / NIK : 0026264515077000
A.2 NAMA : PLAZA LIFESTYLE PRIMA
A.3 NOMOR IDENTITAS TEMPAT KEGIATAN USAHA (NITKU) : 0026264515077000000000 - PLAZA LIFESTYLE PRIMA
C.3 NAMA PEMOTONG DAN/ATAU PEMUNGUT : VOLANS
PPh
C.4 TANGGAL : 31 Januari 2026"""
    data = ExpCore._extract_rename_bupot_data(text)
    assert data["NAMA_PENERIMA"] == "PLAZA LIFESTYLE PRIMA", data
    assert data["NAMA_PEMOTONG"] == "VOLANS", data

    wrapped = text.replace("A.2 NAMA : PLAZA LIFESTYLE PRIMA",
                           "A.2 NAMA :\nPLAZA LIFESTYLE\nPRIMA")
    assert ExpCore._extract_rename_bupot_data(wrapped)["NAMA_PENERIMA"] == \
        "PLAZA LIFESTYLE PRIMA"
    blank = text.replace("A.2 NAMA : PLAZA LIFESTYLE PRIMA", "A.2 NAMA :")
    absent = text.replace("A.2 NAMA : PLAZA LIFESTYLE PRIMA\n", "")
    for incomplete in (blank, absent):
        assert ExpCore._extract_rename_bupot_data(incomplete)["NAMA_PENERIMA"] == ""

    without_pemotong = text[:text.index("C.3")]
    blank_pemotong = text.replace(": VOLANS", ":")
    wrapped_pemotong = text.replace(": VOLANS", ":\nVOLANS")
    # Sumber nama -> (field, label CSV, nama file, teks yang nama sumbernya kosong). Tanpa fallback:
    # A.2 kosong tidak boleh diganti C.3, dan sebaliknya.
    sources = {
        "pemotong": ("NAMA_PEMOTONG", "Identitas Pemotong (C.3)", "VOLANS - 26007GORO - 01-2026 - FINAL - NORMAL.pdf",
                     (without_pemotong, blank_pemotong)),
        "penerima": ("NAMA_PENERIMA", "Wajib Pajak yang Dipotong (A.2)",
                     "PLAZA LIFESTYLE PRIMA - 26007GORO - 01-2026 - FINAL - NORMAL.pdf", (blank, absent)),
    }
    for source, (field, label, expected_name, incomplete) in sources.items():
        for pdf_text in (text, wrapped, wrapped_pemotong, without_pemotong, blank_pemotong, blank, absent):
            complete = pdf_text not in incomplete
            for apply_changes in (False, True):
                with tempfile.TemporaryDirectory() as folder:
                    original = os.path.join(folder, "original.pdf")
                    with open(original, "wb") as pdf_file:
                        pdf_file.write(b"test PDF placeholder")
                    app = SimpleNamespace(
                        progress=Mock(), log=Mock(),
                        _extract_rename_bupot_data=ExpCore._extract_rename_bupot_data,
                        _safe_filename=ExpCore._safe_filename,
                        _unique_filename=ExpCore._unique_filename,
                    )
                    pdf = SimpleNamespace(pages=[SimpleNamespace(extract_text=lambda: pdf_text)])
                    with patch("ExpCore.pdfplumber.open") as open_pdf:
                        open_pdf.return_value.__enter__.return_value = pdf
                        result_path, summary = ExpCore.process_rename_bupot(
                            app, folder, apply_changes=apply_changes, name_source=source)
                        assert Path(result_path).is_file()
                        assert "selesai" in summary
                    assert label in app.log.call_args_list[0].args[0], app.log.call_args_list[0]

                    csv_name, = [name for name in os.listdir(folder) if name.endswith(".csv")]
                    with open(os.path.join(folder, csv_name), encoding="utf-8-sig", newline="") as log:
                        row, = list(csv.DictReader(log))
                    assert row["sumber_nama"] == label, row
                    assert row["NAMA_PEMOTONG"] == ("" if pdf_text in (without_pemotong, blank_pemotong) else "VOLANS")
                    assert row["NAMA_PENERIMA"] == ("" if pdf_text in (blank, absent) else "PLAZA LIFESTYLE PRIMA"), row
                    if complete:
                        assert row["nama_baru"] == expected_name, (source, row)
                        assert row["status"] == ("BERHASIL" if apply_changes else "SIAP"), row
                        assert row["data_tidak_lengkap"] == "", row
                    else:
                        assert row["status"] == ("DILEWATI" if apply_changes else "PERLU CEK"), row
                        assert row["data_tidak_lengkap"] == field, row
                    assert os.path.exists(original) == (not (complete and apply_changes))
                    assert os.path.exists(os.path.join(folder, expected_name)) == (complete and apply_changes)

    try:
        ExpCore.process_rename_bupot(SimpleNamespace(), ".", name_source="C.3")
        raise AssertionError("sumber nama tidak dikenal harus ditolak")
    except ValueError as error:
        assert "Sumber nama tidak dikenal" in str(error)

    print("Rename Bupot: sumber nama C.3 dan A.2 (pratinjau dan penerapan, tanpa fallback): ok")


def read_rekening(path):
    with pdfplumber.open(path) as pdf:
        return ExpCore._extract_rekening_koran(pdf.pages)


def test_rekening_koran():
    """e-Statement BCA: kolom dari posisi x, debit bertanda DB, ringkasan terpisah dan dicocokkan."""
    from datetime import datetime
    from decimal import Decimal

    from tests.fixtures import REKENING_LINES, REKENING_SUMMARY, write_rekening

    with tempfile.TemporaryDirectory() as temp:
        temp = Path(temp)

        def variant(name, **options):
            path = temp / f"{name}.pdf"
            write_rekening(path, **options)
            return read_rekening(path)

        data = variant("asli")
        assert {k: data[k] for k in ("jenis", "norek", "nama", "periode", "mata_uang", "catatan")} == {
            "jenis": "REKENING GIRO", "norek": "1234567890", "nama": "PT CONTOH SEJAHTERA",
            "periode": "JANUARI 2025", "mata_uang": "IDR", "catatan": []}, data
        D = Decimal
        assert data["transaksi"] == [
            {"tanggal": datetime(2025, 1, 2), "keterangan": "SETORAN TUNAI", "cbg": "0473",
             "debit": None, "kredit": D("2500000.00"), "saldo": None},
            {"tanggal": datetime(2025, 1, 2), "keterangan": "TRSF E-BANKING DB 0201/FTSCY/WS95051 750000.00 BUDI SANTOSO",
             "cbg": "", "debit": D("750000.00"), "kredit": None, "saldo": D("2750000.00")},
            # Keterangan berlanjut ke halaman 2 tetap milik transaksi yang sama.
            {"tanggal": datetime(2025, 1, 3), "keterangan": "TRSF E-BANKING CR 0301/FTSCY/WS95031 1234567.89 PT MITRA UJI",
             "cbg": "", "debit": None, "kredit": D("1234567.89"), "saldo": D("3984567.89")},
            {"tanggal": datetime(2025, 1, 31), "keterangan": "BUNGA", "cbg": "",
             "debit": None, "kredit": D("1857.12"), "saldo": None},
            {"tanggal": datetime(2025, 1, 31), "keterangan": "PAJAK BUNGA", "cbg": "",
             "debit": D("371.42"), "kredit": None, "saldo": D("3986053.59")},
        ], data["transaksi"]
        assert data["ringkasan"] == {"SALDO AWAL": (D("1000000.00"), None), "MUTASI CR": (D("3736425.01"), 3),
                                     "MUTASI DB": (D("750371.42"), 2), "SALDO AKHIR": (D("3986053.59"), None)}

        # Mutasi bulan sebelumnya pada periode Januari milik tahun sebelumnya.
        rollover = [line if line is None or line[0] != "02/01" or line[1] != "SETORAN TUNAI"
                    else ("31/12", *line[1:]) for line in REKENING_LINES]
        data = variant("tahun", lines=rollover)
        assert data["transaksi"][0]["tanggal"] == datetime(2024, 12, 31) and data["catatan"] == [], data

        # Setiap ketidakcocokan tercatat; tidak ada yang lolos sebagai SESUAI.
        no_db = [line if line is None or line[1] != "PAJAK BUNGA" else (*line[:5], "", line[6])
                 for line in REKENING_LINES]
        wrong_total = [row if row[0] != "MUTASI CR" else ("MUTASI CR", "3,736,425.00", "3") for row in REKENING_SUMMARY]
        odd_saldo = [line if line is None or line[1] != "PAJAK BUNGA" else (*line[:6], "-3,986,053.59")
                     for line in REKENING_LINES]
        for name, options, expected in (
            ("tanpa-db", {"lines": no_db}, ["Kredit terbaca 3,736,796.43 dari 4 transaksi, ringkasan PDF "
                                            "3,736,425.01 dari 3.", "Debit terbaca 750,000.00 dari 1 transaksi, "
                                            "ringkasan PDF 750,371.42 dari 2.",
                                            "31/01: saldo PDF 3,986,053.59, hasil hitung 3,986,796.43."]),
            ("total", {"summary": wrong_total}, ["Kredit terbaca 3,736,425.01 dari 3 transaksi, ringkasan PDF "
                                                 "3,736,425.00 dari 3.", "Ringkasan PDF tidak seimbang: saldo awal "
                                                 "+ mutasi CR − mutasi DB ≠ saldo akhir."]),
            ("tanpa-ringkasan", {"summary": []}, ["Ringkasan saldo dan mutasi di akhir PDF tidak lengkap."]),
            ("halaman", {"total_pages": 3}, ["PDF hanya berisi 2 dari 3 halaman."]),
            ("saldo-aneh", {"lines": odd_saldo}, ["Halaman 2: teks tak dikenal di kolom tanggal/angka: -3,986,053.59"]),
        ):
            assert variant(name, **options)["catatan"] == expected, (name, variant(name, **options)["catatan"])

        # PDF lain (bukan e-Statement BCA) dilewati.
        write_all(temp / "lain")
        for name in ("bppu", "bpbs", "faktur"):
            assert read_rekening(temp / "lain" / f"{name}.pdf") is None, name

        # Rekap folder: Ringkasan + sheet per PDF urut rekening/periode, PDF lain & rusak dilewati.
        folder = temp / "Rekening Ünïcode"
        write_rekening(folder / "b" / "feb.pdf", periode="FEBRUARI 2025")
        write_rekening(folder / "a" / "jan.pdf")
        write_rekening(folder / "a" / "jan salinan.pdf")
        write_rekening(folder / "tahapan.pdf", title="REKENING TAHAPAN", summary=wrong_total)
        write_all(folder / "lain")
        (folder / "lain" / "rekening.pdf").unlink()
        (folder / "rusak.pdf").write_bytes(b"corrupt")
        app = ExpCore(log=Mock(), progress=Mock())
        output, summary = app.process_rekening_koran(str(folder))
        assert summary == "Selesai — 4 rekening koran, 20 transaksi, 1 perlu dicek, 4 PDF dilewati.", summary
        logs = [call.args[0] for call in app.log.call_args_list]
        assert ("PERINGATAN: REKENING GIRO 1234567890 periode 01-2025 muncul di 2 PDF: jan salinan.pdf, jan.pdf"
                in logs), logs
        assert "DILEWATI: lain\\faktur.pdf — bukan e-Statement Rekening Giro/Tahapan BCA." in logs, logs

        book = load_workbook(output)
        try:
            assert book.sheetnames == ["Ringkasan", "Giro 1234567890 2025-01", "Giro 1234567890 2025-01 (2)",
                                       "Giro 1234567890 2025-02", "Tahapan 1234567890 2025-01"], book.sheetnames
            overview = [[cell.value for cell in row] for row in book["Ringkasan"].iter_rows()]
            assert overview[0][:8] == ["No", "Sheet", "Jenis Rekening", "No. Rekening", "Nama", "Periode",
                                       "Mata Uang", "Saldo Awal"], overview[0]
            assert overview[1] == [1, "Giro 1234567890 2025-01", "REKENING GIRO", "1234567890", "PT CONTOH SEJAHTERA",
                                   "JANUARI 2025", "IDR", 1000000, 3736425.01, 3, 750371.42, 2, 3986053.59, 5,
                                   "SESUAI", None, "a", "jan salinan.pdf"], overview[1]
            assert [row[14] for row in overview[1:]] == ["SESUAI", "SESUAI", "SESUAI", "PERLU CEK"]
            assert overview[4][15].startswith("Kredit terbaca 3,736,425.01 dari 3 transaksi"), overview[4]
            assert book["Ringkasan"]["B2"].hyperlink.location == "'Giro 1234567890 2025-01'!A1"

            sheet = book["Giro 1234567890 2025-02"]
            table = [[cell.value for cell in row[:6]] for row in sheet.iter_rows(max_row=6)]
            assert table[0] == ["TANGGAL", "KETERANGAN", "CBG", "DEBIT", "CREDIT", "SALDO"]
            assert table[1] == [datetime(2025, 1, 2), "SETORAN TUNAI", "0473", None, 2500000, None], table[1]
            assert table[5] == [datetime(2025, 1, 31), "PAJAK BUNGA", None, 371.42, None, 3986053.59], table[5]
            assert sheet.max_row == 16 and sheet["A7"].value is None, "ringkasan tidak boleh di bawah tabel"
            assert (sheet["A2"].number_format, sheet["C2"].number_format, sheet["D3"].number_format) == (
                "dd/mm/yyyy", "@", "#,##0.00")
            assert sheet.freeze_panes == "A2" and sheet.auto_filter.ref == "A1:F6"
            panel = [[cell.value for cell in row] for row in sheet.iter_rows(min_row=9, max_row=16, min_col=8, max_col=10)]
            assert panel == [["RINGKASAN PDF", "NILAI", "TRANSAKSI"], ["SALDO AWAL", 1000000, None],
                             ["MUTASI CR", 3736425.01, 3], ["MUTASI DB", 750371.42, 2],
                             ["SALDO AKHIR", 3986053.59, None], [None, None, None],
                             ["HASIL CEK", None, None], ["SESUAI", None, None]], panel
            assert sheet["I3"].value == "1234567890" and sheet["I5"].value == "FEBRUARI 2025"
            flagged = book["Tahapan 1234567890 2025-01"]
            assert flagged["H16"].value == "PERLU CEK" and flagged["H17"].value.startswith("• Kredit terbaca")
        finally:
            book.close()

        # Nama sheet maks. 31 karakter: jenis rekening yang dipotong, nomor dan periode tetap utuh.
        long_title = temp / "judul panjang"
        write_rekening(long_title / "x.pdf", title="REKENING TAHAPAN XPRESI PLUS")
        book = load_workbook(ExpCore(log=Mock(), progress=Mock()).process_rekening_koran(str(long_title))[0])
        assert book.sheetnames == ["Ringkasan", "Tahapan Xpre 1234567890 2025-01"], book.sheetnames
        book.close()

        empty = temp / "bukan-rekening"
        write_all(empty)
        (empty / "rekening.pdf").unlink()
        assert ExpCore(log=Mock(), progress=Mock()).process_rekening_koran(str(empty))[0] is None
    print("Rekening koran: kolom posisi, debit DB, lintas halaman, cek ringkasan & saldo, Excel: ok")


def test_pdf_samples():
    """Regresi opsional pada PDF contoh lokal di contoh-pdf/ (PDF asli tidak diubah)."""
    import shutil

    root = Path(__file__).parent / "contoh-pdf"

    def text(path):
        with pdfplumber.open(path) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)

    assert len(ExpCore._extract_bupot2024_rows(text(root / "BUPOT 2024" / "BUPOT 2024.pdf"))) == 1
    bupot = root / "BUPOT 2026" / "BUPOT 2026.pdf"
    assert len(ExpCore._extract_bupot_rows(text(bupot))) == 1
    with tempfile.TemporaryDirectory() as folder:
        shutil.copy(bupot, folder)
        for source, name in (("pemotong", "ADIRA DINAMIKA MULTI FINANCE TBK"), ("penerima", "MITRACOLL SARANA JAYA")):
            log_path, _ = ExpCore().process_rename_bupot(folder, name_source=source)
            with open(log_path, encoding="utf-8-sig", newline="") as log:
                row, = list(csv.DictReader(log))
            assert row["nama_baru"] == f"{name} - 2507UMKHM - 12-2025 - TIDAK FINAL - NORMAL.pdf", row
    print("PDF contoh Bupot 2024/2026 (nama C.3 dan A.2): ok", flush=True)

    # Jumlah transaksi per bulan; semua bulan harus SESUAI dan saldo akhir = saldo awal bulan berikutnya.
    for folder, counts in (("Rekening Giro", [28, 29, 20]), ("Rekening Tahapan", [81, 105, 101])):
        statements = [read_rekening(path) for path in sorted((root / folder).glob("*.pdf"))]
        assert [len(s["transaksi"]) for s in statements] == counts, (folder, [len(s["transaksi"]) for s in statements])
        assert all(not s["catatan"] for s in statements), [s["catatan"] for s in statements]
        for before, after in zip(statements, statements[1:]):
            assert before["ringkasan"]["SALDO AKHIR"][0] == after["ringkasan"]["SALDO AWAL"][0], folder
        print(f"PDF contoh {folder}: {len(statements)} bulan, {sum(counts)} transaksi, semua SESUAI", flush=True)


def main():
    test_batch_exports()
    test_rename_pemotong()
    test_rekening_koran()
    test_engine_protocol()
    text = """2505Z0UR6 10-2025 TIDAK FINAL PEMBETULAN KE-2
C.3 NAMA PEMOTONG : PT CONTOH: ABADI
C.4 TANGGAL : 7 Juli 2026"""
    assert ExpCore._extract_rename_bupot_data(text) == {
        "NAMA_PENERIMA": "",
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
        "NAMA_PENERIMA": "",
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

    # Tarif BPBS bisa bulat, desimal titik, atau desimal koma; centang X opsional.
    for tarif, expected_tarif in (("2", 2.0), ("2.00", 2.0), ("2,00", 2.0),
                                  ("1.5", 1.5), ("1,5", 1.5), ("0", 0.0), ("10", 10.0)):
        for checkbox in ("", "X "):
            variant = bupot2024.replace("2.00 26.000,00", f"{checkbox}{tarif} 26.000,00")
            expected_row = dict(rows2024[0])
            expected_row["Tarif (%)"] = expected_tarif
            expected_row["Tarif Lebih Tinggi"] = "Ya" if checkbox else "Tidak"
            assert ExpCore._extract_bupot2024_rows(variant) == [expected_row], (tarif, checkbox)

    # Tarif kosong/rusak tidak boleh membuat nominal PPh terbaca sebagai tarif.
    for invalid_tarif in ("", "2.", "2,", "abc"):
        variant = bupot2024.replace("2.00 26.000,00", f"{invalid_tarif} 26.000,00")
        assert ExpCore._extract_bupot2024_rows(variant) == [], invalid_tarif

    # Formulir Coretax (BPPU) tidak boleh ikut terbaca oleh parser BPBS.
    assert ExpCore._extract_bupot2024_rows(bupot) == []
    # Tanggal dengan kotak kosong menghasilkan string kosong, bukan crash.
    assert ExpCore._form_date("Tanggal dd mm yyyy") == ""
    assert ExpCore._form_date("3 1 dd 0 1 mm 2 0 2 4 yyyy") == "31-01-2024"

    print("Rekap Bukti Potong 2024: ok")


if __name__ == "__main__":
    main()
    if "--pdf-samples" in sys.argv:
        test_pdf_samples()
