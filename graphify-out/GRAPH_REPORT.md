# Graph Report - ExpCore-1  (2026-10-09)

## Corpus Check
- 1 files · ~23,854 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 311 nodes · 515 edges · 13 communities
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 44 edges (avg confidence: 0.79)
- Token cost: 84,567 input · 0 output

## Community Hubs (Navigation)
- Antarmuka Renderer & Desain
- Parser PDF & Fitur Pajak
- Proses Main Electron
- Konfigurasi Installer NSIS
- Tes E2E Aplikasi
- Tes Alur Update
- Metadata & Skrip npm
- Runner & Protokol Engine
- Dependency Pengembangan
- Build Rilis & Aturan Lingkungan
- Keamanan Renderer & Preload
- Ikhtisar Produk & Fixture Uji
- Lisensi Apache 2.0

## God Nodes (most connected - your core abstractions)
1. `ExpCore` - 26 edges
2. `startJob()` - 13 edges
3. `Motion for JavaScript` - 12 edges
4. `main()` - 11 edges
5. `registerIpc()` - 11 edges
6. `build` - 11 edges
7. `Electron Main Process` - 10 edges
8. `init()` - 9 edges
9. `nsis` - 9 edges
10. `buildTool()` - 8 edges

## Surprising Connections (you probably didn't know these)
- `Python Engine (expcore_engine -> ExpCore)` --references--> `ExpCore`  [EXTRACTED]
  DESIGN.md → ExpCore.py
- `Inline Results` --references--> `onJobEvent()`  [EXTRACTED]
  DESIGN.md → app/renderer/src/app.js
- `Job Locking & Busy Navigation` --references--> `setBusyNav()`  [EXTRACTED]
  DESIGN.md → app/renderer/src/app.js
- `Text-based Status Labels & Contrast` --references--> `setStatus()`  [EXTRACTED]
  DESIGN.md → app/renderer/src/app.js
- `Python Test Suite (test_expcore.py)` --references--> `test_bupot2024_pdf_samples()`  [EXTRACTED]
  DESIGN.md → test_expcore.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Four ExpCore PDF Tools** — readme_bukti_potong_2026, readme_bukti_potong_2024, readme_pajak_masukan, readme_penamaan_bupot [EXTRACTED 1.00]
- **Build, Release and Update Pipeline** — readme_build_release, readme_nuitka_engine_build, readme_nsis_installer, readme_package_json_version, readme_release_publishing, readme_auto_update [EXTRACTED 1.00]
- **Build Environment Safety Rules** — readme_explicit_venv_rule, readme_forward_slash_path_rule, readme_nuitka_engine_build [EXTRACTED 1.00]
- **Build, Release and Auto-Update Pipeline** — readme_nsis_installer [EXTRACTED 1.00]
- **Electron IPC Process Architecture** — design_renderer_layer, design_preload_bridge, design_main_process, design_engine_runner, design_python_engine [EXTRACTED 1.00]
- **Motion-animated UI Elements** — design_motion_animation, design_home_landing, design_header_nav, design_status_pill, design_update_banner, design_reduced_motion [EXTRACTED 1.00]
- **Electron Renderer-Preload-Main-Runner-Engine Architecture** — design_renderer_layer, design_preload_bridge, design_main_process, design_engine_runner, design_python_engine [EXTRACTED 1.00]
- **Electron Layered Architecture (renderer -> preload -> main -> runner -> engine)** — design_preload_bridge, design_main_process, design_engine_runner, design_python_engine [EXTRACTED 1.00]
- **ExpCore Four PDF Tools** — readme_bukti_potong_2026, readme_bukti_potong_2024, readme_pajak_masukan, readme_penamaan_bupot [EXTRACTED 1.00]
- **Release Build Pipeline** — readme_build_release, readme_nuitka_engine_build, design_build_renderer, readme_nsis_installer, readme_package_json_version [EXTRACTED 1.00]
- **Job Safety Guards (main process as source of truth)** — design_job_locking, design_rename_preview_gate, design_native_confirmation, design_main_process [INFERRED 0.85]

## Communities (13 total, 0 thin omitted)

### Community 0 - "Antarmuka Renderer & Desain"
Cohesion: 0.08
Nodes (48): Activity Log (role=log), Terapkan nama Apply Button, Folder Input and Browse (Ctrl+O), #main-nav with #nav-indicator, #page-home (hero, tool cards, why, CTA, footer), Status Pill (data-state idle/ready/running/done/empty/error), #tool-card Template, #tool-page Template (+40 more)

### Community 1 - "Parser PDF & Fitur Pajak"
Cohesion: 0.08
Nodes (29): ExpCore, Parser PDF Coretax. Aktivitas dan progres dilaporkan lewat callback., Tulis DataFrame ke Excel dengan header, format angka, dan lebar kolom.…, Ambil semua baris objek pajak dari teks satu PDF Bukti Potong., 4 3 6 1 ...' -> '4361...'. Formulir BPBS menulis angka per kotak., 3 1 dd 0 1 mm 2 0 2 4 yyyy' -> '31-01-2024'. Kotak kosong -> ''., Ambil baris objek pajak dari teks satu PDF Bukti Potong formulir BPBS. Berbeda…, Bukti Potong 2024 (BPBS pra-Coretax) (+21 more)

