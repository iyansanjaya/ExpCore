<p align="center">
  <img src="icon.ico" alt="ExpCore Logo" width="80" />
</p>

<h1 align="center">ExpCore</h1>

<p align="center">
  <strong>PDF Data Extractor untuk Coretax</strong><br/>
  Ekstrak data Bukti Potong &amp; Pajak Masukan dari file PDF Coretax ke format Excel secara otomatis.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/platform-Windows-0078D6?style=flat-square&logo=windows&logoColor=white" alt="Platform" />
  <img src="https://img.shields.io/badge/version-1.0-7c3aed?style=flat-square" alt="Version" />
  <img src="https://img.shields.io/badge/license-Apache%202.0-blue?style=flat-square" alt="License" />
</p>

---

## ✨ Fitur Utama

| Fitur                         | Deskripsi                                                                                      |
| ----------------------------- | ---------------------------------------------------------------------------------------------- |
| 📄 **Ekstrak Bukti Potong**   | Parsing otomatis data Bupot (nama, NPWP, kode objek pajak, DPP, tarif, PPh, dll.)              |
| 📋 **Ekstrak Pajak Masukan**  | Parsing otomatis data Faktur PM (pembeli, nomor seri, rincian barang, DPP, PPN, dll.)          |
| 📊 **Output Excel Terformat** | Hasil ekspor langsung ke `.xlsx` dengan header styling, format angka, dan lebar kolom otomatis |
| 📁 **Batch Processing**       | Proses seluruh folder berisi file PDF sekaligus dalam satu klik                                |
| 🎨 **UI Modern**              | Tampilan dark theme premium dengan sidebar navigation dan animasi interaktif                   |

---

## 🛠️ Tech Stack

- **Bahasa:** Python 3.10+
- **GUI Framework:** [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
- **PDF Parser:** [pdfplumber](https://github.com/jsvine/pdfplumber)
- **Excel Writer:** [openpyxl](https://openpyxl.readthedocs.io/) + [pandas](https://pandas.pydata.org/)
- **Compiler:** [Nuitka](https://nuitka.net/) (standalone `.exe`)
- **Installer:** [Inno Setup](https://jrsoftware.org/isinfo.php)

---

## 📦 Instalasi (Development)

### 1. Clone Repository

```bash
git clone https://github.com/iyansanjaya/ExpCore.git
cd ExpCore
```

### 2. Buat Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install customtkinter pdfplumber pandas openpyxl
```

### 4. Jalankan Aplikasi

```bash
python ExpCore.py
```

---

## 🏗️ Build & Distribusi

### Compile ke Standalone `.exe` (Nuitka)

```bash
& "$env:LOCALAPPDATA\Python\pythoncore-3.14-64\python.exe" -m nuitka --standalone --disable-console --enable-plugin=tk-inter --include-data-files=icon.ico=icon.ico --include-data-files=icon.png=icon.png --windows-icon-from-ico=icon.ico ExpCore.py
```

> Perintah di atas akan menghasilkan folder `ExpCore.dist/` berisi executable beserta seluruh dependensi.

### Buat Installer (Inno Setup)

1. Buka file `ExpCore.iss` di [Inno Setup Compiler](https://jrsoftware.org/isinfo.php).
2. Sesuaikan path pada bagian `[Files]` jika diperlukan.
3. Klik **Build → Compile** untuk menghasilkan file installer `.exe`.

---

## 📂 Struktur Project

```
ExpCore/
├── ExpCore.py        # Kode utama aplikasi (UI + logika ekstraksi)
├── ExpCore.iss       # Script Inno Setup untuk membuat installer
├── icon.ico          # Ikon aplikasi (multi-resolusi, untuk Windows)
├── icon.png          # Ikon aplikasi HD (1024x1024, untuk taskbar & alt-tab)
├── LICENSE.txt       # Apache License 2.0
└── README.md         # Dokumentasi project
```

---

## 📖 Cara Penggunaan

1. **Buka aplikasi** — jalankan `ExpCore.exe` atau `python ExpCore.py`.
2. **Pilih fitur** — klik menu **Bukti Potong** atau **Pajak Masukan** di sidebar.
3. **Pilih folder** — klik tombol **Telusuri…** lalu pilih folder berisi file PDF dari Coretax.
4. **Klik Ekstrak** — tekan tombol **MULAI EKSTRAK** dan tunggu proses selesai.
5. **Cek hasil** — file Excel (`Hasil_Rekap_Bupot.xlsx` atau `Hasil_Pajak_Masukan.xlsx`) akan tersimpan di folder yang sama.

---

## ⚠️ Catatan Penting

- Aplikasi ini dirancang khusus untuk format PDF yang dihasilkan oleh **Coretax DJP**.
- Pastikan file PDF tidak terproteksi password dan tidak corrupt.
- Tarif PPN pada modul Pajak Masukan menggunakan asumsi **12%** — sesuaikan jika ada perubahan regulasi.

---

## 📄 Lisensi

Dilisensikan di bawah **Apache License 2.0** — lihat [LICENSE.txt](LICENSE.txt) untuk detail lengkap.

Copyright © 2026 Iyan Sanjaya.
