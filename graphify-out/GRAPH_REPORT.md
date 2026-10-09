# Graph Report - ExpCore-1  (2026-10-09)

## Corpus Check
- Corpus is ~32,287 words - fits in a single context window. You may not need a graph.

## Summary
- 371 nodes · 723 edges · 11 communities
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 58 edges (avg confidence: 0.81)
- Token cost: 114,341 input · 0 output

## Community Hubs (Navigation)
- Parser PDF, Engine & Tes Python
- Antarmuka Renderer & Menu Alat
- Halaman Alat & Tes E2E
- Proses Main Electron
- Pembaruan Otomatis & Rilis
- Build Rilis, Preload & Keamanan
- Shell Renderer, Ikon & Dependency
- Runner Engine & Kontraknya
- Konfigurasi electron-builder
- Metadata package.json
- Lisensi Apache 2.0

## God Nodes (most connected - your core abstractions)
1. `ExpCore` - 33 edges
2. `startJob()` - 17 edges
3. `Job Locking (main process is source of truth)` - 16 edges
4. `Tools Menu (disclosure pattern, grouped)` - 14 edges
5. `main()` - 12 edges
6. `buildTool()` - 12 edges
7. `runTo()` - 12 edges
8. `Rename Requires Completed Preview` - 12 edges
9. `init()` - 11 edges
10. `registerIpc()` - 11 edges

## Surprising Connections (you probably didn't know these)
- `test_pdf_samples()` --references--> `Query: README.md Code References Remeasure`  [AMBIGUOUS]
  test_expcore.py → graphify-out/memory/query_20261008_170442_tambahkan_rujukan_kode_ke_readme_md_lalu_ukur_ulan.md
- `setSize()` --references--> `Window Sizing (screen/DPI aware, min 960x620)`  [EXTRACTED]
  tests/app.test.js → DESIGN.md
- `test_engine_protocol()` --references--> `Rename Requires Completed Preview`  [EXTRACTED]
  test_expcore.py → DESIGN.md
- `test_rename_pemotong()` --references--> `Name Source Selection (C.3 Pemotong / A.2 Wajib Pajak)`  [EXTRACTED]
  test_expcore.py → DESIGN.md
- `folderChanged()` --references--> `Folder Field (type, paste Copy-as-path, native dialog)`  [EXTRACTED]
  app/renderer/src/app.js → DESIGN.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Electron Process Architecture Layers** — design_renderer_layer, design_preload_bridge, design_main_process, design_engine_runner, design_python_engine [EXTRACTED 1.00]
- **Build-to-Update Release Flow** — readme_build_release, readme_package_json_version, readme_nsis_installer, readme_release_publishing, readme_auto_update [EXTRACTED 1.00]
- **Five ExpCore Tools (Ekstraksi ke Excel / Kelola PDF)** — readme_bukti_potong_2026, readme_bukti_potong_2024, readme_pajak_masukan, readme_rekening_koran, readme_penamaan_bupot [EXTRACTED 1.00]

## Communities (11 total, 0 thin omitted)

### Community 0 - "Parser PDF, Engine & Tes Python"
Cohesion: 0.06
Nodes (53): ExpCore, main(), main(), read_rekening(), run_engine(), sheet_row(), test_batch_exports(), test_engine_protocol() (+45 more)

### Community 1 - "Antarmuka Renderer & Menu Alat"
Cohesion: 0.08
Nodes (49): appendLog(), buildMenuItem(), closeMenu(), field(), folderChanged(), init(), menuItems(), menuList() (+41 more)

### Community 2 - "Halaman Alat & Tes E2E"
Cohesion: 0.08
Nodes (42): browse(), buildNameSources(), buildTool(), nameSourceChanged(), fixtures(), focused(), logBaseline(), runTo() (+34 more)

