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
| **Bukti Potong 2026**       | Mengekstrak nomor dokumen, masa pajak, NPWP/NIK, nama, status bukti, jenis PPh, objek pajak, DPP, tarif, PPh, dokumen dasar, dan data pemotong. |
| **Bukti Potong 2024**       | Mengekstrak PDF formulir **BPBS** (pra-Coretax): nomor bukti, pembetulan, NPWP/NIK, masa pajak, objek pajak, DPP, tarif, PPh, dokumen referensi, dan data pemotong. |
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

```bash
git clone https://github.com/iyansanjaya/ExpCore.git
cd ExpCore

python -m venv .venv
./.venv/Scripts/python.exe -m pip install --upgrade pip
./.venv/Scripts/python.exe -m pip install customtkinter pdfplumber pandas openpyxl
./.venv/Scripts/python.exe ExpCore.py
```

> **Dua aturan yang mencegah hampir semua masalah build:**
>
> 1. **Panggil <code>./.venv/Scripts/python.exe</code> secara eksplisit, jangan <code>python</code> saja.**
>    Perintah <code>python</code> mengikuti PATH, sehingga bisa mengarah ke interpreter lain di sistem Anda
>    (Python global, Microsoft Store, conda, atau venv milik tool lain) walaupun Anda merasa sudah
>    mengaktifkan virtual environment.
> 2. **Tulis path dengan garis miring <code>/</code>, bukan <code>\\</code>.**
>    Bentuk <code>/</code> jalan di PowerShell maupun Git Bash. Bentuk <code>\\</code> hanya jalan di
>    PowerShell — di Git Bash, <code>\\</code> adalah karakter escape, sehingga
>    <code>.\\.venv\\Scripts\\python.exe</code> berubah menjadi <code>..venvScriptspython.exe</code> dan
>    gagal dengan pesan <code>command not found</code>.
>
> Lihat [Pemecahan Masalah](#pemecahan-masalah) kalau tetap bermasalah.

Verifikasi environment sudah benar. Perintah berikut harus mencetak <code>lengkap</code>:

```bash
./.venv/Scripts/python.exe -c "import customtkinter, pdfplumber, pandas, openpyxl; print('lengkap')"
```

---

## Cara Penggunaan

### Ekstraksi Bukti Potong atau Pajak Masukan

1. Pilih menu **Bukti Potong 2026**, **Bukti Potong 2024**, atau **Pajak Masukan**.
2. Pilih folder biasa atau folder induk.
3. Klik **Mulai Ekstrak**.
4. Aplikasi memproses seluruh PDF di folder tersebut dan semua subfolder.
5. Satu file Excel disimpan di folder yang dipilih:
   - Bukti Potong 2026: <code>!Hasil_Rekap_Bupot.xlsx</code>
   - Pajak Masukan: <code>Hasil_Pajak_Masukan.xlsx</code>
   - Bukti Potong 2024: <code>!Hasil_Rekap_Bupot_2024.xlsx</code>

**Memilih menu yang tepat.** Kedua modul Bukti Potong membaca formulir yang berbeda dan
tidak saling menggantikan:

| Menu | Formulir | Ciri di PDF |
| --- | --- | --- |
| **Bukti Potong 2026** | BPPU (Coretax) | Judul <code>BUKTI PEMOTONGAN DAN/ATAU PEMUNGUTAN PPh</code>, bagian <code>B.3</code>–<code>B.11</code> |
| **Bukti Potong 2024** | BPBS (pra-Coretax) | Judul <code>FORMULIR BPBS</code>, bagian <code>H.1</code>–<code>H.5</code> |

Salah pilih menu tidak merusak data — PDF yang formatnya tidak cocok dilewati dan dicatat di log.

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

```bash
./.venv/Scripts/python.exe test_expcore.py
```

---

## Build dan Distribusi

### Compile dengan Nuitka

> **Nuitka mem-bundle dari interpreter yang menjalankannya, bukan dari folder proyek.**
> Kalau Nuitka dijalankan oleh interpreter yang tidak punya dependency aplikasi, modul yang hilang
> **tidak** membuat build gagal — Nuitka hanya memberi peringatan lalu tetap menghasilkan
> <code>.exe</code> yang crash saat dibuka. Karena itu semua perintah di bawah memakai path venv
> secara eksplisit.

**Langkah 1** — install Nuitka ke venv proyek (bukan ke Python global):

```bash
./.venv/Scripts/python.exe -m pip install Nuitka
```

**Langkah 2** — pastikan venv sudah lengkap sebelum build. Perintah ini harus mencetak <code>siap build</code>:

```bash
./.venv/Scripts/python.exe -c "import customtkinter, pdfplumber, pandas, openpyxl, nuitka; print('siap build')"
```

**Langkah 3** — build standalone:

```bash
./.venv/Scripts/python.exe -m nuitka --mode=standalone --windows-console-mode=disable --enable-plugin=tk-inter --include-data-files=icon.ico=icon.ico --include-data-files=icon.png=icon.png --windows-icon-from-ico=icon.ico ExpCore.py
```

Hasil build berada di <code>ExpCore.dist/</code>. **Proses ini lama** — pandas dan numpy ikut
dikompilasi, jadi siapkan waktu belasan menit. Jangan tutup terminal sebelum selesai; build yang
terputus tidak meninggalkan <code>ExpCore.dist/</code> sama sekali.

**Langkah 4** — verifikasi hasil build sebelum dibuat installer. Semua paket berikut harus muncul:

```bash
ls ExpCore.dist | grep -E "pdfplumber|pdfminer|pandas|numpy|customtkinter"
```

Kalau hasilnya kosong, berarti build memakai interpreter yang salah. Ulangi dari Langkah 2 —
membersihkan <code>ExpCore.build/</code> tidak akan menolong, karena masalahnya bukan artefak lama.

### Membuat Installer

1. Buka <code>ExpCore.iss</code> dengan Inno Setup Compiler.
2. Pilih **Build → Compile**.
3. Installer dihasilkan sebagai <code>ExpCore/ExpCore.exe</code>.

---

## Pemecahan Masalah

### Aplikasi hasil build tidak terbuka saat double click

Build memakai <code>--windows-console-mode=disable</code>, sehingga aplikasi yang crash saat start
tidak menampilkan pesan apa pun — jendela tidak muncul dan tidak ada error. Untuk melihat
penyebab sebenarnya, jalankan exe dengan output dialihkan ke file:

Git Bash:

```bash
./ExpCore.dist/ExpCore.exe 2> err.txt; cat err.txt
```

PowerShell:

```powershell
Start-Process ./ExpCore.dist/ExpCore.exe -RedirectStandardError err.txt -RedirectStandardOutput out.txt -Wait; Get-Content err.txt
```

Pesan seperti <code>ModuleNotFoundError: No module named 'pdfplumber'</code> berarti dependency tidak
ikut ter-bundle. Penyebabnya hampir selalu Nuitka dijalankan oleh interpreter yang salah. Periksa
interpreter mana yang sebenarnya dipakai oleh perintah <code>python</code> di shell Anda —
<code>which python</code> di Git Bash, atau di PowerShell:

```powershell
(Get-Command python).Source
```

Kalau hasilnya bukan <code>.../ExpCore/.venv/Scripts/python.exe</code>, ulangi build memakai path venv
secara eksplisit seperti pada [Compile dengan Nuitka](#compile-dengan-nuitka).

Untuk build percobaan, ganti sementara ke <code>--windows-console-mode=force</code> supaya error
langsung terlihat di jendela konsol tanpa perlu mengalihkan output.

### Membedakan masalah kode dan masalah build

Jalankan aplikasi langsung dari source. Kalau di sini jalan normal tetapi hasil build tidak,
masalahnya ada di proses build, bukan di kode:

```bash
./.venv/Scripts/python.exe ExpCore.py
```

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
- Pada modul Bukti Potong 2024, kolom **Sifat** dibaca dari tanda centang <code>X</code> pada
  <code>H.4</code>/<code>H.5</code>. Bila tidak tepat satu kotak yang tercentang, kolom ini
  berisi <code>-</code> daripada menebak. Kolom **NIK** kosong (<code>-</code>) bila field
  <code>A.2</code> pada formulir memang tidak diisi.
- File Excel dengan nama yang sama akan ditimpa pada proses berikutnya.
- Gunakan **Pratinjau Nama** sebelum menerapkan perubahan nama PDF.

---

## Lisensi

Dilisensikan di bawah **Apache License 2.0**. Lihat [LICENSE.txt](LICENSE.txt).

Copyright © 2026 Iyan Sanjaya.
