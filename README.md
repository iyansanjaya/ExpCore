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
  <img src="https://img.shields.io/badge/version-1.6.0-7c3aed?style=flat-square" alt="Version" />
  <img src="https://img.shields.io/badge/license-Apache%202.0-blue?style=flat-square" alt="License" />
</p>

---

## Fitur

| Fitur                       | Deskripsi                                                                                                               |
| --------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| **Bukti Potong 2026**       | Mengekstrak nomor dokumen, masa pajak, NPWP/NIK, nama, status bukti, jenis PPh, objek pajak, DPP, tarif, PPh, dokumen dasar, dan data pemotong. |
| **Bukti Potong 2024**       | Mengekstrak PDF formulir **BPBS** (pra-Coretax): nomor bukti, pembetulan, NPWP/NIK, masa pajak, objek pajak, DPP, tarif, PPh, dokumen referensi, dan data pemotong. |
| **Pajak Masukan**           | Mengekstrak pembeli, nomor faktur, rincian barang, harga, kuantitas, DPP, PPN, dan nilai netto.                         |
| **Penamaan Otomatis Bupot** | Mempratinjau dan mengganti nama PDF menjadi <code>Nama Pemotong (C.3) - Nomor Bukti - Masa Pajak - Sifat - Status.pdf</code>. |
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

### Ruang kerja baru

Beranda menyediakan empat alat dalam satu workspace terang dengan navigasi tetap.
Setiap halaman memiliki pemilihan folder, progres, log aktivitas, dan akses langsung
ke hasil. Folder bisa diketik atau dipilih menggunakan **Pilih folder** / `Ctrl+O`.

Pemrosesan berjalan di latar sehingga navigasi tetap responsif. Tombol proses dan
perubahan folder dikunci sementara untuk mencegah pekerjaan bertumpuk. Gunakan
**Buka hasil** untuk membuka Excel hasil ekstraksi atau folder PDF pada Penamaan Bupot
(setelah pratinjau maupun penerapan nama). Log CSV penamaan tetap disimpan di folder
tersebut. Gunakan **Salin log** untuk
menyalin aktivitas. Jendela pendek menyediakan area konten yang dapat digulir,
sementara tombol aksi utama tetap terlihat di bawah.
Roda mouse bekerja di atas kartu dan isian. Saat log kosong atau sudah mencapai
ujung, scroll diteruskan ke halaman; gunakan juga scrollbar atau `Page Up` / `Page Down`.

Gunakan `Alt+0` untuk beranda dan `Alt+1`–`Alt+4` untuk empat alat. Tombol dapat
diakses menggunakan `Tab`, lalu diaktifkan dengan `Enter` atau `Space`.
Lihat [DESIGN.md](DESIGN.md) untuk sistem visual dan aturan interaksi.

### Ekstraksi Bukti Potong atau Pajak Masukan

1. Pilih menu **Bukti Potong 2026**, **Bukti Potong 2024**, atau **Pajak Masukan**.
2. Pilih folder biasa atau folder induk.
3. Klik **Mulai ekstraksi**. Jika rekap lama sudah ada, konfirmasikan penggantiannya.
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
4. Tombol **Terapkan nama** aktif setelah pratinjau selesai. Periksa CSV, lalu klik
   tombol tersebut dan konfirmasikan perubahan. Penerapan memindai ulang folder,
   sehingga perubahan file sejak pratinjau ikut diperiksa.

Nama diambil dari **C.3 Nama Pemotong dan/atau Pemungut PPh** pada BPPU Coretax. Contoh hasil:

```text
KARUNIA INTI CEMERLANG - 2604BX1RN - 06-2026 - TIDAK FINAL - NORMAL.pdf
```

Jika C.3 kosong atau tidak terbaca, PDF dilewati tanpa menggunakan nama penerima sebagai pengganti. Log CSV tetap mencatat `NAMA_PENERIMA` dan `NAMA_PEMOTONG` untuk audit.

PDF dengan data wajib yang tidak lengkap akan dilewati. Nama yang sudah digunakan tidak ditimpa; aplikasi menambahkan nomor seperti <code>(2)</code>. Setiap proses menghasilkan log audit:

