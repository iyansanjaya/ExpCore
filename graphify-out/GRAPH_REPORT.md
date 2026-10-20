# Graph Report - ExpCore-1  (2026-10-20)

## Corpus Check
- 14 files · ~45,255 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 481 nodes · 1125 edges · 16 communities (13 shown, 3 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 148 edges (avg confidence: 0.82)
- Token cost: 173,703 input · 0 output

## Community Hubs (Navigation)
- Engine ExpCore & Pembaca Paralel
- Antarmuka Renderer & Menu Alat
- Dokumentasi, Fixture & Acuan Excel
- Tes E2E & Runner Engine
- Riwayat Rilis & Keamanan Renderer
- Parser Bupot & Penamaan
- Proses Main & Pembaruan
- Build Rilis & package.json
- Banner & Tes Pembaruan
- Konfigurasi electron-builder
- Dependency package.json
- Lisensi Apache 2.0
- Ikon Aplikasi
- Meta CSP
- Input Folder
- Halaman Beranda

## God Nodes (most connected - your core abstractions)
1. `ExpCore` - 60 edges
2. `ExpCore - Toolkit PDF Coretax (README)` - 30 edges
3. `Release 3.0.0 (2026-10-09, Electron)` - 28 edges
4. `Penamaan Otomatis Bupot` - 23 edges
5. `ExpCore 3.0.0 Release Notes` - 23 edges
6. `ExpCore 3.1.0 Release Notes` - 22 edges
7. `Automatic Update (electron-updater, GitHub Releases, SHA-512 latest.yml)` - 18 edges
8. `Rekening Koran CIMB Niaga (Combine Statement Portfolio Recap)` - 18 edges
9. `Release 3.1.0 (2026-10-12, CIMB, BPBS rename, duplicate flag)` - 18 edges
10. `startJob()` - 17 edges

## Surprising Connections (you probably didn't know these)
- `Window Sizing (screen/DPI aware, min 960x620)` --references--> `setSize()`  [EXTRACTED]
  DESIGN.md → tests/app.test.js
- `Query: README.md Code References Remeasure` --references--> `test_pdf_samples()`  [AMBIGUOUS]
  graphify-out/memory/query_20261008_170442_tambahkan_rujukan_kode_ke_readme_md_lalu_ukur_ulan.md → test_expcore.py
- `pandas/numpy Excluded From Nuitka Engine (--nofollow-import-to)` --conceptually_related_to--> `build_engine()`  [INFERRED]
  README.md → build_release.py
- `Rekening Koran CIMB Niaga (Combine Statement Portfolio Recap)` --references--> `write_cimb()`  [EXTRACTED]
  README.md → tests/fixtures.py
- `Folder Field (type, paste Copy-as-path, native dialog)` --references--> `cleanFolder()`  [EXTRACTED]
  DESIGN.md → app/main.js

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Bank statement automatic check (SESUAI / PERLU CEK)** — readme_rekening_koran_check, readme_cimb_check, readme_duplicate_statement_flag, expcore_expcore_cek_saldo_berjalan, expcore_expcore_tandai_ganda [INFERRED 0.85]
- **Installer and taskbar identity (appId, NSIS GUID, APP_ID)** — package_build_appid, package_build_nsis, app_main, readme_installer_guid_pin, readme_v2_uninstall_requirement, tests_app_test [EXTRACTED 1.00]
- **Renderer build as single point for start, test and release** — package_scripts_build_renderer, package_scripts_start, package_scripts_pretest, build_release_build_app, readme_renderer_build, design_build_renderer [EXTRACTED 1.00]
- **Shared Excel Helpers of BCA & CIMB Writers** — expcore_expcore_write_rekening_excel, expcore_expcore_write_cimb_excel, expcore_expcore_judul_excel, expcore_expcore_nama_sheet, expcore_expcore_tulis_panel, expcore_expcore_tautan_sheet, expcore_expcore_rapikan_tabel, expcore_expcore_angka [EXTRACTED 1.00]

## Communities (16 total, 3 thin omitted)

### Community 0 - "Engine ExpCore & Pembaca Paralel"
Cohesion: 0.06
Nodes (39): { contextBridge, ipcRenderer }, Parallel PDF Reading (max 4 worker processes), Electron Process Architecture (Renderer/Preload/Main/Runner/Engine), Engine Runner (app/engine.js), JSON-per-line Engine Protocol, Preload Bridge (window.expcore API), Python Engine (one process per job, parallel PDF workers), Worker stdout Redirected to stderr (+31 more)

### Community 1 - "Antarmuka Renderer & Menu Alat"
Cohesion: 0.07
Nodes (59): MODULES, openOutput(), Name Source Fieldset (Ambil nama file dari), #nav-indicator Sliding Pill, index.html Renderer Shell, Progress Bar (role=progressbar), Status Pill (data-state), #tool-card Template (+51 more)

### Community 2 - "Dokumentasi, Fixture & Acuan Excel"
Cohesion: 0.07
Nodes (51): Bupot 2026 Unreadable Amount Logged GAGAL (excluded from recap), Lean Engine (pandas and numpy dropped), Unreleased Changes (parallel PDFs, lean engine, Bupot 2026 GAGAL fix), Release 1.0 (2026-06-10, initial), Release 1.1 (2026-06-10), Release 1.1.1 (2026-06-10), Release 1.2 (2026-07-07), Release 1.3 (2026-08-21) (+43 more)

### Community 3 - "Tes E2E & Runner Engine"
Cohesion: 0.07
Nodes (45): lastLines(), readline, runEngine(), { spawn }, Activity Log (role=log), #main-nav Pill Navigation, #tool-page Template, Release 2.0.1 (2026-09-10) (+37 more)

### Community 4 - "Riwayat Rilis & Keamanan Renderer"
Cohesion: 0.10
Nodes (47): Release Assets (ExpCore-Setup-3.0.0.exe, .blockmap, latest.yml), ExpCore 3.0.0 Release Notes, Release Assets (ExpCore-Setup-3.1.0.exe, .blockmap, latest.yml), ExpCore 3.1.0 Release Notes, createWindow(), Lokal & privat Badge, Bun Package Manager (bun.lock), ExpCore Changelog (+39 more)

### Community 5 - "Parser Bupot & Penamaan"
Cohesion: 0.08
Nodes (28): Release 1.5 (2026-09-02), Field nama file Penamaan Bupot dari BPPU (Bupot 2026) atau BPBS (Bupot 2024).…, Field nama file dari BPBS. Tidak menebak: data yang ambigu dibiarkan kosong…, Ambil semua baris objek pajak dari teks satu PDF Bukti Potong., 4 3 6 1 ...' -> '4361...'. Formulir BPBS menulis angka per kotak., 3 1 dd 0 1 mm 2 0 2 4 yyyy' -> '31-01-2024'. Kotak kosong -> ''., Identitas, dokumen referensi, dan bagian H satu PDF BPBS (dipakai rekap 2024…, Ambil baris objek pajak dari teks satu PDF Bukti Potong formulir BPBS. (+20 more)

### Community 6 - "Proses Main & Pembaruan"
Cohesion: 0.13
Nodes (36): { app, BrowserWindow, clipboard, dialog, ipcMain, screen, session, shell }, { autoUpdater }, checkForUpdate(), cleanFolder(), confirm(), describeUpdateError(), downloadUpdate(), errorText() (+28 more)

### Community 7 - "Build Rilis & package.json"
Cohesion: 0.09
Nodes (35): engineCommand(), app_version(), build_app(), build_engine(), check_engine(), main(), Build installer Windows: engine Python (Nuitka) lalu aplikasi Electron…, Keenam pekerjaan pada PDF sintetis: import lazy (mis. writer Excel) ikut teruji. (+27 more)

### Community 8 - "Banner & Tes Pembaruan"
Cohesion: 0.09
Nodes (29): #update-banner, onUpdateEvent(), showUpdate(), Update Banner (spring, non-overlapping), { after, before, describe, it }, assert, bannerText(), CACHE (+21 more)

### Community 9 - "Konfigurasi electron-builder"
Cohesion: 0.08
Nodes (23): build, copyright, directories, electronLanguages, extraResources, files, nsis, productName (+15 more)

### Community 10 - "Dependency package.json"
Cohesion: 0.11
Nodes (19): electron, electron-builder, esbuild, @fontsource-variable/inter, motion, devDependencies, electron, electron-builder (+11 more)

### Community 11 - "Lisensi Apache 2.0"
Cohesion: 0.33
Nodes (6): Apache License, Version 2.0, Copyright 2026 Iyan Sanjaya, Disclaimer of Warranty and Limitation of Liability (Sections 7-8), Non-standard appendix note about Eclipse Public License, Grant of Patent License (Section 3), Redistribution Conditions (Section 4)

### Community 12 - "Ikon Aplikasi"
Cohesion: 0.67
Nodes (3): Document Glyph (folded corner + text lines), ExpCore App Icon (SVG), Purple Gradient Rounded Tile (#8270f9 to #5944e0)

## Ambiguous Edges - Review These
- `Query: README.md Code References Remeasure` → `test_pdf_samples()`  [AMBIGUOUS]
  graphify-out/memory/query_20261008_170442_tambahkan_rujukan_kode_ke_readme_md_lalu_ukur_ulan.md · relation: references
- `Apache License, Version 2.0` → `Non-standard appendix note about Eclipse Public License`  [AMBIGUOUS]
  LICENSE.txt · relation: references

## Knowledge Gaps
- **107 isolated node(s):** `Name Source Fieldset (Ambil nama file dari)`, `#nav-indicator Sliding Pill`, `Status Pill (data-state)`, `#tool-card Template`, `Content-Security-Policy Meta Tag` (+102 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Query: README.md Code References Remeasure` and `test_pdf_samples()`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **What is the exact relationship between `Apache License, Version 2.0` and `Non-standard appendix note about Eclipse Public License`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **Why does `Query: Diuji (feature -> test) References Remeasure` connect `Dokumentasi, Fixture & Acuan Excel` to `Engine ExpCore & Pembaca Paralel`, `Antarmuka Renderer & Menu Alat`, `Tes E2E & Runner Engine`, `Riwayat Rilis & Keamanan Renderer`, `Proses Main & Pembaruan`, `Banner & Tes Pembaruan`?**
  _High betweenness centrality (0.171) - this node is a cross-community bridge._
- **Why does `ExpCore - Toolkit PDF Coretax (README)` connect `Dokumentasi, Fixture & Acuan Excel` to `Engine ExpCore & Pembaca Paralel`, `Antarmuka Renderer & Menu Alat`, `Tes E2E & Runner Engine`, `Riwayat Rilis & Keamanan Renderer`, `Parser Bupot & Penamaan`, `Build Rilis & package.json`?**
  _High betweenness centrality (0.168) - this node is a cross-community bridge._
- **Why does `ExpCore` connect `Engine ExpCore & Pembaca Paralel` to `Dokumentasi, Fixture & Acuan Excel`, `Parser Bupot & Penamaan`?**
  _High betweenness centrality (0.162) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `ExpCore` (e.g. with `main()` and `main()`) actually correct?**
  _`ExpCore` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `Release 3.0.0 (2026-10-09, Electron)` (e.g. with `ExpCore 3.0.0 Release Notes` and `Visual Tokens (@theme in styles.css)`) actually correct?**
  _`Release 3.0.0 (2026-10-09, Electron)` has 2 INFERRED edges - model-reasoned connections that need verification._