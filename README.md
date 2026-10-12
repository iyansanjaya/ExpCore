<p align="center">
  <img src="icon.svg" alt="ExpCore Logo" width="80" />
</p>

<h1 align="center">ExpCore</h1>

<p align="center">
  <strong>Toolkit PDF Coretax</strong><br/>
  Ekstrak data Bukti Potong, Pajak Masukan, dan rekening koran ke Excel, serta beri nama PDF Bupot secara otomatis.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/electron-44-47848F?style=flat-square&logo=electron&logoColor=white" alt="Electron" />
  <img src="https://img.shields.io/badge/platform-Windows-0078D6?style=flat-square&logo=windows&logoColor=white" alt="Platform" />
  <img src="https://img.shields.io/badge/version-3.1.0-7c3aed?style=flat-square" alt="Version" />
  <img src="https://img.shields.io/badge/license-Apache%202.0-blue?style=flat-square" alt="License" />
</p>

---

## Fitur

| Fitur                       | Deskripsi                                                                                                               |
| --------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| **Bukti Potong 2026**       | Mengekstrak nomor dokumen, masa pajak, NPWP/NIK, nama, status bukti, jenis PPh, objek pajak, DPP, tarif, PPh, dokumen dasar, dan data pemotong. |
| **Bukti Potong 2024**       | Mengekstrak PDF formulir **BPBS** (pra-Coretax): nomor bukti, pembetulan, NPWP/NIK, masa pajak, objek pajak, DPP, tarif, PPh, dokumen referensi, dan data pemotong. |
| **Pajak Masukan**           | Mengekstrak pembeli, nomor faktur, rincian barang, harga, kuantitas, DPP, PPN, dan nilai netto.                         |
| **Penamaan Otomatis Bupot** | Mempratinjau dan mengganti nama PDF **Bupot 2026 (BPPU)** dan **Bupot 2024 (BPBS)** menjadi <code>Nama - Nomor Bukti - Masa Pajak - Sifat - Status.pdf</code>. Jenis formulir dikenali otomatis; nama diambil dari **Identitas Pemotong** atau **Wajib Pajak yang Dipotong**, sesuai pilihan pengguna. |
| **Rekening Koran BCA**      | Merekap e-Statement BCA **Rekening Giro** dan **Rekening Tahapan**: tanggal, keterangan, CBG, debit, kredit, dan saldo. Ringkasan saldo dan mutasi ditulis terpisah lalu dicocokkan dengan transaksi. |
| **Rekening Koran CIMB**     | Merekap **Combine Statement Portfolio** (Laporan Konsolidasi) CIMB Niaga: semua transaksi rekening **Tabungan/Giro** dan **Tabungan Berjangka** di RINCIAN ASET, beserta total kedua kategori (Ekuivalen IDR). Total, saldo, dan daftar aset dicocokkan otomatis. |
| **Pemindaian Subfolder**    | Memproses seluruh PDF dalam folder induk dan semua subfolder menjadi satu hasil.                                        |
| **Output Terformat**        | Menghasilkan Excel dengan format angka, header, lebar kolom otomatis, dan informasi folder sumber.                      |

*Kode* (kelas `ExpCore` di `ExpCore.py`): Bukti Potong 2026 → `process_bupot()` dan
`_extract_bupot_rows()`; Bukti Potong 2024 → `process_bupot_2024()` dan
`_extract_bupot2024_rows()`; Pajak Masukan → `process_pm()`; Penamaan Otomatis Bupot →
`process_rename_bupot()` dan `_extract_rename_bupot_data()`; Rekening Koran BCA →
`process_rekening_koran()`, `_extract_rekening_koran()`, dan `_write_rekening_excel()`; Rekening Koran
CIMB → `process_rekening_cimb()`, `_extract_rekening_cimb()`, dan `_write_cimb_excel()`;
output Excel → `_write_excel()`.
*Diuji:* `test_batch_exports()` dan `test_engine_protocol()` (kelima ekspor),
`test_rename_pemotong()` (penamaan C.3/A.2), `test_rekening_koran()`, `test_rekening_cimb()`, dan
`test_pdf_samples()` di `test_expcore.py`, dengan PDF sintetis dari `write_all()`, `write_rekening()`, dan
`write_cimb()` di `tests/fixtures.py`.

Semua proses berjalan secara lokal. ExpCore TIDAK mengirim PDF atau hasil ekstraksi ke internet.

---

## Teknologi

