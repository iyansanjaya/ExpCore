# Graph Report - ExpCore-1  (2026-11-20)

## Corpus Check
- 7 files · ~46,572 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 491 nodes · 1185 edges · 26 communities (23 shown, 3 thin omitted)
- Extraction: 84% EXTRACTED · 15% INFERRED · 0% AMBIGUOUS · INFERRED: 183 edges (avg confidence: 0.84)
- Token cost: 141,924 input · 0 output

## Community Hubs (Navigation)
- Riwayat Rilis & README
- Antarmuka Renderer & Menu Alat
- Runner Engine & Log Aktivitas
- Proses Main & Pembaruan
- Build Rilis & Skrip
- Banner & Tes Pembaruan
- Tes Python & Acuan Excel
- Dependency package.json
- Alur Rekap Bupot & Peringatan
- Parser Bupot & Kelas ExpCore
- Parser Rekening CIMB
- Tes E2E Aplikasi
- Penulis Excel Rekening
- Parser Rekening BCA
- Konfigurasi Installer NSIS
- Pembaca PDF Paralel
- Fixture PDF Sintetis
- Konfigurasi electron-builder
- Lisensi Apache 2.0
- Ikon & Target Windows
- Berkas Paket
- Instans Tunggal
- Ikon Aplikasi
- Meta CSP
- Input Folder
- Halaman Beranda

## God Nodes (most connected - your core abstractions)
1. `ExpCore` - 61 edges
2. `ExpCore - Toolkit PDF Coretax (README)` - 31 edges
3. `Release 3.0.0 (2026-10-09, Electron)` - 28 edges
4. `Penamaan Otomatis Bupot` - 26 edges
5. `Automatic Update (electron-updater, GitHub Releases, SHA-512 latest.yml)` - 24 edges
6. `ExpCore 3.0.0 Release Notes` - 23 edges
7. `ExpCore 3.1.0 Release Notes` - 23 edges
8. `ExpCore Changelog` - 20 edges
9. `Rekening Koran CIMB Niaga (Combine Statement Portfolio Recap)` - 19 edges
10. `Release 3.1.0 (2026-10-12, CIMB, BPBS rename, duplicate flag)` - 18 edges

## Surprising Connections (you probably didn't know these)
- `Query: README.md Code References Remeasure` --references--> `test_pdf_samples()`  [AMBIGUOUS]
  graphify-out/memory/query_20261008_170442_tambahkan_rujukan_kode_ke_readme_md_lalu_ukur_ulan.md → test_expcore.py
- `Window Sizing (screen/DPI aware, min 960x620)` --references--> `setSize()`  [EXTRACTED]
  DESIGN.md → tests/app.test.js
- `Name Source Selection (Identitas Pemotong C.3/C.2 vs Wajib Pajak A.2/A.3)` --references--> `buildNameSources()`  [EXTRACTED]
  DESIGN.md → app/renderer/src/app.js
- `Log Edge Mouse-Wheel Forwarding` --references--> `buildTool()`  [EXTRACTED]
  DESIGN.md → app/renderer/src/app.js
- `Inline Results (open Excel/CSV, copy log)` --references--> `folderChanged()`  [EXTRACTED]
  DESIGN.md → app/renderer/src/app.js

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Bank statement automatic check (SESUAI / PERLU CEK)** — readme_rekening_koran_check, readme_cimb_check, readme_duplicate_statement_flag, expcore_expcore_cek_saldo_berjalan, expcore_expcore_tandai_ganda [INFERRED 0.85]
- **Unreadable data surfaced in the log instead of silent defaults** — changelog_bupot2026_unreadable_amount_gagal, changelog_unreadable_identity_warning, readme_no_guess_principle, readme_format_mismatch_skip [INFERRED 0.85]
- **3.2.1 BPBS NITKU layout fix (recap and rename share the header parser)** — changelog_bpbs_nitku_layout, expcore_expcore_bpbs_header, expcore_expcore_extract_bpbs_rename_data, readme_bukti_potong_2024, readme_penamaan_bupot [INFERRED 0.85]
- **Installer and taskbar identity (appId, NSIS GUID, APP_ID)** — package_build_appid, package_build_nsis, app_main, readme_installer_guid_pin, readme_v2_uninstall_requirement, tests_app_test [EXTRACTED 1.00]
- **Shared Excel Helpers of BCA & CIMB Writers** — expcore_expcore_write_rekening_excel, expcore_expcore_write_cimb_excel, expcore_expcore_judul_excel, expcore_expcore_nama_sheet, expcore_expcore_tulis_panel, expcore_expcore_tautan_sheet, expcore_expcore_rapikan_tabel, expcore_expcore_angka [EXTRACTED 1.00]
- **Renderer build as single point for start, test and release** — package_scripts_build_renderer, package_scripts_start, package_scripts_pretest, build_release_build_app, readme_renderer_build, design_build_renderer [EXTRACTED 1.00]

