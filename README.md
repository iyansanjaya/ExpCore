<p align="center">
  <img src="icon.ico" alt="ExpCore Logo" width="80" />
</p>

<h1 align="center">ExpCore</h1>

<p align="center">
  <strong>Toolkit PDF Coretax</strong><br/>
  Ekstrak data Bukti Potong dan Pajak Masukan ke Excel, serta beri nama PDF Bupot secara otomatis.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/platform-Windows-0078D6?style=flat-square&logo=windows&logoColor=white" alt="Platform" />
  <img src="https://img.shields.io/badge/version-1.2-7c3aed?style=flat-square" alt="Version" />
  <img src="https://img.shields.io/badge/license-Apache%202.0-blue?style=flat-square" alt="License" />
</p>

---

## Fitur

| Fitur                       | Deskripsi                                                                                                               |
| --------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| **Bukti Potong**            | Mengekstrak nama, status bukti, jenis PPh, objek pajak, DPP, tarif, PPh, dokumen dasar, dan data pemotong.              |
| **Pajak Masukan**           | Mengekstrak pembeli, nomor faktur, rincian barang, harga, kuantitas, DPP, PPN, dan nilai netto.                         |
| **Penamaan Otomatis Bupot** | Mempratinjau dan mengganti nama PDF menjadi <code>Nama Pemotong - Nomor Bukti - Masa Pajak - Sifat - Status.pdf</code>. |
| **Pemindaian Subfolder**    | Memproses seluruh PDF dalam folder induk dan semua subfolder menjadi satu hasil.                                        |
| **Output Terformat**        | Menghasilkan Excel dengan format angka, header, lebar kolom otomatis, dan informasi folder sumber.                      |

Semua proses berjalan secara lokal. ExpCore TIDAK mengirim PDF atau hasil ekstraksi ke internet.

---

## Teknologi

- **GUI:** [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
- **PDF:** [pdfplumber](https://github.com/jsvine/pdfplumber)
- **Excel:** [pandas](https://pandas.pydata.org/) dan [openpyxl](https://openpyxl.readthedocs.io/)
- **Executable:** [Nuitka](https://nuitka.net/)
- **Installer:** [Inno Setup](https://jrsoftware.org/isinfo.php)

---

## Menjalankan dari Source

```powershell
git clone https://github.com/iyansanjaya/ExpCore.git
cd ExpCore

python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install customtkinter pdfplumber pandas openpyxl
python ExpCore.py
```

Pastikan perintah <code>python</code> berasal dari virtual environment tersebut:

```powershell
python -c "import sys; print(sys.executable)"
```

---

## Cara Penggunaan

### Ekstraksi Bukti Potong atau Pajak Masukan

1. Pilih menu **Bukti Potong** atau **Pajak Masukan**.
2. Pilih folder biasa atau folder induk.
3. Klik **Mulai Ekstrak**.
4. Aplikasi memproses seluruh PDF di folder tersebut dan semua subfolder.
5. Satu file Excel disimpan di folder yang dipilih:
   - Bukti Potong: <code>!Hasil_Rekap_Bupot.xlsx</code>
   - Pajak Masukan: <code>Hasil_Pajak_Masukan.xlsx</code>

Kolom **Folder Sumber** menunjukkan lokasi asal PDF ketika beberapa subfolder digabungkan.

### Penamaan Otomatis Bupot

1. Pilih menu **Penamaan Bupot**.
2. Pilih folder yang berisi PDF Bupot, termasuk jika PDF berada dalam subfolder.
3. Klik **Pratinjau Nama** dan periksa log CSV.
4. Klik **Terapkan Nama** setelah hasil pratinjau sesuai.

PDF dengan data wajib yang tidak lengkap akan dilewati. Nama yang sudah digunakan tidak ditimpa; aplikasi menambahkan nomor seperti <code>(2)</code>. Setiap proses menghasilkan log audit:

```text
Log_Penamaan_Bupot_Pratinjau_YYYYMMDD_HHMMSS.csv
Log_Penamaan_Bupot_Penerapan_YYYYMMDD_HHMMSS.csv
```

---

## Pengujian

Pemeriksaan parser dan keamanan nama file:

```powershell
python test_expcore.py
```

---

## Build dan Distribusi

### Compile dengan Nuitka

Install dan verifikasi Nuitka pada interpreter yang sama dengan dependency aplikasi:

```powershell
python -m pip install Nuitka
python -m nuitka --version
```

Build standalone:

```powershell
python -m nuitka --mode=standalone --windows-console-mode=disable --enable-plugin=tk-inter --include-data-files=icon.ico=icon.ico --include-data-files=icon.png=icon.png --windows-icon-from-ico=icon.ico ExpCore.py
```

Hasil build berada di <code>ExpCore.dist/</code>.

### Membuat Installer

1. Buka <code>ExpCore.iss</code> dengan Inno Setup Compiler.
2. Pilih **Build → Compile**.
3. Installer dihasilkan sebagai <code>ExpCore/ExpCore.exe</code>.

---

## Struktur Utama

```text
ExpCore/
├── ExpCore.py          # UI dan logika aplikasi
├── ExpCore.iss         # Konfigurasi installer
├── test_expcore.py     # Pemeriksaan parser penamaan Bupot
├── icon.ico
├── icon.png
├── LICENSE.txt
└── README.md
```

---

## Catatan

- Parser dirancang untuk PDF yang dihasilkan oleh **Coretax DJP**.
- PDF terproteksi, rusak, hasil scan tanpa lapisan teks, atau memiliki layout berbeda dapat gagal diproses.
- Modul Pajak Masukan menghitung PPN menggunakan tarif tetap **12%**.
- File Excel dengan nama yang sama akan ditimpa pada proses berikutnya.
- Gunakan **Pratinjau Nama** sebelum menerapkan perubahan nama PDF.

---

## Lisensi

Dilisensikan di bawah **Apache License 2.0**. Lihat [LICENSE.txt](LICENSE.txt).

Copyright © 2026 Iyan Sanjaya.
