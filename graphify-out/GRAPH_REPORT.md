# Graph Report - ExpCore-1  (2026-10-08)

## Corpus Check
- Corpus is ~19,506 words - fits in a single context window. You may not need a graph.

## Summary
- 268 nodes · 384 edges · 13 communities (12 shown, 1 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 38 edges (avg confidence: 0.78)
- Token cost: 106,502 input · 0 output

## Community Hubs (Navigation)
- Desain Antarmuka Workspace
- Parser PDF & Engine Python
- Konfigurasi Installer NSIS
- Proses Main Electron
- Tes Alur Update
- Metadata & Dependency npm
- Tes E2E Aplikasi
- Logika Renderer
- Build Rilis & Fixture PDF
- Runner Engine & Kontraknya
- Lisensi Apache 2.0
- Isolasi Keamanan Renderer
- Jembatan Preload

## God Nodes (most connected - your core abstractions)
1. `ExpCore` - 25 edges
2. `build` - 11 edges
3. `main()` - 11 edges
4. `startJob()` - 9 edges
5. `registerIpc()` - 9 edges
6. `nsis` - 9 edges
7. `Automatic Updates` - 9 edges
8. `init()` - 7 edges
9. `Python Engine (expcore_engine.py -> ExpCore.py)` - 7 edges
10. `ExpCore - Toolkit PDF Coretax (README)` - 7 edges

## Surprising Connections (you probably didn't know these)
- `main()` --uses--> `ExpCore`  [INFERRED]
  expcore_engine.py → ExpCore.py
- `tool-page Template (picker, activity log, run/apply footer)` --implements--> `Independently Scrolling Activity Log`  [INFERRED]
  app/renderer/index.html → DESIGN.md
- `tool-page Template (picker, activity log, run/apply footer)` --implements--> `Folder Field and Picker Control`  [INFERRED]
  app/renderer/index.html → DESIGN.md
- `tool-page Template (picker, activity log, run/apply footer)` --implements--> `Inline Results (Open Excel/CSV, Copy Log)`  [INFERRED]
  app/renderer/index.html → DESIGN.md
- `Electron Migration Verification (8 Oct 2026)` --references--> `151 PDF Samples Regression (--pdf-samples)`  [INFERRED]
  DESIGN.md → README.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Electron Layered Architecture (renderer -> preload -> main -> runner -> engine)** — design_renderer_sandbox, design_preload_bridge, design_main_process, design_engine_runner, design_python_engine [EXTRACTED 1.00]
- **ExpCore Four Document Tools** — readme_bukti_potong_2026, readme_bukti_potong_2024, readme_pajak_masukan, readme_penamaan_otomatis_bupot [EXTRACTED 1.00]
- **Build, Release and Auto-Update Pipeline** — readme_build_release_pipeline, readme_nuitka, readme_electron_builder, readme_nsis_installer, readme_github_releases, readme_electron_updater, readme_automatic_updates [EXTRACTED 1.00]

## Communities (13 total, 1 thin omitted)

### Community 0 - "Desain Antarmuka Workspace"
Cohesion: 0.05
Nodes (53): Home Page Section (hero, guide, tool-cards), Sidebar Navigation (nav-tools, privacy note), tool-card Template, tool-page Template (picker, activity log, run/apply footer), Topbar (breadcrumb, Periksa update, LOKAL & PRIVAT badge), Update Banner (update-action, Nanti), Awesomic Editorial Style (inspiration), Container-Query Responsive Layout (+45 more)

### Community 1 - "Parser PDF & Engine Python"
Cohesion: 0.11
Nodes (19): main(), Mesin pemroses ExpCore yang dijalankan aplikasi Electron, satu proses per…, ExpCore, Parser PDF Coretax. Aktivitas dan progres dilaporkan lewat callback., Tulis DataFrame ke Excel dengan header, format angka, dan lebar kolom.…, Ambil semua baris objek pajak dari teks satu PDF Bukti Potong., 4 3 6 1 ...' -> '4361...'. Formulir BPBS menulis angka per kotak., 3 1 dd 0 1 mm 2 0 2 4 yyyy' -> '31-01-2024'. Kotak kosong -> ''. (+11 more)

### Community 2 - "Konfigurasi Installer NSIS"
Cohesion: 0.07
Nodes (26): build, appId, copyright, directories, electronLanguages, extraResources, files, nsis (+18 more)

### Community 3 - "Proses Main Electron"
Cohesion: 0.16
Nodes (24): { app, BrowserWindow, clipboard, dialog, ipcMain, screen, session, shell }, { autoUpdater }, checkForUpdate(), cleanFolder(), confirm(), createWindow(), describeUpdateError(), downloadUpdate() (+16 more)

### Community 4 - "Tes Alur Update"
Cohesion: 0.10
Nodes (21): { after, before, describe, it }, assert, CACHE, COPY, CORRUPT, crypto, dialogs(), { _electron: electron } (+13 more)

### Community 5 - "Metadata & Dependency npm"
Cohesion: 0.09
Nodes (22): electron, electron-builder, electron-updater, author, dependencies, electron-updater, description, devDependencies (+14 more)

### Community 6 - "Tes E2E Aplikasi"
Cohesion: 0.11
Nodes (15): { after, afterEach, before, describe, it }, assert, { _electron: electron }, { execFileSync }, fs, launch(), launchArgs(), os (+7 more)

### Community 7 - "Logika Renderer"
Cohesion: 0.23
Nodes (18): appendLog(), browse(), buildTool(), field(), folderChanged(), init(), modules, navigate() (+10 more)

### Community 8 - "Build Rilis & Fixture PDF"
Cohesion: 0.21
Nodes (13): app_version(), build_app(), build_engine(), check_engine(), main(), Build installer Windows: engine Python (Nuitka) lalu aplikasi Electron…, Keempat pekerjaan pada PDF sintetis: import lazy (mis. writer Excel) ikut…, run_engine() (+5 more)

### Community 9 - "Runner Engine & Kontraknya"
Cohesion: 0.27
Nodes (8): lastLines(), readline, runEngine(), { spawn }, assert, fake(), { runEngine }, test

### Community 10 - "Lisensi Apache 2.0"
Cohesion: 0.33
Nodes (6): Apache License, Version 2.0, Copyright 2026 Iyan Sanjaya, Disclaimer of Warranty and Limitation of Liability (Sections 7-8), Non-standard appendix note about Eclipse Public License, Grant of Patent License (Section 3), Redistribution Conditions (Section 4)

### Community 11 - "Isolasi Keamanan Renderer"
Cohesion: 0.50
Nodes (4): Content-Security-Policy Meta Tag, Preload Bridge (window.expcore API), Sandboxed Renderer (app/renderer, contextIsolation), Strict CSP and Navigation Lockdown

## Ambiguous Edges - Review These
- `Apache License, Version 2.0` → `Non-standard appendix note about Eclipse Public License`  [AMBIGUOUS]
  LICENSE.txt · relation: references

## Knowledge Gaps
- **90 isolated node(s):** `{ spawn }`, `readline`, `fs`, `path`, `{ app, BrowserWindow, clipboard, dialog, ipcMain, screen, session, shell }` (+85 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Apache License, Version 2.0` and `Non-standard appendix note about Eclipse Public License`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **Why does `build` connect `Konfigurasi Installer NSIS` to `Metadata & Dependency npm`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._
- **Why does `write_all()` connect `Build Rilis & Fixture PDF` to `Parser PDF & Engine Python`?**
  _High betweenness centrality (0.012) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `ExpCore` (e.g. with `main()` and `main()`) actually correct?**
  _`ExpCore` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `registerIpc()` (e.g. with `downloadUpdate()` and `installUpdate()`) actually correct?**
  _`registerIpc()` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `{ spawn }`, `readline`, `fs` to the rest of the system?**
  _90 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Desain Antarmuka Workspace` be split into smaller, more focused modules?**
  _Cohesion score 0.05224963715529753 - nodes in this community are weakly interconnected._