```text
Log_Penamaan_Bupot_Pratinjau_YYYYMMDD_HHMMSS.csv
Log_Penamaan_Bupot_Penerapan_YYYYMMDD_HHMMSS.csv
```

---

## Pengujian

Pemeriksaan update (offline, semua respons GitHub dimock):

```bash
./.venv/Scripts/python.exe -m unittest test_expcore_updates -v
```

Mencakup perbandingan versi, rilis stabil, kesiapan installer, URL resmi, cache,
throttling, respons rusak/terlalu besar, timeout, TLS, HTTP 404/403/429/503,
dan kegagalan penyimpanan cache. Tes UI juga memeriksa banner, tombol unduh,
penutupan saat worker berjalan, serta pemulihan kontrol setelah kesalahan.

Pemeriksaan antarmuka desktop (memerlukan Tcl/Tk; tidak mengubah PDF pengguna):

```bash
./.venv/Scripts/python.exe test_expcore_ui.py
./.venv/Scripts/python.exe test_expcore_ui.py --scale 1.25
./.venv/Scripts/python.exe test_expcore_ui.py --scale 1.5
```

Pemeriksaan parser dan keamanan nama file:

```bash
./.venv/Scripts/python.exe test_expcore.py
```

Untuk menguji ulang 151 PDF feedback lokal di `contoh-pdf/JAN` dan `contoh-pdf/FEB` tanpa mengubah PDF:

```bash
./.venv/Scripts/python.exe test_expcore.py --pdf-samples
```

Tes memeriksa JAN menghasilkan 75 baris dan FEB 76 baris, termasuk sembilan file yang sebelumnya terlewat karena tarif ditulis sebagai bilangan bulat.

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
./.venv/Scripts/python.exe build_release.py
```

Hasil build berada di <code>ExpCore.dist/</code>. **Proses ini lama** — pandas dan numpy ikut
dikompilasi, jadi siapkan waktu belasan menit. Jangan tutup terminal sebelum selesai; build yang
terputus tidak meninggalkan <code>ExpCore.dist/</code> sama sekali.

`VERSION` adalah sumber nomor versi aplikasi, metadata executable, dan installer.
Gunakan format `MAJOR.MINOR.PATCH`, misalnya `1.6.0`. Skrip build membundel file ini
secara otomatis; jangan mengubah salinan di `ExpCore.dist/` secara manual.
Build pertama memerlukan internet untuk mengunduh alat pendukung Nuitka ke cache
pengguna. Skrip menyetujui unduhan alat build ini agar kompilasi tidak berhenti pada
prompt interaktif; build selanjutnya memakai cache yang tersedia.

**Langkah 4** — verifikasi hasil build sebelum dibuat installer. Semua paket berikut harus muncul:

```bash
ls ExpCore.dist | grep -E "pdfplumber|pdfminer|pandas|numpy|customtkinter"
```

Kalau hasilnya kosong, berarti build memakai interpreter yang salah. Ulangi dari Langkah 2 —
membersihkan <code>ExpCore.build/</code> tidak akan menolong, karena masalahnya bukan artefak lama.

### Membuat Installer

1. Buka <code>ExpCore.iss</code> dengan Inno Setup Compiler.
2. Pilih **Build → Compile**.
3. Installer dihasilkan sebagai <code>ExpCore/ExpCore-Setup-1.6.0.exe</code> (nama mengikuti `VERSION`).

Compiler installer menolak build jika `ExpCore.dist/VERSION` belum tersedia atau
berbeda dari `VERSION` sumber. Jalankan ulang `build_release.py` setelah mengubah versi.

### Pemberitahuan pembaruan

- Aplikasi memeriksa rilis stabil terbaru dari `iyansanjaya/ExpCore` melalui GitHub
  setelah antarmuka terbuka. Pekerjaan PDF dan navigasi tetap berjalan.
- Hasil disimpan selama 24 jam di `%LOCALAPPDATA%/ExpCore/update-check.json`.
  Tombol **Periksa update** melewati cache setelah 60 detik. Kegagalan koneksi
  menunda percobaan berikutnya 15 menit; batas GitHub mengikuti waktu tunggu server
  (minimal 60 detik, maksimal 24 jam).
- Jika ada versi lebih baru dengan installer siap, banner menyediakan **Unduh update**
  dan **Nanti**. Unduh membuka halaman rilis resmi di browser. Pengguna mengunduh
  dan menjalankan installer sendiri. Nanti menyembunyikan banner untuk sesi tersebut;
  pemeriksaan manual dapat menampilkannya kembali.
- Gangguan jaringan saat pengecekan otomatis tidak memunculkan dialog. Pengecekan
  manual menjelaskan kegagalan; aplikasi tetap dapat dipakai saat offline.
- Permintaan hanya membaca metadata rilis publik dengan HTTPS; PDF, isi dokumen,
  nama file, dan folder pengguna tidak dikirim. Tidak ada token GitHub dalam aplikasi.
- Rilis draft/prerelease, tag tidak valid, tautan di luar repositori resmi, dan
  installer yang belum selesai diunggah tidak menghasilkan tawaran unduh.

### Menerbitkan versi berikutnya

1. Ubah `VERSION`, lalu jalankan tes parser, update, dan UI di atas.
2. Jalankan `build_release.py`, buka hasil executable, lalu compile `ExpCore.iss`.
3. Buat **draft release** GitHub dengan tag persis `v` + isi `VERSION`, misalnya `v1.6.0`.
4. Unggah `ExpCore-Setup-1.6.0.exe` ke draft beserta catatan perubahan. Nama installer
   mengikuti versi. Nama lama `ExpCore.exe` juga didukung untuk kompatibilitas.
5. Setelah executable dan installer diperiksa, publikasikan sebagai rilis stabil
   dan tandai **latest**. Push commit atau tag saja tidak memicu pemberitahuan.

Pengguna versi 1.5 dan sebelumnya perlu memasang versi 1.6.0 sekali secara manual.
Pemberitahuan otomatis tersedia mulai versi yang sudah memiliki pemeriksa update ini.

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
├── ExpCore.py          # Parser PDF dan ekspor data
├── expcore_ui.py       # Workspace desktop dan pemrosesan latar
├── expcore_updates.py  # Pemeriksaan rilis GitHub dan cache per pengguna
├── VERSION            # Nomor versi tunggal aplikasi dan installer
├── build_release.py   # Build Nuitka dengan versi dan data yang konsisten
├── DESIGN.md           # Token visual dan aturan interaksi
├── ExpCore.iss         # Konfigurasi installer
├── test_expcore.py     # Pemeriksaan ketiga parser + keamanan nama file
├── test_expcore_ui.py  # Pemeriksaan layout, worker dan interaksi desktop
├── test_expcore_updates.py # Pengujian update tanpa jaringan
├── contoh_pdf.pdf      # Contoh Bupot BPPU (Coretax) untuk pengujian
├── graphify-out/       # Graph pengetahuan proyek (graph.html, GRAPH_REPORT.md)
├── icon.ico
├── icon.png
├── .gitignore
├── LICENSE.txt
└── README.md
```

