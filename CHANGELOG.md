# Changelog

Semua perubahan penting pada ExpCore dicatat di berkas ini.

Format mengikuti [Keep a Changelog](https://keepachangelog.com/id-ID/1.1.0/). Sejak 3.0.0,
penomoran versi mengikuti [Semantic Versioning](https://semver.org/lang/id/) dengan
`version` di `package.json` sebagai satu-satunya sumber. Versi 1.x memakai penomoran lama
(`1.1`, `1.2`, …).

## [3.1.0] - 2026-10-12

Alat baru Rekening Koran CIMB Niaga, Penamaan Bupot untuk Bupot 2024 (BPBS), dan penandaan
rekening koran ganda. Pengguna 3.0.0 menerima versi ini lewat pembaruan otomatis.

### Ditambahkan

- **Rekening Koran CIMB**: merekap Combine Statement Portfolio (Laporan Konsolidasi) CIMB Niaga
  ke `!Hasil_Rekap_Rekening_CIMB.xlsx`.
  - Semua transaksi rekening **Tabungan/Giro** dan **Tabungan Berjangka** yang tercantum di
    RINCIAN ASET, termasuk rekening valas, beserta total kedua kategori (Ekuivalen IDR). Bagian
    dikenali dari judul dan isinya, bukan dari nomor halaman; deposito, MLD, kartu kredit, dan
    Poin Xtra diabaikan.
  - Sheet **Ringkasan** (per rekening, nama sheet dapat diklik), **Total Kategori** (per laporan),
    **Semua Transaksi** (transaksi seluruh rekening dalam satu tabel, kronologis per rekening),
    dan satu sheet per rekening per laporan dengan kolom TANGGAL TRANSAKSI, TANGGAL VALUTA,
    URAIAN TRANSAKSI, NO CEK/BG, DEBIT, KREDIT, dan SALDO; ringkasan PDF di panel kanan.
  - Uraian yang tertulis beberapa baris tetap satu transaksi: baris dikelompokkan per sel memakai
    garis batas tabel, dan kolom ditentukan dari garis di bawah judul tabel yang diverifikasi.
  - Cek otomatis per rekening: debit/kredit terhadap baris Total, saldo berjalan, saldo akhir
    terhadap daftar aset, dan kelengkapan halaman; per kategori: jumlah saldo Ekuivalen IDR
    terhadap baris totalnya. Hasilnya **SESUAI** atau **PERLU CEK** beserta alasannya.
- **Penamaan Bupot** kini membaca **Bupot 2026 (BPPU)** dan **Bupot 2024 (BPBS)** dalam satu
  folder; jenis formulir dikenali otomatis per PDF. Pada BPBS, nama diambil dari C.2/A.3, nomor
  dari H.1, masa dari B.1, sifat dari centang H.4/H.5, dan status dari H.2/H.3; PDF dengan data
  ambigu dilewati, tidak ditebak. Log CSV mencatat kode bagian sumber nama dan kolom `FORMULIR`,
  dan log aktivitas menandai setiap PDF dengan `[BPPU]` atau `[BPBS]`.

### Diubah

- **Rekening koran ganda ditandai di Excel**: rekening dan periode yang sama di lebih dari satu
  PDF (BCA maupun CIMB) kini ditandai **PERLU CEK** di setiap salinannya, beserta lokasi salinan
  lain, agar transaksinya tidak terhitung ganda tanpa terlihat. Sebelumnya hanya ada peringatan di
  log. Tidak ada PDF yang dibuang.
- Alat Rekening Koran berganti nama menjadi **Rekening Koran BCA**.
- Pilihan sumber nama Penamaan Bupot berlaku untuk kedua formulir: **Identitas Pemotong**
  (BPPU C.3, BPBS C.2) atau **Wajib Pajak yang Dipotong** (BPPU A.2, BPBS A.3).
- Urutan alat: Bukti Potong 2026, Bukti Potong 2024, Pajak Masukan, Rekening Koran BCA,
  Rekening Koran CIMB, Penamaan Bupot. Pintasan `Alt+1`–`Alt+6` mengikuti urutan ini
  (Penamaan Bupot kini `Alt+6`).
- Identitas installer (GUID) dipatok sama dengan 3.0.0, sehingga pembaruan selalu memasang di
  tempat yang sama, tidak berdampingan.

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

[3.1.0]: https://github.com/iyansanjaya/ExpCore/compare/v3.0.0...v3.1.0
[3.0.0]: https://github.com/iyansanjaya/ExpCore/compare/v2.0.1...v3.0.0
[2.0.1]: https://github.com/iyansanjaya/ExpCore/compare/v2.0.0...v2.0.1
[2.0.0]: https://github.com/iyansanjaya/ExpCore/compare/v1.5...v2.0.0
[1.5]: https://github.com/iyansanjaya/ExpCore/compare/e2fe140...v1.5
[1.4]: https://github.com/iyansanjaya/ExpCore/compare/v1.3...e2fe140
[1.3]: https://github.com/iyansanjaya/ExpCore/compare/v1.2...v1.3
[1.2]: https://github.com/iyansanjaya/ExpCore/compare/v1.1.1...v1.2
[1.1.1]: https://github.com/iyansanjaya/ExpCore/compare/v1.1...v1.1.1
[1.1]: https://github.com/iyansanjaya/ExpCore/releases/tag/v1.1
