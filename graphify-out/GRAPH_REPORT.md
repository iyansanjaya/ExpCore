# Graph Report - ExpCore-1  (2026-09-10)

## Corpus Check
- Corpus is ~38,070 words - fits in a single context window. You may not need a graph.

## Update Integrity Notes

- Updated 11 new/changed files; pruned 9 nodes from deleted `contoh_pdf.pdf`.
- Final graph: no missing endpoints, dangling endpoints, self-loops, or duplicate edges.
- Extraction limitations: 32 external-module import references have no corpus nodes and were omitted by the builder; 2 pairs of distinct relations were combined by the existing undirected graph format.
- Semantic token usage is unavailable because the collaboration tool exposes no usage counters. Cost totals exclude this unreported run.

## Summary
- 142 nodes · 227 edges · 10 communities (9 shown, 1 thin omitted)
- Extraction: 95% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 10 edges (avg confidence: 0.64)
- Token cost: unavailable (subagent usage counters are not exposed; not zero)

## Community Hubs (Navigation)
- Workspace dan Kontrol UI
- Dokumentasi Produk dan Build
- Parser Ekspor dan Pengujian
- Desain Desktop dan Responsivitas
- Penamaan Bupot dan Audit
- Entrypoint dan Pengujian UI
- Struktur Formulir BPBS
- Lisensi Apache 2.0
- Analisis Historis Alur Penamaan
- Identitas Visual Ikon

## God Nodes (most connected - your core abstractions)
1. `Workspace` - 34 edges
2. `ExpCore` - 25 edges
3. `ExpCore (Toolkit PDF Coretax)` - 18 edges
4. `main()` - 10 edges
5. `ExpCore Desktop Workspace` - 10 edges
6. `Formulir BPBS: Bukti Pemotongan/Pemungutan PPh Pasal 4 ayat (2), 15, 22, dan 23` - 7 edges
7. `Penamaan Otomatis Bupot` - 6 edges
8. `Apache License, Version 2.0` - 5 edges
9. `test_rename_pemotong()` - 5 edges
10. `Bukti Potong 2024 / BPBS pra-Coretax` - 5 edges

## Surprising Connections (you probably didn't know these)
- `ExpCore` --uses--> `Workspace`  [INFERRED]
  ExpCore.py → expcore_ui.py
- `main()` --uses--> `ExpCore`  [INFERRED]
  test_expcore_ui.py → ExpCore.py
- `main()` --uses--> `ExpCore`  [INFERRED]
  test_expcore.py → ExpCore.py
- `test_batch_exports()` --uses--> `ExpCore`  [INFERRED]
  test_expcore.py → ExpCore.py
- `test_bupot2024_pdf_samples()` --uses--> `ExpCore`  [INFERRED]
  test_expcore.py → ExpCore.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Sistem scroll responsif dan verifikasi DPI** — design_responsive_scroll_layout, design_additive_layout_bindings, design_nested_scroll_handoff, design_scroll_verification_20260908 [EXTRACTED 1.00]
- **Alur penamaan: pratinjau, C.3 wajib, benturan aman, audit** — readme_rename_bupot, design_rename_preview_gate, readme_pemotong_c3, readme_collision_suffix, readme_rename_audit_csv [EXTRACTED 1.00]
- **Analisis Bantahan Jembatan Tunggal ExpCore** — graphify_out_memory_query_20260821_140214_kenapa_expcore_menjadi_jembatan_tunggal_antara_she_premis_jembatan_dibantah, graphify_out_memory_query_20260821_140214_kenapa_expcore_menjadi_jembatan_tunggal_antara_she_uji_hapus_node, graphify_out_memory_query_20260821_140214_kenapa_expcore_menjadi_jembatan_tunggal_antara_she_god_class_betweenness_artifact, graphify_out_memory_query_20260821_140214_kenapa_expcore_menjadi_jembatan_tunggal_antara_she_alur_penamaan_bupot_jembatan_nyata, graphify_out_memory_query_20260821_140214_kenapa_expcore_menjadi_jembatan_tunggal_antara_she_graph_undirected_caveat [EXTRACTED 1.00]
- **ExpCore Brand Identity System** — icon_app_icon, icon_document_export_glyph, icon_dark_theme_branding, icon_visual_identity_rationale [INFERRED 0.85]

## Communities (10 total, 1 thin omitted)

### Community 1 - "Dokumentasi Produk dan Build"
Cohesion: 0.09
Nodes (30): Betweenness sebagai Artefak God Class, Caveat: Graph Undirected, Arah Edge Tidak Reliabel, Premis Jembatan Tunggal Dibantah, Uji Hapus-Node (Node Deletion Test), Jurang kode-dokumen pada snapshot historis, Betweenness kelas sebagai artefak kepemilikan metode, README sebagai jembatan graph dokumen (28 Agustus 2026), Eksperimen normalisasi tarif integer di memori (+22 more)

### Community 2 - "Parser Ekspor dan Pengujian"
Cohesion: 0.15
Nodes (13): ExpCore, PDF processing; the inherited workspace owns the desktop interface., Tulis DataFrame ke Excel dengan header, format angka, dan lebar kolom.…, Ambil semua baris objek pajak dari teks satu PDF Bukti Potong., 4 3 6 1 ...' -> '4361...'. Formulir BPBS menulis angka per kotak., 3 1 dd 0 1 mm 2 0 2 4 yyyy' -> '31-01-2024'. Kotak kosong -> ''., Ambil baris objek pajak dari teks satu PDF Bukti Potong formulir BPBS. Berbeda…, main() (+5 more)