---

## Catatan

- Parser dirancang untuk PDF resmi DJP: formulir **BPPU** dari Coretax (modul 2026)
  dan formulir **BPBS** pra-Coretax (modul 2024). Keduanya punya parser terpisah.
- PDF terproteksi, rusak, hasil scan tanpa lapisan teks, atau memiliki layout berbeda dapat gagal diproses.
- Modul Pajak Masukan menghitung PPN menggunakan tarif tetap **12%**.
- Pada modul Bukti Potong 2024, kolom **Sifat** dibaca dari tanda centang <code>X</code> pada
  <code>H.4</code>/<code>H.5</code>. Bila tidak tepat satu kotak yang tercentang, kolom ini
  berisi <code>-</code> daripada menebak. Kolom **NIK** kosong (<code>-</code>) bila field
  <code>A.2</code> pada formulir memang tidak diisi.
- Tarif pada formulir BPBS dapat ditulis sebagai bilangan bulat (`2`) maupun desimal (`2.00` atau `2,00`); ketiganya dibaca sebagai tarif 2%.
- File Excel dengan nama yang sama diganti setelah pengguna mengonfirmasi.
- Gunakan **Pratinjau Nama** sebelum menerapkan perubahan nama PDF.

---

## Lisensi

Dilisensikan di bawah **Apache License 2.0**. Lihat [LICENSE.txt](LICENSE.txt).

Copyright © 2026 Iyan Sanjaya.