### Community 2 - "Proses Main Electron"
Cohesion: 0.13
Nodes (34): { app, BrowserWindow, clipboard, dialog, ipcMain, screen, session, shell }, { autoUpdater }, checkForUpdate(), cleanFolder(), confirm(), createWindow(), describeUpdateError(), downloadUpdate() (+26 more)

### Community 3 - "Konfigurasi Installer NSIS"
Cohesion: 0.07
Nodes (27): build, appId, copyright, directories, electronLanguages, extraResources, files, nsis (+19 more)

### Community 4 - "Tes E2E Aplikasi"
Cohesion: 0.11
Nodes (19): npm test E2E Suite, { after, afterEach, before, beforeEach, describe, it }, assert, { _electron: electron }, { execFileSync }, fs, launch(), launchArgs() (+11 more)

### Community 5 - "Tes Alur Update"
Cohesion: 0.10
Nodes (23): { after, before, describe, it }, assert, CACHE, COPY, CORRUPT, crypto, dialogs(), { _electron: electron } (+15 more)

### Community 6 - "Metadata & Skrip npm"
Cohesion: 0.11
Nodes (17): electron-updater, author, dependencies, electron-updater, description, license, main, name (+9 more)

### Community 7 - "Runner & Protokol Engine"
Cohesion: 0.15
Nodes (14): lastLines(), readline, runEngine(), { spawn }, Engine Runner, Per-line JSON Engine Protocol, Python Engine (expcore_engine -> ExpCore), main() (+6 more)

### Community 8 - "Dependency Pengembangan"
Cohesion: 0.12
Nodes (17): electron, electron-builder, esbuild, @fontsource-variable/inter, motion, devDependencies, electron, electron-builder (+9 more)

### Community 9 - "Build Rilis & Aturan Lingkungan"
Cohesion: 0.17
Nodes (15): app_version(), build_app(), build_engine(), check_engine(), main(), Build installer Windows: engine Python (Nuitka) lalu aplikasi Electron…, Keempat pekerjaan pada PDF sintetis: import lazy (mis. writer Excel) ikut…, run_engine() (+7 more)

### Community 10 - "Keamanan Renderer & Preload"
Cohesion: 0.18
Nodes (13): { contextBridge, ipcRenderer }, Content-Security-Policy meta tag, Renderer Page (index.html), hydrateIcons(), build:renderer Pipeline, Inter Variable Font, Preload Bridge (window.expcore), Reicon Icons (+5 more)

### Community 11 - "Ikhtisar Produk & Fixture Uji"
Cohesion: 0.18
Nodes (13): #check-update Button, Lokal & privat Badge, Auto Update (electron-updater), Electron E2E Tests (npm test), ExpCore (Toolkit PDF Coretax), Local-only Processing, GitHub Release Publishing, Renderer Build (Tailwind CLI + esbuild) (+5 more)

### Community 12 - "Lisensi Apache 2.0"
Cohesion: 0.33
Nodes (6): Apache License, Version 2.0, Copyright 2026 Iyan Sanjaya, Disclaimer of Warranty and Limitation of Liability (Sections 7-8), Non-standard appendix note about Eclipse Public License, Grant of Patent License (Section 3), Redistribution Conditions (Section 4)

## Ambiguous Edges - Review These
- `Apache License, Version 2.0` → `Non-standard appendix note about Eclipse Public License`  [AMBIGUOUS]
  LICENSE.txt · relation: references

## Knowledge Gaps
- **102 isolated node(s):** `#tool-card Template`, `#update-banner Section`, `Content-Security-Policy meta tag`, `Lokal & privat Badge`, `#check-update Button` (+97 more)
  These have ≤1 connection - possible missing edges or undocumented components.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Apache License, Version 2.0` and `Non-standard appendix note about Eclipse Public License`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **Why does `ExpCore` connect `Parser PDF & Fitur Pajak` to `Runner & Protokol Engine`?**
  _High betweenness centrality (0.171) - this node is a cross-community bridge._
- **Why does `build` connect `Konfigurasi Installer NSIS` to `Metadata & Skrip npm`?**
  _High betweenness centrality (0.162) - this node is a cross-community bridge._
- **Why does `Electron E2E Tests (npm test)` connect `Ikhtisar Produk & Fixture Uji` to `Tes E2E Aplikasi`?**
  _High betweenness centrality (0.160) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `ExpCore` (e.g. with `main()` and `main()`) actually correct?**
  _`ExpCore` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `registerIpc()` (e.g. with `downloadUpdate()` and `installUpdate()`) actually correct?**
  _`registerIpc()` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `#tool-card Template`, `#update-banner Section`, `Content-Security-Policy meta tag` to the rest of the system?**
  _102 weakly-connected nodes found - possible documentation gaps or missing edges._