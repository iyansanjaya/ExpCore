# ExpCore — Desktop workspace

Desain terinspirasi selera editorial Awesomic: zinc yang tenang, hierarki tegas,
permukaan membulat, dan aksen oranye sebagai penanda. Disesuaikan untuk aplikasi
desktop pengolahan dokumen, dengan informasi dan tindakan yang mudah ditemukan.

## Token visual

| Peran | Nilai |
| --- | --- |
| Kanvas | `#f4f4f5` |
| Kartu / sidebar | `#ffffff` |
| Teks utama / aksi utama | `#09090b` |
| Panel gelap | `#18181b` |
| Teks pendukung | `#52525b` |
| Metadata | `#71717a` |
| Garis pemisah | `#e4e4e7` |
| Aksen badge / fokus keyboard | `#ff5a00` |
| Font | Segoe UI, tersedia secara native di Windows |
| Judul beranda | 34–40 px, bold |
| Judul alat | 36 px, bold |
| Judul kartu | 20 px, bold |
| Teks antarmuka | 12–14 px |
| Radius kartu | 28 px |
| Radius kontrol | 14 px |

Warna ditetapkan sekali sebagai variabel CSS di `app/renderer/styles.css`; metadata
keempat alat di `MODULES` pada `app/main.js`. Segoe UI menghindari pengunduhan font
dan tetap bekerja offline. Kartu memakai garis tipis tanpa drop shadow. Status memakai teks,
sehingga warna bukan satu-satunya pembeda.

## Struktur dan interaksi

- Beranda berisi pengantar, panduan tiga langkah, dan akses ke empat alat.
- Sidebar menetap; setiap alat menyimpan folder, aktivitas, dan hasilnya sendiri
  selama sesi. Jalur folder dapat diketik atau dipilih melalui dialog native.
- Konten dapat digulir pada jendela pendek. Tombol pemrosesan menetap di bawah.
  Komposisi pengantar beranda ditumpuk pada area konten sempit.
- Tata letak responsif memakai container query pada lebar halaman: judul beranda
  34 px di bawah 840 px, panduan beranda menjadi baris ringkas di bawah 690 px, dan
  kartu menjadi satu kolom di bawah 600 px. Scrollbar berkontras jelas.
- Log panjang digulir secara mandiri dan mengisi sisa tinggi kartu aktivitas (minimal
  130 px). Di ujung log, roda mouse diteruskan ke halaman oleh scroll chaining bawaan.
- Badge oranye memakai teks gelap untuk meningkatkan kontras teks kecil.
- Field folder dan tombol pemilih memiliki tinggi 44 px, radius 14 px, dan border
  2 px; perubahan warna fokus tidak mengubah ukuran kontrol. Jalur yang ditempel dari
  "Copy as path" Explorer (bertanda kutip) diterima. Teks bantuan menjelaskan format
  untuk alat aktif.
- Ukuran awal menyesuaikan layar dan DPI. Ukuran minimum: 960 × 620 logical px.
- Kontrol folder dan pemrosesan dikunci selama satu pekerjaan berjalan;
  navigasi tetap aktif. Proses main Electron adalah sumber kebenaran status pekerjaan;
  progres dan log dari engine diteruskan ke renderer lewat IPC.
- Hasil selesai ditampilkan inline, dengan tombol membuka Excel/CSV dan salin
  log. Folder yang berubah membatalkan tautan hasil dan status pratinjau lama.
- Penamaan memerlukan pratinjau selesai sebelum tombol penerapan aktif; proses main
  juga menolak penerapan untuk folder tanpa pratinjau. Konfirmasi menjelaskan bahwa
  penerapan memindai ulang kondisi folder terkini.
- Mengganti rekap yang sudah ada memerlukan konfirmasi. Dialog konfirmasi native
  memakai tombol bernama aksi, dengan **Batal** sebagai pilihan bawaan. Menutup aplikasi
  atau memasang update saat proses berjalan ditahan sampai hasil dan log selesai ditulis.
- PDF yang gagal dibaca dicatat dan dilewati; dokumen lain tetap diproses.

## Keyboard

