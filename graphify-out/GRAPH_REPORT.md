# Graph Report - ExpCore-1  (2026-09-10)

## Corpus Check
- Corpus is ~40,627 words - fits in a single context window. You may not need a graph.

## Update Integrity Notes

- Updated 9 new/changed files; 0 deleted sources.
- Final graph: 0 missing endpoints, 0 dangling endpoints, 0 self-loops.
- This extraction omitted 40 external-module import references with no corpus node and combined 2 same-endpoint relation pairs in the existing undirected graph format.
- VERSION and ExpCore.iss are not directly classified by the detector; their configuration concepts are sourced from README/DESIGN documentation.
- Semantic token usage is unavailable; cumulative token totals exclude unreported runs.

## Summary
- 220 nodes · 370 edges · 12 communities (11 shown, 1 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 14 edges (avg confidence: 0.61)
- Token cost: unavailable (subagent usage counters are not exposed; not zero)

## Graph Freshness
- Built from commit: `940c7c6d`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Workspace dan Kontrol UI
- Fitur Ekstraksi dan Penamaan
- Updater Build dan Integrasi UI
- Parser Ekspor dan Pengujian
- Rilis Versi dan Distribusi
- Desain Desktop dan Interaksi
- Pengujian Pemeriksa Update
- Struktur Formulir BPBS
- Lisensi Apache 2.0
- Analisis Historis Alur Penamaan
- Identitas Visual Ikon
- Riwayat Perbaikan Tarif BPBS

## God Nodes (most connected - your core abstractions)
1. `Workspace` - 40 edges
2. `ExpCore 1.6.0: Windows PDF Coretax toolkit` - 25 edges
3. `ExpCore` - 24 edges
4. `ExpCore desktop workspace` - 15 edges
5. `UpdateChecks` - 12 edges
6. `main()` - 10 edges
7. `UpdateResult` - 10 edges
8. `UpdateChecker` - 10 edges
9. `GitHub stable release update checker` - 10 edges
10. `version_tuple()` - 9 edges

## Surprising Connections (you probably didn't know these)
- `ExpCore` --uses--> `Workspace`  [INFERRED]
  ExpCore.py → expcore_ui.py
- `Workspace` --uses--> `UpdateChecker`  [INFERRED]
  expcore_ui.py → expcore_updates.py
- `Workspace` --uses--> `UpdateResult`  [INFERRED]
  expcore_ui.py → expcore_updates.py
- `main()` --uses--> `ExpCore`  [INFERRED]
  test_expcore.py → ExpCore.py
- `test_batch_exports()` --uses--> `ExpCore`  [INFERRED]
  test_expcore.py → ExpCore.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Responsive desktop navigation with nested scrolling and accessible actions** — design_responsive_layout, design_nested_scroll_routing, design_scaled_reflow, design_keyboard_access, design_folder_controls [EXTRACTED 1.00]
- **Nonblocking private validated update notification** — readme_update_checker, readme_update_cache, readme_update_backoff, readme_release_validation, readme_update_privacy, readme_update_banner [EXTRACTED 1.00]
- **Single-version verified release pipeline** — readme_version, readme_build_release, readme_dist, readme_installer_config, readme_release_publication [EXTRACTED 1.00]
- **Analisis Bantahan Jembatan Tunggal ExpCore** — graphify_out_memory_query_20260821_140214_kenapa_expcore_menjadi_jembatan_tunggal_antara_she_premis_jembatan_dibantah, graphify_out_memory_query_20260821_140214_kenapa_expcore_menjadi_jembatan_tunggal_antara_she_uji_hapus_node, graphify_out_memory_query_20260821_140214_kenapa_expcore_menjadi_jembatan_tunggal_antara_she_god_class_betweenness_artifact, graphify_out_memory_query_20260821_140214_kenapa_expcore_menjadi_jembatan_tunggal_antara_she_alur_penamaan_bupot_jembatan_nyata, graphify_out_memory_query_20260821_140214_kenapa_expcore_menjadi_jembatan_tunggal_antara_she_graph_undirected_caveat [EXTRACTED 1.00]
- **ExpCore Brand Identity System** — icon_app_icon, icon_document_export_glyph, icon_dark_theme_branding, icon_visual_identity_rationale [INFERRED 0.85]

## Communities (12 total, 1 thin omitted)

### Community 1 - "Fitur Ekstraksi dan Penamaan"
Cohesion: 0.08
Nodes (34): Betweenness sebagai Artefak God Class, Caveat: Graph Undirected, Arah Edge Tidak Reliabel, Premis Jembatan Tunggal Dibantah, Uji Hapus-Node (Node Deletion Test), Kebijakan historis nama penerima A.2 (2 September 2026), Regresi historis penamaan A.2, Perubahan nama file ke pemotong C.3 (10 September 2026), Verifikasi PDF contoh pemotong C.3 (+26 more)

### Community 2 - "Updater Build dan Integrasi UI"
Cohesion: 0.11
Nodes (20): main(), Build the Windows application using the invoking virtual environment., The local desktop workspace. Tk widgets are only accessed on the UI thread., _NoRedirects, Read-only GitHub release checks. No credentials, PDF data, or executable…, One worker per UI instance; a small per-user cache also limits restart traffic., Stable vMAJOR.MINOR[.PATCH] tags; numeric comparison, never lexicographic., Honor GitHub's Retry-After / rate reset, bounded against malformed headers. (+12 more)

### Community 3 - "Parser Ekspor dan Pengujian"
Cohesion: 0.15
Nodes (13): ExpCore, PDF processing; the inherited workspace owns the desktop interface., Tulis DataFrame ke Excel dengan header, format angka, dan lebar kolom.…, Ambil semua baris objek pajak dari teks satu PDF Bukti Potong., 4 3 6 1 ...' -> '4361...'. Formulir BPBS menulis angka per kotak., 3 1 dd 0 1 mm 2 0 2 4 yyyy' -> '31-01-2024'. Kotak kosong -> ''., Ambil baris objek pajak dari teks satu PDF Bukti Potong formulir BPBS. Berbeda…, main() (+5 more)

### Community 4 - "Rilis Versi dan Distribusi"
Cohesion: 0.14
Nodes (24): Jurang kode-dokumen pada snapshot historis, Betweenness kelas sebagai artefak kepemilikan metode, README sebagai jembatan graph dokumen (28 Agustus 2026), build_release.py consistent Nuitka release build, Diagnosing silent standalone startup crashes, Dependency import preflight, ExpCore.dist standalone distribution, expcore_updates.py GitHub release checks and per-user cache (+16 more)

### Community 5 - "Desain Desktop dan Interaksi"
Cohesion: 0.11
Nodes (23): Additive responsive bind(..., add="+") handlers, Overwrite confirmation and batch completion safeguards, ExpCore desktop workspace, ExpCore.py parser and export, expcore_ui.py desktop interface, 44 px folder field and picker; 14 px radius; 2 px border, Inline results, open Excel/CSV and copy log, Keyboard navigation and shortcuts (+15 more)

### Community 6 - "Pengujian Pemeriksa Update"
Cohesion: 0.20
Nodes (3): Offline release/check/cache regressions. Run with the standard library unittest…, release(), UpdateChecks

### Community 7 - "Struktur Formulir BPBS"
Cohesion: 0.25
Nodes (8): C.5 Pernyataan wajib pajak, kode QR, dan keterangan tanda tangan elektronik, Formulir BPBS: Bukti Pemotongan/Pemungutan PPh Pasal 4 ayat (2), 15, 22, dan 23, Header H.1 nomor 2000000015; H.2 pembetulan ke-0; H.5 PPh Tidak Final terpilih, B.7 Dokumen referensi: nomor 1, Invoice, tanggal 20-02-2024, A. Identitas wajib pajak yang dipotong/dipungut; A.3 Nama: MITRACOLL SARANA JAYA, B. Tabel pajak: masa 2-2024, kode 24-104-18, DPP Rp1.200.000, tarif 2%, PPh Rp24.000, C. Identitas pemotong/pemungut; C.2 Nama Wajib Pajak: SMART MULTI FINANCE, C.3 Tanggal 20-02-2024; C.4 Nama Penandatangan PETRUS DENNY ARIJAWAN BUDIYANTO

### Community 8 - "Lisensi Apache 2.0"
Cohesion: 0.33
Nodes (6): Apache License, Version 2.0, Copyright 2026 Iyan Sanjaya, Disclaimer of Warranty and Limitation of Liability (Sections 7-8), Non-standard appendix note about Eclipse Public License, Grant of Patent License (Section 3), Redistribution Conditions (Section 4)

### Community 9 - "Analisis Historis Alur Penamaan"
Cohesion: 0.50
Nodes (4): Alur Penamaan Bupot sebagai Jembatan Nyata, _page_rename_bupot (betweenness 0.476), process_rename_bupot (betweenness 0.499), Pemakaian Ulang Helper Lintas Komunitas Penamaan-Parser

### Community 10 - "Identitas Visual Ikon"
Cohesion: 0.67
Nodes (4): ExpCore Application Icon, Dark Navy / Periwinkle Brand Palette, Document-with-Chevron Export Glyph, Icon Visual Identity Choice

### Community 11 - "Riwayat Perbaikan Tarif BPBS"
Cohesion: 0.67
Nodes (3): Eksperimen normalisasi tarif integer di memori, Cacat historis regex tarif integer BPBS, Feedback JAN 75/72 dan FEB 76/70

## Ambiguous Edges - Review These
- `Apache License, Version 2.0` → `Non-standard appendix note about Eclipse Public License`  [AMBIGUOUS]
  LICENSE.txt · relation: references

## Knowledge Gaps
- **32 isolated node(s):** `Copyright 2026 Iyan Sanjaya`, `_page_rename_bupot (betweenness 0.476)`, `process_rename_bupot (betweenness 0.499)`, `Disclaimer of Warranty and Limitation of Liability (Sections 7-8)`, `Grant of Patent License (Section 3)` (+27 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Apache License, Version 2.0` and `Non-standard appendix note about Eclipse Public License`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **Why does `Workspace` connect `Workspace dan Kontrol UI` to `Updater Build dan Integrasi UI`, `Parser Ekspor dan Pengujian`?**
  _High betweenness centrality (0.161) - this node is a cross-community bridge._
- **Why does `ExpCore` connect `Parser Ekspor dan Pengujian` to `Workspace dan Kontrol UI`, `Updater Build dan Integrasi UI`?**
  _High betweenness centrality (0.108) - this node is a cross-community bridge._
- **Why does `ExpCore 1.6.0: Windows PDF Coretax toolkit` connect `Fitur Ekstraksi dan Penamaan` to `Rilis Versi dan Distribusi`?**
  _High betweenness centrality (0.051) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `Workspace` (e.g. with `ExpCore` and `UpdateChecker`) actually correct?**
  _`Workspace` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `ExpCore` (e.g. with `Workspace` and `main()`) actually correct?**
  _`ExpCore` has 5 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Copyright 2026 Iyan Sanjaya`, `_page_rename_bupot (betweenness 0.476)`, `process_rename_bupot (betweenness 0.499)` to the rest of the system?**
  _32 weakly-connected nodes found - possible documentation gaps or missing edges._