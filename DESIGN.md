# ExpCore — Desktop workspace

Bahasa visual SaaS modern yang terang dan lembut: kanvas putih kebiruan, aksen ungu,
panel lavender, kartu putih membulat dengan bayangan halus, dan tipografi Inter yang
tenang. Gerakan (Motion) dipakai secukupnya agar antarmuka terasa hidup tanpa
mengganggu pekerjaan dokumen.

Setiap konsep di bawah memuat rujukan *Kode:* ke fungsi dan berkas yang menjalankannya.

## Token visual

Semua token didefinisikan sekali di blok `@theme` pada `app/renderer/src/styles.css`
dan dipakai sebagai kelas Tailwind (`bg-brand-600`, `text-ink-soft`, `shadow-card`, …).

| Peran | Token | Nilai |
| --- | --- | --- |
| Aksen utama, tombol utama | `brand-600` | `#6d5bf7` |
| Teks di atas lavender | `brand-700` | `#5944e0` |
| Panel lavender, badge | `lavender` / `brand-50` | `#f4f2ff` / `#f5f3ff` |
| Teks utama, tombol gelap | `ink` | `#12122b` |
| Teks pendukung | `ink-soft` | `#4b4f6b` |
| Metadata (hanya di atas putih) | `ink-muted` | `#6b6f8a` |
| Garis pemisah | `line` | `#ebeaf3` |
| Kanvas | `canvas` | `#fbfbfe` |
| Footer | `navy` | `#0e0d2b` |
| Font | `font-sans` | Inter Variable (dibundel lokal), cadangan Segoe UI |
| Judul beranda | | 40 px (< 1100 px), 50 px; medium, tracking rapat |
| Judul alat | | 34 px medium |
| Radius kartu / kontrol | | 24 px / 12 px; tombol pill pada navigasi |

Kontras: `ink-soft` 8:1 dan `ink-muted` 4,9:1 di atas putih; teks putih di atas
`brand-600` 4,7:1; teks status memakai warna -700/-800 di atas latar -50. Status
selalu berupa teks (MENUNGGU FOLDER, SIAP DIPROSES, MEMPROSES, SELESAI, TIDAK ADA
HASIL, PERLU DIPERIKSA), sehingga warna bukan satu-satunya pembeda.
*Kode:* `setStatus()` di `app/renderer/src/app.js`.