| Tombol | Tindakan |
| --- | --- |
| `Tab` / `Shift+Tab` | Pindah fokus kontrol |
| `Enter` / `Space` pada tombol | Aktifkan tombol |
| `Ctrl+O` | Pilih folder pada alat aktif |
| `Alt+0` | Beranda |
| `Alt+1`–`Alt+4` | Alat sesuai urutan sidebar |
| `Page Up` / `Page Down` | Gulir halaman saat fokus berada di luar editor teks |

## Arsitektur

| Bagian | Berkas | Tanggung jawab |
| --- | --- | --- |
| Renderer | `app/renderer/` | HTML/CSS/JS tanpa framework; tanpa akses Node (sandbox, `contextIsolation`) |
| Preload | `app/preload.js` | Satu-satunya jembatan: API `window.expcore` |
| Main | `app/main.js` | Jendela, dialog native, validasi IPC, status pekerjaan, update |
| Runner | `app/engine.js` | Menjalankan engine dan membaca protokol JSON per baris |
| Engine | `expcore_engine.py` → `ExpCore.py` | Parser PDF dan ekspor Excel/CSV, satu proses per pekerjaan |

Renderer hanya memuat berkas lokal dengan Content-Security-Policy ketat. Navigasi,
jendela baru, webview, dan izin perangkat ditolak. Menu bawaan dan DevTools tidak
tersedia pada aplikasi terpasang.

## Pemeriksaan

`test_expcore.py` mencakup parser, penamaan, ekspor tiga modul, subfolder, kelanjutan
batch saat PDF rusak, dan protokol engine pada PDF sintetis (`tests/fixtures.py`).
Opsi `--pdf-samples` memeriksa 151 PDF lokal tanpa mengubah dokumen.

`npm test` menjalankan `tests/engine.test.js` (kontrak runner: urutan event, crash,
stderr besar, keluaran liar) dan `tests/app.test.js` (E2E Electron + engine: navigasi,
tata letak responsif tanpa overflow, keyboard, keempat alat, konfirmasi, penguncian
saat memproses, isolasi renderer, satu instance). Atur `EXPCORE_SCALE=1.25` atau
`1.5` untuk pembesaran tampilan. Dengan `EXPCORE_APP=dist/win-unpacked/ExpCore.exe`,
tes yang sama berjalan pada aplikasi hasil paket, ditambah `tests/update.test.js`
untuk alur update terhadap server lokal.

### Hasil verifikasi migrasi Electron (8 Oktober 2026)

- **Parser tidak berubah:** kode v2.0.1 dan kode baru dijalankan pada 151 PDF
  BPBS asli serta PDF sintetis untuk keempat alat. Excel (nilai, format angka, font,
  warna, lebar kolom), log CSV, hasil penamaan, dan pesan log identik pada 12/12
  perbandingan, diulang tiga kali.
- **Tes otomatis**, masing-masing pada skala 100%, 125%, dan 150%: mode pengembangan
  25/25; aplikasi hasil paket (`dist/win-unpacked`) dan aplikasi terpasang di
  `C:\Program Files\ExpCore` masing-masing 29 lulus + 1 dilewati (tes khusus mode
  pengembangan). `test_expcore.py --pdf-samples` lulus tiga kali.
- **Installer di Windows 11 nyata:** instalasi baru, pemasangan di atas 3.0.0 yang sudah
  ada (jalur yang sama dengan update otomatis), dan uninstall diuji. Hasilnya satu entri
  uninstall; shortcut Start Menu/desktop memakai AUMID yang sama dengan aplikasi;
  uninstall bersih dengan data pengguna tetap. Installer tidak melepas ExpCore 2.x
  secara otomatis (lihat README, bagian Installer).
- **Tes E2E yang gagal** menyimpan screenshot dan keadaan jendela/UI di
  `%TEMP%\expcore-e2e-artefak`. Kegagalan sesekali hanya teramati saat desktop sedang
  dipakai (jendela tes dimaksimalkan, di-snap, atau menerima gangguan); tidak muncul
  pada lebih dari 50 putaran tanpa gangguan.
- **Ditemukan dan diperbaiki selama pengujian:** log yang digulir otomatis menahan satu
  putaran roda mouse pada DPI 150%; log tampil dari atas bila pekerjaan selesai saat
  halaman lain aktif. Keduanya kini dicakup tes yang terbukti gagal tanpa perbaikan.
