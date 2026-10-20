import os
import glob
import re
import bisect
import csv
import unicodedata
import pdfplumber
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.hyperlink import Hyperlink
from datetime import datetime
from decimal import Decimal


def _baca_aman(pembaca, path):
    """Satu PDF: (hasil, None), atau (None, pesan galat) agar satu PDF rusak tidak menghentikan batch."""
    try:
        return pembaca(path), None
    except Exception as error:
        return None, str(error)


def _baca_teks(ekstrak, path):
    """Teks seluruh halaman satu PDF ke `ekstrak` (Bupot 2026 dan 2024)."""
    with pdfplumber.open(path) as pdf:
        return ekstrak("\n".join(p.extract_text() or "" for p in pdf.pages))


def _baca_halaman(ekstrak, path):
    """Halaman pdfplumber satu PDF ke `ekstrak` (rekening koran BCA dan CIMB)."""
    with pdfplumber.open(path) as pdf:
        return ekstrak(pdf.pages)


class ExpCore:
    """Parser PDF Coretax. Aktivitas dan progres dilaporkan lewat callback."""

    # Sumber nama file pada Penamaan Bupot: kunci CLI -> (field data, label, kode bagian per formulir).
    # BPPU = Bupot 2026 (Coretax), BPBS = Bupot 2024; dokumen tak dikenal dibaca sebagai BPPU.
    RENAME_NAME_SOURCES = {
        "pemotong": ("NAMA_PEMOTONG", "Identitas Pemotong", {"BPPU": "C.3", "BPBS": "C.2"}),
        "penerima": ("NAMA_PENERIMA", "Wajib Pajak yang Dipotong", {"BPPU": "A.2", "BPBS": "A.3"}),
    }

    def __init__(self, log=None, progress=None, workers=None):
        self.log = log or (lambda message: None)
        self.progress = progress or (lambda done, total: None)
        # ponytail: maks 4 proses pembaca PDF; tiap proses butuh ~0,4 s untuk mulai, jadi beberapa PDF tipis
        # bisa ~0,2 s lebih lambat daripada serial. Naikkan (6 terukur lebih cepat) bila memori pengguna cukup.
        self.workers = workers or min(os.cpu_count() or 1, 4)

    def _peta_pdf(self, pembaca, pdf_files):
        """(hasil, galat) per PDF, urut sesuai pdf_files.

        pdfminer murni Python sehingga satu proses hanya memakai satu inti CPU: lebih dari satu PDF dibaca
        paralel di proses terpisah. Log, progres, dan penulisan Excel tetap di proses ini, dalam urutan file.
        """
        workers = min(self.workers, len(pdf_files))
        if workers <= 1:
            yield from (_baca_aman(pembaca, path) for path in pdf_files)
            return
        # Di Windows, pekerja mewarisi stdout engine yang berisi protokol JSON: dup2(2, 1) mengarahkannya ke
        # stderr di tingkat descriptor agar print() maupun keluaran pustaka C tidak mencemari protokol.
        with ProcessPoolExecutor(workers, initializer=partial(os.dup2, 2, 1)) as pool:
            yield from pool.map(partial(_baca_aman, pembaca), pdf_files)

    @staticmethod
    def _write_excel(rows, output_path, sheet_name, text_cols=(), money_cols=(), center_cols=("No",)):
        """Tulis baris (dict, kolom = kunci baris pertama) ke Excel dengan header, format angka, dan lebar kolom.

        text_cols dipaksa format teks agar NPWP, masa pajak, dan nomor dokumen
        tidak diubah Excel jadi angka atau tanggal.
        """
        book = Workbook()
        ws = book.active
        ws.title = sheet_name
        columns = list(rows[0])
        ws.append(columns)
        for row in rows:
            ws.append([row.get(col) for col in columns])

        for cell in ws[1]:
            cell.fill = PatternFill(start_color="D9D9D9", end_color="D9D9D9", fill_type="solid")
            cell.font = Font(bold=True)

        col_idx = {col: i + 1 for i, col in enumerate(columns)}
        for col_name in text_cols:
            if col_name in col_idx:
                for cell in ws[get_column_letter(col_idx[col_name])]:
                    cell.number_format = '@'

        for col_name in money_cols:
            if col_name in col_idx:
                for cell in ws[get_column_letter(col_idx[col_name])][1:]:
                    cell.number_format = '#,##0'

        if "Tarif (%)" in col_idx:
            for cell in ws[get_column_letter(col_idx["Tarif (%)"])][1:]:
                cell.number_format = '0.00'

        for col_name in center_cols:
            if col_name in col_idx:
                for cell in ws[get_column_letter(col_idx[col_name])][1:]:
                    cell.alignment = Alignment(horizontal='center')

        for column in ws.columns:
            max_length = max((len(str(cell.value)) for cell in column if cell.value), default=0)
            ws.column_dimensions[column[0].column_letter].width = min(max_length + 2, 55)
        book.save(output_path)

    @staticmethod
    def parse_values(val_str):
        v = str(val_str).replace('%', '').replace('Rp', '').strip()
        if ',' in v:
            v = v.replace('.', '').replace(',', '.')
        else:
            v = v.replace('.', '')
        # Nominal yang tidak terbaca menggagalkan PDF (dicatat di log), bukan menjadi 0 di rekap.
        try: return float(v)
        except ValueError: raise ValueError(f"Nilai angka tidak terbaca: {val_str!r}") from None

    @staticmethod
    def parse_tarif(val_str):
        v = str(val_str).replace('%', '').strip()
        v = v.replace(',', '.')
        try: return float(v)
        except ValueError: raise ValueError(f"Tarif tidak terbaca: {val_str!r}") from None

    @staticmethod
    def _clean_filename_value(value):
        value = unicodedata.normalize("NFKC", str(value or "")).replace("\u00a0", " ")
        return re.sub(r"\s+", " ", value).strip(" :-–—\t\r\n")

    @staticmethod
    def _safe_filename(value, max_len=180):
        value = ExpCore._clean_filename_value(value)
        value = re.sub(r'[<>:"/\\|?*\x00-\x1f]', " ", value)
        value = re.sub(r"\s+", " ", value).rstrip(". ").strip()
        return (value or "UNKNOWN")[:max_len].rstrip(". ")

    @classmethod
    def _extract_rename_bupot_data(cls, text):
        """Field nama file Penamaan Bupot dari BPPU (Bupot 2026) atau BPBS (Bupot 2024).

        Formulir dikenali dari judulnya. FORMULIR kosong bila dokumen bukan keduanya; dokumen
        seperti itu tetap dibaca dengan parser BPPU (perilaku lama) dan biasanya dilewati.
        """
        text = unicodedata.normalize("NFKC", text or "").replace(" ", " ")
        if re.search(r"\bFORMULIR\s+BPBS\b", text, re.IGNORECASE):
            return {**cls._extract_bpbs_rename_data(text), "FORMULIR": "BPBS"}
        bppu = re.search(r"\bBPPU\b|PEMOTONGAN\s+DAN/ATAU\s+PEMUNGUTAN\s+PPh", text, re.IGNORECASE)
        return {**cls._extract_bppu_rename_data(text), "FORMULIR": "BPPU" if bppu else ""}

    @classmethod
    def _extract_bpbs_rename_data(cls, text):
        """Field nama file dari BPBS. Tidak menebak: data yang ambigu dibiarkan kosong sehingga PDF dilewati."""
        header = cls._bpbs_header(text)
        # Satu bukti potong = satu masa pajak; bila baris objek pajak berbeda masa, jangan memilih salah satu.
        masa = {f"{int(bulan):02d}-{tahun}" for bulan, tahun in
                (match.group(1).split("-") for match in cls._BPBS_ROW.finditer(text))}
        return {
            "NAMA_PENERIMA": cls._clean_filename_value(header["nama"]),
            "NAMA_PEMOTONG": cls._clean_filename_value(header["nama_pemotong"]),
            "NOMOR_BUKTI": header["nomor_bukti"],
            "MASA_PAJAK": masa.pop() if len(masa) == 1 else "",
            "SIFAT": "" if header["sifat"] == "-" else header["sifat"],
            # Status hanya dari kotak H.2 yang terbaca, bukan bawaan NORMAL.
            "STATUS": header["status"] if header["pembetulan_terbaca"] else "",
        }

    @staticmethod
    def _extract_bppu_rename_data(text):
        # ponytail: tambah fallback hanya saat ada contoh layout Coretax yang benar-benar gagal.
        text = unicodedata.normalize("NFKC", text or "").replace("\u00a0", " ")
        text_flat = re.sub(r"\s+", " ", text)
        top_text = text[:2500]
        data = {
            "NAMA_PENERIMA": "",
            "NAMA_PEMOTONG": "",
            "NOMOR_BUKTI": "",
            "MASA_PAJAK": "",
            "SIFAT": "",
            "STATUS": "",
        }

        # A.2 adalah nama wajib pajak penerima penghasilan, bukan pemotong C.3.
        # Batasi sampai A.3 agar NITKU/identitas lain tidak ikut menjadi nama.
        recipient = re.search(
            r"\bA\.?\s*2\s*NAMA\s*[:：]\s*(.*?)\s*\bA\.?\s*3\b",
            text_flat,
            re.IGNORECASE,
        )
        if recipient:
            data["NAMA_PENERIMA"] = ExpCore._clean_filename_value(recipient.group(1))

        name_patterns = [
            r"C\.?\s*3\s*(?:NAMA\s*)?PEMOTONG.*?[:：]\s*(.*?)\s*C\.?\s*4\b",
            r"C\.?\s*3\s*NAMA\s*PEMOTONG[^:：]*[:：]\s*([^\n\r]{2,100})",
            r"NAMA\s*PEMOTONG\s*DAN/?ATAU\s*PEMUNGUT\s*PPh\s*[:：]?\s*([^\n\r]{2,100})",
        ]
        for pattern in name_patterns:
            match = re.search(pattern, text_flat if "C\\.?\\s*4" in pattern else text, re.IGNORECASE)
            if match:
                # Label "…DAN/ATAU PEMUNGUT PPh" terpotong baris, sisa "PPh" ikut tercapture.
                nama = re.sub(r"\s*PPh\s*$", "", match.group(1), flags=re.IGNORECASE)
                data["NAMA_PEMOTONG"] = ExpCore._clean_filename_value(nama)
                break

        header = re.search(
            r"\b([A-Z0-9-]{8,20})\s+(\d{2}-\d{4})\s+"
            r"(TIDAK\s*FINAL|FINAL)\s+"
            r"(NORMAL|PEMBETULAN(?:\s*(?:KE-?)?\s*\d+)?|DIBATALKAN)\b",
            top_text,
            re.IGNORECASE,
        )
        if header:
            data["NOMOR_BUKTI"] = ExpCore._clean_filename_value(header.group(1)).upper()
            data["MASA_PAJAK"] = ExpCore._clean_filename_value(header.group(2)).upper()
            data["SIFAT"] = ExpCore._clean_filename_value(header.group(3)).upper()
            data["STATUS"] = ExpCore._clean_filename_value(header.group(4)).upper()
            return data

        match = re.search(r"\b(\d{2}-\d{4})\b", top_text)
        if match:
            data["MASA_PAJAK"] = match.group(1)

        match = re.search(r"\b(TIDAK\s*FINAL|FINAL)\b", top_text, re.IGNORECASE)
        if match:
            data["SIFAT"] = ExpCore._clean_filename_value(match.group(1)).upper()

        match = re.search(
            r"\b(NORMAL|PEMBETULAN(?:\s*(?:KE-?)?\s*\d+)?|DIBATALKAN)\b",
            top_text,
            re.IGNORECASE,
        )
        if match:
            data["STATUS"] = ExpCore._clean_filename_value(match.group(1)).upper()

        for candidate in re.findall(r"\b[A-Z0-9-]{8,20}\b", top_text.upper()):
            if any(ch.isalpha() for ch in candidate) and any(ch.isdigit() for ch in candidate):
                data["NOMOR_BUKTI"] = candidate
                break

        return data

    @staticmethod
    def _unique_filename(path):
        if not os.path.exists(path):
            return path
        stem, suffix = os.path.splitext(path)
        number = 2
        while os.path.exists(f"{stem} ({number}){suffix}"):
            number += 1
        return f"{stem} ({number}){suffix}"

    def process_rename_bupot(self, folder, apply_changes=False, name_source="pemotong"):
        if name_source not in ExpCore.RENAME_NAME_SOURCES:
            raise ValueError(f"Sumber nama tidak dikenal: {name_source}")
        if not folder or not os.path.isdir(folder):
            raise ValueError("Folder tidak ditemukan. Pilih folder yang tersedia.")
        pdf_files = sorted(glob.glob(os.path.join(folder, "**", "*.pdf"), recursive=True))
        if not pdf_files:
            raise ValueError("Tidak ada PDF di folder atau subfolder ini. Pilih folder lain.")

        name_field, name_label, name_codes = ExpCore.RENAME_NAME_SOURCES[name_source]
        mode = "Penerapan" if apply_changes else "Pratinjau"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = os.path.join(folder, f"Log_Penamaan_Bupot_{mode}_{timestamp}.csv")
        fields = [
            "status", "folder_sumber", "nama_lama", "nama_baru", "data_tidak_lengkap",
            "NAMA_PENERIMA", "NAMA_PEMOTONG", "NOMOR_BUKTI", "MASA_PAJAK", "SIFAT", "STATUS",
            "sumber_nama", "FORMULIR",
        ]
        # Tanpa fallback: bila nama dari sumber terpilih kosong, PDF dilewati, bukan memakai nama lain.
        required_fields = (name_field, "NOMOR_BUKTI", "MASA_PAJAK", "SIFAT", "STATUS")
        complete = skipped = failed = unchanged = 0
        self.log(f"{mode}: memeriksa {len(pdf_files)} PDF … (nama dari {name_label})")

        try:
            with open(log_path, "w", newline="", encoding="utf-8-sig") as log_file:
                writer = csv.DictWriter(log_file, fieldnames=fields)
                writer.writeheader()

                for index, file_pdf in enumerate(pdf_files):
                    self.progress(index, len(pdf_files))
                    relative_file = os.path.relpath(file_pdf, folder)
                    folder_source = os.path.dirname(relative_file) or "."
                    row = {
                        "status": "ERROR",
                        "folder_sumber": folder_source,
                        "nama_lama": os.path.basename(file_pdf),
                        "nama_baru": "",
                        "data_tidak_lengkap": "exception",
                        "sumber_nama": name_label,
                    }
                    try:
                        with pdfplumber.open(file_pdf) as pdf:
                            page_texts = []
                            for page in pdf.pages:
                                page_text = page.extract_text()
                                if page_text:
                                    page_texts.append(page_text)

                        data = self._extract_rename_bupot_data("\n".join(page_texts))
                        missing = [key for key in required_fields if not data[key]]
                        components = [
                            self._safe_filename(data[name_field] or "UNKNOWN_NAMA", 80),
                            self._safe_filename(data["NOMOR_BUKTI"] or "UNKNOWN_NOMOR", 30),
                            self._safe_filename(data["MASA_PAJAK"] or "UNKNOWN_MASA", 20),
                            self._safe_filename(data["SIFAT"] or "UNKNOWN_SIFAT", 20),
                            self._safe_filename(data["STATUS"] or "UNKNOWN_STATUS", 30),
                        ]
                        new_name = f"{self._safe_filename(' - '.join(components))}.pdf"
                        new_path = os.path.join(os.path.dirname(file_pdf), new_name)

                        if missing:
                            status = "DILEWATI" if apply_changes else "PERLU CEK"
                            skipped += 1
                        elif os.path.basename(file_pdf).casefold() == new_name.casefold():
                            status = "SUDAH SESUAI"
                            unchanged += 1
                        elif apply_changes:
                            new_path = self._unique_filename(new_path)
                            os.rename(file_pdf, new_path)
                            new_name = os.path.basename(new_path)
                            status = "BERHASIL"
                            complete += 1
                        else:
                            new_path = self._unique_filename(new_path)
                            new_name = os.path.basename(new_path)
                            status = "SIAP"
                            complete += 1

                        code = name_codes.get(data["FORMULIR"], name_codes["BPPU"])
                        row.update({
                            "status": status,
                            "nama_baru": new_name,
                            "data_tidak_lengkap": ", ".join(missing),
                            "sumber_nama": f"{name_label} ({code})",
                            **data,
                        })
                        form = f" [{data['FORMULIR']}]" if data["FORMULIR"] else ""
                        self.log(f"{status}: {relative_file} → {new_name}{form}")
                    except Exception as error:
                        failed += 1
                        self.log(f"ERROR: {relative_file} — {error}")

                    writer.writerow(row)
                    log_file.flush()

            summary = (
                f"{mode} selesai — {complete} siap/berhasil, {unchanged} sudah sesuai, "
                f"{skipped} perlu diperiksa, {failed} gagal."
            )
            self.log(summary)
            self.log(f"Log: {log_path}")
            return log_path, summary
        except Exception as error:
            self.log(f"Error: {error}")
            raise

    # ══════════════════════════════════════════
    #  EKSTRAKSI — BUKTI POTONG
    # ══════════════════════════════════════════
    @classmethod
    def _extract_bupot_rows(cls, teks_lengkap):
        """Ambil semua baris objek pajak dari teks satu PDF Bukti Potong."""
        teks_rata = teks_lengkap.replace('\n', ' ')

        # Nomor bukti, masa pajak & status ada di header — logika sama dengan
        # fitur penamaan otomatis, jadi dipakai ulang.
        header = cls._extract_bppu_rename_data(teks_lengkap)
        nomor_bukti = header["NOMOR_BUKTI"] or "-"
        masa_pajak = header["MASA_PAJAK"] or "-"
        status_bukti = header["STATUS"] or "NORMAL"
        nama_pemotong = header["NAMA_PEMOTONG"] or "-"

        match_nama = re.search(r'A\.2\s*NAMA\s*:\s*(.*?)\s*A\.3', teks_rata)
        nama_penerima = match_nama.group(1).strip() if match_nama else "-"
        match_npwp_penerima = re.search(r'A\.1\s*NPWP\s*/\s*NIK\s*:\s*(\d+)', teks_rata)
        npwp_penerima = match_npwp_penerima.group(1) if match_npwp_penerima else "-"
        match_fasilitas = re.search(r'B\.1\s*Jenis Fasilitas\s*:\s*(.*?)\s*B\.2', teks_rata, re.IGNORECASE)
        jenis_fasilitas = match_fasilitas.group(1).strip() if match_fasilitas else "-"
        match_jpph = re.search(r'B\.2\s*Jenis PPh\s*:\s*(.*?)\s*(?:KODE OBJEK PAJAK|B\.3)', teks_rata, re.IGNORECASE)
        jenis_pph = match_jpph.group(1).strip() if match_jpph else "-"
        # Tanggal dibatasi pola tanggal agar tidak menelan sisa label B.8 yang terpotong baris.
        match_jenis_dok = re.search(
            r'Jenis Dokumen\s*:\s*(.*?)\s*Tanggal\s*:\s*(\d{1,2}\s+\S+\s+\d{4})',
            teks_rata, re.IGNORECASE,
        )
        jenis_dokumen = match_jenis_dok.group(1).strip() if match_jenis_dok else "-"
        tanggal_dokumen = match_jenis_dok.group(2).strip() if match_jenis_dok else "-"
        match_nodok = re.search(r'B\.9\s*Nomor Dokumen\s*:\s*(.*?)\s*B\.10', teks_rata, re.IGNORECASE)
        nomor_dokumen = match_nodok.group(1).strip() if match_nodok else "-"
        match_npwp_pemotong = re.search(r'C\.1\s*NPWP\s*/\s*NIK\s*:\s*([\d]+)', teks_rata)
        npwp_pemotong = match_npwp_pemotong.group(1) if match_npwp_pemotong else "-"
        match_tanggal = re.search(r'C\.4\s*TANGGAL\s*:\s*([A-Za-z0-9\s]+?)\s*C\.5', teks_rata)
        tanggal_bupot = match_tanggal.group(1).strip() if match_tanggal else "-"

        match_blok = re.search(r'B\.7\s*(.*?)\s*B\.8\s*Dokumen', teks_rata, re.IGNORECASE)
        if not match_blok:
            return []

        baris_data = []
        blok_tabel = match_blok.group(1).strip()
        for m in re.finditer(r'(\d{2}-\d{3}-\d{2})\s+(.*?)(?=(?:\d{2}-\d{3}-\d{2})|$)', blok_tabel):
            kode_objek = m.group(1)
            isi_baris = m.group(2).strip()

            pattern_angka = r'(?<!\S)(\d{1,3}(?:\.\d{3})*(?:,\d+)?)\s+(\d+(?:[\.,]\d+)?%?)\s+(\d{1,3}(?:\.\d{3})*(?:,\d+)?)(?!\S)'
            match_angka = re.search(pattern_angka, isi_baris)

            if match_angka:
                dpp_str, tarif_str, pph_str = match_angka.groups()
                objek_pajak_desc = isi_baris[:match_angka.start()] + " " + isi_baris[match_angka.end():]
                objek_pajak_desc = re.sub(r'\s+', ' ', objek_pajak_desc).strip()
            else:
                tokens = isi_baris.split()
                if len(tokens) >= 3:
                    dpp_str, tarif_str, pph_str = tokens[-3], tokens[-2], tokens[-1]
                    objek_pajak_desc = " ".join(tokens[:-3])
                else:
                    dpp_str, tarif_str, pph_str = "0", "0", "0"
                    objek_pajak_desc = isi_baris

            baris_data.append({
                "Nomor Dokumen": nomor_bukti, "Masa Pajak": masa_pajak,
                "NPWP/NIK": npwp_penerima, "Nama": nama_penerima,
                "Status Bukti": status_bukti, "Jenis Fasilitas": jenis_fasilitas,
                "Jenis PPh": jenis_pph, "Kode Objek Pajak": kode_objek, "Objek Pajak": objek_pajak_desc,
                "DPP (Rp)": cls.parse_values(dpp_str), "Tarif (%)": cls.parse_tarif(tarif_str),
                "Pajak Penghasilan (Rp)": cls.parse_values(pph_str), "Jenis Dokumen": jenis_dokumen,
                "Nomor Dokumen Dasar": nomor_dokumen, "Tanggal Dokumen": tanggal_dokumen,
                "NPWP/NIK Pemotong": npwp_pemotong, "Nama Pemotong": nama_pemotong,
                "Tanggal Bukti Potong": tanggal_bupot,
            })

        return baris_data

    def process_bupot(self, folder):
        if not folder or not os.path.isdir(folder):
            raise ValueError("Folder tidak ditemukan. Pilih folder yang tersedia.")
        pdf_files = sorted(glob.glob(os.path.join(folder, "**", "*.pdf"), recursive=True))
        if not pdf_files:
            raise ValueError("Tidak ada PDF di folder atau subfolder ini. Pilih folder lain.")

        self.log(f"Memproses {len(pdf_files)} file …")

        semua_baris_data = []
        dilewati = 0
        try:
            hasil = self._peta_pdf(partial(_baca_teks, self._extract_bupot_rows), pdf_files)
            for index, (file_pdf, (rows, galat)) in enumerate(zip(pdf_files, hasil)):
                self.progress(index, len(pdf_files))
                nama_file = os.path.basename(file_pdf)
                folder_sumber = os.path.relpath(os.path.dirname(file_pdf), folder)
                self.log(f"Membaca {os.path.relpath(file_pdf, folder)}")

                if galat is not None:
                    dilewati += 1
                    self.log(f"GAGAL: {nama_file} — {galat}")
                    continue
                if not rows:
                    dilewati += 1
                    self.log(f"DILEWATI: {nama_file} — tidak ada baris BPPU yang dapat dibaca.")
                for baris in rows:
                    baris["Folder Sumber"] = folder_sumber
                    baris["File Name"] = nama_file
                    semua_baris_data.append(baris)

            if semua_baris_data:
                output_path = os.path.join(folder, "!Hasil_Rekap_Bupot.xlsx")

                self._write_excel(
                    [{"No": nomor, **baris} for nomor, baris in enumerate(semua_baris_data, 1)], output_path, "Rekap",
                    text_cols=["Nomor Dokumen", "Masa Pajak", "NPWP/NIK", "Kode Objek Pajak",
                               "Nomor Dokumen Dasar", "NPWP/NIK Pemotong"],
                    money_cols=["DPP (Rp)", "Pajak Penghasilan (Rp)"],
                )

                self.log(f"Selesai — {output_path}")
                return output_path, f"Selesai — {len(semua_baris_data)} baris, {dilewati} PDF dilewati."
            else:
                self.log("Tidak ada data yang ditemukan.")
                return None, "Tidak ada data yang cocok. Periksa jenis formulir dan pastikan PDF memiliki lapisan teks."

        except Exception as e:
            self.log(f"Error: {str(e)}")
            raise

    # ══════════════════════════════════════════
    #  EKSTRAKSI — BUKTI POTONG 2024 (formulir BPBS)
    # ══════════════════════════════════════════
    @staticmethod
    def _despace_digits(value):
        """'4 3 6 1 ...' -> '4361...'. Formulir BPBS menulis angka per kotak."""
        return re.sub(r"\s+", "", value or "")

    @staticmethod
    def _form_date(value):
        """'3 1 dd 0 1 mm 2 0 2 4 yyyy' -> '31-01-2024'. Kotak kosong -> ''."""
        match = re.search(r"([\d\s]*?)dd\s*([\d\s]*?)mm\s*([\d\s]*?)yyyy", value or "")
        if not match:
            return ""
        day, month, year = (ExpCore._despace_digits(g) for g in match.groups())
        if not (day and month and year):
            return ""
        return f"{day.zfill(2)}-{month.zfill(2)}-{year}"

    # Baris objek pajak BPBS: masa, kode objek, DPP, centang tarif lebih tinggi, tarif, PPh.
    # Tarif dapat berupa bilangan bulat (2) atau desimal (2.00 / 2,00).
    _BPBS_ROW = re.compile(
        r"(\d{1,2}-\d{4})\s+(\d{2}-\d{3}-\d{2})\s+([\d.]+,\d{2})\s+"
        r"(?:(X)\s+)?(\d+(?:[.,]\d+)?)\s+([\d.]+,\d{2})"
    )

    @classmethod
    def _bpbs_header(cls, teks_lengkap):
        """Identitas, dokumen referensi, dan bagian H satu PDF BPBS (dipakai rekap 2024 dan penamaan).

        Berbeda dari BPPU Coretax: angka ditulis per kotak (NPWP, tanggal) dan
        sifat Final/Tidak Final ditandai centang "X" di depan labelnya.
        """
        teks = teks_lengkap or ""
        teks_rata = re.sub(r"[ \t]+", " ", teks.replace("\n", " "))

        def ambil(pattern, sumber=None, flags=re.IGNORECASE):
            match = re.search(pattern, teks_rata if sumber is None else sumber, flags)
            return match.group(1).strip() if match else ""

        npwp = cls._despace_digits(ambil(r"A\.1\s*NPWP\s*:\s*([\d\s]*?)\s*A\.2"))
        nik = cls._despace_digits(ambil(r"A\.2\s*NIK\s*:\s*([\d\s]*?)\s*A\.3"))
        nama = ambil(r"A\.3\s*Nama\s*:\s*(.*?)\s*B\.\s*PAJAK")
        objek_pajak = ambil(r"Keterangan Kode Objek Pajak\s*:\s*(.*?)\s*B\.7")
        nomor_dokumen = ambil(r"B\.7.*?Nomor Dokumen\s+(\S+?)\s+Nama Dokumen")
        nama_dokumen = ambil(r"Nama Dokumen\s+(.*?)\s+Tanggal\s")
        tanggal_dokumen = cls._form_date(ambil(r"Nama Dokumen.*?Tanggal\s+(.*?yyyy)"))
        npwp_pemotong = cls._despace_digits(ambil(r"C\.1\s*NPWP\s*:\s*([\d\s]*?)\s*C\.2"))
        nama_pemotong = ambil(r"C\.2\s*Nama Wajib Pajak\s*:\s*(.*?)\s*C\.3")
        tanggal_bukti = cls._form_date(ambil(r"C\.3\s*Tanggal\s*:\s*(.*?yyyy)"))
        # Label C.5 terpotong baris, kata "elektronik" jatuh ke depan C.5.
        penandatangan = ambil(r"C\.4\s*Nama Penandatangan\s*:\s*(.*?)\s*(?:elektronik\s+)?C\.5")

        # Header H semuanya inline pada teks pdfplumber: nomor, pembetulan,
        # dan tanda centang sifat. Centang muncul sebagai "X" antara nomor
        # bagian dan labelnya, mis. "H.5 X PPh Tidak Final".
        nomor_bukti = cls._despace_digits(ambil(r"H\.1\s*NOMOR\s*:\s*([\d\s]*?)\s*H\.\d"))
        pembetulan_str = ambil(r"H\.2\s*Pembetulan\s*Ke-\s*(\d+)")
        pembetulan = int(pembetulan_str) if pembetulan_str.isdigit() else 0
        dibatalkan = bool(ambil(r"H\.3\s*(X)\s*Pembatalan"))
        final = bool(ambil(r"H\.4\s*(X)\s*PPh\s*Final"))
        tidak_final = bool(ambil(r"H\.5\s*(X)\s*PPh\s*Tidak\s*Final"))

        if dibatalkan:
            status_bukti = "DIBATALKAN"
        elif pembetulan:
            status_bukti = f"PEMBETULAN KE-{pembetulan}"
        else:
            status_bukti = "NORMAL"

        # Tepat satu kotak harus tercentang; selain itu jangan menebak.
        sifat = "-" if final == tidak_final else ("FINAL" if final else "TIDAK FINAL")

        return {
            "npwp": npwp, "nik": nik, "nama": nama, "objek_pajak": objek_pajak,
            "nomor_dokumen": nomor_dokumen, "nama_dokumen": nama_dokumen, "tanggal_dokumen": tanggal_dokumen,
            "npwp_pemotong": npwp_pemotong, "nama_pemotong": nama_pemotong, "tanggal_bukti": tanggal_bukti,
            "penandatangan": penandatangan, "nomor_bukti": nomor_bukti, "pembetulan": pembetulan,
            "pembetulan_terbaca": pembetulan_str.isdigit(), "status": status_bukti, "sifat": sifat,
        }

    @classmethod
    def _extract_bupot2024_rows(cls, teks_lengkap):
        """Ambil baris objek pajak dari teks satu PDF Bukti Potong formulir BPBS."""
        h = cls._bpbs_header(teks_lengkap)
        baris_data = []
        for match in cls._BPBS_ROW.finditer(teks_lengkap or ""):
            masa, kode_objek, dpp, tarif_tinggi, tarif, pph = match.groups()
            bulan, tahun = masa.split("-")
            baris_data.append({
                "Nomor Bukti Potong": h["nomor_bukti"] or "-",
                "Pembetulan Ke": h["pembetulan"],
                "Status Bukti": h["status"],
                "Sifat": h["sifat"],
                "NPWP": h["npwp"] or "-",
                "NIK": h["nik"] or "-",
                "Nama": h["nama"] or "-",
                "Masa Pajak": f"{bulan.zfill(2)}-{tahun}",
                "Kode Objek Pajak": kode_objek,
                "Objek Pajak": h["objek_pajak"] or "-",
                "DPP (Rp)": cls.parse_values(dpp),
                "Tarif Lebih Tinggi": "Ya" if tarif_tinggi else "Tidak",
                "Tarif (%)": cls.parse_tarif(tarif),
                "Pajak Penghasilan (Rp)": cls.parse_values(pph),
                "Nomor Dokumen Referensi": h["nomor_dokumen"] or "-",
                "Nama Dokumen": h["nama_dokumen"] or "-",
                "Tanggal Dokumen": h["tanggal_dokumen"] or "-",
                "NPWP Pemotong": h["npwp_pemotong"] or "-",
                "Nama Pemotong": h["nama_pemotong"] or "-",
                "Tanggal Bukti Potong": h["tanggal_bukti"] or "-",
                "Nama Penandatangan": h["penandatangan"] or "-",
            })
        return baris_data

    def process_bupot_2024(self, folder):
        if not folder or not os.path.isdir(folder):
            raise ValueError("Folder tidak ditemukan. Pilih folder yang tersedia.")
        pdf_files = sorted(glob.glob(os.path.join(folder, "**", "*.pdf"), recursive=True))
        if not pdf_files:
            raise ValueError("Tidak ada PDF di folder atau subfolder ini. Pilih folder lain.")

        self.log(f"Memproses {len(pdf_files)} file …")

        semua_baris_data = []
        dilewati = 0
        try:
            hasil = self._peta_pdf(partial(_baca_teks, self._extract_bupot2024_rows), pdf_files)
            for index, (file_pdf, (baris_pdf, galat)) in enumerate(zip(pdf_files, hasil)):
                self.progress(index, len(pdf_files))
                nama_file = os.path.basename(file_pdf)
                folder_sumber = os.path.relpath(os.path.dirname(file_pdf), folder)
                relatif = os.path.relpath(file_pdf, folder)
                self.log(f"Membaca {relatif}")

                if galat is not None:
                    dilewati += 1
                    self.log(f"GAGAL: {relatif} — {galat}")
                    continue
                if not baris_pdf:
                    dilewati += 1
                    self.log(f"DILEWATI: {relatif} — tidak ada baris objek pajak BPBS yang berhasil dibaca.")
                    continue

                for baris in baris_pdf:
                    baris["Folder Sumber"] = folder_sumber
                    baris["File Name"] = nama_file
                    semua_baris_data.append(baris)

            if semua_baris_data:
                output_path = os.path.join(folder, "!Hasil_Rekap_Bupot_2024.xlsx")
                self._write_excel(
                    [{"No": nomor, **baris} for nomor, baris in enumerate(semua_baris_data, 1)],
                    output_path, "Rekap 2024",
                    text_cols=[
                        "Nomor Bukti Potong", "NPWP", "NIK", "Masa Pajak",
                        "Kode Objek Pajak", "Nomor Dokumen Referensi", "NPWP Pemotong",
                    ],
                    money_cols=["DPP (Rp)", "Pajak Penghasilan (Rp)"],
                )
                self.log(
                    f"Selesai — {len(semua_baris_data)} baris, {dilewati} file dilewati."
                )
                self.log(f"Output: {output_path}")
                return output_path, f"Selesai — {len(semua_baris_data)} baris, {dilewati} PDF dilewati."
            else:
                self.log("Tidak ada data yang ditemukan.")
                return None, "Tidak ada data yang cocok. Periksa jenis formulir dan pastikan PDF memiliki lapisan teks."


        except Exception as e:
            self.log(f"Error: {str(e)}")
            raise

    # ══════════════════════════════════════════
    #  EKSTRAKSI — PAJAK MASUKAN
    # ══════════════════════════════════════════
    @classmethod
    def _baca_pm(cls, path):
        """Rincian barang satu faktur pajak; kolom Folder Sumber dan Nama File PDF diisi pemanggil."""
        baris_data = []
        with pdfplumber.open(path) as pdf:
            teks_lengkap = "\n".join(page.extract_text() or "" for page in pdf.pages)

            nama_pembeli_match = re.search(r'Pembeli Barang Kena Pajak.*?Nama\s*:\s*([^\n]+)', teks_lengkap, re.DOTALL | re.IGNORECASE)
            nama_pembeli = nama_pembeli_match.group(1).strip() if nama_pembeli_match else "-"

            pembeli_block = re.search(r'Pembeli Barang Kena Pajak.*?(?P<npwp>\d{15,16})', teks_lengkap.replace('.', '').replace('-', ''), re.DOTALL | re.IGNORECASE)
            if pembeli_block:
                npwp_pembeli = pembeli_block.group('npwp')
            else:
                npwp_matches = re.findall(r'NPWP\s*:\s*([\d\.\-]+)', teks_lengkap)
                npwp_pembeli = npwp_matches[-1].replace('.', '').replace('-', '') if npwp_matches else "-"

            no_seri_match = re.search(r'Kode dan Nomor Seri Faktur Pajak\s*:\s*([\d\-\.]+)', teks_lengkap, re.IGNORECASE)
            no_seri = no_seri_match.group(1).replace('.', '').replace('-', '') if no_seri_match else "-"

            no_urut = 1
            for page in pdf.pages:
                tabel_halaman = page.extract_tables()
                for tabel in tabel_halaman:
                    for row in tabel:
                        if not row or len(row) < 3: continue

                        kode_col, desc_col = str(row[1] or ""), str(row[2] or "")
                        if "Nama Barang" in desc_col or not desc_col.strip() or "Harga Jual" in kode_col:
                            continue

                        kodes = re.findall(r'\d{6,}', kode_col)
                        blocks = re.split(r'PPnBM.*?=.*?\n?', desc_col)

                        for i, block in enumerate(blocks):
                            if "Rp" not in block: continue

                            match_harga = re.search(r'Rp\s*([\d\.]+,\d{2})\s*x\s*([\d\.,]+)\s*([A-Za-z]+)', block)
                            if match_harga:
                                harga = float(match_harga.group(1).replace('.', '').replace(',', '.'))
                                qty = float(match_harga.group(2).replace('.', '').replace(',', '.'))
                                satuan = match_harga.group(3)
                                potongan_harga = 0

                                nama_barang = block[:match_harga.start()].replace('\n', ' ').strip()
                                kode_barang = kodes[i] if i < len(kodes) else (kodes[0] if kodes else "")

                                dpp = (harga * qty) - potongan_harga
                                ppn = dpp * 0.12  # Asumsi PPN 12%
                                netto = dpp + ppn

                                baris_data.append({
                                    "Nama Pembeli": nama_pembeli, "NPWP Pembeli": npwp_pembeli,
                                    "Kode dan Nomor Seri Faktur Pajak": no_seri, "No": no_urut,
                                    "Kode Barang": kode_barang, "Nama Barang": nama_barang,
                                    "Harga": harga, "Qty": qty, "Satuan": satuan, "Potongan Harga": potongan_harga,
                                    "DPP": dpp, "PPN": ppn, "NETTO": netto,
                                })
                                no_urut += 1
        return baris_data

    def process_pm(self, folder):
        if not folder or not os.path.isdir(folder):
            raise ValueError("Folder tidak ditemukan. Pilih folder yang tersedia.")
        pdf_files = sorted(glob.glob(os.path.join(folder, "**", "*.pdf"), recursive=True))
        if not pdf_files:
            raise ValueError("Tidak ada PDF di folder atau subfolder ini. Pilih folder lain.")

        self.log(f"Memproses {len(pdf_files)} file …")

        semua_baris_data = []
        dilewati = 0
        try:
            hasil = self._peta_pdf(self._baca_pm, pdf_files)
            for index, (file_pdf, (rows, galat)) in enumerate(zip(pdf_files, hasil)):
                self.progress(index, len(pdf_files))
                nama_file = os.path.basename(file_pdf)
                folder_sumber = os.path.relpath(os.path.dirname(file_pdf), folder)
                self.log(f"Membaca {os.path.relpath(file_pdf, folder)}")

                if galat is not None:
                    dilewati += 1
                    self.log(f"Gagal: {nama_file} — {galat}")
                    continue
                if not rows:
                    dilewati += 1
                    self.log(f"DILEWATI: {nama_file} — tidak ada rincian faktur yang dapat dibaca.")
                for baris in rows:
                    baris["Folder Sumber"] = folder_sumber
                    baris["Nama File PDF"] = nama_file
                    semua_baris_data.append(baris)

            if semua_baris_data:
                output_path = os.path.join(folder, "Hasil_Pajak_Masukan.xlsx")
                # Kolom mengikuti urutan kunci baris; "No" (nomor barang per faktur) tidak dirata-tengahkan.
                self._write_excel(
                    semua_baris_data, output_path, "Rekap_Faktur",
                    text_cols=["NPWP Pembeli", "Kode dan Nomor Seri Faktur Pajak", "Kode Barang"],
                    money_cols=["Harga", "Potongan Harga", "DPP", "PPN", "NETTO"],
                    center_cols=(),
                )

                self.log(f"Selesai — {output_path}")
                return output_path, f"Selesai — {len(semua_baris_data)} baris, {dilewati} PDF dilewati."
            else:
                self.log("Tidak ada data yang ditemukan.")
                return None, "Tidak ada data yang cocok. Periksa jenis formulir dan pastikan PDF memiliki lapisan teks."

        except Exception as e:
            self.log(f"Error: {str(e)}")
            raise

    # ══════════════════════════════════════════
    #  EKSTRAKSI — REKENING KORAN (e-Statement BCA: Giro & Tahapan)
    # ══════════════════════════════════════════
    BULAN = ("JANUARI", "FEBRUARI", "MARET", "APRIL", "MEI", "JUNI",
             "JULI", "AGUSTUS", "SEPTEMBER", "OKTOBER", "NOVEMBER", "DESEMBER")
    _KOLOM_REKENING = ["TANGGAL", "KETERANGAN", "CBG", "MUTASI", "SALDO"]
    _UANG = re.compile(r"\d{1,3}(?:,\d{3})*\.\d{2}")
    _RINGKASAN_REKENING = re.compile(r"(SALDO AWAL|MUTASI CR|MUTASI DB|SALDO AKHIR)\s*:\s*(\S+)(?:\s+(\d+))?")

    @staticmethod
    def _rupiah(value):
        return Decimal(value.replace(",", ""))

    @staticmethod
    def _teks_uang(value):
        return f"{value:,.2f}"

    @staticmethod
    def _tanggal_mutasi(teks, bulan, tahun):
        """'31/12' pada laporan bulan/tahun tertentu -> datetime; ValueError bila tidak valid.

        Mutasi bulan sebelumnya (mis. 31/12 pada periode Januari) milik tahun sebelumnya.
        """
        hari, bulan_baris = (int(part) for part in teks.split("/"))
        return datetime(tahun - 1 if bulan_baris > bulan else tahun, bulan_baris, hari)

    @staticmethod
    def _tandai_ganda(laporan, kunci, daftar_catatan):
        """Laporan dengan periode sama di lebih dari satu PDF: setiap salinan diberi catatan (jadi PERLU CEK).

        Tidak ada yang dibuang karena ExpCore tidak tahu salinan mana yang dimaksud; tanpa tanda ini
        transaksinya terhitung ganda di Excel tanpa terlihat. Mengembalikan kelompok salinan untuk log.
        """
        kelompok = {}
        for data in laporan:
            kelompok.setdefault(kunci(data), []).append(data)
        ganda = [salinan for salinan in kelompok.values() if len(salinan) > 1]
        for salinan in ganda:
            for data in salinan:
                lain = ", ".join(os.path.normpath(os.path.join(d["folder_sumber"], d["file"]))
                                 for d in salinan if d is not data)
                for catatan in daftar_catatan(data):
                    catatan.append(f"Laporan periode yang sama juga ada di {lain}; transaksinya bisa tercatat ganda.")
        return ganda

    @classmethod
    def _cek_saldo_berjalan(cls, transaksi, awal, akhir):
        """Catatan selisih saldo berjalan: mendeteksi debit/kredit yang tertukar walau totalnya cocok."""
        catatan, berjalan, uang = [], awal, cls._teks_uang
        for t in transaksi:
            berjalan += (t["kredit"] or 0) - (t["debit"] or 0)
            if t["saldo"] is not None and t["saldo"] != berjalan:
                tanggal = t["tanggal"].strftime("%d/%m") if isinstance(t["tanggal"], datetime) else t["tanggal"]
                catatan.append(f"{tanggal}: saldo PDF {uang(t['saldo'])}, hasil hitung {uang(berjalan)}.")
                berjalan = t["saldo"]
        if berjalan != akhir:
            catatan.append(f"Saldo hasil hitung {uang(berjalan)} berbeda dari saldo akhir {uang(akhir)}.")
        return catatan

    @staticmethod
    def _baris_halaman(page):
        """Kata pdfplumber per baris visual: urut dari atas, lalu dari kiri."""
        lines = []
        for word in sorted(page.extract_words(), key=lambda w: (w["top"], w["x0"])):
            if lines and word["top"] - lines[-1][0]["top"] <= 2:
                lines[-1].append(word)
            else:
                lines.append([word])
        return [sorted(line, key=lambda w: w["x0"]) for line in lines]

    @classmethod
    def _extract_rekening_koran(cls, pages):
        """Baca satu e-Statement BCA (Rekening Giro/Tahapan) dari halaman pdfplumber.

        Kolom ditentukan dari posisi judul tabel di setiap halaman, bukan dari urutan teks:
        nomor cabang (CBG) dan angka di dalam keterangan tidak boleh terbaca sebagai mutasi.
        Mutasi bertanda DB adalah debit, lainnya kredit. Ringkasan di akhir PDF dibaca
        terpisah lalu dicocokkan dengan transaksi; setiap selisih masuk "catatan".
        Mengembalikan None bila PDF bukan e-Statement tersebut.
        """
        teks = (pages[0].extract_text() or "") if pages else ""
        judul = teks.strip().split("\n", 1)[0].strip()
        norek = re.search(r"NO\.\s*REKENING\s*:\s*(\d+)", teks)
        periode = re.search(r"PERIODE\s*:\s*([A-Z]+)\s+(\d{4})", teks)
        if not (judul.startswith("REKENING") and norek and periode and periode.group(1) in cls.BULAN):
            return None
        nama = re.search(r"^(.*?)\s*NO\.\s*REKENING", teks, re.MULTILINE)
        mata_uang = re.search(r"MATA\s*UANG\s*:\s*(\S+)", teks)
        halaman = re.search(r"HALAMAN\s*:\s*\d+\s*/\s*(\d+)", teks)
        bulan, tahun = cls.BULAN.index(periode.group(1)) + 1, int(periode.group(2))

        catatan, baris, ringkasan = [], [], {}
        for nomor, page in enumerate(pages, 1):
            lines = cls._baris_halaman(page)
            judul_tabel = next((i for i, line in enumerate(lines)
                                if [w["text"] for w in line] == cls._KOLOM_REKENING), None)
            if judul_tabel is None:
                catatan.append(f"Halaman {nomor}: tabel mutasi tidak ditemukan.")
                continue
            kolom = {w["text"]: w for w in lines[judul_tabel]}
            batas_cbg = kolom["CBG"]["x0"] - 15  # kiri batas ini: keterangan
            batas_angka = kolom["CBG"]["x1"] + 5  # kanan batas ini: mutasi, tanda DB/CR, saldo
            for line in lines[judul_tabel + 1:]:
                teks_baris = " ".join(w["text"] for w in line)
                if teks_baris.startswith("Bersambung ke Halaman"):
                    break
                cocok = cls._RINGKASAN_REKENING.fullmatch(teks_baris)
                if cocok:
                    ringkasan[cocok.group(1)] = cocok.group(2, 3)
                    continue
                if ringkasan:
                    catatan.append(f"Halaman {nomor}: teks setelah ringkasan diabaikan: {teks_baris[:60]}")
                    continue

                tanggal, cbg, mutasi, tanda, saldo, keterangan, asing = None, [], [], [], [], [], []
                for word in line:
                    text = word["text"]
                    if word["x1"] <= kolom["TANGGAL"]["x1"] + 2:
                        if tanggal is None and re.fullmatch(r"\d{2}/\d{2}", text):
                            tanggal = text
                        else:
                            asing.append(text)
                    elif word["x0"] >= batas_angka:
                        sebelum_saldo = word["x1"] < kolom["SALDO"]["x0"]
                        if cls._UANG.fullmatch(text):
                            (mutasi if sebelum_saldo else saldo).append(text)
                        elif text in ("DB", "CR") and sebelum_saldo:
                            tanda.append(text)
                        else:
                            asing.append(text)
                    elif word["x0"] >= batas_cbg:
                        cbg.append(text)
                    else:
                        keterangan.append(text)
                if asing:
                    catatan.append(f"Halaman {nomor}: teks tak dikenal di kolom tanggal/angka: {' '.join(asing)[:60]}")

                isi = {"keterangan": keterangan, "cbg": cbg, "mutasi": mutasi, "tanda": tanda, "saldo": saldo}
                if tanggal:
                    baris.append({"tanggal": tanggal, "halaman": nomor, **isi})
                elif baris:  # Lanjutan keterangan, termasuk yang berlanjut ke halaman berikutnya.
                    for key, values in isi.items():
                        baris[-1][key] += values
                elif any(isi.values()):
                    catatan.append(f"Halaman {nomor}: baris tanpa tanggal sebelum transaksi pertama: {teks_baris[:60]}")

        transaksi, saldo_awal_tabel = [], None
        for item in baris:
            keterangan = " ".join(item["keterangan"])
            asal = f"{item['tanggal']} (hal. {item['halaman']})"
            if not item["mutasi"] and keterangan == "SALDO AWAL" and not transaksi and len(item["saldo"]) == 1:
                saldo_awal_tabel = cls._rupiah(item["saldo"][0])
                continue
            if len(item["mutasi"]) != 1 or len(item["tanda"]) > 1 or len(item["saldo"]) > 1 or len(item["cbg"]) > 1:
                catatan.append(f"{asal}: susunan kolom tidak dikenal — {keterangan[:50]}")
            try:
                tanggal = cls._tanggal_mutasi(item["tanggal"], bulan, tahun)
            except ValueError:
                tanggal = item["tanggal"]
                catatan.append(f"{asal}: tanggal tidak valid.")
            nilai = cls._rupiah(item["mutasi"][0]) if item["mutasi"] else None
            debit = item["tanda"][:1] == ["DB"]
            transaksi.append({
                "tanggal": tanggal, "keterangan": keterangan, "cbg": " ".join(item["cbg"]),
                "debit": nilai if debit else None, "kredit": None if debit else nilai,
                "saldo": cls._rupiah(item["saldo"][0]) if item["saldo"] else None,
            })

        nilai_ringkasan = {
            label: (cls._rupiah(nilai), int(jumlah) if jumlah else None)
            for label, (nilai, jumlah) in ringkasan.items() if cls._UANG.fullmatch(nilai)
        }
        uang = cls._teks_uang
        if len(nilai_ringkasan) < 4 or None in (nilai_ringkasan["MUTASI CR"][1], nilai_ringkasan["MUTASI DB"][1]):
            catatan.append("Ringkasan saldo dan mutasi di akhir PDF tidak lengkap.")
        else:
            awal, akhir = nilai_ringkasan["SALDO AWAL"][0], nilai_ringkasan["SALDO AKHIR"][0]
            for label, field in (("MUTASI CR", "kredit"), ("MUTASI DB", "debit")):
                values = [t[field] for t in transaksi if t[field] is not None]
                total, jumlah = nilai_ringkasan[label]
                if (sum(values, Decimal(0)), len(values)) != (total, jumlah):
                    catatan.append(f"{field.title()} terbaca {uang(sum(values, Decimal(0)))} dari {len(values)} "
                                   f"transaksi, ringkasan PDF {uang(total)} dari {jumlah}.")
            if awal + nilai_ringkasan["MUTASI CR"][0] - nilai_ringkasan["MUTASI DB"][0] != akhir:
                catatan.append("Ringkasan PDF tidak seimbang: saldo awal + mutasi CR − mutasi DB ≠ saldo akhir.")
            if saldo_awal_tabel is not None and saldo_awal_tabel != awal:
                catatan.append(f"Saldo awal di tabel {uang(saldo_awal_tabel)} berbeda dari ringkasan {uang(awal)}.")
            catatan += cls._cek_saldo_berjalan(transaksi, awal, akhir)
        if halaman and int(halaman.group(1)) != len(pages):
            catatan.append(f"PDF hanya berisi {len(pages)} dari {halaman.group(1)} halaman.")

        return {
            "jenis": judul, "norek": norek.group(1), "nama": nama.group(1).strip() if nama else "",
            "periode": f"{periode.group(1)} {tahun}", "bulan": bulan, "tahun": tahun,
            "mata_uang": mata_uang.group(1) if mata_uang else "",
            "transaksi": transaksi, "ringkasan": nilai_ringkasan, "catatan": catatan,
        }

    _ISI_JUDUL = PatternFill(start_color="D9D9D9", end_color="D9D9D9", fill_type="solid")
    _GAYA_HASIL = {
        "SESUAI": (PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid"),
                   Font(bold=True, color="006100")),
        "PERLU CEK": (PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid"),
                      Font(bold=True, color="9C0006")),
    }
    _FORMAT_UANG = "#,##0.00"

    @classmethod
    def _judul_excel(cls, cells):
        for cell in cells:
            cell.fill, cell.font = cls._ISI_JUDUL, Font(bold=True)

    @staticmethod
    def _angka(value):
        return float(value) if value is not None else None

    @staticmethod
    def _nama_sheet(used, awalan, akhiran):
        """Nama sheet unik maks. 31 karakter: awalan yang dipotong, akhiran (nomor & periode) tetap utuh."""
        base = re.sub(r"[\[\]:*?/\\]", " ", awalan[:max(0, 31 - len(akhiran))] + akhiran)[:31].strip()
        name, copy = base, 2
        while name.casefold() in used:
            suffix = f" ({copy})"
            name, copy = base[:31 - len(suffix)].rstrip() + suffix, copy + 1
        used.add(name.casefold())
        return name

    @classmethod
    def _tulis_panel(cls, ws, panel, kolom, hasil, judul):
        """Panel label–nilai di kanan tabel mutasi, mulai kolom `kolom`; None = baris kosong."""
        for row_number, values in enumerate(panel, 1):
            if values is None:
                continue
            cells = [ws.cell(row=row_number, column=kolom + index, value=value) for index, value in enumerate(values)]
            if values[0] in judul:
                cls._judul_excel(cells)
            elif values[0] == "No. Rekening":
                cells[1].number_format = "@"
            elif isinstance(values[1], float):
                cells[1].number_format = cls._FORMAT_UANG
            elif isinstance(values[1], datetime):
                cells[1].number_format = "dd/mm/yyyy"
            if values[0] == hasil:
                cells[0].fill, cells[0].font = cls._GAYA_HASIL[hasil]

    @classmethod
    def _tautan_sheet(cls, cell, name):
        cell.hyperlink = Hyperlink(ref=cell.coordinate, location=f"'{name}'!A1")
        cell.font = Font(color="0563C1", underline="single")

    @classmethod
    def _rapikan_tabel(cls, ws):
        """Judul tebal, baris judul dibekukan, filter, dan lebar kolom mengikuti isi (maks. 55)."""
        cls._judul_excel(ws[1])
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions
        for column in ws.columns:
            max_length = max((len(str(cell.value)) for cell in column if cell.value is not None), default=0)
            ws.column_dimensions[column[0].column_letter].width = min(max_length + 2, 55)

    @classmethod
    def _write_rekening_excel(cls, rekening, output_path):
        """Sheet Ringkasan + satu sheet per PDF (tabel mutasi, panel informasi & ringkasan di kanan).

        Ringkasan PDF ditulis di panel terpisah (kolom H–J), bukan di bawah tabel: kolom DEBIT/CREDIT
        tetap berisi transaksi saja sehingga SUM, filter, dan pengurutan tidak ikut menghitung ringkasan.
        """
        uang, angka = cls._FORMAT_UANG, cls._angka
        book = Workbook()
        overview = book.active
        overview.title = "Ringkasan"
        overview.append(["No", "Sheet", "Jenis Rekening", "No. Rekening", "Nama", "Periode", "Mata Uang",
                         "Saldo Awal", "Mutasi CR", "Jumlah CR", "Mutasi DB", "Jumlah DB", "Saldo Akhir",
                         "Transaksi Terbaca", "Hasil Cek", "Catatan", "Folder Sumber", "File Name"])
        used = {"ringkasan"}
        for number, data in enumerate(rekening, 1):
            jenis = re.sub(r"^REKENING\s*", "", data["jenis"]).title() or "Rekening"
            name = cls._nama_sheet(used, jenis, f" {data['norek']} {data['tahun']}-{data['bulan']:02d}")

            ws = book.create_sheet(name)
            ws.append(["TANGGAL", "KETERANGAN", "CBG", "DEBIT", "CREDIT", "SALDO"])
            cls._judul_excel(ws[1])
            for t in data["transaksi"]:
                ws.append([t["tanggal"], t["keterangan"], t["cbg"] or None,
                           angka(t["debit"]), angka(t["kredit"]), angka(t["saldo"])])
            last = ws.max_row
            for row in ws.iter_rows(min_row=2, max_row=last):
                row[0].number_format = "dd/mm/yyyy"
                row[2].number_format = "@"
                for cell in row[3:6]:
                    cell.number_format = uang
            ws.freeze_panes = "A2"
            ws.auto_filter.ref = f"A1:F{last}"

            ringkasan = data["ringkasan"]
            nilai = lambda label, index=0: ringkasan[label][index] if label in ringkasan else None
            hasil = "PERLU CEK" if data["catatan"] else "SESUAI"
            panel = [
                ("INFORMASI REKENING", None, None),
                ("Jenis Rekening", data["jenis"], None), ("No. Rekening", data["norek"], None),
                ("Nama", data["nama"], None), ("Periode", data["periode"], None),
                ("Mata Uang", data["mata_uang"], None), ("File", data["file"], None),
                None,
                ("RINGKASAN PDF", "NILAI", "TRANSAKSI"),
                ("SALDO AWAL", angka(nilai("SALDO AWAL")), None),
                ("MUTASI CR", angka(nilai("MUTASI CR")), nilai("MUTASI CR", 1)),
                ("MUTASI DB", angka(nilai("MUTASI DB")), nilai("MUTASI DB", 1)),
                ("SALDO AKHIR", angka(nilai("SALDO AKHIR")), None),
                None,
                ("HASIL CEK", None, None),
                (hasil, None, None),
                *((f"• {note}", None, None) for note in data["catatan"]),
            ]
            cls._tulis_panel(ws, panel, 8, hasil, ("INFORMASI REKENING", "RINGKASAN PDF", "HASIL CEK"))

            widths = {"A": 12, "B": min(max((len(t["keterangan"]) for t in data["transaksi"]), default=10) + 2, 80),
                      "C": 7, "D": 17, "E": 17, "F": 18, "G": 3, "H": 20, "J": 11,
                      "I": min(max(len(str(v)) for v in (data["jenis"], data["nama"], data["file"], "1,000,000,000.00")) + 2, 45)}
            for column, width in widths.items():
                ws.column_dimensions[column].width = width

            overview.append([
                number, name, data["jenis"], data["norek"], data["nama"], data["periode"], data["mata_uang"],
                angka(nilai("SALDO AWAL")), angka(nilai("MUTASI CR")), nilai("MUTASI CR", 1),
                angka(nilai("MUTASI DB")), nilai("MUTASI DB", 1), angka(nilai("SALDO AKHIR")),
                len(data["transaksi"]), hasil, "; ".join(data["catatan"]) or None, data["folder_sumber"], data["file"],
            ])
            row = overview[overview.max_row]
            cls._tautan_sheet(row[1], name)
            row[3].number_format = "@"
            for cell in (row[7], row[8], row[10], row[12]):
                cell.number_format = uang
            row[14].fill, row[14].font = cls._GAYA_HASIL[hasil]
            row[0].alignment = Alignment(horizontal="center")

        cls._rapikan_tabel(overview)
        book.save(output_path)

    def process_rekening_koran(self, folder):
        if not folder or not os.path.isdir(folder):
            raise ValueError("Folder tidak ditemukan. Pilih folder yang tersedia.")
        pdf_files = sorted(glob.glob(os.path.join(folder, "**", "*.pdf"), recursive=True))
        if not pdf_files:
            raise ValueError("Tidak ada PDF di folder atau subfolder ini. Pilih folder lain.")

        self.log(f"Memproses {len(pdf_files)} file …")
        rekening, dilewati = [], 0
        try:
            hasil = self._peta_pdf(partial(_baca_halaman, self._extract_rekening_koran), pdf_files)
            for index, (file_pdf, (data, galat)) in enumerate(zip(pdf_files, hasil)):
                self.progress(index, len(pdf_files))
                relatif = os.path.relpath(file_pdf, folder)
                self.log(f"Membaca {relatif}")
                if galat is not None:
                    dilewati += 1
                    self.log(f"GAGAL: {relatif} — {galat}")
                    continue
                if data is None:
                    dilewati += 1
                    self.log(f"DILEWATI: {relatif} — bukan e-Statement Rekening Giro/Tahapan BCA.")
                    continue
                data["folder_sumber"] = os.path.relpath(os.path.dirname(file_pdf), folder)
                data["file"] = os.path.basename(file_pdf)
                rekening.append(data)
                hasil = "PERLU CEK" if data["catatan"] else "SESUAI"
                self.log(f"{hasil}: {data['jenis']} {data['norek']} {data['periode']} — "
                         f"{len(data['transaksi'])} transaksi")
                for note in data["catatan"]:
                    self.log(f"  • {note}")

            if not rekening:
                self.log("Tidak ada data yang ditemukan.")
                return None, ("Tidak ada rekening koran yang cocok. Gunakan e-Statement BCA (Giro/Tahapan) "
                              "yang memiliki lapisan teks.")

            rekening.sort(key=lambda d: (d["jenis"], d["norek"], d["tahun"], d["bulan"], d["file"]))
            for salinan in self._tandai_ganda(rekening, lambda d: (d["jenis"], d["norek"], d["tahun"], d["bulan"]),
                                              lambda d: [d["catatan"]]):
                d = salinan[0]
                self.log(f"PERINGATAN: {d['jenis']} {d['norek']} periode {d['bulan']:02d}-{d['tahun']} muncul di "
                         f"{len(salinan)} PDF: {', '.join(x['file'] for x in salinan)} — ditandai PERLU CEK.")

            output_path = os.path.join(folder, "!Hasil_Rekap_Rekening_Koran.xlsx")
            self._write_rekening_excel(rekening, output_path)
            transaksi = sum(len(d["transaksi"]) for d in rekening)
            perlu_cek = sum(bool(d["catatan"]) for d in rekening)
            self.log(f"Output: {output_path}")
            return output_path, (f"Selesai — {len(rekening)} rekening koran, {transaksi} transaksi, "
                                 f"{perlu_cek} perlu dicek, {dilewati} PDF dilewati.")
        except Exception as e:
            self.log(f"Error: {str(e)}")
            raise

    # ══════════════════════════════════════════
    #  EKSTRAKSI — REKENING KORAN CIMB NIAGA (Combine Statement Portfolio)
    # ══════════════════════════════════════════
    _BULAN_INGGRIS = ("JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", "JUNE", "JULY", "AUGUST",
                      "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER")
    # Judul tabel mutasi (baris kedua judul dua bahasa), kiri ke kanan = urutan kolom.
    _CIMB_JUDUL = ("Transaksi/", "Valuta/", "Uraian", "Cek/BG", "Debit/", "Kredit/", "Saldo/")
    # Daftar rekening di RINCIAN ASET yang direkap: kategori, judul daftar, baris total (Ekuivalen IDR).
    _CIMB_KATEGORI = (
        ("Tabungan/Giro", re.compile(r"Tabungan\s*/\s*Giro\s*/\s*Savings\s*/\s*Current\s+Account", re.I),
         re.compile(r"Total\s+Tabungan\s*/\s*Giro\s*/.*\s(\S+)", re.I)),
        ("Tabungan Berjangka", re.compile(r"Tabungan\s+Berjangka\s*/\s*Installment\s+Savings?", re.I),
         re.compile(r"TOTAL\s+TABUNGAN\s+BERJANGKA\s*/.*\s(\S+)", re.I)),
    )
    _CIMB_ASET = re.compile(r"RINCIAN\s+ASET\s*/\s*ASSET\s+DETAIL", re.I)
    _CIMB_AKUN = re.compile(r"Nomor\s+Rekening\s*-\s*Mata\s+Uang\s*/\s*Account\s+Number\s*-\s*Currency\s*:"
                            r"\s*(\d+)\s*-\s*([A-Z]{3})")
    _CIMB_PRODUK = re.compile(r"Nama\s+Produk\s*/\s*Product\s+Name\s*:\s*(.*)")
    # Isi kotak kepala setiap halaman (setelah halaman sampul): tanggal laporan, nomor CIF, profil risiko.
    _CIMB_KEPALA = re.compile(r"\d{1,2}\s+[A-Za-z]+\s+\d{4}\s+(\d{6,})\b")

    @staticmethod
    def _cimb_garis(page):
        """Garis horizontal tabel (batas sel) di halaman, urut dari atas: [(y, [(x0, x1), ...]), ...]."""
        garis = []
        for edge in sorted(page.rects + page.lines, key=lambda e: e["top"]):
            if edge["height"] < 1.5 and edge["width"] > 2:
                if garis and edge["top"] - garis[-1][0] <= 1:
                    garis[-1][1].append((edge["x0"], edge["x1"]))
                else:
                    garis.append((edge["top"], [(edge["x0"], edge["x1"])]))
        return garis

    @classmethod
    def _cimb_kolom(cls, judul, garis):
        """Tepi kolom tabel mutasi dari garis tepat di bawah judulnya; None bila susunannya tidak dikenal."""
        bawah = max(w["bottom"] for w in judul)
        tepi = []
        for x in sorted(x for segmen in next((s for y, s in garis if y > bawah), []) for x in segmen):
            if not tepi or x - tepi[-1] > 1.5:
                tepi.append(x)
        kolom = lambda w: bisect.bisect(tepi, (w["x0"] + w["x1"]) / 2) - 1
        if len(tepi) == len(cls._CIMB_JUDUL) + 1 and all(
                any(w["text"] == teks and kolom(w) == index for w in judul)
                for index, teks in enumerate(cls._CIMB_JUDUL)):
            return tepi
        return None

    @classmethod
    def _cimb_isi(cls, pages):
        """Isi laporan berurutan lintas halaman: penanda bagian dan sel tabel, tanpa bergantung nomor halaman.

        Baris yang dikenali dari teksnya (judul bagian, baris total, identitas rekening) menjadi penanda
        (tuple). Baris lain dikelompokkan per sel tabel, yaitu di antara dua garis batas: satu transaksi
        CIMB bisa beberapa baris dengan tanggal dan nominal di tengah sel. Setiap sel membawa tepi kolom
        tabel mutasi yang berlaku di halamannya (None bila belum ada judul tabel di halaman itu).
        """
        isi, cif, jumlah_halaman = [], "", None
        for nomor, page in enumerate(pages, 1):
            garis = cls._cimb_garis(page)
            ys = [y for y, _ in garis]
            lines = cls._baris_halaman(page)
            teks = [" ".join(w["text"] for w in line) for line in lines]
            # Kotak kepala halaman diakhiri baris tanggal laporan + CIF; halaman n/total ada di dalamnya.
            kepala = next((index for index, text in enumerate(teks[:10]) if cls._CIMB_KEPALA.match(text)), None)
            if kepala is not None:
                cif = cif or cls._CIMB_KEPALA.match(teks[kepala]).group(1)
                halaman = re.search(r"\b\d+\s*/\s*(\d+)\b", " ".join(teks[:kepala + 1]))
                jumlah_halaman = int(halaman.group(1)) if halaman else jumlah_halaman
            # Nomor dokumen di kaki halaman: angka saja dan di bawah garis tabel terakhir, sehingga uraian
            # yang kebetulan hanya angka (mis. nomor rekening tujuan) tidak ikut terbuang.
            if teks and teks[-1].isdigit() and (not ys or lines[-1][0]["top"] > ys[-1]):
                lines, teks = lines[:-1], teks[:-1]
            awal = 0 if kepala is None else kepala + 1
            lines, teks = lines[awal:], teks[awal:]
            sel = lambda line: bisect.bisect(ys, (line[0]["top"] + line[0]["bottom"]) / 2)
            judul = {sel(line): cls._cimb_kolom(line, garis) for line in lines
                     if {"Uraian", "Debit/", "Kredit/", "Saldo/"} <= {w["text"] for w in line}}
            kolom, aktif = None, None
            for line, text in zip(lines, teks):
                kunci = sel(line)
                if kunci in judul:  # judul tabel mutasi: beberapa baris dalam satu sel
                    if aktif != ("judul", kunci):
                        kolom, aktif = judul[kunci], ("judul", kunci)
                        isi.append(("judul", nomor, kolom))
                    continue
                penanda = None
                if cls._CIMB_ASET.fullmatch(text):
                    penanda = ("aset",)
                for kategori, judul_daftar, baris_total in cls._CIMB_KATEGORI:
                    total = baris_total.fullmatch(text)
                    if judul_daftar.fullmatch(text):
                        penanda = ("daftar", kategori)
                    elif total:
                        penanda = ("total", kategori, total.group(1))
                akun, produk = cls._CIMB_AKUN.fullmatch(text), cls._CIMB_PRODUK.fullmatch(text)
                if akun:
                    penanda = ("akun", akun.group(1), akun.group(2))
                elif produk:
                    penanda = ("produk", produk.group(1).strip())
                if penanda:
                    isi.append(penanda)
                    aktif = None
                    continue
                if aktif != ("sel", kunci):
                    isi.append({"halaman": nomor, "kolom": kolom, "words": [], "teks": []})
                    aktif = ("sel", kunci)
                isi[-1]["words"] += line
                isi[-1]["teks"].append(text)
        return isi, cif, jumlah_halaman

    @classmethod
    def _cimb_mutasi(cls, akun, sel, bulan, tahun):
        """Masukkan satu sel tabel mutasi ke rekening: SALDO AWAL, transaksi, Total, atau SALDO AKHIR."""
        asal, ringkas = f"Hal. {sel['halaman']}", " ".join(sel["teks"])[:70]
        if sel["kolom"] is None:
            akun["catatan"].append(f"{asal}: teks di luar tabel mutasi — {ringkas}")
            return
        isi, asing = [[] for _ in cls._CIMB_JUDUL], []
        for word in sel["words"]:
            index = bisect.bisect(sel["kolom"], (word["x0"] + word["x1"]) / 2) - 1
            (isi[index] if 0 <= index < len(isi) else asing).append(word["text"])
        tanggal, valuta, uraian, cek, debit, kredit, saldo = (" ".join(teks) for teks in isi)
        uang = {nama: cls._rupiah(teks) if cls._UANG.fullmatch(teks) else None
                for nama, teks in (("debit", debit), ("kredit", kredit), ("saldo", saldo))}
        # Setiap kolom nominal kosong atau tepat satu angka; tidak ada teks di luar kolom tabel.
        rapi = not asing and all(uang[nama] is not None or not teks
                                 for nama, teks in (("debit", debit), ("kredit", kredit), ("saldo", saldo)))

        if not tanggal and uraian in ("SALDO AWAL", "SALDO AKHIR"):
            if not rapi or valuta or cek or debit or kredit or uang["saldo"] is None or akun[uraian] is not None:
                akun["catatan"].append(f"{asal}: baris {uraian} tidak dikenal — {ringkas}")
            if akun[uraian] is None:
                akun[uraian] = uang["saldo"]
            akun["tutup"] = uraian == "SALDO AKHIR"
        elif tanggal == "Total":
            if not rapi or valuta or uraian or cek or saldo or akun["total"] is not None:
                akun["catatan"].append(f"{asal}: baris Total tidak dikenal — {ringkas}")
            if akun["total"] is None:
                akun["total"] = (uang["debit"] or Decimal(0), uang["kredit"] or Decimal(0))
        elif re.fullmatch(r"\d{2}/\d{2}", tanggal):
            tanggal_mutasi = {"tanggal": None, "valuta": None}
            for nama, label, teks in (("tanggal", "transaksi", tanggal), ("valuta", "valuta", valuta)):
                if not teks:
                    continue
                try:
                    acuan = tanggal_mutasi["tanggal"]
                    if nama == "valuta" and isinstance(acuan, datetime):
                        # Valuta bisa melewati pergantian tahun (31/12 -> 02/01): tahun terdekat dengan transaksi.
                        hari, bulan_valuta = (int(part) for part in teks.split("/"))
                        tahun_valuta = acuan.year + (acuan.month - bulan_valuta > 6) - (bulan_valuta - acuan.month > 6)
                        tanggal_mutasi[nama] = datetime(tahun_valuta, bulan_valuta, hari)
                    else:
                        tanggal_mutasi[nama] = cls._tanggal_mutasi(teks, bulan, tahun)
                except ValueError:
                    tanggal_mutasi[nama] = teks
                    akun["catatan"].append(f"{asal} {tanggal}: tanggal {label} tidak valid ({teks}).")
            if not rapi or bool(debit) == bool(kredit) or uang["saldo"] is None:
                akun["catatan"].append(f"{asal} {tanggal}: susunan kolom tidak dikenal — {uraian[:50]}")
            akun["transaksi"].append({**tanggal_mutasi, "keterangan": uraian, "cek": cek,
                                      "debit": uang["debit"], "kredit": uang["kredit"], "saldo": uang["saldo"]})
        else:
            akun["catatan"].append(f"{asal}: baris tidak dikenal — {ringkas}")

    @classmethod
    def _extract_rekening_cimb(cls, pages):
        """Baca satu Combine Statement Portfolio (Laporan Konsolidasi) CIMB Niaga dari halaman pdfplumber.

        Yang direkap hanya rekening yang tercantum di daftar RINCIAN ASET bagian Tabungan/Giro dan
        Tabungan Berjangka; rincian rekening lain (mis. deposito) dan halaman lain diabaikan. Setiap
        rekening dicek: total debit/kredit terhadap baris Total, saldo berjalan, saldo akhir terhadap
        daftar aset, dan per kategori jumlah saldo Ekuivalen IDR terhadap baris totalnya. Setiap selisih
        masuk "catatan". Mengembalikan None bila PDF bukan laporan tersebut.
        """
        teks = (pages[0].extract_text() or "") if pages else ""
        if "CIMB" not in teks or not re.search(r"COMBINE\s+STATEMENT\s+PORTFOLIO|LAPORAN\s+KONSOLIDASI\s+PORTFOLIO",
                                               teks, re.IGNORECASE):
            return None
        laporan = re.search(r"Tanggal\s+Laporan\s*:\s*(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})", teks)
        nama_bulan = laporan.group(2).upper() if laporan else ""
        bulan = next((index % 12 + 1 for index, nama in enumerate(cls._BULAN_INGGRIS + cls.BULAN)
                      if nama == nama_bulan), None)
        if not bulan:
            raise ValueError("Tanggal laporan di halaman pertama tidak terbaca.")
        tanggal_laporan = datetime(int(laporan.group(3)), bulan, int(laporan.group(1)))
        tahun = tanggal_laporan.year
        nasabah = re.search(r"Bapak/Ibu/Sir/Madam\s*\n(.+)", teks)
        isi, cif, jumlah_halaman = cls._cimb_isi(pages)

        uang = cls._teks_uang
        catatan_pdf, daftar, total, dilihat, blok = [], {}, {}, set(), []
        aset, bagian, akun = False, None, None
        for item in isi:
            jenis = item[0] if isinstance(item, tuple) else "sel"
            if jenis == "aset":
                aset = True
            elif not aset:
                continue
            elif jenis in ("daftar", "total", "akun"):
                bagian = item[1] if jenis == "daftar" else None
                akun = None
                if jenis == "daftar":
                    dilihat.add(item[1])
                elif jenis == "total":
                    total[item[1]] = item[2]
                else:
                    akun = {"norek": item[1], "mata_uang": item[2], "produk": "", "tutup": False,
                            "SALDO AWAL": None, "SALDO AKHIR": None, "total": None, "transaksi": [], "catatan": []}
                    blok.append(akun)
            elif akun is None or akun["tutup"]:
                # Baris daftar rekening: nomor rekening di depan, dua nilai paling kanan adalah saldo
                # mata uang asal dan saldo Ekuivalen IDR ("-" = 0, rekening jatuh tempo). Baris lain
                # (judul daftar) diabaikan. Salah baca tertangkap cek saldo akhir dan cek total kategori.
                words = item["words"] if jenis == "sel" else []
                if bagian and words and re.fullmatch(r"\d{6,20}", words[0]["text"]):
                    nilai = sorted((w for w in words if w["text"] == "-" or cls._UANG.fullmatch(w["text"])),
                                   key=lambda w: w["x1"])[-2:]
                    saldo, saldo_idr = ((Decimal(0) if w["text"] == "-" else cls._rupiah(w["text"]) for w in nilai)
                                        if len(nilai) == 2 else (None, None))
                    if words[0]["text"] in daftar:
                        catatan_pdf.append(f"Rekening {words[0]['text']} tercantum lebih dari sekali di daftar aset.")
                    else:
                        daftar[words[0]["text"]] = {"kategori": bagian, "saldo": saldo, "saldo_idr": saldo_idr}
            elif jenis == "produk":
                akun["produk"] = item[1]
            elif jenis == "judul":
                if item[2] is None:
                    akun["catatan"].append(f"Hal. {item[1]}: susunan kolom tabel mutasi tidak dikenal.")
            else:
                cls._cimb_mutasi(akun, item, bulan, tahun)

        if jumlah_halaman and jumlah_halaman != len(pages):
            catatan_pdf.append(f"PDF hanya berisi {len(pages)} dari {jumlah_halaman} halaman.")
        for akun in blok:
            catatan, transaksi = akun["catatan"], akun["transaksi"]
            awal, akhir = akun["SALDO AWAL"], akun["SALDO AKHIR"]
            for label, nilai in (("SALDO AWAL", awal), ("SALDO AKHIR", akhir)):
                if nilai is None:
                    catatan.append(f"Baris {label} tidak ditemukan.")
            if akun["total"] is None:
                catatan.append("Baris Total debit/kredit tidak ditemukan.")
            else:
                for field, nilai in zip(("debit", "kredit"), akun["total"]):
                    values = [t[field] for t in transaksi if t[field] is not None]
                    if sum(values, Decimal(0)) != nilai:
                        catatan.append(f"{field.title()} terbaca {uang(sum(values, Decimal(0)))} dari {len(values)} "
                                       f"transaksi, baris Total PDF {uang(nilai)}.")
                if None not in (awal, akhir) and awal + akun["total"][1] - akun["total"][0] != akhir:
                    catatan.append("Tabel PDF tidak seimbang: saldo awal + total kredit − total debit ≠ saldo akhir.")
            if None not in (awal, akhir):
                catatan += cls._cek_saldo_berjalan(transaksi, awal, akhir)

        per_rekening = {}
        for akun in blok:
            per_rekening.setdefault(akun["norek"], []).append(akun)
        rekening = []
        for norek, info in daftar.items():
            rincian = per_rekening.get(norek) or [{
                "norek": norek, "mata_uang": "", "produk": "", "SALDO AWAL": None, "SALDO AKHIR": None,
                "total": None, "transaksi": [], "catatan": ["Rincian transaksi rekening ini tidak ditemukan di PDF."],
            }]
            for akun in rincian:
                if len(rincian) > 1:
                    akun["catatan"].append(f"Rincian rekening ini muncul {len(rincian)} kali di PDF.")
                if info["saldo"] is None:
                    akun["catatan"].append(f"Saldo rekening di daftar {info['kategori']} tidak terbaca.")
                elif akun["SALDO AKHIR"] is not None and akun["SALDO AKHIR"] != info["saldo"]:
                    akun["catatan"].append(f"Saldo akhir {uang(akun['SALDO AKHIR'])} berbeda dari saldo di daftar "
                                           f"{info['kategori']} {uang(info['saldo'])}.")
                akun.update(kategori=info["kategori"], saldo_daftar=info["saldo"], saldo_idr=info["saldo_idr"])
                akun["catatan"] += catatan_pdf
                rekening.append(akun)

        kategori = []
        for nama, _, _ in cls._CIMB_KATEGORI:
            anggota = [info for info in daftar.values() if info["kategori"] == nama]
            if nama not in dilihat and nama not in total:
                continue
            catatan = []
            nilai_total = cls._rupiah(total[nama]) if cls._UANG.fullmatch(total.get(nama, "")) else None
            jumlah = sum((info["saldo_idr"] for info in anggota if info["saldo_idr"] is not None), Decimal(0))
            if nilai_total is None:
                catatan.append(f"Baris total {nama} tidak ditemukan atau tidak terbaca.")
            if not anggota:
                catatan.append(f"Daftar rekening {nama} tidak terbaca.")
            elif any(info["saldo_idr"] is None for info in anggota):
                catatan.append("Saldo Ekuivalen IDR sebagian rekening tidak terbaca.")
            elif nilai_total is not None and jumlah != nilai_total:
                catatan.append(f"Jumlah saldo Ekuivalen IDR {uang(jumlah)} berbeda dari total PDF {uang(nilai_total)}.")
            kategori.append({"kategori": nama, "rekening": len(anggota), "total": nilai_total, "jumlah": jumlah,
                             "catatan": catatan + catatan_pdf})

        return {
            "nasabah": nasabah.group(1).strip() if nasabah else "", "cif": cif,
            "tanggal_laporan": tanggal_laporan, "periode": f"{cls.BULAN[bulan - 1]} {tahun}",
            "bulan": bulan, "tahun": tahun, "rekening": rekening, "kategori": kategori,
        }

    @classmethod
    def _write_cimb_excel(cls, laporan, output_path):
        """Sheet Ringkasan (per rekening), Total Kategori (per PDF), Semua Transaksi, dan satu sheet mutasi
        per rekening per PDF.

        Seperti rekening koran BCA, ringkasan PDF ada di panel kanan (kolom I–J), bukan di bawah tabel,
        sehingga kolom DEBIT/KREDIT hanya berisi transaksi. Semua Transaksi menggabungkan transaksi seluruh
        rekening, urut per kategori lalu nomor rekening dan tetap kronologis di dalam setiap rekening, sehingga
        kolom SALDO tetap saldo berjalan rekening itu.
        """
        uang, angka = cls._FORMAT_UANG, cls._angka
        hasil_cek = lambda catatan: "PERLU CEK" if catatan else "SESUAI"
        book = Workbook()
        overview = book.active
        overview.title = "Ringkasan"
        overview.append(["No", "Sheet", "Kategori", "No. Rekening", "Nama Produk", "Mata Uang", "Tanggal Laporan",
                         "Saldo Awal", "Total Debit", "Total Kredit", "Saldo Akhir", "Saldo Ekuivalen IDR",
                         "Transaksi Terbaca", "Hasil Cek", "Catatan", "Nasabah", "Folder Sumber", "File Name"])
        totals = book.create_sheet("Total Kategori")
        totals.append(["No", "Tanggal Laporan", "Kategori", "Jumlah Rekening", "Total PDF (Ekuivalen IDR)",
                       "Jumlah Saldo Rekening (Ekuivalen IDR)", "Hasil Cek", "Catatan", "Nasabah",
                       "Folder Sumber", "File Name"])
        semua = book.create_sheet("Semua Transaksi")
        semua.append(["No", "Tanggal Transaksi", "Tanggal Valuta", "Kategori", "No. Rekening", "Nama Produk",
                      "Mata Uang", "Uraian Transaksi", "No Cek/BG", "Debit", "Kredit", "Saldo", "Hasil Cek",
                      "Tanggal Laporan", "Sheet", "File Name"])
        gabungan = []
        used = {"ringkasan", "total kategori", "semua transaksi"}
        for data in laporan:
            for kat in data["kategori"]:
                hasil = hasil_cek(kat["catatan"])
                totals.append([totals.max_row, data["tanggal_laporan"], kat["kategori"], kat["rekening"],
                               angka(kat["total"]), angka(kat["jumlah"]), hasil, "; ".join(kat["catatan"]) or None,
                               data["nasabah"], data["folder_sumber"], data["file"]])
                row = totals[totals.max_row]
                row[1].number_format = "dd/mm/yyyy"
                for cell in row[4:6]:
                    cell.number_format = uang
                row[6].fill, row[6].font = cls._GAYA_HASIL[hasil]
                row[0].alignment = Alignment(horizontal="center")

            for akun in data["rekening"]:
                name = cls._nama_sheet(used, "", f"{akun['norek']} {data['tahun']}-{data['bulan']:02d}")
                ws = book.create_sheet(name)
                ws.append(["TANGGAL TRANSAKSI", "TANGGAL VALUTA", "URAIAN TRANSAKSI", "NO CEK/BG",
                           "DEBIT", "KREDIT", "SALDO"])
                cls._judul_excel(ws[1])
                for t in akun["transaksi"]:
                    ws.append([t["tanggal"], t["valuta"], t["keterangan"], t["cek"] or None,
                               angka(t["debit"]), angka(t["kredit"]), angka(t["saldo"])])
                last = ws.max_row
                for row in ws.iter_rows(min_row=2, max_row=last):
                    for cell in row[:2]:
                        cell.number_format = "dd/mm/yyyy"
                    row[3].number_format = "@"
                    for cell in row[4:7]:
                        cell.number_format = uang
                ws.freeze_panes = "A2"
                ws.auto_filter.ref = f"A1:G{last}"

                debit, kredit = akun["total"] or (None, None)
                hasil = hasil_cek(akun["catatan"])
                panel = [
                    ("INFORMASI REKENING", None),
                    ("Kategori", akun["kategori"]), ("No. Rekening", akun["norek"]), ("Nama Produk", akun["produk"]),
                    ("Mata Uang", akun["mata_uang"]), ("Nasabah", data["nasabah"]),
                    ("Tanggal Laporan", data["tanggal_laporan"]), ("File", data["file"]),
                    None,
                    ("RINGKASAN PDF", "NILAI"),
                    ("SALDO AWAL", angka(akun["SALDO AWAL"])), ("TOTAL DEBIT", angka(debit)),
                    ("TOTAL KREDIT", angka(kredit)), ("SALDO AKHIR", angka(akun["SALDO AKHIR"])),
                    ("SALDO DI DAFTAR ASET", angka(akun["saldo_daftar"])),
                    ("SALDO EKUIVALEN IDR", angka(akun["saldo_idr"])),
                    None,
                    ("HASIL CEK", None),
                    (hasil, None),
                    *((f"• {note}", None) for note in akun["catatan"]),
                ]
                cls._tulis_panel(ws, panel, 9, hasil, ("INFORMASI REKENING", "RINGKASAN PDF", "HASIL CEK"))
                widths = {"A": 12, "B": 12, "D": 14, "E": 17, "F": 17, "G": 18, "H": 3, "I": 22,
                          "C": min(max((len(t["keterangan"]) for t in akun["transaksi"]), default=10) + 2, 80),
                          "J": min(max(len(str(v)) for v in (akun["produk"], data["nasabah"], data["file"],
                                                              "1,000,000,000.00")) + 2, 45)}
                for column, width in widths.items():
                    ws.column_dimensions[column].width = width

                overview.append([
                    overview.max_row, name, akun["kategori"], akun["norek"], akun["produk"], akun["mata_uang"],
                    data["tanggal_laporan"], angka(akun["SALDO AWAL"]), angka(debit), angka(kredit),
                    angka(akun["SALDO AKHIR"]), angka(akun["saldo_idr"]), len(akun["transaksi"]), hasil,
                    "; ".join(akun["catatan"]) or None, data["nasabah"], data["folder_sumber"], data["file"],
                ])
                row = overview[overview.max_row]
                cls._tautan_sheet(row[1], name)
                row[3].number_format = "@"
                row[6].number_format = "dd/mm/yyyy"
                for cell in row[7:12]:
                    cell.number_format = uang
                row[13].fill, row[13].font = cls._GAYA_HASIL[hasil]
                row[0].alignment = Alignment(horizontal="center")
                gabungan += [(akun, t, data, name, hasil) for t in akun["transaksi"]]

        # Urutan laporan sudah kronologis; sort stabil per kategori lalu nomor rekening menjaga urutan itu.
        kategori = {nama: index for index, (nama, _, _) in enumerate(cls._CIMB_KATEGORI)}
        gabungan.sort(key=lambda item: (kategori.get(item[0]["kategori"], len(kategori)), item[0]["norek"]))
        for number, (akun, t, data, name, hasil) in enumerate(gabungan, 1):
            semua.append([number, t["tanggal"], t["valuta"], akun["kategori"], akun["norek"], akun["produk"],
                          akun["mata_uang"], t["keterangan"], t["cek"] or None, angka(t["debit"]),
                          angka(t["kredit"]), angka(t["saldo"]), hasil, data["tanggal_laporan"], name, data["file"]])
            row = semua[semua.max_row]
            for cell in (row[1], row[2], row[13]):
                cell.number_format = "dd/mm/yyyy"
            row[4].number_format = row[8].number_format = "@"
            for cell in row[9:12]:
                cell.number_format = uang
            row[12].fill, row[12].font = cls._GAYA_HASIL[hasil]
            cls._tautan_sheet(row[14], name)
            row[0].alignment = Alignment(horizontal="center")

        cls._rapikan_tabel(overview)
        cls._rapikan_tabel(totals)
        cls._rapikan_tabel(semua)
        book.save(output_path)

    def process_rekening_cimb(self, folder):
        if not folder or not os.path.isdir(folder):
            raise ValueError("Folder tidak ditemukan. Pilih folder yang tersedia.")
        pdf_files = sorted(glob.glob(os.path.join(folder, "**", "*.pdf"), recursive=True))
        if not pdf_files:
            raise ValueError("Tidak ada PDF di folder atau subfolder ini. Pilih folder lain.")

        self.log(f"Memproses {len(pdf_files)} file …")
        laporan, dilewati = [], 0
        try:
            hasil = self._peta_pdf(partial(_baca_halaman, self._extract_rekening_cimb), pdf_files)
            for index, (file_pdf, (data, galat)) in enumerate(zip(pdf_files, hasil)):
                self.progress(index, len(pdf_files))
                relatif = os.path.relpath(file_pdf, folder)
                self.log(f"Membaca {relatif}")
                if galat is not None:
                    dilewati += 1
                    self.log(f"GAGAL: {relatif} — {galat}")
                    continue
                if data is None:
                    dilewati += 1
                    self.log(f"DILEWATI: {relatif} — bukan Combine Statement Portfolio CIMB Niaga.")
                    continue
                if not data["rekening"]:
                    dilewati += 1
                    self.log(f"DILEWATI: {relatif} — tidak ada rekening Tabungan/Giro atau Tabungan Berjangka "
                             f"yang terbaca di RINCIAN ASET.")
                    continue
                data["folder_sumber"] = os.path.relpath(os.path.dirname(file_pdf), folder)
                data["file"] = os.path.basename(file_pdf)
                laporan.append(data)
                for akun in data["rekening"]:
                    self.log(f"{'PERLU CEK' if akun['catatan'] else 'SESUAI'}: {akun['kategori']} {akun['norek']} "
                             f"{akun['mata_uang']} {data['periode']} — {len(akun['transaksi'])} transaksi")
                    for note in akun["catatan"]:
                        self.log(f"  • {note}")
                for kat in data["kategori"]:
                    total = self._teks_uang(kat["total"]) if kat["total"] is not None else "-"
                    self.log(f"{'PERLU CEK' if kat['catatan'] else 'SESUAI'}: Total {kat['kategori']} "
                             f"{data['periode']} — {total} (Ekuivalen IDR)")
                    for note in kat["catatan"]:
                        self.log(f"  • {note}")

            if not laporan:
                self.log("Tidak ada data yang ditemukan.")
                return None, ("Tidak ada laporan CIMB Niaga yang cocok. Gunakan Combine Statement Portfolio "
                              "(Laporan Konsolidasi) CIMB Niaga yang memiliki lapisan teks.")

            laporan.sort(key=lambda d: (d["cif"], d["tanggal_laporan"], d["file"]))
            # Tanpa CIF terbaca, laporan yang sama dikenali dari daftar rekeningnya (nasabah lain beda rekening).
            for salinan in self._tandai_ganda(
                    laporan, lambda d: (d["cif"] or tuple(a["norek"] for a in d["rekening"]), d["tanggal_laporan"]),
                    lambda d: [item["catatan"] for item in d["rekening"] + d["kategori"]]):
                d = salinan[0]
                self.log(f"PERINGATAN: laporan CIF {d['cif'] or '-'} tanggal {d['tanggal_laporan']:%d-%m-%Y} muncul "
                         f"di {len(salinan)} PDF: {', '.join(x['file'] for x in salinan)} — ditandai PERLU CEK.")

            output_path = os.path.join(folder, "!Hasil_Rekap_Rekening_CIMB.xlsx")
            self._write_cimb_excel(laporan, output_path)
            rekening = [akun for data in laporan for akun in data["rekening"]]
            perlu_cek = sum(bool(item["catatan"]) for data in laporan for item in data["rekening"] + data["kategori"])
            self.log(f"Output: {output_path}")
            return output_path, (f"Selesai — {len(laporan)} laporan, {len(rekening)} rekening, "
                                 f"{sum(len(akun['transaksi']) for akun in rekening)} transaksi, "
                                 f"{perlu_cek} perlu dicek, {dilewati} PDF dilewati.")
        except Exception as e:
            self.log(f"Error: {str(e)}")
            raise
