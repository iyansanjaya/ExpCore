# Changelog

Semua perubahan penting pada ExpCore dicatat di berkas ini.

Format mengikuti [Keep a Changelog](https://keepachangelog.com/id-ID/1.1.0/). Sejak 3.0.0,
penomoran versi mengikuti [Semantic Versioning](https://semver.org/lang/id/) dengan
`version` di `package.json` sebagai satu-satunya sumber. Versi 1.x memakai penomoran lama
(`1.1`, `1.2`, …).

## [3.0.0] - 2026-10-09

Versi besar pertama berbasis Electron: aplikasi desktop baru, alat Rekening Koran BCA,
pilihan sumber nama pada Penamaan Bupot, dan pembaruan otomatis dari GitHub Releases.

### Penting untuk pengguna 2.x

- **Lepas ExpCore 2.x terlebih dahulu** melalui **Settings > Apps > ExpCore version 2.x >
  Uninstall**, baru jalankan installer 3.0.0. Installer 3.x tidak melepas versi 2.x secara
  otomatis; tanpa langkah ini akan ada dua entri ExpCore, dan melepas versi lama setelahnya
  dapat merusak instalasi 3.x. PDF dan hasil di folder pengguna tidak terpengaruh.

### Ditambahkan

- **Rekening Koran (BCA)**: merekap e-Statement BCA Rekening Giro dan Rekening Tahapan ke
  `!Hasil_Rekap_Rekening_Koran.xlsx`.
  - Sheet **Ringkasan** (satu baris per PDF, nama sheet dapat diklik) dan satu sheet per PDF
    dengan kolom TANGGAL, KETERANGAN, CBG, DEBIT, CREDIT, dan SALDO.
  - Mutasi bertanda `DB` masuk DEBIT, selainnya CREDIT. Kode cabang dipisah ke kolom CBG,
    dan tanggal ditulis lengkap dengan tahun dari periode rekening.
  - Ringkasan PDF (SALDO AWAL, MUTASI CR + jumlah, MUTASI DB + jumlah, SALDO AKHIR) ditulis di
    panel terpisah, sehingga `SUM` dan filter kolom DEBIT/CREDIT hanya menghitung transaksi.
  - Cek otomatis per PDF: total dan jumlah transaksi terhadap ringkasan PDF, saldo berjalan
    terhadap setiap saldo yang tercetak, dan kelengkapan halaman. Hasilnya **SESUAI** atau
    **PERLU CEK** beserta alasannya; periode yang muncul di lebih dari satu PDF diberi
    peringatan.
- **Penamaan Bupot**: pilihan **Ambil nama file dari**, yaitu **Identitas Pemotong (C.3)**
  (bawaan) atau **Wajib Pajak yang Dipotong (A.2)**. Bila nama pada sumber terpilih kosong,
  PDF dilewati tanpa memakai nama dari sumber lain. Log CSV mencatat `sumber_nama`.
- **Pembaruan otomatis** dari GitHub Releases: banner versi baru, unduhan dengan progres,
  verifikasi SHA-512, lalu **Pasang & mulai ulang**. Pemasangan ditahan selama ada proses PDF,
  dan gangguan jaringan saat pengecekan otomatis tidak memunculkan dialog.
- Menu **Alat** berkelompok (**Ekstraksi ke Excel** dan **Kelola PDF**) yang menampilkan alat
  aktif dan status proses, serta dapat dipakai dengan keyboard.
- Pintasan keyboard: `Alt+0` (beranda), `Alt+1`–`Alt+5` (alat), `Ctrl+O` (pilih folder),
  `Page Up`/`Page Down`, dan panah/`Enter`/`Esc` di menu Alat.
- Dukungan pengaturan Windows "kurangi animasi": konten langsung tampil tanpa gerakan.
- Ikon aplikasi baru, sama dengan logo di header (`icon.svg` sebagai sumber desain).

### Diubah

- Antarmuka ditulis ulang dengan Electron, menggantikan CustomTkinter: tampilan terang
  bernuansa ungu (Tailwind CSS v4), animasi halus (Motion), ikon Reicon, dan font Inter yang
  dibundel lokal sehingga tetap bekerja offline.
- Pemrosesan PDF berjalan di proses engine terpisah. Navigasi tetap responsif, hanya satu
  pekerjaan berjalan sekaligus, dan aplikasi tidak dapat ditutup sebelum hasil serta log
  selesai ditulis.
- Installer beralih dari Inno Setup ke NSIS (electron-builder). Aplikasi dipasang per mesin ke
  `C:\Program Files\ExpCore` dengan shortcut Start Menu dan desktop.
- Urutan alat: Bukti Potong 2026, Bukti Potong 2024, Pajak Masukan, Rekening Koran,
  Penamaan Bupot.
- Nomor versi aplikasi, executable, dan installer kini hanya berasal dari `package.json`.
- Pengembangan memakai Bun sebagai pengelola paket (`bun.lock`).

### Dihapus

- Antarmuka CustomTkinter (`expcore_ui.py`) dan pemeriksa update lama (`expcore_updates.py`).
- Skrip installer Inno Setup (`ExpCore.iss`) dan berkas `VERSION`.

### Keamanan

- Renderer berjalan dalam sandbox dengan `contextIsolation`, tanpa akses Node, dan dibatasi
  Content-Security-Policy ketat (tanpa inline script/style dan tanpa `eval`).
- Navigasi keluar, jendela baru, webview, dan izin perangkat ditolak; pengirim IPC divalidasi;
  DevTools tidak tersedia pada aplikasi terpasang.
- Pembaruan hanya membaca metadata dan berkas rilis publik melalui HTTPS. Tidak ada token di
  aplikasi, dan PDF, isi dokumen, nama file, serta folder pengguna tidak dikirim.

## [2.0.1] - 2026-09-10

### Diperbaiki

- **Buka hasil** pada Penamaan Bupot membuka folder PDF (bukan berkas log) setelah pratinjau
  maupun penerapan nama.

## [2.0.0] - 2026-09-10

### Ditambahkan

- Antarmuka desktop baru dengan CustomTkinter.
- Pemeriksa pembaruan yang membaca rilis GitHub.
- Skrip build rilis (`build_release.py`) dan dokumen desain (`DESIGN.md`).
- Berkas `VERSION` sebagai sumber nomor versi UI dan installer.

### Diubah

- Logika parser dan ekspor di `ExpCore.py` dipisahkan dari antarmuka.
- Penamaan Bupot memakai nama pemotong (C.3).

## [1.5] - 2026-09-02

### Diubah

- Penamaan Bupot memakai nama wajib pajak penerima (A.2).

### Diperbaiki

- Tarif BPBS yang ditulis sebagai bilangan bulat (mis. `2`) kini terbaca, selain `2.00` dan
  `2,00`.

## [1.4] - 2026-08-28

### Ditambahkan

- Modul **Bukti Potong 2024** untuk formulir BPBS (pra-Coretax).

### Diubah

- Format ekspor Excel diseragamkan untuk semua modul: header, format angka dan teks, serta
  lebar kolom otomatis.

## [1.3] - 2026-08-21

### Diperbaiki

- Nama pemotong tidak lagi ikut memuat sisa label "PPh" saat label terpotong baris.

## [1.2] - 2026-07-07

### Ditambahkan

- Modul **Penamaan Otomatis Bupot** dengan pratinjau dan penerapan.
- Pemindaian subfolder dan kolom **Folder Sumber** pada hasil ekstraksi.

## [1.1.1] - 2026-06-10

### Diubah

- Nama berkas hasil Excel diawali `!` agar berada di urutan teratas folder.

## [1.1] - 2026-06-10

### Ditambahkan

- Ikon resolusi tinggi dan pengelompokan taskbar Windows.

### Diubah

- Tampilan bertema gelap.
- Lisensi menjadi Apache License 2.0.

## 1.0 - 2026-06-10

### Ditambahkan

- Rilis awal: ekstraksi PDF Bukti Potong dan Pajak Masukan dari Coretax ke Excel.

[3.0.0]: https://github.com/iyansanjaya/ExpCore/compare/v2.0.1...v3.0.0
[2.0.1]: https://github.com/iyansanjaya/ExpCore/compare/v2.0.0...v2.0.1
[2.0.0]: https://github.com/iyansanjaya/ExpCore/compare/v1.5...v2.0.0
[1.5]: https://github.com/iyansanjaya/ExpCore/compare/e2fe140...v1.5
[1.4]: https://github.com/iyansanjaya/ExpCore/compare/v1.3...e2fe140
[1.3]: https://github.com/iyansanjaya/ExpCore/compare/v1.2...v1.3
[1.2]: https://github.com/iyansanjaya/ExpCore/compare/v1.1.1...v1.2
[1.1.1]: https://github.com/iyansanjaya/ExpCore/compare/v1.1...v1.1.1
[1.1]: https://github.com/iyansanjaya/ExpCore/releases/tag/v1.1
