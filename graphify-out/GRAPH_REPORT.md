# Graph Report - ExpCore-1  (2026-10-12)

## Corpus Check
- 9 files · ~43,314 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 452 nodes · 1014 edges · 17 communities (14 shown, 3 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 111 edges (avg confidence: 0.82)
- Token cost: 146,560 input · 0 output

## Community Hubs (Navigation)
- Dokumentasi, Penamaan & Tes Python
- Antarmuka Renderer & Menu Alat
- Runner Engine & Tes E2E
- Kelas ExpCore & Rekening Koran
- Rilis 3.0.0, Keamanan & Cek Rekening
- Proses Main & Penguncian Job
- Dependency package.json
- Banner & Tes Pembaruan
- Konfigurasi electron-builder
- Changelog & Ekspor Bupot/Faktur
- Build Rilis (Nuitka + electron-builder)
- Arsitektur Proses & Protokol JSON
- Lisensi Apache 2.0
- Ikon Aplikasi
- Meta CSP
- Input Folder
- Halaman Beranda

## God Nodes (most connected - your core abstractions)
1. `ExpCore` - 58 edges
2. `Release 3.0.0 (2026-10-09, Electron)` - 35 edges
3. `ExpCore 3.0.0 Release Notes` - 30 edges
4. `ExpCore - Toolkit PDF Coretax (README)` - 27 edges
5. `Penamaan Otomatis Bupot` - 23 edges
6. `Rekening Koran CIMB Niaga (Combine Statement Portfolio Recap)` - 18 edges
7. `startJob()` - 17 edges
8. `Job Locking (main process is source of truth)` - 16 edges
9. `Query: Impact of changing shared Excel helpers (_write_rekening_excel <-> _write_cimb_excel)` - 16 edges
10. `Query: Diuji (feature -> test) References Remeasure` - 15 edges

## Surprising Connections (you probably didn't know these)
- `Query: README.md Code References Remeasure` --references--> `test_pdf_samples()`  [AMBIGUOUS]
  graphify-out/memory/query_20261008_170442_tambahkan_rujukan_kode_ke_readme_md_lalu_ukur_ulan.md → test_expcore.py
- `Window Sizing (screen/DPI aware, min 960x620)` --references--> `setSize()`  [EXTRACTED]
  DESIGN.md → tests/app.test.js
- `PDF Samples Regression Test (--pdf-samples)` --references--> `test_pdf_samples()`  [EXTRACTED]
  README.md → test_expcore.py
- `Name Source Selection (Identitas Pemotong C.3/C.2 vs Wajib Pajak A.2/A.3)` --references--> `buildNameSources()`  [EXTRACTED]
  DESIGN.md → app/renderer/src/app.js
- `#tool-page Template` --references--> `buildTool()`  [INFERRED]
  app/renderer/index.html → app/renderer/src/app.js

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Bank Statement Recap & Reconciliation (BCA + CIMB)** — readme_rekening_koran, readme_rekening_koran_check, readme_rekening_position_columns, readme_rekening_cimb, readme_cimb_check, readme_cimb_cell_grouping, readme_cimb_section_detection, readme_duplicate_statement_flag, readme_summary_side_panel [INFERRED 0.85]
- **Penamaan Bupot Rename Flow (BPPU + BPBS, chosen name source)** — readme_penamaan_bupot, readme_form_type_detection, design_name_source_selection, readme_bpbs_rename_fields, readme_name_source_no_fallback, design_rename_preview_gate, readme_naming_audit_log [INFERRED 0.85]
- **Shared Excel Helpers of BCA & CIMB Writers** — expcore_expcore_write_rekening_excel, expcore_expcore_write_cimb_excel, expcore_expcore_judul_excel, expcore_expcore_nama_sheet, expcore_expcore_tulis_panel, expcore_expcore_tautan_sheet, expcore_expcore_rapikan_tabel, expcore_expcore_angka [EXTRACTED 1.00]
- **3.0.0 platform replacements (CustomTkinter/Inno Setup/VERSION/old updater -> Electron/NSIS/package.json/electron-updater)** — changelog_v3_0_0, changelog_customtkinter_ui, changelog_inno_setup, changelog_version_file, changelog_legacy_update_checker, design_renderer_layer, readme_nsis_installer, readme_package_json_version, readme_auto_update [EXTRACTED 1.00]
- **Electron process pipeline (Renderer -> Preload -> Main -> Runner -> Python Engine)** — design_renderer_layer, design_preload_bridge, design_main_process, design_engine_runner, design_python_engine, design_json_line_protocol [EXTRACTED 1.00]
- **Electron process chain Renderer -> Preload -> Main -> Runner -> Engine** — design_renderer_layer, design_preload_bridge, design_main_process, design_engine_runner, design_python_engine, design_json_line_protocol [EXTRACTED 1.00]
- **Never-guess data safeguards (skip or flag instead of inferring)** — readme_no_guess_principle, readme_name_source_no_fallback, readme_sifat_checkbox_rule, readme_wrapped_description_rule, readme_format_mismatch_skip, readme_cimb_check [INFERRED 0.85]

## Communities (17 total, 3 thin omitted)

### Community 0 - "Dokumentasi, Penamaan & Tes Python"
Cohesion: 0.07
Nodes (52): Release 1.5 (2026-09-02), Release 2.0.0 (2026-09-10, CustomTkinter), ExpCore Desktop Workspace (DESIGN.md), Name Source Selection (Identitas Pemotong C.3/C.2 vs Wajib Pajak A.2/A.3), Python Test Suite (test_expcore.py), Verification Results 9 Oct 2026 (Penamaan Bupot BPPU + BPBS), Field nama file Penamaan Bupot dari BPPU (Bupot 2026) atau BPBS (Bupot 2024).…, Field nama file dari BPBS. Tidak menebak: data yang ambigu dibiarkan kosong… (+44 more)

### Community 1 - "Antarmuka Renderer & Menu Alat"
Cohesion: 0.07
Nodes (54): cleanFolder(), MODULES, Name Source Fieldset (Ambil nama file dari), #nav-indicator Sliding Pill, Progress Bar (role=progressbar), Status Pill (data-state), #tool-card Template, #tools-trigger / #tools-menu Disclosure (+46 more)

### Community 2 - "Runner Engine & Tes E2E"
Cohesion: 0.06
Nodes (46): lastLines(), readline, runEngine(), { spawn }, Activity Log (role=log), #main-nav Pill Navigation, #tool-page Template, Release 2.0.1 (2026-09-10) (+38 more)

### Community 3 - "Kelas ExpCore & Rekening Koran"
Cohesion: 0.09
Nodes (23): Python Engine (one process per job), main(), Mesin pemroses ExpCore yang dijalankan aplikasi Electron, satu proses per…, ExpCore, Judul tebal, baris judul dibekukan, filter, dan lebar kolom mengikuti isi…, Sheet Ringkasan + satu sheet per PDF (tabel mutasi, panel informasi & ringkasan…, Garis horizontal tabel (batas sel) di halaman, urut dari atas: [(y, [(x0, x1),…, Tepi kolom tabel mutasi dari garis tepat di bawah judulnya; None bila… (+15 more)

### Community 4 - "Rilis 3.0.0, Keamanan & Cek Rekening"
Cohesion: 0.10
Nodes (39): Release Assets (ExpCore-Setup-3.0.0.exe, .blockmap, latest.yml), ExpCore 3.0.0 Release Notes, createWindow(), index.html Renderer Shell, Lokal & privat Badge, Kenapa ExpCore? Panel, Bun Package Manager (bun.lock), CustomTkinter UI (expcore_ui.py, removed in 3.0.0) (+31 more)

### Community 5 - "Proses Main & Penguncian Job"
Cohesion: 0.12
Nodes (38): { app, BrowserWindow, clipboard, dialog, ipcMain, screen, session, shell }, { autoUpdater }, checkForUpdate(), confirm(), describeUpdateError(), downloadUpdate(), errorText(), fs (+30 more)

### Community 6 - "Dependency package.json"
Cohesion: 0.06
Nodes (35): electron, electron-builder, electron-updater, esbuild, @fontsource-variable/inter, motion, author, dependencies (+27 more)

### Community 7 - "Banner & Tes Pembaruan"
Cohesion: 0.09
Nodes (28): #update-banner, onUpdateEvent(), showUpdate(), Update Banner (spring, non-overlapping), { after, before, describe, it }, assert, bannerText(), CACHE (+20 more)

### Community 8 - "Konfigurasi electron-builder"
Cohesion: 0.07
Nodes (27): build, appId, copyright, directories, electronLanguages, extraResources, files, nsis (+19 more)

### Community 9 - "Changelog & Ekspor Bupot/Faktur"
Cohesion: 0.13
Nodes (18): ExpCore Changelog, Release 1.0 (2026-06-10, initial), Release 1.1 (2026-06-10), Release 1.1.1 (2026-06-10), Release 1.2 (2026-07-07), Release 1.3 (2026-08-21), Release 1.4 (2026-08-28), Tulis DataFrame ke Excel dengan header, format angka, dan lebar kolom.… (+10 more)

### Community 10 - "Build Rilis (Nuitka + electron-builder)"
Cohesion: 0.17
Nodes (18): engineCommand(), app_version(), build_app(), build_engine(), check_engine(), main(), Build installer Windows: engine Python (Nuitka) lalu aplikasi Electron…, Keenam pekerjaan pada PDF sintetis: import lazy (mis. writer Excel) ikut teruji. (+10 more)

### Community 11 - "Arsitektur Proses & Protokol JSON"
Cohesion: 0.29
Nodes (6): { contextBridge, ipcRenderer }, Electron Process Architecture (Renderer/Preload/Main/Runner/Engine), Engine Runner (app/engine.js), JSON-per-line Engine Protocol, Preload Bridge (window.expcore API), Engine JSON-per-line Protocol (expcore_engine.py)

### Community 12 - "Lisensi Apache 2.0"
Cohesion: 0.33
Nodes (6): Apache License, Version 2.0, Copyright 2026 Iyan Sanjaya, Disclaimer of Warranty and Limitation of Liability (Sections 7-8), Non-standard appendix note about Eclipse Public License, Grant of Patent License (Section 3), Redistribution Conditions (Section 4)

### Community 13 - "Ikon Aplikasi"
Cohesion: 0.67
Nodes (3): Document Glyph (folded corner + text lines), ExpCore App Icon (SVG), Purple Gradient Rounded Tile (#8270f9 to #5944e0)

## Ambiguous Edges - Review These
- `Query: README.md Code References Remeasure` → `test_pdf_samples()`  [AMBIGUOUS]
  graphify-out/memory/query_20261008_170442_tambahkan_rujukan_kode_ke_readme_md_lalu_ukur_ulan.md · relation: references
- `Apache License, Version 2.0` → `Non-standard appendix note about Eclipse Public License`  [AMBIGUOUS]
  LICENSE.txt · relation: references

## Knowledge Gaps
- **111 isolated node(s):** `#main-nav Pill Navigation`, `Name Source Fieldset (Ambil nama file dari)`, `#nav-indicator Sliding Pill`, `index.html Renderer Shell`, `Status Pill (data-state)` (+106 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Query: README.md Code References Remeasure` and `test_pdf_samples()`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **What is the exact relationship between `Apache License, Version 2.0` and `Non-standard appendix note about Eclipse Public License`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **Why does `Renderer Build (bun run build:renderer)` connect `Build Rilis (Nuitka + electron-builder)` to `Changelog & Ekspor Bupot/Faktur`?**
  _High betweenness centrality (0.242) - this node is a cross-community bridge._
- **Why does `build:renderer` connect `Build Rilis (Nuitka + electron-builder)` to `Dependency package.json`?**
  _High betweenness centrality (0.237) - this node is a cross-community bridge._
- **Why does `scripts` connect `Dependency package.json` to `Build Rilis (Nuitka + electron-builder)`?**
  _High betweenness centrality (0.236) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `ExpCore` (e.g. with `main()` and `main()`) actually correct?**
  _`ExpCore` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `Release 3.0.0 (2026-10-09, Electron)` (e.g. with `ExpCore 3.0.0 Release Notes` and `Job Locking (main process is source of truth)`) actually correct?**
  _`Release 3.0.0 (2026-10-09, Electron)` has 3 INFERRED edges - model-reasoned connections that need verification._