- **Aplikasi desktop:** [Electron](https://www.electronjs.org/)
- **Antarmuka:** [Tailwind CSS](https://tailwindcss.com/) v4, [Motion](https://motion.dev/) (Framer Motion untuk JavaScript), ikon [Reicon](https://reicon.dev/), dan font Inter yang dibundel lokal
- **Engine PDF:** Python — [pdfplumber](https://github.com/jsvine/pdfplumber), [pandas](https://pandas.pydata.org/), dan [openpyxl](https://openpyxl.readthedocs.io/)
- **Executable engine:** [Nuitka](https://nuitka.net/)
- **Installer & update:** [electron-builder](https://www.electron.build/) (NSIS) dan electron-updater melalui GitHub Releases

Electron menampilkan antarmuka. Setiap pekerjaan menjalankan satu proses engine Python
(`expcore_engine.py`) yang mengirim log, progres, dan hasil dalam JSON per baris.
Logika ekstraksi di `ExpCore.py` tidak bergantung pada antarmuka. Kode antarmuka di
`app/renderer/src/` dibangun ke `app/renderer/dist/` dengan `bun run build:renderer`
(Tailwind CLI + esbuild); `bun start`, `bun run test`, dan `build_release.py` menjalankannya
otomatis, jadi aplikasi tetap bekerja sepenuhnya offline.

---

## Menjalankan dari Source

Kebutuhan: Windows, Python 3.10 atau lebih baru, dan Node.js 22.12 atau lebih baru.

```bash
git clone https://github.com/iyansanjaya/ExpCore.git
cd ExpCore

python -m venv .venv
./.venv/Scripts/python.exe -m pip install --upgrade pip
./.venv/Scripts/python.exe -m pip install pdfplumber pandas openpyxl
bun ci
bun start
```

Dalam mode pengembangan, aplikasi menjalankan engine dengan `./.venv/Scripts/python.exe`,
jadi venv harus berada di folder proyek dengan nama `.venv`.

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
./.venv/Scripts/python.exe -c "import pdfplumber, pandas, openpyxl; print('lengkap')"
```

---

## Cara Penggunaan

### Ruang kerja baru

Beranda menyediakan enam alat dalam satu workspace terang dengan navigasi tetap. Semua alat
dibuka dari menu **Alat** di header, dikelompokkan menjadi **Ekstraksi ke Excel** (Bukti Potong
2026, Bukti Potong 2024, Pajak Masukan, Rekening Koran BCA, Rekening Koran CIMB) dan **Kelola PDF**
(Penamaan Bupot).
Saat sebuah alat terbuka, namanya tampil di tombol **Alat**; titik berdenyut di tombol itu
menandakan ada proses yang sedang berjalan.
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

Gunakan `Alt+0` untuk beranda dan `Alt+1`–`Alt+6` untuk keenam alat sesuai urutan menu. Tombol dapat
diakses menggunakan `Tab`, lalu diaktifkan dengan `Enter` atau `Space`. Di menu **Alat**, gunakan
panah atas/bawah untuk berpindah, `Enter` untuk membuka alat, dan `Esc` untuk menutup.
Lihat [DESIGN.md](DESIGN.md) untuk sistem visual dan aturan interaksi.

### Ekstraksi Bukti Potong atau Pajak Masukan

1. Buka **Alat** lalu pilih **Bukti Potong 2026**, **Bukti Potong 2024**, atau **Pajak Masukan**.
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

1. Buka **Alat** lalu pilih **Penamaan Bupot**.
2. Pilih folder yang berisi PDF Bupot, termasuk jika PDF berada dalam subfolder. Bupot 2026
   (BPPU Coretax) dan Bupot 2024 (formulir BPBS) boleh tercampur; jenis formulir dikenali dari
   judulnya untuk setiap PDF.
3. Pada **Ambil nama file dari**, pilih sumber nama:

   | Pilihan | BPPU (Bupot 2026) | BPBS (Bupot 2024) |
   | --- | --- | --- |
   | **Identitas Pemotong** (bawaan) | C.3 Nama Pemotong dan/atau Pemungut PPh | C.2 Nama Wajib Pajak (Identitas Pemotong/Pemungut) |
   | **Wajib Pajak yang Dipotong** | A.2 Nama | A.3 Nama |

4. Klik **Pratinjau nama** dan periksa log CSV.
5. Tombol **Terapkan nama** aktif setelah pratinjau selesai. Periksa CSV, lalu klik
   tombol tersebut dan konfirmasikan perubahan. Penerapan memindai ulang folder,
   sehingga perubahan file sejak pratinjau ikut diperiksa. Mengganti folder atau sumber
   nama membatalkan pratinjau; jalankan pratinjau ulang sebelum menerapkan.

Contoh hasil:

```text
ADIRA DINAMIKA MULTI FINANCE TBK - 2507UMKHM - 12-2025 - TIDAK FINAL - NORMAL.pdf   (BPPU, Identitas Pemotong C.3)
MITRACOLL SARANA JAYA - 2507UMKHM - 12-2025 - TIDAK FINAL - NORMAL.pdf              (BPPU, Wajib Pajak yang Dipotong A.2)
BFI FINANCE INDONESIA TBK - 2000000001 - 01-2024 - TIDAK FINAL - NORMAL.pdf          (BPBS, Identitas Pemotong C.2)
MITRACOLL SARANA JAYA - 2000000001 - 01-2024 - TIDAK FINAL - NORMAL.pdf              (BPBS, Wajib Pajak yang Dipotong A.3)
```

Pada BPBS, nomor bukti diambil dari **H.1**, masa pajak dari kolom **B.1** baris objek pajak
(mis. `1-2024` menjadi `01-2024`), sifat dari tanda centang **H.4**/**H.5**, dan status dari
**H.2 Pembetulan** serta **H.3 Pembatalan**. ExpCore tidak menebak: PDF dilewati bila tidak tepat
satu kotak sifat yang tercentang, bila baris objek pajak memiliki masa yang berbeda, atau bila
kotak H.2 tidak terbaca.

Jika nama pada sumber terpilih kosong atau tidak terbaca, PDF dilewati tanpa memakai nama dari
sumber lain. Log CSV tetap mencatat `NAMA_PENERIMA` dan `NAMA_PEMOTONG`, `sumber_nama` beserta
kode bagian yang dipakai (mis. `Identitas Pemotong (C.2)`), dan `FORMULIR` (`BPPU`, `BPBS`, atau
kosong bila bukan Bupot), untuk audit. Log aktivitas menandai setiap PDF dengan `[BPPU]` atau
`[BPBS]`.

PDF dengan data wajib yang tidak lengkap akan dilewati. Nama yang sudah digunakan tidak ditimpa; aplikasi menambahkan nomor seperti <code>(2)</code>. Setiap proses menghasilkan log audit:

```text
Log_Penamaan_Bupot_Pratinjau_YYYYMMDD_HHMMSS.csv
Log_Penamaan_Bupot_Penerapan_YYYYMMDD_HHMMSS.csv
```

*Kode:* log CSV ditulis oleh `process_rename_bupot()` di `ExpCore.py`; jenis formulir dikenali
`_extract_rename_bupot_data()`, lalu dibaca `_extract_bppu_rename_data()` (BPPU) atau
`_extract_bpbs_rename_data()` (BPBS, memakai `_bpbs_header()` yang sama dengan rekap Bukti Potong
2024); pilihan sumber nama ada di `RENAME_NAME_SOURCES`
(`ExpCore.py`) dan `MODULES.rename.nameSources` (`app/main.js`).
*Diuji:* `test_rename_pemotong()` dan `test_rename_bpbs()` di `test_expcore.py`; tes E2E "penamaan: …" memakai `setFolder()`,
`runTo()`, dan `stubMain()` di `tests/app.test.js`.

### Rekap Rekening Koran (BCA)

1. Buka **Alat** lalu pilih **Rekening Koran BCA**.
2. Pilih folder berisi e-Statement BCA **Rekening Giro** dan/atau **Rekening Tahapan**
   (PDF asli dari BCA, bukan hasil scan). Subfolder ikut diproses.
3. Klik **Mulai ekstraksi**. Hasil disimpan sebagai <code>!Hasil_Rekap_Rekening_Koran.xlsx</code>
   di folder yang dipilih.

Isi Excel:

- **Ringkasan** — satu baris per PDF: jenis rekening, nomor, nama, periode, saldo awal,
  mutasi CR beserta jumlah transaksinya, mutasi DB beserta jumlah transaksinya, saldo akhir,
  **Hasil Cek**, dan catatan. Nama sheet dapat diklik untuk membuka rinciannya.
- **Satu sheet per PDF** (mis. `Giro 6470994949 2023-01`), diurutkan per rekening dan periode:
  - Tabel **TANGGAL · KETERANGAN · CBG · DEBIT · CREDIT · SALDO**. Mutasi bertanda `DB` di PDF
    masuk kolom **DEBIT**, selainnya **CREDIT**. Tanggal lengkap dengan tahun dari periode
    rekening; SALDO hanya terisi bila tercetak di PDF.
  - Panel di kanan tabel: informasi rekening, lalu ringkasan PDF dalam baris terpisah
    (**SALDO AWAL**, **MUTASI CR** + jumlah, **MUTASI DB** + jumlah, **SALDO AKHIR**).
    Ringkasan sengaja tidak ditulis di bawah tabel dan tidak digabung ke keterangan, sehingga
    `SUM`, filter, dan pengurutan kolom DEBIT/CREDIT hanya menghitung transaksi.

Setiap PDF dicek otomatis: total dan jumlah transaksi debit/kredit harus sama dengan ringkasan
PDF, saldo berjalan harus sama dengan setiap saldo yang tercetak, dan jumlah halaman harus
lengkap. Bila ada selisih, **Hasil Cek** berisi **PERLU CEK** beserta alasannya, dan alasan yang
sama tampil di log aktivitas. Rekening dan periode yang sama di lebih dari satu PDF (mis. file terunduh
dua kali) juga ditandai **PERLU CEK** dengan catatan lokasi salinannya, agar transaksinya tidak
terhitung ganda tanpa terlihat. Tidak ada PDF yang dibuang; pilih sendiri salinan yang dipakai.

*Kode:* `process_rekening_koran()`, `_extract_rekening_koran()`, dan `_write_rekening_excel()`
di `ExpCore.py`.
*Diuji:* `test_rekening_koran()` dan `read_rekening()` di `test_expcore.py` (e-Statement sintetis dari
`write_rekening()` di `tests/fixtures.py`); `test_pdf_samples()` untuk keenam e-Statement asli.

### Rekap Rekening Koran CIMB Niaga

1. Buka **Alat** lalu pilih **Rekening Koran CIMB**.
2. Pilih folder berisi **Combine Statement Portfolio** (Laporan Konsolidasi) CIMB Niaga, PDF asli
   dari bank (bukan hasil scan). Satu folder boleh berisi beberapa bulan; subfolder ikut diproses.
3. Klik **Mulai ekstraksi**. Hasil disimpan sebagai <code>!Hasil_Rekap_Rekening_CIMB.xlsx</code>
   di folder yang dipilih.

Yang diambil hanya rekening yang tercantum di **RINCIAN ASET /ASSET DETAIL** pada daftar
**Tabungan/Giro/Savings/Current Account** dan **Tabungan Berjangka /Installment Saving**, beserta
baris totalnya (*Total Tabungan / Giro* dan *TOTAL TABUNGAN BERJANGKA / TOTAL INSTALLMENT SAVINGS*).
Bagian dikenali dari judul dan isinya, bukan dari nomor halaman, sehingga jumlah halaman, rekening,
dan transaksi boleh berbeda setiap bulan. Deposito, Market Linked Deposit, kartu kredit, Poin Xtra,
dan halaman lain diabaikan.

Isi Excel:

- **Ringkasan** — satu baris per rekening per laporan: kategori, nomor rekening, nama produk, mata
  uang, tanggal laporan, saldo awal, total debit, total kredit, saldo akhir, saldo Ekuivalen IDR,
  jumlah transaksi, **Hasil Cek**, dan catatan. Nama sheet dapat diklik untuk membuka rinciannya.
- **Total Kategori** — per laporan, total Tabungan/Giro dan Tabungan Berjangka (Ekuivalen IDR) dari
  PDF, dicocokkan dengan jumlah saldo Ekuivalen IDR setiap rekening di daftar.
- **Semua Transaksi** — seluruh transaksi dari semua rekening dan semua laporan dalam satu tabel, siap
  difilter atau dibuat pivot: tanggal transaksi dan valuta, kategori, nomor rekening, nama produk, mata
  uang, uraian, no cek/BG, debit, kredit, saldo, hasil cek rekeningnya, tanggal laporan, dan tautan ke
  sheet asalnya. Diurutkan per kategori lalu nomor rekening, dan kronologis di dalam setiap rekening,
  sehingga kolom saldo tetap saldo berjalan rekening itu. Laporan yang sama di dua PDF ikut tercatat dua
  kali, tetapi baris-barisnya bertanda **PERLU CEK** di kolom Hasil Cek.
- **Satu sheet per rekening per laporan** (mis. `705375094000 2024-12`):
  - Tabel **TANGGAL TRANSAKSI · TANGGAL VALUTA · URAIAN TRANSAKSI · NO CEK/BG · DEBIT · KREDIT ·
    SALDO**. Uraian yang di PDF tertulis beberapa baris digabung menjadi satu transaksi. Tanggal
    lengkap dengan tahun dari tanggal laporan (31/12 pada laporan Januari = tahun sebelumnya).
  - Panel di kanan tabel: informasi rekening, ringkasan PDF (**SALDO AWAL**, **TOTAL DEBIT**,
    **TOTAL KREDIT**, **SALDO AKHIR**, saldo di daftar aset, saldo Ekuivalen IDR), dan hasil cek.

Satu transaksi CIMB adalah satu sel tabel yang bisa terdiri dari beberapa baris, dengan tanggal dan
nominal di tengah sel. ExpCore mengelompokkan baris per sel memakai garis batas tabel, dan
menentukan kolom DEBIT/KREDIT/SALDO dari garis di bawah judul tabel yang judul kolomnya diverifikasi,
bukan dari urutan teks.

Setiap rekening dicek otomatis: jumlah debit dan kredit harus sama dengan baris **Total** PDF,
saldo awal + kredit − debit harus sama dengan saldo akhir, saldo berjalan harus sama dengan setiap
saldo yang tercetak, saldo akhir harus sama dengan saldo di daftar aset, dan jumlah halaman harus
lengkap. Per kategori, jumlah saldo Ekuivalen IDR harus sama dengan baris totalnya. Rekening di
daftar aset yang rinciannya tidak ditemukan tetap muncul dengan catatan. Bila ada selisih atau
teks yang tidak dikenali, **Hasil Cek** berisi **PERLU CEK** beserta alasannya, dan alasan yang sama
tampil di log aktivitas. Laporan dengan CIF dan tanggal laporan sama di lebih dari satu PDF (tanpa CIF
terbaca: daftar rekening dan tanggal sama) ditandai **PERLU CEK** di setiap salinannya, beserta lokasi
salinan lainnya; tidak ada PDF yang dibuang.

*Kode:* `process_rekening_cimb()`, `_extract_rekening_cimb()`, `_cimb_isi()`, `_cimb_mutasi()`, dan
`_write_cimb_excel()` di `ExpCore.py`.
*Diuji:* `test_rekening_cimb()` dan `read_cimb()` di `test_expcore.py` (laporan sintetis dari
`write_cimb()` di `tests/fixtures.py`); `test_pdf_samples()` untuk keenam laporan asli Jul–Des 2024.

---

## Pengujian

Parser, ekspor, penamaan (C.3/A.2), rekening koran BCA dan CIMB, dan protokol engine (PDF sintetis,
folder Unicode, PDF rusak):

```bash
./.venv/Scripts/python.exe test_expcore.py
```

Untuk menguji ulang PDF contoh lokal di `contoh-pdf/` (`BUPOT 2024`, `BUPOT 2026`,
`Rekening Giro`, `Rekening Tahapan`, `BANG CIMB`) tanpa mengubah PDF:

```bash
./.venv/Scripts/python.exe test_expcore.py --pdf-samples
```

Tes memeriksa kedua Bupot terbaca dan diberi nama dari kedua sumber (BPPU C.3/A.2, BPBS C.2/A.3), serta keenam e-Statement:
Giro 28/29/20 transaksi dan Tahapan 81/105/101 transaksi, semuanya **SESUAI** dengan
ringkasan PDF, dan saldo akhir setiap bulan sama dengan saldo awal bulan berikutnya. Untuk CIMB
Niaga Jul–Des 2024: 29/46/36/32/41/24 transaksi (208), semua rekening dan total kategori **SESUAI**,
serta saldo akhir setiap rekening sama dengan saldo awalnya di bulan berikutnya.
*Kode:* `test_pdf_samples()` di `test_expcore.py`.

Aplikasi Electron end-to-end (renderer dibangun otomatis lebih dulu; memakai engine dari `.venv`; dialog native di-stub, PDF yang
diproses adalah fixture sintetis di folder sementara):

```bash
bun run test
```

Ulangi pada pembesaran tampilan 125% dan 150%:

```bash
EXPCORE_SCALE=1.25 bun run test
```

```bash
EXPCORE_SCALE=1.5 bun run test
```

Setelah build, uji aplikasi hasil paket beserta engine Nuitka dan alur update (server
update lokal, tanpa GitHub):

```bash
EXPCORE_APP=dist/win-unpacked/ExpCore.exe bun run test
```

Di PowerShell, atur variabel lebih dulu, misalnya `$env:EXPCORE_SCALE = '1.5'; bun run test`.

Tes E2E membuka jendela aplikasi sungguhan; jangan memakai desktop (memaksimalkan,
memindahkan, atau menutupi jendela tes) selama tes berjalan. Tes yang gagal menyimpan
screenshot dan keadaan UI di `%TEMP%\expcore-e2e-artefak`.
*Kode:* pembantu E2E `setFolder()`, `runTo()`, `openTool()`, `setSize()`, dan `wheelOver()` di
`tests/app.test.js`; `manualCheck()` dan `latestYml()` di `tests/update.test.js`; `fake()` di
`tests/engine.test.js`.

---

## Build dan Distribusi

### Alur build

Sejak versi 3.0, build terdiri dari tiga bagian yang dibangun terpisah, lalu digabung
oleh electron-builder menjadi satu installer:

| Bagian | Sumber | Alat | Hasil |
| --- | --- | --- | --- |
| Antarmuka (renderer) | `app/renderer/src/` | Tailwind CLI + esbuild | `app/renderer/dist/` (CSS, JS, font) |
| Engine PDF | `expcore_engine.py` + `ExpCore.py` | Nuitka (standalone) | `expcore_engine.dist/expcore_engine.exe` |
| Aplikasi + installer | `app/`, `package.json`, engine | electron-builder (NSIS) | `dist/win-unpacked/` dan `dist/ExpCore-Setup-<versi>.exe` |

Perbedaan dengan 2.x: Nuitka tidak lagi mengompilasi seluruh aplikasi, hanya engine
Python. Jendela aplikasi kini Electron, dan Inno Setup diganti NSIS dari electron-builder,
yang sekaligus menghasilkan `latest.yml` untuk pembaruan otomatis.

Isi aplikasi hasil paket (sama dengan isi `C:\Program Files\ExpCore` setelah dipasang):

```text
dist/win-unpacked/
├── ExpCore.exe                 # Electron
└── resources/
    ├── app.asar                # app/ (tanpa renderer/src), package.json, electron-updater
    └── engine/
        └── expcore_engine.exe  # Engine Nuitka beserta Python, pdfplumber, pandas, openpyxl
```

Aplikasi memilih engine sesuai cara dijalankan:

- **`bun start` (pengembangan):** renderer dibangun, lalu Electron berjalan dari source dan
  memanggil `./.venv/Scripts/python.exe expcore_engine.py`. Nuitka tidak diperlukan.
- **Hasil paket / terpasang:** Electron memanggil `resources/engine/expcore_engine.exe`.

Build pertama memerlukan internet: Nuitka mengunduh compiler C (MinGW64) bila Visual Studio
tidak terpasang, dan electron-builder mengunduh NSIS. Keduanya disimpan di cache
`%LOCALAPPDATA%`, sehingga build berikutnya tidak mengunduh ulang. Semua hasil build
(`app/renderer/dist/`, `expcore_engine.build/`, `expcore_engine.dist/`, `dist/`) tidak
di-commit.

*Kode:* `build_engine()`, `check_engine()`, dan `build_app()` di `build_release.py`;
`engineCommand()` di `app/main.js`; konfigurasi paket di bagian `build` pada `package.json`.

### Build installer

> **Nuitka mem-bundle dari interpreter yang menjalankannya, bukan dari folder proyek.**
> Kalau Nuitka dijalankan oleh interpreter yang tidak punya dependency aplikasi, modul yang hilang
> **tidak** membuat build gagal — Nuitka hanya memberi peringatan lalu tetap menghasilkan
> <code>.exe</code> yang rusak. Karena itu build memakai path venv secara eksplisit.

**Langkah 1** — install Nuitka ke venv proyek dan dependency bun:

```bash
./.venv/Scripts/python.exe -m pip install Nuitka
```

```bash
bun ci
```

**Langkah 2** — build engine dan installer sekaligus:

```bash
./.venv/Scripts/python.exe build_release.py
```

Skrip ini berhenti pada kesalahan pertama, dengan urutan:

1. Memvalidasi `version` di `package.json`.
2. Memastikan pdfplumber, pandas, openpyxl, dan Nuitka dapat di-import oleh interpreter
   yang menjalankan skrip.
3. Mengompilasi `expcore_engine.py` dengan Nuitka ke `expcore_engine.dist/` (folder lama
   dihapus dulu). **Proses ini lama** — pandas dan numpy ikut dikompilasi.
4. Menjalankan engine hasil build pada PDF sintetis untuk keenam alat, termasuk pratinjau
   dan penerapan nama. Modul yang tidak ter-bundle membuat build berhenti di sini.
5. Membangun ulang renderer (`bun run build:renderer`) agar paket tidak memuat CSS/JS lama.
6. Menjalankan electron-builder: `app/` dikemas ke `app.asar` dan engine disalin ke
   `resources/engine/`.
7. Memeriksa hasil: `app.asar` memuat renderer hasil build tanpa `app/renderer/src/`;
   `ExpCore.exe`, engine, installer, dan `.blockmap` ada; `latest.yml` cocok dengan versi
   dan nama installer.

Setelah selesai, skrip mencetak tiga file yang harus diunggah ke GitHub Release.

Jika engine tidak berubah, lewati langkah 2–4 (memerlukan `expcore_engine.dist/` dari
build sebelumnya):

```bash
./.venv/Scripts/python.exe build_release.py --app-only
```

`bun run dist` hanya menjalankan electron-builder tanpa membangun renderer dan tanpa
pemeriksaan di atas. Untuk rilis, selalu gunakan `build_release.py`.

`version` di `package.json` adalah satu-satunya sumber nomor versi aplikasi, metadata
executable, dan installer. Gunakan format `MAJOR.MINOR.PATCH`, misalnya `3.0.0`.

### Installer

- Dipasang per mesin ke `C:\Program Files\ExpCore` (memerlukan izin administrator),
  dengan shortcut Start Menu dan desktop.
- **Pengguna ExpCore 2.x wajib melepas versi lama terlebih dahulu** melalui
  **Settings > Apps > ExpCore version 2.x > Uninstall**, baru menjalankan installer 3.x.
  Installer 3.x tidak melepas versi 2.x secara otomatis; tanpa langkah ini akan ada dua
  entri ExpCore, dan melepas versi lama setelahnya dapat merusak instalasi 3.x di folder
  yang sama. PDF dan hasil di folder pengguna tidak terpengaruh.
- Identitas installer dipatok di `build.nsis.guid` (`3d25c37a-f1b9-5b71-aaa6-3b5abfae652c`), yaitu kunci
  registry Uninstall ExpCore 3.x. **Jangan ubah GUID ini, dan jangan ubah `build.appId`** (walau berisi
  `1.0`, itu bukan versi; versi ada di `version`). GUID lain membuat installer baru terpasang berdampingan
  dengan versi lama, seperti kasus 2.x di atas. `appId` juga menjadi identitas taskbar (AppUserModelID)
  shortcut dan harus sama dengan `APP_ID` di `app/main.js`.
  *Diuji:* tes E2E "membuka jendela dengan identitas…" di `tests/app.test.js` memeriksa keduanya.
- Executable belum ditandatangani (code signing). Windows SmartScreen dapat menampilkan
  peringatan saat installer pertama kali dijalankan.

### Pembaruan otomatis

- Aplikasi terpasang memeriksa rilis stabil terbaru dari `iyansanjaya/ExpCore` setelah
  jendela terbuka. Pekerjaan PDF dan navigasi tetap berjalan.
- Jika ada versi baru, banner menyediakan **Unduh update** dan **Nanti**. Unduhan berjalan
  di latar dengan persentase progres, lalu diverifikasi dengan checksum SHA-512 dari
  `latest.yml`. Setelah selesai, **Pasang & mulai ulang** menutup aplikasi, memasang
  update (Windows meminta izin administrator), lalu membukanya kembali.
- Pemasangan ditahan selama proses PDF berjalan. Tidak ada unduhan atau pemasangan
  tanpa persetujuan pengguna.
- Gangguan jaringan saat pengecekan otomatis tidak memunculkan dialog. Tombol
  **Periksa update** menjelaskan hasilnya; aplikasi tetap dapat dipakai saat offline.
- Updater membaca rilis yang ditandai **Latest** di GitHub beserta `latest.yml`-nya. Bila belum
  ada rilis atau rilis Latest belum memuat `latest.yml` (mis. rilis 2.x), **Periksa update**
  menyatakan belum ada pembaruan yang siap dipasang.
- *Diuji:* `manualCheck()`, `waitBanner()`, `latestYml()`, dan `handle()` (server update lokal) di
  `tests/update.test.js`.
- Permintaan hanya membaca metadata dan file rilis publik melalui HTTPS; PDF, isi
  dokumen, nama file, dan folder pengguna tidak dikirim. Tidak ada token GitHub di aplikasi.

### Menerbitkan versi berikutnya

1. Ubah `version` di `package.json`, catat perubahannya di `CHANGELOG.md`, dan tulis catatan
   rilis di `.github/release-notes/v<versi>.md`. Lalu jalankan semua tes di atas.
2. Jalankan `build_release.py`, lalu uji hasil paket dengan `EXPCORE_APP=dist/win-unpacked/ExpCore.exe bun run test`.
3. Buat **draft release** GitHub dengan tag persis `v` + versi, misalnya `v3.0.0`, dan isi
   deskripsinya dari `.github/release-notes/v<versi>.md`.
4. Unggah ketiga file dari `dist/`: `ExpCore-Setup-<versi>.exe`, `ExpCore-Setup-<versi>.exe.blockmap`,
   dan `latest.yml`. Tanpa `latest.yml`, aplikasi tidak menawarkan update.
5. Publikasikan sebagai rilis stabil dan tandai **latest**.

Pengguna ExpCore 2.x mendapat pemberitahuan dari pemeriksa update di versi lama (nama
installer `ExpCore-Setup-<versi>.exe` tetap dikenali). Tulis di catatan rilis 3.0.0 bahwa
versi 2.x harus di-uninstall dulu (lihat [Installer](#installer)). Setelah 3.x terpasang,
pembaruan berikutnya berjalan otomatis.

---

## Pemecahan Masalah

### Pemrosesan gagal dengan pesan "Mesin pemroses …"

Log aktivitas menampilkan beberapa baris terakhir dari pesan kesalahan engine. Gunakan
**Salin log** untuk menyimpannya. Pada build sendiri, jalankan engine langsung untuk
melihat pesan lengkap:

```bash
./expcore_engine.dist/expcore_engine.exe bupot "D:/folder/pdf"
```

Pesan seperti <code>ModuleNotFoundError: No module named 'pdfplumber'</code> berarti dependency tidak
ikut ter-bundle. Penyebabnya hampir selalu Nuitka dijalankan oleh interpreter yang salah. Periksa
interpreter mana yang sebenarnya dipakai oleh perintah <code>python</code> di shell Anda —
<code>which python</code> di Git Bash, atau di PowerShell:

```powershell
(Get-Command python).Source
```

Kalau hasilnya bukan <code>.../ExpCore/.venv/Scripts/python.exe</code>, ulangi build memakai path venv
secara eksplisit seperti pada [Build installer](#build-installer).

### Membedakan masalah kode dan masalah build

Jalankan aplikasi langsung dari source. Kalau di sini jalan normal tetapi hasil build tidak,
masalahnya ada di proses build, bukan di kode:

```bash
bun start
```

---

## Struktur Utama

```text
ExpCore/
├── app/
│   ├── main.js            # Proses main: jendela, dialog, IPC, status pekerjaan, update
│   ├── preload.js         # Jembatan aman renderer -> main (window.expcore)
│   ├── engine.js          # Menjalankan engine Python dan membaca protokol JSON
│   └── renderer/
│       ├── index.html     # Markup halaman dan template (kelas Tailwind)
│       ├── src/           # styles.css (tema Tailwind) dan app.js (logika, Motion, Reicon)
│       └── dist/          # Hasil build renderer (tidak di-commit)
├── ExpCore.py             # Parser PDF dan ekspor data
├── expcore_engine.py      # CLI engine: satu pekerjaan per proses
├── build_release.py       # Build engine (Nuitka) + installer (electron-builder)
├── package.json           # Versi, dependency, dan konfigurasi installer
├── tests/
│   ├── fixtures.py        # PDF sintetis untuk tes
│   ├── engine.test.js     # Kontrak runner engine
│   ├── app.test.js        # E2E aplikasi Electron
│   └── update.test.js     # Alur update pada aplikasi hasil paket
├── test_expcore.py        # Parser, penamaan, ekspor, dan protokol engine
├── DESIGN.md              # Token visual, interaksi, dan arsitektur
├── CHANGELOG.md           # Riwayat perubahan per versi
├── .github/release-notes/ # Catatan rilis GitHub per versi
├── graphify-out/          # Graph pengetahuan proyek (graph.html, GRAPH_REPORT.md)
├── icon.ico               # Ikon aplikasi, engine, dan installer (16–256 px)
├── icon.svg               # Sumber desain ikon (sama dengan logo di header)
├── LICENSE.txt
└── README.md
```

---

## Catatan

- Parser dirancang untuk PDF resmi DJP: formulir **BPPU** dari Coretax (modul 2026)
  dan formulir **BPBS** pra-Coretax (modul 2024). Keduanya punya parser terpisah.
- PDF terproteksi, rusak, hasil scan tanpa lapisan teks, atau memiliki layout berbeda dapat gagal diproses.
- Modul Pajak Masukan menghitung PPN menggunakan tarif tetap **12%**.
- Modul Rekening Koran BCA membaca layout e-Statement BCA (kolom <code>TANGGAL</code>,
  <code>KETERANGAN</code>, <code>CBG</code>, <code>MUTASI</code>, <code>SALDO</code>). Kolom dikenali
  dari posisinya di halaman, sehingga kode cabang dan angka di dalam keterangan tidak tertukar
  dengan nominal mutasi. Rekening koran bank lain atau berformat lain dilewati dan dicatat di log.
- Modul Rekening Koran CIMB membaca layout Combine Statement Portfolio CIMB Niaga yang tabelnya
  bergaris (sel per transaksi). Laporan dengan judul kolom atau garis tabel yang berbeda tidak
  ditebak: rekeningnya ditandai **PERLU CEK** beserta alasannya. Nominal valas (mis. USD) ditulis
  dalam mata uang asalnya; gunakan kolom **Mata Uang** atau **Saldo Ekuivalen IDR** sebelum
  menjumlahkan lintas rekening.
- Keterangan rekening koran yang di PDF terpotong antarbaris (mis. <code>ABDULLA</code> /
  <code>H</code>) digabung dengan spasi persis seperti di PDF. ExpCore tidak menebak
  penyambungan kata karena tidak dapat membedakan kata yang terpotong dari kolom yang terpisah.
- Pada modul Bukti Potong 2024, kolom **Sifat** dibaca dari tanda centang <code>X</code> pada
  <code>H.4</code>/<code>H.5</code>. Bila tidak tepat satu kotak yang tercentang, kolom ini
  berisi <code>-</code> daripada menebak. Kolom **NIK** kosong (<code>-</code>) bila field
  <code>A.2</code> pada formulir memang tidak diisi.
- Tarif pada formulir BPBS dapat ditulis sebagai bilangan bulat (`2`) maupun desimal (`2.00` atau `2,00`); ketiganya dibaca sebagai tarif 2%.
- File Excel dengan nama yang sama diganti setelah pengguna mengonfirmasi.
- Jalur folder dapat ditempel langsung dari **Copy as path** di Explorer, termasuk tanda kutipnya.
- Gunakan **Pratinjau nama** sebelum menerapkan perubahan nama PDF.

---

## Lisensi

Dilisensikan di bawah **Apache License 2.0**. Lihat [LICENSE.txt](LICENSE.txt).

Copyright © 2026 Iyan Sanjaya.
