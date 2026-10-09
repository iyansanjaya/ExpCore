import os
import glob
import re
import csv
import unicodedata
import pdfplumber
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.hyperlink import Hyperlink
from datetime import datetime
from decimal import Decimal


class ExpCore:
    """Parser PDF Coretax. Aktivitas dan progres dilaporkan lewat callback."""

    # Sumber nama file pada Penamaan Bupot: kunci CLI -> (field data, label untuk log/CSV).
    RENAME_NAME_SOURCES = {
        "pemotong": ("NAMA_PEMOTONG", "Identitas Pemotong (C.3)"),
        "penerima": ("NAMA_PENERIMA", "Wajib Pajak yang Dipotong (A.2)"),
    }

    def __init__(self, log=None, progress=None):
        self.log = log or (lambda message: None)
        self.progress = progress or (lambda done, total: None)

    @staticmethod
    def _write_excel(df, output_path, sheet_name, text_cols=(), money_cols=()):
        """Tulis DataFrame ke Excel dengan header, format angka, dan lebar kolom.

        text_cols dipaksa format teks agar NPWP, masa pajak, dan nomor dokumen
        tidak diubah Excel jadi angka atau tanggal.
        """
        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name=sheet_name)
            ws = writer.sheets[sheet_name]

            for cell in ws[1]:
                cell.fill = PatternFill(start_color="D9D9D9", end_color="D9D9D9", fill_type="solid")
                cell.font = Font(bold=True)

            col_idx = {col: i + 1 for i, col in enumerate(df.columns)}
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

            if "No" in col_idx:
                for cell in ws[get_column_letter(col_idx["No"])][1:]:
                    cell.alignment = Alignment(horizontal='center')

            for column in ws.columns:
                max_length = max((len(str(cell.value)) for cell in column if cell.value), default=0)
                ws.column_dimensions[column[0].column_letter].width = min(max_length + 2, 55)

    @staticmethod
    def parse_values(val_str):
        v = str(val_str).replace('%', '').replace('Rp', '').strip()
        if ',' in v:
            v = v.replace('.', '').replace(',', '.')
        else:
            v = v.replace('.', '')
        try: return float(v)
        except: return 0.0

    @staticmethod
    def parse_tarif(val_str):
        v = str(val_str).replace('%', '').strip()
        v = v.replace(',', '.')
        try: return float(v)
        except: return 0.0

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

    @staticmethod
    def _extract_rename_bupot_data(text):
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

        name_field, name_label = ExpCore.RENAME_NAME_SOURCES[name_source]
        mode = "Penerapan" if apply_changes else "Pratinjau"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = os.path.join(folder, f"Log_Penamaan_Bupot_{mode}_{timestamp}.csv")
        fields = [
            "status", "folder_sumber", "nama_lama", "nama_baru", "data_tidak_lengkap",
            "NAMA_PENERIMA", "NAMA_PEMOTONG", "NOMOR_BUKTI", "MASA_PAJAK", "SIFAT", "STATUS",
            "sumber_nama",
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

                        row.update({
                            "status": status,
                            "nama_baru": new_name,
                            "data_tidak_lengkap": ", ".join(missing),
                            **data,
                        })
                        self.log(f"{status}: {relative_file} → {new_name}")
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
        header = cls._extract_rename_bupot_data(teks_lengkap)
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
            for index, file_pdf in enumerate(pdf_files):
                self.progress(index, len(pdf_files))
                nama_file = os.path.basename(file_pdf)
                folder_sumber = os.path.relpath(os.path.dirname(file_pdf), folder)
                self.log(f"Membaca {os.path.relpath(file_pdf, folder)}")

                try:
                    with pdfplumber.open(file_pdf) as pdf:
                        teks_lengkap = "\n".join(p.extract_text() or "" for p in pdf.pages)
                    rows = self._extract_bupot_rows(teks_lengkap)
                    if not rows:
                        dilewati += 1
                        self.log(f"DILEWATI: {nama_file} — tidak ada baris BPPU yang dapat dibaca.")
                    for baris in rows:
                        baris["Folder Sumber"] = folder_sumber
                        baris["File Name"] = nama_file
                        semua_baris_data.append(baris)
                except Exception as error:
                    dilewati += 1
                    self.log(f"GAGAL: {nama_file} — {error}")

            if semua_baris_data:
                df = pd.DataFrame(semua_baris_data)
                df.insert(0, 'No', range(1, len(df) + 1))
                output_path = os.path.join(folder, "!Hasil_Rekap_Bupot.xlsx")

                self._write_excel(
                    df, output_path, "Rekap",
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

    @classmethod
    def _extract_bupot2024_rows(cls, teks_lengkap):
        """Ambil baris objek pajak dari teks satu PDF Bukti Potong formulir BPBS.

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

        baris_data = []
        # Tarif BPBS dapat berupa bilangan bulat (2) atau desimal (2.00 / 2,00).
        pola_baris = (
            r"(\d{1,2}-\d{4})\s+(\d{2}-\d{3}-\d{2})\s+([\d.]+,\d{2})\s+"
            r"(?:(X)\s+)?(\d+(?:[.,]\d+)?)\s+([\d.]+,\d{2})"
        )
        for match in re.finditer(pola_baris, teks):
            masa, kode_objek, dpp, tarif_tinggi, tarif, pph = match.groups()
            bulan, tahun = masa.split("-")
            baris_data.append({
                "Nomor Bukti Potong": nomor_bukti or "-",
                "Pembetulan Ke": pembetulan,
                "Status Bukti": status_bukti,
                "Sifat": sifat,
                "NPWP": npwp or "-",
                "NIK": nik or "-",
                "Nama": nama or "-",
                "Masa Pajak": f"{bulan.zfill(2)}-{tahun}",
                "Kode Objek Pajak": kode_objek,
                "Objek Pajak": objek_pajak or "-",
                "DPP (Rp)": cls.parse_values(dpp),
                "Tarif Lebih Tinggi": "Ya" if tarif_tinggi else "Tidak",
                "Tarif (%)": cls.parse_tarif(tarif),
                "Pajak Penghasilan (Rp)": cls.parse_values(pph),
                "Nomor Dokumen Referensi": nomor_dokumen or "-",
                "Nama Dokumen": nama_dokumen or "-",
                "Tanggal Dokumen": tanggal_dokumen or "-",
                "NPWP Pemotong": npwp_pemotong or "-",
                "Nama Pemotong": nama_pemotong or "-",
                "Tanggal Bukti Potong": tanggal_bukti or "-",
                "Nama Penandatangan": penandatangan or "-",
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
            for index, file_pdf in enumerate(pdf_files):
                self.progress(index, len(pdf_files))
                nama_file = os.path.basename(file_pdf)
                folder_sumber = os.path.relpath(os.path.dirname(file_pdf), folder)
                relatif = os.path.relpath(file_pdf, folder)
                self.log(f"Membaca {relatif}")

                try:
                    with pdfplumber.open(file_pdf) as pdf:
                        teks_lengkap = "\n".join(
                            p.extract_text() or "" for p in pdf.pages
                        )

                    baris_pdf = self._extract_bupot2024_rows(teks_lengkap)
                    if not baris_pdf:
                        dilewati += 1
                        self.log(
                            f"DILEWATI: {relatif} — tidak ada baris objek pajak BPBS yang berhasil dibaca."
                        )
                        continue

                    for baris in baris_pdf:
                        baris["Folder Sumber"] = folder_sumber
                        baris["File Name"] = nama_file
                        semua_baris_data.append(baris)
                except Exception as error:
                    dilewati += 1
                    self.log(f"GAGAL: {relatif} — {error}")

            if semua_baris_data:
                df = pd.DataFrame(semua_baris_data)
                df.insert(0, "No", range(1, len(df) + 1))
                output_path = os.path.join(folder, "!Hasil_Rekap_Bupot_2024.xlsx")
                self._write_excel(
                    df, output_path, "Rekap 2024",
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
            for index, file_pdf in enumerate(pdf_files):
                self.progress(index, len(pdf_files))
                nama_file = os.path.basename(file_pdf)
                folder_sumber = os.path.relpath(os.path.dirname(file_pdf), folder)
                self.log(f"Membaca {os.path.relpath(file_pdf, folder)}")

                try:
                    rows_before = len(semua_baris_data)
                    with pdfplumber.open(file_pdf) as pdf:
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

                                            semua_baris_data.append({
                                                "Nama Pembeli": nama_pembeli, "NPWP Pembeli": npwp_pembeli,
                                                "Kode dan Nomor Seri Faktur Pajak": no_seri, "No": no_urut,
                                                "Kode Barang": kode_barang, "Nama Barang": nama_barang,
                                                "Harga": harga, "Qty": qty, "Satuan": satuan, "Potongan Harga": potongan_harga,
                                                "DPP": dpp, "PPN": ppn, "NETTO": netto,
                                                "Folder Sumber": folder_sumber, "Nama File PDF": nama_file
                                            })
                                            no_urut += 1
                    if len(semua_baris_data) == rows_before:
                        dilewati += 1
                        self.log(f"DILEWATI: {nama_file} — tidak ada rincian faktur yang dapat dibaca.")
                except Exception as inner_e:
                    dilewati += 1
                    self.log(f"Gagal: {nama_file} — {str(inner_e)}")

            if semua_baris_data:
                kolom_urutan = ['Nama Pembeli', 'NPWP Pembeli', 'Kode dan Nomor Seri Faktur Pajak', 'No', 'Kode Barang', 'Nama Barang', 'Harga', 'Qty', 'Satuan', 'Potongan Harga', 'DPP', 'PPN', 'NETTO', 'Folder Sumber', 'Nama File PDF']
                df = pd.DataFrame(semua_baris_data, columns=kolom_urutan)
                output_path = os.path.join(folder, "Hasil_Pajak_Masukan.xlsx")

                with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name="Rekap_Faktur")
                    ws = writer.sheets["Rekap_Faktur"]

                    for cell in ws[1]:
                        cell.fill = PatternFill(start_color="D9D9D9", end_color="D9D9D9", fill_type="solid")
                        cell.font = Font(bold=True)

                    for col_letter in ['B', 'C', 'E']:
                        for cell in ws[col_letter]: cell.number_format = '@'

                    col_idx = {col: i+1 for i, col in enumerate(df.columns)}
                    for col_name in ["Harga", "Potongan Harga", "DPP", "PPN", "NETTO"]:
                        if col_name in col_idx:
                            for cell in ws[get_column_letter(col_idx[col_name])][1:]: cell.number_format = '#,##0'

                    for column in ws.columns:
                        max_length = max((len(str(cell.value)) for cell in column if cell.value), default=0)
                        ws.column_dimensions[column[0].column_letter].width = min(max_length + 2, 55)

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
            hari, bulan_baris = (int(part) for part in item["tanggal"].split("/"))
            try:
                # Mutasi bulan sebelumnya (mis. 31/12 pada periode Januari) milik tahun sebelumnya.
                tanggal = datetime(tahun - 1 if bulan_baris > bulan else tahun, bulan_baris, hari)
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
        uang = lambda value: f"{value:,.2f}"
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
            # Saldo berjalan: mendeteksi debit/kredit yang tertukar walau totalnya kebetulan cocok.
            berjalan = awal
            for t in transaksi:
                berjalan += (t["kredit"] or 0) - (t["debit"] or 0)
                if t["saldo"] is not None and t["saldo"] != berjalan:
                    tanggal = t["tanggal"].strftime("%d/%m") if isinstance(t["tanggal"], datetime) else t["tanggal"]
                    catatan.append(f"{tanggal}: saldo PDF {uang(t['saldo'])}, hasil hitung {uang(berjalan)}.")
                    berjalan = t["saldo"]
            if berjalan != akhir:
                catatan.append(f"Saldo hasil hitung {uang(berjalan)} berbeda dari saldo akhir {uang(akhir)}.")
        if halaman and int(halaman.group(1)) != len(pages):
            catatan.append(f"PDF hanya berisi {len(pages)} dari {halaman.group(1)} halaman.")

        return {
            "jenis": judul, "norek": norek.group(1), "nama": nama.group(1).strip() if nama else "",
            "periode": f"{periode.group(1)} {tahun}", "bulan": bulan, "tahun": tahun,
            "mata_uang": mata_uang.group(1) if mata_uang else "",
            "transaksi": transaksi, "ringkasan": nilai_ringkasan, "catatan": catatan,
        }

    @staticmethod
    def _write_rekening_excel(rekening, output_path):
        """Sheet Ringkasan + satu sheet per PDF (tabel mutasi, panel informasi & ringkasan di kanan).

        Ringkasan PDF ditulis di panel terpisah (kolom H–J), bukan di bawah tabel: kolom DEBIT/CREDIT
        tetap berisi transaksi saja sehingga SUM, filter, dan pengurutan tidak ikut menghitung ringkasan.
        """
        header_fill = PatternFill(start_color="D9D9D9", end_color="D9D9D9", fill_type="solid")
        hasil_style = {
            "SESUAI": (PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid"),
                       Font(bold=True, color="006100")),
            "PERLU CEK": (PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid"),
                          Font(bold=True, color="9C0006")),
        }
        uang = "#,##0.00"
        angka = lambda value: float(value) if value is not None else None

        def header(cells):
            for cell in cells:
                cell.fill, cell.font = header_fill, Font(bold=True)

        book = Workbook()
        overview = book.active
        overview.title = "Ringkasan"
        overview.append(["No", "Sheet", "Jenis Rekening", "No. Rekening", "Nama", "Periode", "Mata Uang",
                         "Saldo Awal", "Mutasi CR", "Jumlah CR", "Mutasi DB", "Jumlah DB", "Saldo Akhir",
                         "Transaksi Terbaca", "Hasil Cek", "Catatan", "Folder Sumber", "File Name"])
        used = {"ringkasan"}
        for number, data in enumerate(rekening, 1):
            jenis = re.sub(r"^REKENING\s*", "", data["jenis"]).title() or "Rekening"
            suffix = f" {data['norek']} {data['tahun']}-{data['bulan']:02d}"
            base = re.sub(r"[\[\]:*?/\\]", " ", jenis[:max(0, 31 - len(suffix))] + suffix)[:31].strip()
            name, copy = base, 2
            while name.casefold() in used:
                suffix = f" ({copy})"
                name, copy = base[:31 - len(suffix)].rstrip() + suffix, copy + 1
            used.add(name.casefold())

            ws = book.create_sheet(name)
            ws.append(["TANGGAL", "KETERANGAN", "CBG", "DEBIT", "CREDIT", "SALDO"])
            header(ws[1])
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
            for row_number, values in enumerate(panel, 1):
                if values is None:
                    continue
                cells = [ws.cell(row=row_number, column=column, value=value)
                         for column, value in zip((8, 9, 10), values)]
                if values[0] in ("INFORMASI REKENING", "RINGKASAN PDF", "HASIL CEK"):
                    header(cells)
                elif values[0] == "No. Rekening":
                    cells[1].number_format = "@"
                elif isinstance(values[1], float):
                    cells[1].number_format = uang
                if values[0] == hasil:
                    cells[0].fill, cells[0].font = hasil_style[hasil]

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
            row[1].hyperlink = Hyperlink(ref=row[1].coordinate, location=f"'{name}'!A1")
            row[1].font = Font(color="0563C1", underline="single")
            row[3].number_format = "@"
            for cell in (row[7], row[8], row[10], row[12]):
                cell.number_format = uang
            row[14].fill, row[14].font = hasil_style[hasil]
            row[0].alignment = Alignment(horizontal="center")

        header(overview[1])
        overview.freeze_panes = "A2"
        overview.auto_filter.ref = f"A1:R{overview.max_row}"
        for column in overview.columns:
            max_length = max((len(str(cell.value)) for cell in column if cell.value is not None), default=0)
            overview.column_dimensions[column[0].column_letter].width = min(max_length + 2, 55)
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
            for index, file_pdf in enumerate(pdf_files):
                self.progress(index, len(pdf_files))
                relatif = os.path.relpath(file_pdf, folder)
                self.log(f"Membaca {relatif}")
                try:
                    with pdfplumber.open(file_pdf) as pdf:
                        data = self._extract_rekening_koran(pdf.pages)
                except Exception as error:
                    dilewati += 1
                    self.log(f"GAGAL: {relatif} — {error}")
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
            periode = {}
            for data in rekening:
                key = (data["jenis"], data["norek"], data["tahun"], data["bulan"])
                periode.setdefault(key, []).append(data["file"])
            for (jenis, norek, tahun, bulan), files in periode.items():
                if len(files) > 1:
                    self.log(f"PERINGATAN: {jenis} {norek} periode {bulan:02d}-{tahun} muncul di "
                             f"{len(files)} PDF: {', '.join(files)}")

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

