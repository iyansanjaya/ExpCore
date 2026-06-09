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

# ==========================================
# KONFIGURASI TEMA UI
# ==========================================
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class ExpCore(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Pengaturan Jendela Utama
        self.title("ExpCore by Iyan Sanjaya")
        self.geometry("700x550")
        self.minsize(600, 500)

        # Set Icon (delayed agar tidak ditimpa oleh default icon CustomTkinter)
        # Deteksi apakah dijalankan sebagai Nuitka compiled atau script biasa
        if "__compiled__" in dir():
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(base_dir, "icon.ico")
        if os.path.exists(icon_path):
            self.after(200, lambda: self.iconbitmap(icon_path))

        # Variabel Path
        self.folder_path_bupot = ctk.StringVar(value="Belum pilih folder...")
        self.folder_path_pm = ctk.StringVar(value="Belum pilih folder...")

        self.create_widgets()

    def create_widgets(self):
        # --- HEADER ---
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=20, pady=(20, 10))

        self.label_title = ctk.CTkLabel(self.header_frame, text="PDF to Excel Extractor", font=ctk.CTkFont(size=28, weight="bold"))
        self.label_title.pack()

        self.label_subtitle = ctk.CTkLabel(self.header_frame, text="Ekstrak data PDF Bukti Potong & Pajak Masukan ke Excel dari Coretax", font=ctk.CTkFont(size=14), text_color="gray")
        self.label_subtitle.pack()

        # --- TABVIEW (Untuk memilih fitur) ---
        self.tabview = ctk.CTkTabview(self, width=650)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=10)

        self.tab_bupot = self.tabview.add("Bukti Potong (Bupot)")
        self.tab_pm = self.tabview.add("Pajak Masukan (PM)")

        # Mengatur Grid pada masing-masing Tab
        self.tab_bupot.grid_columnconfigure(0, weight=1)
        self.tab_pm.grid_columnconfigure(0, weight=1)

        self.setup_bupot_tab()
        self.setup_pm_tab()

    # ==========================================
    # TAB 1: BUKTI POTONG
    # ==========================================
    def setup_bupot_tab(self):
        # Frame Input Folder
        frame_input = ctk.CTkFrame(self.tab_bupot)
        frame_input.pack(fill="x", padx=10, pady=(10, 5))
        frame_input.grid_columnconfigure(0, weight=1)

        entry_path = ctk.CTkEntry(frame_input, textvariable=self.folder_path_bupot, state="readonly", height=35)
        entry_path.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="ew")

        btn_browse = ctk.CTkButton(frame_input, text="Pilih Folder", width=120, height=35, command=lambda: self.browse_folder(self.folder_path_bupot, self.log_bupot))
        btn_browse.grid(row=0, column=1, padx=(5, 10), pady=10)

        # Log Textbox
        self.log_bupot_box = ctk.CTkTextbox(self.tab_bupot, height=180)
        self.log_bupot_box.pack(fill="both", expand=True, padx=10, pady=10)
        self.log_bupot_box.insert("0.0", "Status: Siap.\nSilakan pilih folder PDF Bukti Potong lalu klik Ekstrak.\n")
        self.log_bupot_box.configure(state="disabled")

        # Tombol Proses
        self.btn_process_bupot = ctk.CTkButton(self.tab_bupot, text="MULAI EKSTRAK BUPOT", height=45, font=ctk.CTkFont(weight="bold", size=14), command=self.process_bupot)
        self.btn_process_bupot.pack(fill="x", padx=10, pady=(5, 15))

    # ==========================================
    # TAB 2: PAJAK MASUKAN
    # ==========================================
    def setup_pm_tab(self):
        # Frame Input Folder
        frame_input = ctk.CTkFrame(self.tab_pm)
        frame_input.pack(fill="x", padx=10, pady=(10, 5))
        frame_input.grid_columnconfigure(0, weight=1)

        entry_path = ctk.CTkEntry(frame_input, textvariable=self.folder_path_pm, state="readonly", height=35)
        entry_path.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="ew")

        btn_browse = ctk.CTkButton(frame_input, text="Pilih Folder", width=120, height=35, command=lambda: self.browse_folder(self.folder_path_pm, self.log_pm))
        btn_browse.grid(row=0, column=1, padx=(5, 10), pady=10)

        # Log Textbox
        self.log_pm_box = ctk.CTkTextbox(self.tab_pm, height=180)
        self.log_pm_box.pack(fill="both", expand=True, padx=10, pady=10)
        self.log_pm_box.insert("0.0", "Status: Siap.\nSilakan pilih folder PDF Faktur Pajak Masukan lalu klik Ekstrak.\n")
        self.log_pm_box.configure(state="disabled")

        # Tombol Proses
        self.btn_process_pm = ctk.CTkButton(self.tab_pm, text="MULAI EKSTRAK PAJAK MASUKAN", height=45, font=ctk.CTkFont(weight="bold", size=14), command=self.process_pm, fg_color="#2E8B57", hover_color="#236B43")
        self.btn_process_pm.pack(fill="x", padx=10, pady=(5, 15))

    # ==========================================
    # FUNGSI UTILITAS UMUM
    # ==========================================
    def browse_folder(self, string_var, log_func):
        path = filedialog.askdirectory()
        if path:
            string_var.set(path)
            log_func(f"Folder terpilih: {path}")

    def log_bupot(self, message):
        self._write_log(self.log_bupot_box, message)

    def log_pm(self, message):
        self._write_log(self.log_pm_box, message)

    def _write_log(self, textbox, message):
        textbox.configure(state="normal")
        textbox.insert("end", f"> {message}\n")
        textbox.see("end")
        textbox.configure(state="disabled")
        self.update_idletasks()

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

    # ==========================================
    # LOGIKA EKSTRAKSI: BUKTI POTONG
    # ==========================================
    def process_bupot(self):
        folder = self.folder_path_bupot.get()
        if not os.path.exists(folder) or folder == "Belum pilih folder...":
            messagebox.showwarning("Peringatan", "Silakan pilih folder terlebih dahulu!")
            return

        pdf_files = glob.glob(os.path.join(folder, "*.pdf"))
        if not pdf_files:
            messagebox.showerror("Error", "Tidak ada file PDF di folder tersebut!")
            return

        self.btn_process_bupot.configure(state="disabled", text="Memproses...")
        self.log_bupot(f"Memulai pemrosesan {len(pdf_files)} file Bupot...")
        
        semua_baris_data = []
        try:
            for file_pdf in pdf_files:
                nama_file = os.path.basename(file_pdf)
                self.log_bupot(f"Membaca: {nama_file}")
                
                with pdfplumber.open(file_pdf) as pdf:
                    teks_lengkap = "\n".join([p.extract_text() for p in pdf.pages if p.extract_text()])
                    teks_rata = teks_lengkap.replace('\n', ' ')

                    # --- Ekstraksi Pola Regex Bupot ---
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
                                "Nama Pemotong": nama_pemotong, "Tanggal": tanggal_bupot, "File Name": nama_file
                            })

            if semua_baris_data:
                df = pd.DataFrame(semua_baris_data)
                df.insert(0, 'No', range(1, len(df) + 1))
                output_path = os.path.join(folder, "Hasil_Rekap_Bupot.xlsx")
                
                with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name="Rekap")
                    ws = writer.sheets["Rekap"]
                    
                    # Styling
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
                
                self.log_bupot(f"SUKSES! Data diekstrak ke {output_path}")
                messagebox.showinfo("Selesai", f"Data Bupot berhasil disimpan di:\n{output_path}")
            else:
                self.log_bupot("Gagal: Tidak ada data rincian objek pajak ditemukan.")
        
        except Exception as e:
            self.log_bupot(f"Error: {str(e)}")
            messagebox.showerror("Error Bupot", str(e))
        finally:
            self.btn_process_bupot.configure(state="normal", text="MULAI EKSTRAK BUPOT")

    # ==========================================
    # LOGIKA EKSTRAKSI: PAJAK MASUKAN
    # ==========================================
    def process_pm(self):
        folder = self.folder_path_pm.get()
        if not os.path.exists(folder) or folder == "Belum pilih folder...":
            messagebox.showwarning("Peringatan", "Silakan pilih folder terlebih dahulu!")
            return

        pdf_files = glob.glob(os.path.join(folder, "*.pdf"))
        if not pdf_files:
            messagebox.showerror("Error", "Tidak ada file PDF di folder tersebut!")
            return

        self.btn_process_pm.configure(state="disabled", text="Memproses...")
        self.log_pm(f"Memulai pemrosesan {len(pdf_files)} file Faktur Pajak Masukan...")
        
        semua_baris_data = []
        try:
            for file_pdf in pdf_files:
                nama_file = os.path.basename(file_pdf)
                self.log_pm(f"Membaca: {nama_file}")
                
                try:
                    with pdfplumber.open(file_pdf) as pdf:
                        teks_lengkap = "".join([page.extract_text() + "\n" for page in pdf.pages if page.extract_text()])
                        
                        # Pola Data PM
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
                                            ppn = dpp * 0.12 # Asumsi PPN 12%
                                            netto = dpp + ppn
                                            
                                            semua_baris_data.append({
                                                "Nama Pembeli": nama_pembeli, "NPWP Pembeli": npwp_pembeli, 
                                                "Kode dan Nomor Seri Faktur Pajak": no_seri, "No": no_urut,
                                                "Kode Barang": kode_barang, "Nama Barang": nama_barang, 
                                                "Harga": harga, "Qty": qty, "Satuan": satuan, "Potongan Harga": potongan_harga,
                                                "DPP": dpp, "PPN": ppn, "NETTO": netto, "Nama File PDF": nama_file
                                            })
                                            no_urut += 1
                except Exception as inner_e:
                    self.log_pm(f"Gagal ekstrak rincian {nama_file}: {str(inner_e)}")

            if semua_baris_data:
                kolom_urutan = ['Nama Pembeli', 'NPWP Pembeli', 'Kode dan Nomor Seri Faktur Pajak', 'No', 'Kode Barang', 'Nama Barang', 'Harga', 'Qty', 'Satuan', 'Potongan Harga', 'DPP', 'PPN', 'NETTO', 'Nama File PDF']
                df = pd.DataFrame(semua_baris_data, columns=kolom_urutan)
                output_path = os.path.join(folder, "Hasil_Pajak_Masukan.xlsx")
                
                with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name="Rekap_Faktur")
                    ws = writer.sheets["Rekap_Faktur"]
                    
                    # Styling Header
                    for cell in ws[1]:
                        cell.fill = PatternFill(start_color="D9D9D9", end_color="D9D9D9", fill_type="solid")
                        cell.font = Font(bold=True)

                    for col_letter in ['B', 'C', 'E']:
                        for cell in ws[col_letter]: cell.number_format = '@'

                    # Formatting Currency
                    col_idx = {col: i+1 for i, col in enumerate(df.columns)}
                    for col_name in ["Harga", "Potongan Harga", "DPP", "PPN", "NETTO"]:
                        if col_name in col_idx:
                            for cell in ws[get_column_letter(col_idx[col_name])][1:]: cell.number_format = '#,##0'
                    
                    for column in ws.columns:
                        max_length = max((len(str(cell.value)) for cell in column if cell.value), default=0)
                        ws.column_dimensions[column[0].column_letter].width = min(max_length + 2, 55)

                self.log_pm(f"SUKSES! Data diekstrak ke {output_path}")
                messagebox.showinfo("Selesai", f"Data Pajak Masukan berhasil disimpan di:\n{output_path}")
            else:
                self.log_pm("Gagal: Tidak ada data rincian barang yang berhasil diekstrak.")

        except Exception as e:
            self.log_pm(f"Error: {str(e)}")
            messagebox.showerror("Error PM", str(e))
        finally:
            self.btn_process_pm.configure(state="normal", text="MULAI EKSTRAK PAJAK MASUKAN")


if __name__ == "__main__":
    app = ExpCore()
    app.mainloop()