Ikon berasal dari [Reicon](https://reicon.dev) (varian Outline/Filled). Placeholder
`<span data-icon="Nama">` diganti SVG saat dimuat; semua ikon dekoratif memakai
`aria-hidden` dan warnanya mengikuti `currentColor`. *Kode:* `hydrateIcons()` di
`app/renderer/src/app.js`.

Ikon aplikasi (jendela, taskbar, shortcut, installer, engine) sama dengan logo header: tile
gradien `brand-500` → `brand-700` bersudut 30% dengan glyph Reicon `DocumentText` (Filled) putih.
`icon.svg` adalah sumber desainnya; `icon.ico` berisi 15 ukuran (16–256 px, BMP 32-bit beralfa)
yang masing-masing digambar langsung pada ukurannya. Pada 32 px ke bawah glyph diperbesar
(66% tile) agar tetap terbaca di judul jendela dan taskbar.
*Kode:* `icon.svg` dan `icon.ico` di akar proyek; dipakai `createWindow()` di `app/main.js` (mode
pengembangan), `build_engine()` di `build_release.py` (engine Nuitka), dan `win.icon` di `package.json`.

## Struktur dan interaksi

- **Header** tetap di atas: logo, navigasi pill berisi **Beranda** dan tombol **Alat**
  dengan indikator ungu yang meluncur (spring Motion), tombol **Periksa update**, dan badge
  **Lokal & privat** (label selalu tampil, juga di lebar minimum 960 px). Navigasi rata kiri
  di samping logo, bukan di tengah: nama alat aktif memanjangkan tombol Alat ke kanan tanpa
  menggeser Beranda. Pill memotong (`overflow-hidden`) indikator yang sedang meluncur, dan
  pegas indikator dimulai dengan kecepatan 0.
  *Kode:* `moveIndicator()` dan `navigate()` di `app/renderer/src/app.js`.
  *Diuji:* tes "navigasi lewat menu Alat, kartu beranda, dan Alt+0..5" (lebar indikator diukur
  tiap frame) dan "tata letak responsif tanpa overflow…", memakai `openTool()` dan `setSize()` di `tests/app.test.js`.
- **Menu Alat** (pola disclosure: tombol `aria-expanded` + daftar tombol, bukan `role="menu"`):
  panel putih 360 px di bawah navigasi (rata kiri dengan pill), dikelompokkan **Ekstraksi ke Excel** dan **Kelola PDF**.
  Setiap baris berisi ikon Reicon dalam kotak lavender, judul, keterangan singkat, dan
  shortcut; alat aktif berlatar lavender, ikon ungu penuh, dan centang. Ikon: `ReceiptText`
  (Bupot 2026), `Receipt` (Bupot 2024), `Invoice` (Pajak Masukan), `Bank` (Rekening Koran),
  `Edit2` (Penamaan Bupot), `Category` dan `ChevronDown` untuk tombolnya.
  - Di halaman alat, tombol menampilkan **Alat · nama alat** dan berada di bawah pill
    indikator; di beranda tombol yang terbuka berlatar `brand-50`.
  - Titik berdenyut muncul di tombol Alat dan di baris alat yang sedang memproses
    (`aria-busy`), sehingga status tetap terlihat walau menu tertutup.
  - Membuka dengan klik tidak memindahkan fokus; `Enter`/`Space` atau panah bawah memfokuskan
    alat aktif (atau alat pertama), panah atas memfokuskan alat terakhir. Panah, `Home`,
    dan `End` berpindah antaralat. `Esc` menutup dan mengembalikan fokus ke tombol; klik di
    luar atau `Tab` keluar juga menutup. Memilih alat memindahkan fokus ke judul halaman.
  - Panel muncul dengan fade + geser 6 px (180 ms, Motion), tanpa animasi pada mode gerak
    dikurangi; chevron berputar 180°.
  *Kode:* `openMenu()`, `closeMenu()`, `setupMenu()`, `buildMenuItem()`, dan `setBusyNav()` di
  `app/renderer/src/app.js`; `group`, `icon`, dan `brief` per alat di `MODULES` (`app/main.js`);
  `.menu-item` di `app/renderer/src/styles.css`.
  *Diuji:* tes "menu Alat: grup, klik di luar, Esc, panah, Enter, Tab keluar…" memakai `focused()` dan
  `setSize()` di `tests/app.test.js`.
- **Beranda** bergaya landing page: hero dengan kartu PDF → XLSX → CSV yang melayang,
  chip fitur, kartu bento kelima alat (kartu terakhir yang sendirian di barisnya melebar
  dua kolom dengan pratinjau di kanan), panel lavender "Kenapa ExpCore?", banner
  ajakan ungu, dan footer navy. Elemen muncul bertahap (stagger) saat masuk pandangan.
  *Kode:* `revealHero()` dan `revealSectionsInView()` di `app/renderer/src/app.js`.
  *Diuji:* tes "animasi beranda: hero bergerak, setiap bagian muncul penuh saat digulir" memakai
  `waitFor()` di `tests/app.test.js`.
- **Halaman alat**: kepala halaman (badge, judul, kartu nama hasil), kartu 01 sumber
  dokumen, kartu 02 aktivitas & hasil, dan bilah aksi yang menetap di bawah. Setiap
  alat menyimpan folder, aktivitas, dan hasilnya sendiri selama sesi.
  *Kode:* `buildTool()` di `app/renderer/src/app.js`.
  *Diuji:* tes "ekstraksi …: PDF -> Excel, ringkasan, log, dan Buka hasil" untuk keempat ekstraksi,
  memakai `setFolder()`, `runTo()`, dan `fixtures()` di `tests/app.test.js`.
- **Penamaan Bupot** menambahkan pilihan **Ambil nama file dari** di kartu 01: dua kartu
  radio, **Identitas Pemotong** (C.3, bawaan) dan **Wajib Pajak yang Dipotong** (A.2).
  Input radio asli tetap menerima fokus dan tombol panah; kartu terpilih bergaris ungu.
  Mengganti sumber membatalkan pratinjau. Proses main hanya menerima penerapan untuk
  folder dan sumber nama yang sama dengan pratinjau terakhir. *Kode:* `buildNameSources()`
  dan `nameSourceChanged()` di `app/renderer/src/app.js`; `startJob()` di `app/main.js`;
  `.source-option` di `app/renderer/src/styles.css`.
  *Diuji:* `test_rename_pemotong()` di `test_expcore.py`; tes E2E "penamaan: sumber nama C.3 atau A.2,
  pratinjau terikat pada sumbernya" memakai `setFolder()`, `runTo()`, dan `stubMain()` di `tests/app.test.js`.
- Field folder 48 px dengan ikon; jalur dapat diketik, ditempel dari "Copy as path"
  Explorer (bertanda kutip), atau dipilih lewat dialog native. *Kode:* `browse()` dan
  `folderChanged()` di `app/renderer/src/app.js`; `cleanFolder()` dan `registerIpc()`
  di `app/main.js`.
  *Diuji:* tes "isian folder mengatur label, status, dan tombol" (memakai `status()`), "folder yang
  tidak ada ditolak sebelum engine berjalan" (memakai `setFolder()` dan `stubMain()`), dan "salin log,
  Ctrl+O…" (memakai `fixtures()` dan `stubMain()`) di `tests/app.test.js`.
- Pill status berganti warna per keadaan dengan animasi pop; progres memakai bar
  gradien (determinan) atau kilau berjalan (indeterminan). *Kode:* `setStatus()` dan
  `setProgress()` di `app/renderer/src/app.js`.
  *Diuji:* `status()` dan `runTo()` di `tests/app.test.js`.
- Log panjang digulir mandiri dan mengisi sisa tinggi kartu aktivitas (minimal 130 px).
  Di tepi log, roda mouse diteruskan ke halaman secara eksplisit karena scroll chaining
  bawaan tidak konsisten pada DPI pecahan. *Kode:* `scrollLogToEnd()` dan listener roda
  mouse di `buildTool()`, keduanya di `app/renderer/src/app.js`.
  *Diuji:* tes "roda mouse: kartu menggulir halaman, log panjang menggulir sendiri, ujung log
  meneruskan" memakai `wheelOver()`, `wheelPoint()`, dan `logBaseline()` di `tests/app.test.js`.
- Kontrol folder dan pemrosesan dikunci selama satu pekerjaan berjalan; navigasi tetap
  aktif, dan item menu alat yang sibuk ditandai titik berdenyut (`aria-busy`). Proses
  main Electron adalah sumber kebenaran status pekerjaan. *Kode:* `startJob()`,
  `installUpdate()`, dan `createWindow()` di `app/main.js`; `refreshControls()` dan
  `setBusyNav()` di `app/renderer/src/app.js`.
  *Diuji:* tes "selama memproses: kontrol terkunci, navigasi bebas, satu pekerjaan, jendela tidak
  ditutup" memakai `fixtures()` dan `calls()` di `tests/app.test.js`; tes "pemasangan ditahan selama pekerjaan
  berjalan…" memakai `dialogs()` di `tests/update.test.js`.
- Hasil selesai ditampilkan inline, dengan tombol membuka Excel/CSV dan salin log.
  Folder yang berubah membatalkan tautan hasil dan status pratinjau lama. *Kode:*
  `openOutput()` di `app/main.js`; `onJobEvent()` dan `folderChanged()` di
  `app/renderer/src/app.js`.
  *Diuji:* tes "ekstraksi …: PDF -> Excel, ringkasan, log, dan Buka hasil" memakai `runTo()` dan
  `calls()` di `tests/app.test.js`.
- Penamaan memerlukan pratinjau selesai sebelum tombol penerapan aktif; proses main
  juga menolak penerapan untuk folder tanpa pratinjau. *Kode:* `startJob()` di
  `app/main.js`; `refreshControls()` di `app/renderer/src/app.js`.
  *Diuji:* tes "penamaan: pratinjau wajib, konfirmasi, penerapan, dan reset saat folder berubah"
  memakai `runTo()` dan `stubMain()` di `tests/app.test.js`; `test_engine_protocol()` di `test_expcore.py`.
- Mengganti rekap atau menerapkan nama memerlukan konfirmasi native dengan tombol
  bernama aksi dan **Batal** sebagai pilihan bawaan. Menutup aplikasi atau memasang
  update saat proses berjalan ditahan sampai hasil dan log selesai ditulis. *Kode:*
  `confirm()`, `startJob()`, dan `installUpdate()` di `app/main.js`.
  *Diuji:* tes "rekap lama hanya diganti setelah konfirmasi" memakai `stubMain()` dan `calls()` di
  `tests/app.test.js`.
- Banner update muncul dengan animasi pegas di bawah header dan tidak menutupi konten.
  *Kode:* `showUpdate()` dan `onUpdateEvent()` di `app/renderer/src/app.js`;
  `checkForUpdate()` di `app/main.js`.
  *Diuji:* `waitBanner()`, `bannerText()`, `manualCheck()`, `latestYml()`, dan `handle()` (server
  update lokal) di `tests/update.test.js`.
- Ukuran awal menyesuaikan layar dan DPI. Ukuran minimum: 960 × 620 logical px.
  *Kode:* `createWindow()` di `app/main.js`.
  *Diuji:* tes "membuka jendela dengan identitas, lima halaman, dan tanpa error" dan `setSize()` di
  `tests/app.test.js`.

## Gerak

Motion for JavaScript (`motion`, padanan vanilla Framer Motion) dipakai untuk: masuk
bertahap beranda dan halaman alat, kartu hero yang melayang, indikator navigasi,
pill status, dan banner update. Transisi hover/fokus memakai transisi CSS Tailwind.
*Kode:* `reveal()`, `revealHero()`, `moveIndicator()`, `setStatus()`, dan `showUpdate()`
di `app/renderer/src/app.js`.

Saat Windows mengaktifkan pengurangan gerak (`prefers-reduced-motion`), semua animasi
Motion dan animasi CSS dimatikan; konten langsung tampil penuh. Keadaan awal animasi
masuk beranda diatur di CSS agar tidak ada kedipan sebelum skrip berjalan. *Kode:*
konstanta `reduceMotion` yang diperiksa `reveal()` di `app/renderer/src/app.js`, dan
media query di `app/renderer/src/styles.css`.
*Diuji:* tes "gerak dikurangi: konten langsung tampil tanpa animasi" di `tests/app.test.js`.

## Keyboard

| Tombol | Tindakan |
| --- | --- |
| `Tab` / `Shift+Tab` | Pindah fokus kontrol; fokus ditandai cincin ungu |
| `Enter` / `Space` pada tombol | Aktifkan tombol |
| `Ctrl+O` | Pilih folder pada alat aktif |
| `Alt+0` | Beranda |
| `Alt+1`–`Alt+5` | Alat sesuai urutan menu Alat |
| `↓` / `↑` pada tombol Alat | Buka menu di alat aktif / alat terakhir |
| `↓` `↑` `Home` `End` di menu Alat | Pindah antaralat; `Enter` membuka, `Esc` menutup |
| `←` / `→` pada sumber nama | Ganti sumber nama Penamaan Bupot (radio asli) |
| `Page Up` / `Page Down` | Gulir halaman saat fokus berada di luar isian teks dan log |

*Kode:* `onKeyDown()` di `app/renderer/src/app.js`.
*Diuji:* tes "salin log, Ctrl+O, Page Down, dan aktivasi tombol lewat keyboard" (memakai `stubMain()`
dan `setSize()`) dan "menu Alat…" (memakai `focused()`) di `tests/app.test.js`.

## Arsitektur

| Bagian | Berkas | Tanggung jawab |
| --- | --- | --- |
| Renderer | `app/renderer/index.html`, `app/renderer/src/` | Tailwind + Motion + Reicon, dibundel ke `app/renderer/dist/`; tanpa akses Node (sandbox, `contextIsolation`) |
| Preload | `app/preload.js` | Satu-satunya jembatan: API `window.expcore` |
| Main | `app/main.js` | Jendela, dialog native, validasi IPC, status pekerjaan, update |
| Runner | `app/engine.js` | Menjalankan engine dan membaca protokol JSON per baris |
| Engine | `expcore_engine.py` → `ExpCore.py` | Parser PDF dan ekspor Excel/CSV, satu proses per pekerjaan |

*Kode:* `createWindow()` (sandbox, `contextIsolation`), `registerIpc()`, `handle()`, dan
`startJob()` di `app/main.js`; `runEngine()` di `app/engine.js`; API `window.expcore` di
`app/preload.js`; `main()` di `expcore_engine.py`; kelas `ExpCore` di `ExpCore.py`.
*Diuji:* `fake()` di `tests/engine.test.js` (kontrak runner); `test_engine_protocol()` dan
`run_engine()` di `test_expcore.py` (protokol engine).

`npm run build:renderer` menjalankan Tailwind CLI (`src/styles.css` → `dist/styles.css`)
dan esbuild (`src/app.js` → `dist/app.js`, beserta font Inter). `npm start`, `npm test`,
dan `build_release.py` menjalankannya otomatis; sumber `src/` tidak ikut dipaketkan.
*Kode:* skrip `build:renderer` di `package.json`; `build_app()` di `build_release.py`.

Renderer hanya memuat berkas lokal dengan Content-Security-Policy ketat (tanpa inline
script/style dan tanpa `eval`). Navigasi, jendela baru, webview, dan izin perangkat
ditolak. Menu bawaan dan DevTools tidak tersedia pada aplikasi terpasang. *Kode:* meta
CSP di `app/renderer/index.html`; handler `web-contents-created`, izin sesi, dan
`createWindow()` di `app/main.js`.
*Diuji:* tes "renderer terisolasi: tanpa Node, jendela baru, atau navigasi keluar" dan "instance
kedua tidak membuka jendela baru" (memakai `launch()`) di `tests/app.test.js`.

## Pemeriksaan

`test_expcore.py` mencakup parser, penamaan dengan sumber nama C.3 dan A.2 (tanpa
fallback), ekspor empat modul termasuk rekening koran, subfolder, kelanjutan batch saat
PDF rusak, dan protokol engine pada PDF sintetis (`tests/fixtures.py`). e-Statement
sintetis dua halaman menguji kolom berbasis posisi, debit bertanda DB, keterangan yang
berlanjut ke halaman berikutnya, serta setiap jenis selisih terhadap ringkasan PDF.
Opsi `--pdf-samples` memeriksa PDF contoh lokal di `contoh-pdf/` tanpa mengubah dokumen.
*Kode:* `test_engine_protocol()`, `test_rename_pemotong()`, `test_rekening_koran()`, dan
`test_pdf_samples()` di `test_expcore.py`; `write_all()` dan `write_rekening()` di
`tests/fixtures.py`.

`npm test` menjalankan `tests/engine.test.js` (kontrak runner) dan `tests/app.test.js`
(E2E Electron + engine): navigasi dan indikatornya, tata letak responsif tanpa overflow
dan header yang tidak bertumpuk, menu Alat (klik, keyboard, klik di luar, Tab keluar, posisi
panel), ikon, font, roda mouse, keyboard, kelima alat,
sumber nama penamaan, konfirmasi, penguncian saat memproses, animasi masuk, mode gerak dikurangi, isolasi
renderer, dan satu instance. Atur `EXPCORE_SCALE=1.25` atau `1.5` untuk pembesaran
tampilan. Dengan `EXPCORE_APP=dist/win-unpacked/ExpCore.exe`, tes yang sama berjalan
pada aplikasi hasil paket, ditambah `tests/update.test.js` untuk alur update terhadap
server lokal. Tes yang gagal menyimpan screenshot dan keadaan UI di
`%TEMP%\expcore-e2e-artefak`. *Kode:* `runTo()`, `setSize()`, dan `logBaseline()` di
`tests/app.test.js`; `fake()` di `tests/engine.test.js`; `manualCheck()` di
`tests/update.test.js`.

## Hasil verifikasi (9 Oktober 2026): sumber nama & Rekening Koran

- **e-Statement BCA asli:** 6 PDF (Giro Jan–Mar 2023: 28/29/20 transaksi; Tahapan
  Jan–Mar 2023: 81/105/101 transaksi) semuanya **SESUAI**: total dan jumlah transaksi
  debit/kredit sama dengan ringkasan PDF, saldo berjalan sama dengan setiap saldo yang
  tercetak, dan saldo akhir setiap bulan sama dengan saldo awal bulan berikutnya. Seluruh
  5.121 kata tabel masuk tepat satu kolom (tidak ada yang hilang atau ganda), dan `SUM`
  kolom DEBIT/CREDIT sama dengan MUTASI DB/CR.
- **Dibanding hasil ekstraksi lama yang dilampirkan pengguna:** tahun tidak lagi salah
  (2023, bukan tahun berjalan), mutasi bertanda `DB` masuk DEBIT, kode cabang terpisah ke
  kolom CBG, nominal PAJAK BUNGA tidak hilang, dan ringkasan tidak lagi tergabung ke
  keterangan baris terakhir.
- **Sumber nama penamaan:** C.3 dan A.2 diuji pada pratinjau dan penerapan, termasuk nama
  kosong tanpa fallback, sumber yang tidak dikenal, dan penerapan yang ditolak bila sumber
  berbeda dari pratinjau; pada BPPU asli menghasilkan nama pemotong maupun nama wajib pajak
  yang dipotong dengan benar.
- **Tes:** `test_expcore.py --pdf-samples` lulus 3 kali; E2E mode pengembangan 29/29 pada
  skala 100%, 125%, dan 150%, dua putaran pada kode akhir; aplikasi hasil paket (engine
  Nuitka) 33 lulus + 1 dilewati (tes khusus mode pengembangan) pada ketiga skala; engine
  Nuitka dan engine Python menghasilkan Excel identik (7 sheet, 3.826 sel) dari keenam
  e-Statement.
- **Ditemukan dan diperbaiki selama pengujian:** dengan enam item menu, header meluap
  86 px pada lebar 960 px dan 33 px pada 1180 px (badge terpotong). Perbaikan awal (label
  menu pendek) kemudian diganti dengan menu **Alat** berkelompok: judul lengkap kembali dan
  label header selalu tampil, diukur tanpa luapan pada 960–1400 px. Tombol kartu alat
  kelima yang melebar dua kolom juga ikut merentang selebar kolom; kini selebar isinya.
- **Menu Alat, ditemukan dan diperbaiki:**
  - Saat berpindah alat dengan cepat, pill indikator sempat melebar hingga 2.680 px dan
    meluap keluar jendela. Penyebabnya: lebar navigasi berubah karena nama alat, lalu
    ResizeObserver memindahkan indikator secara instan, dan pegas berikutnya mewarisi
    kecepatan lompatan tersebut. Diperbaiki dengan pegas berkecepatan awal 0, lompatan instan
    hanya bila posisi tujuan berubah, dan pill yang memotong indikator. Setelah perbaikan,
    lebar maksimum = lebar tombol Alat (209 px) pada 1.096 frame navigasi cepat.
  - Navigasi di tengah header pasti bergeser saat nama alat tampil, sehingga diubah menjadi
    rata kiri.
  - Tes roda mouse sekali gagal acak di skala 125% (halaman masih bergeser saat roda
    diputar). Pembantu tes kini memastikan titik roda mengenai target sebelum memutar roda.
  - Tes regresi baru (navigasi cepat, diukur tiap frame) terbukti gagal pada kode lama
    (indikator 3.411 px untuk tujuan 219 px) dan lulus setelah perbaikan.
- **Menu Alat, hasil akhir:** E2E mode pengembangan 30/30 pada skala 100%, 125%, dan 150%,
  dua putaran; aplikasi hasil paket 34 lulus + 1 dilewati (tes khusus mode pengembangan)
  pada ketiga skala.

## Hasil verifikasi (8 Oktober 2026)

- **Parser tidak berubah sejak migrasi Electron:** kode v2.0.1 dan kode baru dijalankan
  pada 151 PDF BPBS asli serta PDF sintetis untuk keempat alat; Excel, log CSV, hasil
  penamaan, dan pesan log identik pada 12/12 perbandingan, diulang tiga kali.
- **Desain Tailwind + Motion + Reicon:** mode pengembangan 27/27 dan aplikasi hasil
  paket 31 lulus + 1 dilewati (tes khusus mode pengembangan), masing-masing pada skala
  100%, 125%, dan 150%. Tanpa error konsol; isi `app.asar` diperiksa otomatis oleh
  `build_release.py`.
- **Installer di Windows 11 nyata:** instalasi baru, pemasangan di atas 3.0.0 yang sudah
  ada (jalur update otomatis), dan uninstall menghasilkan satu entri uninstall, shortcut
  dengan AUMID yang sama dengan aplikasi, dan data pengguna yang tetap.
- **Ditemukan dan diperbaiki selama pengujian:** roda mouse di ujung log tidak
  diteruskan ke halaman pada DPI 125%/150%; log tampil dari atas bila pekerjaan selesai
  saat halaman lain aktif; kedipan satu frame sebelum animasi masuk. Semuanya dicakup tes
  yang terbukti gagal tanpa perbaikan.
- **Ketahanan tes:** jendela tes yang diminimalkan atau dipindahkan dari luar aplikasi
  dipulihkan sebelum tes berikutnya, dan penantian memakai polling interval (bukan
  animation frame); dibuktikan dengan meminimalkan jendela tes di tengah suite.