### Community 3 - "Desain Desktop dan Responsivitas"
Cohesion: 0.22
Nodes (11): Binding layout add=+, Batch melanjutkan sesudah PDF gagal, ExpCore Desktop Workspace, Kontrol folder dengan renderer polygon canvas, Sistem visual editorial zinc dan aksen oranye, Segoe UI native Windows, Penerusan scroll dari log ke halaman, Status sesi terpisah untuk empat alat (+3 more)

### Community 4 - "Penamaan Bupot dan Audit"
Cohesion: 0.28
Nodes (9): Pratinjau sebagai syarat penerapan nama, Kebijakan historis nama penerima A.2 (2 September 2026), Regresi historis penamaan A.2, Perubahan nama file ke pemotong C.3 (10 September 2026), Verifikasi PDF contoh pemotong C.3, Nomor tambahan untuk benturan nama, Nama Pemotong C.3 sebagai awalan nama PDF, Log audit CSV penamaan (+1 more)

### Community 5 - "Entrypoint dan Pengujian UI"
Cohesion: 0.32
Nodes (5): The local desktop workspace. Tk widgets are only accessed on the UI thread., check_scrolling(), main(), Desktop smoke checks. Run with a working Tcl/Tk installation; no source PDFs…, wait_for()

### Community 6 - "Struktur Formulir BPBS"
Cohesion: 0.25
Nodes (8): C.5 Pernyataan wajib pajak, kode QR, dan keterangan tanda tangan elektronik, Formulir BPBS: Bukti Pemotongan/Pemungutan PPh Pasal 4 ayat (2), 15, 22, dan 23, Header H.1 nomor 2000000015; H.2 pembetulan ke-0; H.5 PPh Tidak Final terpilih, B.7 Dokumen referensi: nomor 1, Invoice, tanggal 20-02-2024, A. Identitas wajib pajak yang dipotong/dipungut; A.3 Nama: MITRACOLL SARANA JAYA, B. Tabel pajak: masa 2-2024, kode 24-104-18, DPP Rp1.200.000, tarif 2%, PPh Rp24.000, C. Identitas pemotong/pemungut; C.2 Nama Wajib Pajak: SMART MULTI FINANCE, C.3 Tanggal 20-02-2024; C.4 Nama Penandatangan PETRUS DENNY ARIJAWAN BUDIYANTO

### Community 7 - "Lisensi Apache 2.0"
Cohesion: 0.33
Nodes (6): Apache License, Version 2.0, Copyright 2026 Iyan Sanjaya, Disclaimer of Warranty and Limitation of Liability (Sections 7-8), Non-standard appendix note about Eclipse Public License, Grant of Patent License (Section 3), Redistribution Conditions (Section 4)

### Community 8 - "Analisis Historis Alur Penamaan"
Cohesion: 0.50
Nodes (4): Alur Penamaan Bupot sebagai Jembatan Nyata, _page_rename_bupot (betweenness 0.476), process_rename_bupot (betweenness 0.499), Pemakaian Ulang Helper Lintas Komunitas Penamaan-Parser

### Community 9 - "Identitas Visual Ikon"
Cohesion: 0.67
Nodes (4): ExpCore Application Icon, Dark Navy / Periwinkle Brand Palette, Document-with-Chevron Export Glyph, Icon Visual Identity Choice

## Ambiguous Edges - Review These
- `Apache License, Version 2.0` → `Non-standard appendix note about Eclipse Public License`  [AMBIGUOUS]
  LICENSE.txt · relation: references

## Knowledge Gaps
- **20 isolated node(s):** `Copyright 2026 Iyan Sanjaya`, `Disclaimer of Warranty and Limitation of Liability (Sections 7-8)`, `Grant of Patent License (Section 3)`, `Redistribution Conditions (Section 4)`, `Non-standard appendix note about Eclipse Public License` (+15 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Apache License, Version 2.0` and `Non-standard appendix note about Eclipse Public License`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **Why does `Workspace` connect `Workspace dan Kontrol UI` to `Parser Ekspor dan Pengujian`, `Entrypoint dan Pengujian UI`?**
  _High betweenness centrality (0.163) - this node is a cross-community bridge._
- **Why does `ExpCore` connect `Parser Ekspor dan Pengujian` to `Workspace dan Kontrol UI`, `Entrypoint dan Pengujian UI`?**
  _High betweenness centrality (0.149) - this node is a cross-community bridge._
- **Why does `ExpCore (Toolkit PDF Coretax)` connect `Dokumentasi Produk dan Build` to `Desain Desktop dan Responsivitas`, `Penamaan Bupot dan Audit`?**
  _High betweenness centrality (0.098) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `ExpCore` (e.g. with `Workspace` and `main()`) actually correct?**
  _`ExpCore` has 6 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Copyright 2026 Iyan Sanjaya`, `Disclaimer of Warranty and Limitation of Liability (Sections 7-8)`, `Grant of Patent License (Section 3)` to the rest of the system?**
  _20 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Workspace dan Kontrol UI` be split into smaller, more focused modules?**
  _Cohesion score 0.13257575757575757 - nodes in this community are weakly interconnected._