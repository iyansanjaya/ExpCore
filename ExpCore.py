import os
import sys
import glob
import re
import pdfplumber
import pandas as pd
import customtkinter as ctk
from tkinter import filedialog, messagebox
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from datetime import datetime

# ==========================================
# KONFIGURASI TEMA
# ==========================================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class ExpCore(ctk.CTk):
    """Aplikasi desktop untuk mengekstrak data PDF Coretax ke Excel."""

    # ── Palet Warna ──
    # Terinspirasi oleh estetika Linear / Raycast — minimal, muted, satu aksen.
    C = {
        "bg":            "#0f1117",
        "surface":       "#161820",
        "surface_hover": "#1c1e28",
        "border":        "#242630",
        "border_focus":  "#3b3e50",

        "accent":        "#818cf8",
        "accent_hover":  "#727de6",
        "accent_muted":  "#272a48",

        "teal":          "#5eead4",
        "teal_hover":    "#4cd9c3",
        "teal_muted":    "#1a3a38",

        "green":         "#4ade80",
        "red":           "#f87171",
        "amber":         "#fbbf24",

        "text":          "#e2e4eb",
        "text_sub":      "#9295a5",
        "text_muted":    "#50536a",

        "input_bg":      "#11131a",
        "log_bg":        "#0c0e14",
    }

    def __init__(self):
        super().__init__()

        self.title("ExpCore")
        self.geometry("940x620")
        self.minsize(840, 540)
        self.configure(fg_color=self.C["bg"])

        # ── Icon ──
        # Set AppUserModelID agar Windows menampilkan ikon ExpCore di taskbar,
        # bukan ikon Python/Nuitka default.
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("iyansanjaya.expcore.1.0")
        except Exception:
            pass

        if "__compiled__" in dir():
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))

        # iconbitmap (.ico) — untuk title bar & taskbar
        ico_path = os.path.join(base_dir, "icon.ico")
        if os.path.exists(ico_path):
            self.after(200, lambda: self.iconbitmap(ico_path))

        # iconphoto (.png) — resolusi lebih tinggi untuk alt-tab & taskbar
        png_path = os.path.join(base_dir, "icon.png")
        if os.path.exists(png_path):
            from tkinter import PhotoImage
            self._icon_img = PhotoImage(file=png_path)
            self.iconphoto(True, self._icon_img)

        # ── State ──
        self.folder_path_bupot = ctk.StringVar(value="")
        self.folder_path_pm = ctk.StringVar(value="")
        self._anim_id = None

        self._build()

    # ══════════════════════════════════════════
    #  LAYOUT
    # ══════════════════════════════════════════
    def _build(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_content()
        self._navigate("bupot")

    # ──────────────────────────────────────────
    #  Sidebar
    # ──────────────────────────────────────────
    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(
            self, width=210, corner_radius=0,
            fg_color=self.C["bg"],
            border_width=0,
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_columnconfigure(0, weight=1)
        self.sidebar.grid_rowconfigure(5, weight=1)

        # ── Brand ──
        ctk.CTkLabel(
            self.sidebar, text="ExpCore",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.C["text"],
        ).grid(row=0, column=0, padx=24, pady=(30, 2), sticky="w")

        ctk.CTkLabel(
            self.sidebar, text="by Iyan Sanjaya",
            font=ctk.CTkFont(size=11),
            text_color=self.C["text_muted"],
        ).grid(row=1, column=0, padx=24, pady=(0, 24), sticky="w")

        # ── Navigation ──
        self.nav = {}
        self.nav["bupot"] = self._make_nav(
            self.sidebar, "Bukti Potong", 2,
            lambda: self._navigate("bupot"),
        )
        self.nav["pm"] = self._make_nav(
            self.sidebar, "Pajak Masukan", 3,
            lambda: self._navigate("pm"),
        )

        # ── Divider ──
        ctk.CTkFrame(
            self.sidebar, height=1, fg_color=self.C["border"],
        ).grid(row=4, column=0, padx=20, pady=(20, 0), sticky="ew")

        # ── Version ──
        ctk.CTkLabel(
            self.sidebar, text="v1.1.1",
            font=ctk.CTkFont(size=10),
            text_color=self.C["text_muted"],
        ).grid(row=6, column=0, padx=24, pady=(0, 20), sticky="sw")

    def _make_nav(self, parent, label, row, cmd):
        """Membuat tombol navigasi sidebar — minimalis, tanpa ikon."""
        btn = ctk.CTkButton(
            parent, text=label, anchor="w",
            height=38, corner_radius=8,
            font=ctk.CTkFont(size=13),
            fg_color="transparent",
            text_color=self.C["text_sub"],
            hover_color=self.C["surface_hover"],
            command=cmd,
        )
        btn.grid(row=row, column=0, padx=14, pady=1, sticky="ew")
        return btn

    def _navigate(self, key):
        """Switch halaman & update state sidebar."""
        for name, btn in self.nav.items():
            if name == key:
                btn.configure(
                    fg_color=self.C["accent_muted"],
                    text_color=self.C["accent"],
                    hover_color=self.C["accent_muted"],
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=self.C["text_sub"],
                    hover_color=self.C["surface_hover"],
                )
        for name, page in self.pages.items():
            if name == key:
                page.grid(row=0, column=0, sticky="nsew", padx=(20, 28), pady=28)
            else:
                page.grid_forget()

    # ──────────────────────────────────────────
    #  Content wrapper
    # ──────────────────────────────────────────
    def _build_content(self):
        # Garis vertikal tipis sebagai pembatas sidebar — content
        divider = ctk.CTkFrame(self, width=1, fg_color=self.C["border"], corner_radius=0)
        divider.grid(row=0, column=0, sticky="nse")

        self.content = ctk.CTkFrame(self, fg_color=self.C["bg"], corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

        self.pages = {}
        self._page_bupot()
        self._page_pm()

    # ══════════════════════════════════════════
    #  HALAMAN — BUKTI POTONG
    # ══════════════════════════════════════════
    def _page_bupot(self):
        p = self._page_frame()
        self.pages["bupot"] = p

        # Header
        self._heading(p, "Bukti Potong", "Ekstrak data PDF Bukti Potong Coretax ke Excel.", row=0)

        # Folder picker
        pick = self._picker_frame(p, row=1)
        self.entry_bupot = self._folder_entry(pick, self.folder_path_bupot)
        self._browse_btn(pick, lambda: self.browse_folder(self.folder_path_bupot, self.log_bupot))

        # Log
        log_wrap = self._log_frame(p, row=2)
        self.log_bupot_box = self._log_box(log_wrap)

        # Action
        self.btn_process_bupot = ctk.CTkButton(
            p, text="Mulai Ekstrak", height=44, corner_radius=8,
            fg_color=self.C["accent"], hover_color=self.C["accent_hover"],
            text_color="#ffffff",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.process_bupot,
        )
        self.btn_process_bupot.grid(row=3, column=0, sticky="ew", pady=(12, 0))

    # ══════════════════════════════════════════
    #  HALAMAN — PAJAK MASUKAN
    # ══════════════════════════════════════════
    def _page_pm(self):
        p = self._page_frame()
        self.pages["pm"] = p

        self._heading(p, "Pajak Masukan", "Ekstrak data PDF Faktur Pajak Masukan Coretax ke Excel.", row=0)

        pick = self._picker_frame(p, row=1)
        self.entry_pm = self._folder_entry(pick, self.folder_path_pm)
        self._browse_btn(pick, lambda: self.browse_folder(self.folder_path_pm, self.log_pm))

        log_wrap = self._log_frame(p, row=2)
        self.log_pm_box = self._log_box(log_wrap)

        self.btn_process_pm = ctk.CTkButton(
            p, text="Mulai Ekstrak", height=44, corner_radius=8,
            fg_color=self.C["teal"], hover_color=self.C["teal_hover"],
            text_color="#0f1117",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.process_pm,
        )
        self.btn_process_pm.grid(row=3, column=0, sticky="ew", pady=(12, 0))

    # ══════════════════════════════════════════
    #  KOMPONEN UI (reusable, bersih)
    # ══════════════════════════════════════════
    def _page_frame(self):
        f = ctk.CTkFrame(self.content, fg_color="transparent")
        f.grid_columnconfigure(0, weight=1)
        f.grid_rowconfigure(2, weight=1)
        return f

    def _heading(self, parent, title, subtitle, row):
        wrap = ctk.CTkFrame(parent, fg_color="transparent")
        wrap.grid(row=row, column=0, sticky="ew", pady=(0, 20))
        ctk.CTkLabel(
            wrap, text=title,
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.C["text"],
        ).pack(anchor="w")
        ctk.CTkLabel(
            wrap, text=subtitle,
            font=ctk.CTkFont(size=13),
            text_color=self.C["text_sub"],
        ).pack(anchor="w", pady=(4, 0))

    def _picker_frame(self, parent, row):
        f = ctk.CTkFrame(
            parent, fg_color=self.C["surface"],
            corner_radius=10, border_width=1,
            border_color=self.C["border"],
        )
        f.grid(row=row, column=0, sticky="ew", pady=(0, 10))
        f.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            f, text="Folder Induk",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.C["text_sub"],
        ).grid(row=0, column=0, columnspan=2, padx=16, pady=(14, 6), sticky="w")

        return f

    def _folder_entry(self, parent, var):
        e = ctk.CTkEntry(
            parent, textvariable=var, state="readonly",
            placeholder_text="Belum ada folder induk dipilih",
            height=40, corner_radius=8,
            fg_color=self.C["input_bg"],
            border_color=self.C["border"],
            border_width=1,
            text_color=self.C["text"],
            placeholder_text_color=self.C["text_muted"],
            font=ctk.CTkFont(size=13),
        )
        e.grid(row=1, column=0, padx=(16, 8), pady=(0, 14), sticky="ew")
        return e

    def _browse_btn(self, parent, cmd):
        ctk.CTkButton(
            parent, text="Pilih", width=80, height=40,
            corner_radius=8,
            fg_color=self.C["surface_hover"],
            hover_color=self.C["border_focus"],
            border_width=1, border_color=self.C["border"],
            text_color=self.C["text_sub"],
            font=ctk.CTkFont(size=13),
            command=cmd,
        ).grid(row=1, column=1, padx=(0, 16), pady=(0, 14))

    def _log_frame(self, parent, row):
        f = ctk.CTkFrame(
            parent, fg_color=self.C["surface"],
            corner_radius=10, border_width=1,
            border_color=self.C["border"],
        )
        f.grid(row=row, column=0, sticky="nsew")
        f.grid_columnconfigure(0, weight=1)
        f.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            f, text="Log",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.C["text_sub"],
        ).grid(row=0, column=0, padx=16, pady=(14, 6), sticky="w")

        return f

    def _log_box(self, parent):
        tb = ctk.CTkTextbox(
            parent, corner_radius=6,
            fg_color=self.C["log_bg"],
            text_color=self.C["text_muted"],
            border_width=1, border_color=self.C["border"],
            font=ctk.CTkFont(family="Consolas", size=12),
            scrollbar_button_color=self.C["border"],
            scrollbar_button_hover_color=self.C["border_focus"],
        )
        tb.grid(row=1, column=0, padx=12, pady=(0, 12), sticky="nsew")
        tb.insert("0.0", f"{self._ts()}  Siap.\n")
        tb.configure(state="disabled")
        return tb

    # ══════════════════════════════════════════
    #  UTILITAS
    # ══════════════════════════════════════════
    def _ts(self):
        return datetime.now().strftime("%H:%M:%S")

    def browse_folder(self, var, log_fn):
        path = filedialog.askdirectory()
        if path:
            var.set(path)
            log_fn(f"Folder: {path}")

    def log_bupot(self, msg):
        self._log(self.log_bupot_box, msg)

    def log_pm(self, msg):
        self._log(self.log_pm_box, msg)

    def _log(self, tb, msg):
        tb.configure(state="normal")
        tb.insert("end", f"{self._ts()}  {msg}\n")
        tb.see("end")
        tb.configure(state="disabled")
        self.update_idletasks()

    def _pulse_start(self, btn):
        """Animasi loading minimalis pada tombol."""
        self._anim_dots = 0

        def tick():
            self._anim_dots = (self._anim_dots % 3) + 1
            btn.configure(text="Memproses" + " ." * self._anim_dots)
            self._anim_id = self.after(420, tick)
        tick()

    def _pulse_stop(self, btn, label, color):
        if self._anim_id:
            self.after_cancel(self._anim_id)
            self._anim_id = None
        btn.configure(text=label, state="normal", fg_color=color)

    def parse_values(self, val_str):
        v = str(val_str).replace('%', '').replace('Rp', '').strip()
        if ',' in v:
            v = v.replace('.', '').replace(',', '.')
        else:
            v = v.replace('.', '')
        try: return float(v)
        except: return 0.0

    def parse_tarif(self, val_str):
        v = str(val_str).replace('%', '').strip()
        v = v.replace(',', '.')
        try: return float(v)
        except: return 0.0

    # ══════════════════════════════════════════
    #  EKSTRAKSI — BUKTI POTONG
    # ══════════════════════════════════════════
    def process_bupot(self):
        folder = self.folder_path_bupot.get()
        if not os.path.exists(folder) or not folder:
            messagebox.showwarning("Peringatan", "Silakan pilih folder terlebih dahulu!")
            return

        pdf_files = sorted(glob.glob(os.path.join(folder, "**", "*.pdf"), recursive=True))
        if not pdf_files:
            messagebox.showerror("Error", "Tidak ada file PDF di folder atau subfolder tersebut!")
            return

        self.btn_process_bupot.configure(state="disabled")
        self._pulse_start(self.btn_process_bupot)
        self.log_bupot(f"Memproses {len(pdf_files)} file …")

        semua_baris_data = []
        try:
            for file_pdf in pdf_files:
                nama_file = os.path.basename(file_pdf)
                folder_sumber = os.path.relpath(os.path.dirname(file_pdf), folder)
                self.log_bupot(f"Membaca {os.path.relpath(file_pdf, folder)}")

                with pdfplumber.open(file_pdf) as pdf:
                    teks_lengkap = "\n".join([p.extract_text() for p in pdf.pages if p.extract_text()])
                    teks_rata = teks_lengkap.replace('\n', ' ')

                    match_nama = re.search(r'A\.2\s*NAMA\s*:\s*(.*?)\s*A\.3', teks_rata)
                    nama_penerima = match_nama.group(1).strip() if match_nama else "-"
                    match_status = re.search(r'(NORMAL|PEMBETULAN)', teks_rata)
                    status_bukti = match_status.group(1).strip() if match_status else "NORMAL"
                    match_fasilitas = re.search(r'B\.1\s*Jenis Fasilitas\s*:\s*(.*?)\s*B\.2', teks_rata, re.IGNORECASE)
                    jenis_fasilitas = match_fasilitas.group(1).strip() if match_fasilitas else "-"
                    match_jpph = re.search(r'B\.2\s*Jenis PPh\s*:\s*(.*?)\s*(?:KODE OBJEK PAJAK|B\.3)', teks_rata, re.IGNORECASE)
                    jenis_pph = match_jpph.group(1).strip() if match_jpph else "-"
                    match_jenis_dok = re.search(r'Jenis Dokumen\s*:\s*(.*?)\s*Tanggal\s*:', teks_rata, re.IGNORECASE)
                    jenis_dokumen = match_jenis_dok.group(1).strip() if match_jenis_dok else "-"
                    match_nodok = re.search(r'B\.9\s*Nomor Dokumen\s*:\s*(.*?)\s*B\.10', teks_rata, re.IGNORECASE)
                    nomor_dokumen = match_nodok.group(1).strip() if match_nodok else "-"
                    match_npwp_pemotong = re.search(r'C\.1\s*NPWP\s*/\s*NIK\s*:\s*([\d]+)', teks_rata)
                    npwp_pemotong = match_npwp_pemotong.group(1) if match_npwp_pemotong else "-"
                    match_nama_pemotong = re.search(r'C\.3.*?NAMA PEMOTONG.*?\:\s*([A-Za-z0-9\s\.\,\&]+?)\s*C\.4', teks_rata, re.IGNORECASE)
                    nama_pemotong = match_nama_pemotong.group(1).strip() if match_nama_pemotong else "-"
                    match_tanggal = re.search(r'C\.4\s*TANGGAL\s*:\s*([A-Za-z0-9\s]+?)\s*C\.5', teks_rata)
                    tanggal_bupot = match_tanggal.group(1).strip() if match_tanggal else "-"

                    match_blok = re.search(r'B\.7\s*(.*?)\s*B\.8\s*Dokumen', teks_rata, re.IGNORECASE)
                    if match_blok:
                        blok_tabel = match_blok.group(1).strip()
                        matches_baris = re.finditer(r'(\d{2}-\d{3}-\d{2})\s+(.*?)(?=(?:\d{2}-\d{3}-\d{2})|$)', blok_tabel)

                        for m in matches_baris:
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

                            semua_baris_data.append({
                                "Nama": nama_penerima, "Status Bukti": status_bukti, "Jenis Fasilitas": jenis_fasilitas,
                                "Jenis PPh": jenis_pph, "Kode Objek Pajak": kode_objek, "Objek Pajak": objek_pajak_desc,
                                "DPP (Rp)": self.parse_values(dpp_str), "Tarif (%)": self.parse_tarif(tarif_str),
                                "Pajak Penghasilan (Rp)": self.parse_values(pph_str), "Jenis Dokumen": jenis_dokumen,
                                "Nomor Dokumen Dasar": nomor_dokumen, "NPWP/NIK Pemotong": npwp_pemotong,
                                "Nama Pemotong": nama_pemotong, "Tanggal": tanggal_bupot,
                                "Folder Sumber": folder_sumber, "File Name": nama_file
                            })

            if semua_baris_data:
                df = pd.DataFrame(semua_baris_data)
                df.insert(0, 'No', range(1, len(df) + 1))
                output_path = os.path.join(folder, "!Hasil_Rekap_Bupot.xlsx")

                with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name="Rekap")
                    ws = writer.sheets["Rekap"]

                    for cell in ws[1]:
                        cell.fill = PatternFill(start_color="D9D9D9", end_color="D9D9D9", fill_type="solid")
                        cell.font = Font(bold=True)

                    col_idx = {col: i+1 for i, col in enumerate(df.columns)}
                    for col_name in ["Kode Objek Pajak", "Nomor Dokumen Dasar", "NPWP/NIK Pemotong"]:
                        if col_name in col_idx:
                            for cell in ws[get_column_letter(col_idx[col_name])]: cell.number_format = '@'

                    for col_name in ["DPP (Rp)", "Pajak Penghasilan (Rp)"]:
                        if col_name in col_idx:
                            for cell in ws[get_column_letter(col_idx[col_name])][1:]: cell.number_format = '#,##0'

                    if "Tarif (%)" in col_idx:
                        for cell in ws[get_column_letter(col_idx["Tarif (%)"])][1:]: cell.number_format = '0.00'

                    if "No" in col_idx:
                        for cell in ws[get_column_letter(col_idx["No"])][1:]: cell.alignment = Alignment(horizontal='center')

                    for column in ws.columns:
                        max_length = max((len(str(cell.value)) for cell in column if cell.value), default=0)
                        ws.column_dimensions[column[0].column_letter].width = min(max_length + 2, 55)

                self.log_bupot(f"Selesai — {output_path}")
                messagebox.showinfo("Selesai", f"Data Bupot berhasil disimpan di:\n{output_path}")
            else:
                self.log_bupot("Tidak ada data yang ditemukan.")

        except Exception as e:
            self.log_bupot(f"Error: {str(e)}")
            messagebox.showerror("Error", str(e))
        finally:
            self._pulse_stop(self.btn_process_bupot, "Mulai Ekstrak", self.C["accent"])

    # ══════════════════════════════════════════
    #  EKSTRAKSI — PAJAK MASUKAN
    # ══════════════════════════════════════════
    def process_pm(self):
        folder = self.folder_path_pm.get()
        if not os.path.exists(folder) or not folder:
            messagebox.showwarning("Peringatan", "Silakan pilih folder terlebih dahulu!")
            return

        pdf_files = sorted(glob.glob(os.path.join(folder, "**", "*.pdf"), recursive=True))
        if not pdf_files:
            messagebox.showerror("Error", "Tidak ada file PDF di folder atau subfolder tersebut!")
            return

        self.btn_process_pm.configure(state="disabled")
        self._pulse_start(self.btn_process_pm)
        self.log_pm(f"Memproses {len(pdf_files)} file …")

        semua_baris_data = []
        try:
            for file_pdf in pdf_files:
                nama_file = os.path.basename(file_pdf)
                folder_sumber = os.path.relpath(os.path.dirname(file_pdf), folder)
                self.log_pm(f"Membaca {os.path.relpath(file_pdf, folder)}")

                try:
                    with pdfplumber.open(file_pdf) as pdf:
                        teks_lengkap = "".join([page.extract_text() + "\n" for page in pdf.pages if page.extract_text()])

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
                except Exception as inner_e:
                    self.log_pm(f"Gagal: {nama_file} — {str(inner_e)}")

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

                self.log_pm(f"Selesai — {output_path}")
                messagebox.showinfo("Selesai", f"Data Pajak Masukan berhasil disimpan di:\n{output_path}")
            else:
                self.log_pm("Tidak ada data yang ditemukan.")

        except Exception as e:
            self.log_pm(f"Error: {str(e)}")
            messagebox.showerror("Error", str(e))
        finally:
            self._pulse_stop(self.btn_process_pm, "Mulai Ekstrak", self.C["teal"])


if __name__ == "__main__":
    app = ExpCore()
    app.mainloop()