### Community 3 - "Proses Main Electron"
Cohesion: 0.11
Nodes (42): checkForUpdate(), cleanFolder(), confirm(), createWindow(), describeUpdateError(), downloadUpdate(), errorText(), handle() (+34 more)

### Community 4 - "Pembaruan Otomatis & Rilis"
Cohesion: 0.08
Nodes (34): onUpdateEvent(), showUpdate(), bannerText(), dialogs(), eventually(), handle(), latestYml(), manualCheck() (+26 more)

### Community 5 - "Build Rilis, Preload & Keamanan"
Cohesion: 0.08
Nodes (31): engineCommand(), app_version(), build_app(), build_engine(), check_engine(), main(), run_engine(), launch() (+23 more)

### Community 6 - "Shell Renderer, Ikon & Dependency"
Cohesion: 0.07
Nodes (30): hydrateIcons(), index.html Renderer Shell, win, devDependencies, electron, electron-builder, esbuild, @fontsource-variable/inter (+22 more)

### Community 9 - "Runner Engine & Kontraknya"
Cohesion: 0.28
Nodes (7): lastLines(), runEngine(), readline, { spawn }, assert, { runEngine }, test

### Community 7 - "Konfigurasi electron-builder"
Cohesion: 0.08
Nodes (23): build, appId, copyright, directories, electronLanguages, extraResources, files, nsis (+15 more)

### Community 8 - "Metadata package.json"
Cohesion: 0.11
Nodes (17): author, dependencies, electron-updater, description, license, main, name, private (+9 more)

### Community 10 - "Lisensi Apache 2.0"
Cohesion: 0.29
Nodes (7): Copyright 2026 Iyan Sanjaya, Disclaimer of Warranty and Limitation of Liability (Sections 7-8), Grant of Patent License (Section 3), Redistribution Conditions (Section 4), Apache License, Version 2.0, Non-standard appendix note about Eclipse Public License, Apache License 2.0

## Ambiguous Edges - Review These
- `test_pdf_samples()` → `Query: README.md Code References Remeasure`  [AMBIGUOUS]
  graphify-out/memory/query_20261008_170442_tambahkan_rujukan_kode_ke_readme_md_lalu_ukur_ulan.md · relation: references
- `Apache License, Version 2.0` → `Non-standard appendix note about Eclipse Public License`  [AMBIGUOUS]
  LICENSE.txt · relation: references

## Knowledge Gaps
- **111 isolated node(s):** `#main-nav Pill Navigation`, `#page-home Landing`, `#tool-card Template`, `Activity Log (role=log)`, `Folder Input & Pilih folder Button` (+106 more)
  These have ≤1 connection - possible missing edges or undocumented components.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `test_pdf_samples()` and `Query: README.md Code References Remeasure`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **What is the exact relationship between `Apache License, Version 2.0` and `Non-standard appendix note about Eclipse Public License`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **Why does `App Icon (icon.svg source, icon.ico 15 sizes)` connect `Shell Renderer, Ikon & Dependency` to `Proses Main Electron`, `Build Rilis, Preload & Keamanan`?**
  _High betweenness centrality (0.228) - this node is a cross-community bridge._
- **Why does `devDependencies` connect `Shell Renderer, Ikon & Dependency` to `Metadata package.json`?**
  _High betweenness centrality (0.149) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `ExpCore` (e.g. with `main()` and `test_pdf_samples()`) actually correct?**
  _`ExpCore` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `Job Locking (main process is source of truth)` (e.g. with `Run Button` and `Five-Tool Workspace (Ekstraksi ke Excel / Kelola PDF)`) actually correct?**
  _`Job Locking (main process is source of truth)` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `Tools Menu (disclosure pattern, grouped)` (e.g. with `#tools-trigger / #tools-menu Disclosure` and `Five-Tool Workspace (Ekstraksi ke Excel / Kelola PDF)`) actually correct?**
  _`Tools Menu (disclosure pattern, grouped)` has 2 INFERRED edges - model-reasoned connections that need verification._