## Communities (26 total, 3 thin omitted)

### Community 0 - "Riwayat Rilis & README"
Cohesion: 0.07
Nodes (69): Release Assets (ExpCore-Setup-3.0.0.exe, .blockmap, latest.yml), ExpCore 3.0.0 Release Notes, Release Assets (ExpCore-Setup-3.1.0.exe, .blockmap, latest.yml), ExpCore 3.1.0 Release Notes, Release Assets (ExpCore-Setup-3.2.0.exe, .blockmap, latest.yml), ExpCore 3.2.0 Release Notes, Release Assets (ExpCore-Setup-3.2.1.exe, .blockmap, latest.yml), ExpCore 3.2.1 Release Notes (+61 more)

### Community 1 - "Antarmuka Renderer & Menu Alat"
Cohesion: 0.08
Nodes (55): #main-nav Pill Navigation, Name Source Fieldset (Ambil nama file dari), #nav-indicator Sliding Pill, index.html Renderer Shell, Progress Bar (role=progressbar), Status Pill (data-state), #tool-card Template, #tool-page Template (+47 more)

### Community 2 - "Runner Engine & Log Aktivitas"
Cohesion: 0.08
Nodes (38): lastLines(), readline, runEngine(), { spawn }, { contextBridge, ipcRenderer }, Activity Log (role=log), Parallel PDF Reading (max 4 worker processes), Release 1.1 (2026-06-10) (+30 more)

### Community 3 - "Proses Main & Pembaruan"
Cohesion: 0.10
Nodes (41): { app, BrowserWindow, clipboard, dialog, ipcMain, screen, session, shell }, { autoUpdater }, checkForUpdate(), cleanFolder(), confirm(), createWindow(), describeUpdateError(), downloadUpdate() (+33 more)

### Community 4 - "Build Rilis & Skrip"
Cohesion: 0.09
Nodes (37): engineCommand(), app_version(), build_app(), build_engine(), check_engine(), main(), Build installer Windows: engine Python (Nuitka) lalu aplikasi Electron…, Keenam pekerjaan pada PDF sintetis: import lazy (mis. writer Excel) ikut teruji. (+29 more)

### Community 5 - "Banner & Tes Pembaruan"
Cohesion: 0.09
Nodes (29): #update-banner, onUpdateEvent(), showUpdate(), Update Banner (spring, non-overlapping), { after, before, describe, it }, assert, bannerText(), CACHE (+21 more)

### Community 6 - "Tes Python & Acuan Excel"
Cohesion: 0.16
Nodes (21): Python Test Suite (test_expcore.py), ExpCore - Toolkit PDF Coretax (README), PDF Samples Regression Test (--pdf-samples), Rekening Koran (BCA e-Statement Recap), PDF Summary in Side Panel (SUM counts only transactions), bandingkan_excel(), gaya_sel(), All three workers export valid PDFs despite a corrupt sibling PDF. (+13 more)

### Community 7 - "Dependency package.json"
Cohesion: 0.11
Nodes (19): electron, electron-builder, esbuild, @fontsource-variable/inter, motion, devDependencies, electron, electron-builder (+11 more)

### Community 8 - "Alur Rekap Bupot & Peringatan"
Cohesion: 0.14
Nodes (13): Release 1.0 (2026-06-10, initial), Release 1.1.1 (2026-06-10), Release 1.2 (2026-07-07), Release 1.4 (2026-08-28), _baca_teks(), Teks seluruh halaman satu PDF ke `ekstrak` (Bupot 2026 dan 2024)., Catat kolom identitas/tanggal yang terbaca "-" agar tidak lolos diam-diam ke…, Tulis baris (dict, kolom = kunci baris pertama) ke Excel dengan header, format… (+5 more)

