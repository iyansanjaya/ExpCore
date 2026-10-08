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

## Struktur dan interaksi

- **Header** tetap di atas: logo, navigasi pill (Beranda + empat alat) dengan
  indikator ungu yang meluncur (spring Motion), tombol **Periksa update**, dan badge
  **Lokal & privat**. Di bawah 1120 px keduanya menyusut menjadi ikon.
  *Kode:* `moveIndicator()` dan `navigate()` di `app/renderer/src/app.js`.
- **Beranda** bergaya landing page: hero dengan kartu PDF → XLSX → CSV yang melayang,
  chip fitur, kartu bento keempat alat, panel lavender "Kenapa ExpCore?", banner
  ajakan ungu, dan footer navy. Elemen muncul bertahap (stagger) saat masuk pandangan.
  *Kode:* `revealHero()` dan `revealSectionsInView()` di `app/renderer/src/app.js`.
- **Halaman alat**: kepala halaman (badge, judul, kartu nama hasil), kartu 01 sumber
  dokumen, kartu 02 aktivitas & hasil, dan bilah aksi yang menetap di bawah. Setiap
  alat menyimpan folder, aktivitas, dan hasilnya sendiri selama sesi.
  *Kode:* `buildTool()` di `app/renderer/src/app.js`.
- Field folder 48 px dengan ikon; jalur dapat diketik, ditempel dari "Copy as path"
  Explorer (bertanda kutip), atau dipilih lewat dialog native. *Kode:* `browse()` dan
  `folderChanged()` di `app/renderer/src/app.js`; `cleanFolder()` dan `registerIpc()`
  di `app/main.js`.
- Pill status berganti warna per keadaan dengan animasi pop; progres memakai bar
  gradien (determinan) atau kilau berjalan (indeterminan). *Kode:* `setStatus()` dan
  `setProgress()` di `app/renderer/src/app.js`.
- Log panjang digulir mandiri dan mengisi sisa tinggi kartu aktivitas (minimal 130 px).
  Di tepi log, roda mouse diteruskan ke halaman secara eksplisit karena scroll chaining
  bawaan tidak konsisten pada DPI pecahan. *Kode:* `scrollLogToEnd()` dan listener roda
  mouse di `buildTool()`, keduanya di `app/renderer/src/app.js`.
- Kontrol folder dan pemrosesan dikunci selama satu pekerjaan berjalan; navigasi tetap
  aktif, dan item menu alat yang sibuk ditandai titik berdenyut (`aria-busy`). Proses
  main Electron adalah sumber kebenaran status pekerjaan. *Kode:* `startJob()`,
  `installUpdate()`, dan `createWindow()` di `app/main.js`; `refreshControls()` dan
  `setBusyNav()` di `app/renderer/src/app.js`.
- Hasil selesai ditampilkan inline, dengan tombol membuka Excel/CSV dan salin log.
  Folder yang berubah membatalkan tautan hasil dan status pratinjau lama. *Kode:*
  `openOutput()` di `app/main.js`; `onJobEvent()` dan `folderChanged()` di
  `app/renderer/src/app.js`.
- Penamaan memerlukan pratinjau selesai sebelum tombol penerapan aktif; proses main
  juga menolak penerapan untuk folder tanpa pratinjau. *Kode:* `startJob()` di
  `app/main.js`; `refreshControls()` di `app/renderer/src/app.js`.
- Mengganti rekap atau menerapkan nama memerlukan konfirmasi native dengan tombol
  bernama aksi dan **Batal** sebagai pilihan bawaan. Menutup aplikasi atau memasang
  update saat proses berjalan ditahan sampai hasil dan log selesai ditulis. *Kode:*
  `confirm()`, `startJob()`, dan `installUpdate()` di `app/main.js`.
- Banner update muncul dengan animasi pegas di bawah header dan tidak menutupi konten.
  *Kode:* `showUpdate()` dan `onUpdateEvent()` di `app/renderer/src/app.js`;
  `checkForUpdate()` di `app/main.js`.
- Ukuran awal menyesuaikan layar dan DPI. Ukuran minimum: 960 × 620 logical px.
  *Kode:* `createWindow()` di `app/main.js`.

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

## Keyboard

| Tombol | Tindakan |
| --- | --- |
| `Tab` / `Shift+Tab` | Pindah fokus kontrol; fokus ditandai cincin ungu |
| `Enter` / `Space` pada tombol | Aktifkan tombol |
| `Ctrl+O` | Pilih folder pada alat aktif |
| `Alt+0` | Beranda |
| `Alt+1`–`Alt+4` | Alat sesuai urutan menu |
| `Page Up` / `Page Down` | Gulir halaman saat fokus berada di luar isian teks dan log |

*Kode:* `onKeyDown()` di `app/renderer/src/app.js`.

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

`npm run build:renderer` menjalankan Tailwind CLI (`src/styles.css` → `dist/styles.css`)
dan esbuild (`src/app.js` → `dist/app.js`, beserta font Inter). `npm start`, `npm test`,
dan `build_release.py` menjalankannya otomatis; sumber `src/` tidak ikut dipaketkan.
*Kode:* skrip `build:renderer` di `package.json`; `build_app()` di `build_release.py`.

Renderer hanya memuat berkas lokal dengan Content-Security-Policy ketat (tanpa inline
script/style dan tanpa `eval`). Navigasi, jendela baru, webview, dan izin perangkat
ditolak. Menu bawaan dan DevTools tidak tersedia pada aplikasi terpasang. *Kode:* meta
CSP di `app/renderer/index.html`; handler `web-contents-created`, izin sesi, dan
`createWindow()` di `app/main.js`.

## Pemeriksaan

`test_expcore.py` mencakup parser, penamaan, ekspor tiga modul, subfolder, kelanjutan
batch saat PDF rusak, dan protokol engine pada PDF sintetis (`tests/fixtures.py`).
Opsi `--pdf-samples` memeriksa 151 PDF lokal tanpa mengubah dokumen.
*Kode:* `test_engine_protocol()` dan `test_bupot2024_pdf_samples()` di `test_expcore.py`;
`write_all()` di `tests/fixtures.py`.

`npm test` menjalankan `tests/engine.test.js` (kontrak runner) dan `tests/app.test.js`
(E2E Electron + engine): navigasi dan indikatornya, tata letak responsif tanpa overflow
dan header yang tidak bertumpuk, ikon, font, roda mouse, keyboard, keempat alat,
konfirmasi, penguncian saat memproses, animasi masuk, mode gerak dikurangi, isolasi
renderer, dan satu instance. Atur `EXPCORE_SCALE=1.25` atau `1.5` untuk pembesaran
tampilan. Dengan `EXPCORE_APP=dist/win-unpacked/ExpCore.exe`, tes yang sama berjalan
pada aplikasi hasil paket, ditambah `tests/update.test.js` untuk alur update terhadap
server lokal. Tes yang gagal menyimpan screenshot dan keadaan UI di
`%TEMP%\expcore-e2e-artefak`. *Kode:* `runTo()`, `setSize()`, dan `logBaseline()` di
`tests/app.test.js`; `fake()` di `tests/engine.test.js`; `manualCheck()` di
`tests/update.test.js`.

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