### Community 9 - "Parser Bupot & Kelas ExpCore"
Cohesion: 0.18
Nodes (8): ExpCore, Ambil semua baris objek pajak dari teks satu PDF Bukti Potong., Parser PDF Coretax. Aktivitas dan progres dilaporkan lewat callback., 4 3 6 1 ...' -> '4361...'. Formulir BPBS menulis angka per kotak., 3 1 dd 0 1 mm 2 0 2 4 yyyy' -> '31-01-2024'. Kotak kosong -> ''., Ambil baris objek pajak dari teks satu PDF Bukti Potong formulir BPBS., Rincian barang satu faktur pajak; kolom Folder Sumber dan Nama File PDF diisi…, main()

### Community 10 - "Parser Rekening CIMB"
Cohesion: 0.17
Nodes (10): Garis horizontal tabel (batas sel) di halaman, urut dari atas: [(y, [(x0, x1),…, Tepi kolom tabel mutasi dari garis tepat di bawah judulnya; None bila…, Isi laporan berurutan lintas halaman: penanda bagian dan sel tabel, tanpa…, Masukkan satu sel tabel mutasi ke rekening: SALDO AWAL, transaksi, Total, atau…, Baca satu Combine Statement Portfolio (Laporan Konsolidasi) CIMB Niaga dari…, CIMB Semua Transaksi Sheet (all accounts in one table), Rekening Koran CIMB Niaga (Combine Statement Portfolio Recap), CIMB Niaga: sel multi-baris per garis tabel, kolom dari garis di bawah judul,… (+2 more)

### Community 11 - "Tes E2E Aplikasi"
Cohesion: 0.14
Nodes (14): { after, afterEach, before, beforeEach, describe, it }, assert, { _electron: electron }, { execFileSync }, fs, os, path, PYTHON (+6 more)

### Community 12 - "Penulis Excel Rekening"
Cohesion: 0.30
Nodes (6): Nama sheet unik maks. 31 karakter: awalan yang dipotong, akhiran (nomor &…, Panel label–nilai di kanan tabel mutasi, mulai kolom `kolom`; None = baris…, Judul tebal, baris judul dibekukan, filter, dan lebar kolom mengikuti isi…, Sheet Ringkasan + satu sheet per PDF (tabel mutasi, panel informasi & ringkasan…, Sheet Ringkasan (per rekening), Total Kategori (per PDF), Semua Transaksi, dan…, Query: Impact of changing shared Excel helpers (_write_rekening_excel <-> _write_cimb_excel)

### Community 13 - "Parser Rekening BCA"
Cohesion: 0.19
Nodes (8): Verification Results 9 Oct 2026 (name source & Rekening Koran), 31/12' pada laporan bulan/tahun tertentu -> datetime; ValueError bila tidak…, Catatan selisih saldo berjalan: mendeteksi debit/kredit yang tertukar walau…, Kata pdfplumber per baris visual: urut dari atas, lalu dari kiri., Baca satu e-Statement BCA (Rekening Giro/Tahapan) dari halaman pdfplumber.…, CIMB Automatic Check (accounts, running balance, category totals), Duplicate Statement Flagged PERLU CEK (no PDF dropped), Rekening Koran Automatic Check (Hasil Cek / PERLU CEK)

### Community 14 - "Konfigurasi Installer NSIS"
Cohesion: 0.19
Nodes (13): Query: Impact of changing appId (package.json -> main.js -> NSIS installer), appId, nsis, allowToChangeInstallationDirectory, artifactName, createDesktopShortcut, createStartMenuShortcut, deleteAppDataOnUninstall (+5 more)

### Community 15 - "Pembaca PDF Paralel"
Cohesion: 0.21
Nodes (7): _baca_aman(), _baca_halaman(), Satu PDF: (hasil, None), atau (None, pesan galat) agar satu PDF rusak tidak…, Halaman pdfplumber satu PDF ke `ekstrak` (rekening koran BCA dan CIMB)., (hasil, galat) per PDF, urut sesuai pdf_files. pdfminer murni Python sehingga…, Laporan dengan periode sama di lebih dari satu PDF: setiap salinan diberi…, Query: Why ExpCore class bridges Parser Bupot, Rekening Koran BCA & CIMB, docs and Release 3.0.0

### Community 16 - "Fixture PDF Sintetis"
Cohesion: 0.30
Nodes (11): PDF uji sintetis (tanpa data wajib pajak asli) untuk tes engine dan aplikasi.…, PDF satu halaman A4, Helvetica (metrik bawaan pdfminer), opsional tabel…, e-Statement BCA sintetis dengan kolom pada posisi x seperti aslinya (lihat…, Combine Statement Portfolio CIMB Niaga sintetis: sampul, kotak kepala tiap…, PDF A4 dengan satu content stream per halaman, font Helvetica sebagai /F1., _text(), write_all(), write_cimb() (+3 more)

### Community 17 - "Konfigurasi electron-builder"
Cohesion: 0.20
Nodes (10): build, copyright, directories, electronLanguages, extraResources, productName, publish, output (+2 more)

### Community 18 - "Lisensi Apache 2.0"
Cohesion: 0.33
Nodes (6): Apache License, Version 2.0, Copyright 2026 Iyan Sanjaya, Disclaimer of Warranty and Limitation of Liability (Sections 7-8), Non-standard appendix note about Eclipse Public License, Grant of Patent License (Section 3), Redistribution Conditions (Section 4)

### Community 19 - "Ikon & Target Windows"
Cohesion: 0.40
Nodes (5): App Icon (icon.svg source, icon.ico 15 sizes), win, executableName, icon, target

### Community 20 - "Berkas Paket"
Cohesion: 0.50
Nodes (3): files, app/**/*, !app/renderer/src/**

### Community 21 - "Instans Tunggal"
Cohesion: 0.67
Nodes (3): Single Instance (second launch opens no new window), launch(), launchArgs()

### Community 22 - "Ikon Aplikasi"
Cohesion: 0.67
Nodes (3): Document Glyph (folded corner + text lines), ExpCore App Icon (SVG), Purple Gradient Rounded Tile (#8270f9 to #5944e0)

## Ambiguous Edges - Review These
- `Query: README.md Code References Remeasure` → `test_pdf_samples()`  [AMBIGUOUS]
  graphify-out/memory/query_20261008_170442_tambahkan_rujukan_kode_ke_readme_md_lalu_ukur_ulan.md · relation: references
- `Apache License, Version 2.0` → `Non-standard appendix note about Eclipse Public License`  [AMBIGUOUS]
  LICENSE.txt · relation: references

## Knowledge Gaps
- **107 isolated node(s):** `Name Source Fieldset (Ambil nama file dari)`, `#nav-indicator Sliding Pill`, `index.html Renderer Shell`, `Status Pill (data-state)`, `#tool-card Template` (+102 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Query: README.md Code References Remeasure` and `test_pdf_samples()`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **What is the exact relationship between `Apache License, Version 2.0` and `Non-standard appendix note about Eclipse Public License`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **Why does `ExpCore - Toolkit PDF Coretax (README)` connect `Tes Python & Acuan Excel` to `Riwayat Rilis & README`, `Runner Engine & Log Aktivitas`, `Build Rilis & Skrip`, `Alur Rekap Bupot & Peringatan`, `Parser Bupot & Kelas ExpCore`, `Parser Rekening CIMB`, `Fixture PDF Sintetis`?**
  _High betweenness centrality (0.165) - this node is a cross-community bridge._
- **Why does `Query: Diuji (feature -> test) References Remeasure` connect `Runner Engine & Log Aktivitas` to `Riwayat Rilis & README`, `Antarmuka Renderer & Menu Alat`, `Banner & Tes Pembaruan`, `Tes Python & Acuan Excel`, `Tes E2E Aplikasi`?**
  _High betweenness centrality (0.162) - this node is a cross-community bridge._
- **Why does `ExpCore` connect `Parser Bupot & Kelas ExpCore` to `Riwayat Rilis & README`, `Runner Engine & Log Aktivitas`, `Tes Python & Acuan Excel`, `Alur Rekap Bupot & Peringatan`, `Parser Rekening CIMB`, `Penulis Excel Rekening`, `Parser Rekening BCA`, `Pembaca PDF Paralel`?**
  _High betweenness centrality (0.161) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `ExpCore` (e.g. with `main()` and `main()`) actually correct?**
  _`ExpCore` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `Release 3.0.0 (2026-10-09, Electron)` (e.g. with `ExpCore 3.0.0 Release Notes` and `Visual Tokens (@theme in styles.css)`) actually correct?**
  _`Release 3.0.0 (2026-10-09, Electron)` has 2 INFERRED edges - model-reasoned connections that need verification._