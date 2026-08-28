# Graph Report - ExpCore-1  (2026-08-28)

## Corpus Check
- 5 files · ~28,320 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 107 nodes · 194 edges · 13 communities (10 shown, 3 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 1% AMBIGUOUS · INFERRED: 7 edges (avg confidence: 0.76)
- Token cost: 52,907 input · 0 output

## Community Hubs (Navigation)
- Shell Aplikasi dan Komponen UI
- Parser dan Penamaan Bupot
- Orkestrasi Proses dan Output Excel
- Struktur Formulir BPPU Coretax
- Tumpukan Teknologi dan Fitur
- Sidebar dan Navigasi
- Lisensi Apache 2.0
- Build Nuitka dan Jebakannya
- Dua Format Bukti Potong
- Penamaan Otomatis dan Audit
- Jembatan Nyata Alur Penamaan
- Temuan Analisis God Class
- Identitas Visual Ikon

## God Nodes (most connected - your core abstractions)
1. `ExpCore` - 45 edges
2. `ExpCore (Toolkit PDF Coretax)` - 13 edges
3. `main()` - 8 edges
4. `Apache License, Version 2.0` - 5 edges
5. `Penamaan Otomatis Bupot` - 5 edges
6. `Bagian B - Pemotongan/Pemungutan PPh` - 4 edges
7. `Bukti Pemotongan/Pemungutan PPh Unifikasi (BPPU) - contoh` - 4 edges
8. `Modul Bukti Potong 2026` - 4 edges
9. `Modul Bukti Potong 2024` - 4 edges
10. `Betweenness sebagai Artefak God Class` - 4 edges

## Surprising Connections (you probably didn't know these)
- `main()` --uses--> `ExpCore`  [INFERRED]
  test_expcore.py → ExpCore.py
- `Pemakaian Ulang Helper Lintas Komunitas Penamaan-Parser` --conceptually_related_to--> `Modul Bukti Potong 2026`  [INFERRED]
  graphify-out/memory/query_20260821_140214_kenapa_expcore_menjadi_jembatan_tunggal_antara_she.md → README.md
- `Alur Penamaan Bupot sebagai Jembatan Nyata` --conceptually_related_to--> `Penamaan Otomatis Bupot`  [INFERRED]
  graphify-out/memory/query_20260821_140214_kenapa_expcore_menjadi_jembatan_tunggal_antara_she.md → README.md
- `Betweenness sebagai Artefak God Class` --references--> `ExpCore (Toolkit PDF Coretax)`  [EXTRACTED]
  graphify-out/memory/query_20260821_140214_kenapa_expcore_menjadi_jembatan_tunggal_antara_she.md → README.md
- `Premis Jembatan Tunggal Dibantah` --references--> `ExpCore (Toolkit PDF Coretax)`  [EXTRACTED]
  graphify-out/memory/query_20260821_140214_kenapa_expcore_menjadi_jembatan_tunggal_antara_she.md → README.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Aturan Build Nuitka + Venv Eksplisit** — readme_aturan_path_venv_eksplisit, readme_aturan_garis_miring_path, readme_nuitka_bundling_interpreter, readme_verifikasi_import_venv, readme_windows_console_mode_disable [EXTRACTED 1.00]
- **Tiga Modul Ekstraksi PDF ke Excel** — readme_bukti_potong_2026, readme_bukti_potong_2024, readme_pajak_masukan, readme_pemindaian_subfolder, readme_kolom_folder_sumber [EXTRACTED 1.00]
- **Analisis Bantahan Jembatan Tunggal ExpCore** — graphify_out_memory_query_20260821_140214_kenapa_expcore_menjadi_jembatan_tunggal_antara_she_premis_jembatan_dibantah, graphify_out_memory_query_20260821_140214_kenapa_expcore_menjadi_jembatan_tunggal_antara_she_uji_hapus_node, graphify_out_memory_query_20260821_140214_kenapa_expcore_menjadi_jembatan_tunggal_antara_she_god_class_betweenness_artifact, graphify_out_memory_query_20260821_140214_kenapa_expcore_menjadi_jembatan_tunggal_antara_she_alur_penamaan_bupot_jembatan_nyata, graphify_out_memory_query_20260821_140214_kenapa_expcore_menjadi_jembatan_tunggal_antara_she_graph_undirected_caveat [EXTRACTED 1.00]
- **ExpCore Brand Identity System** — icon_app_icon, icon_document_export_glyph, icon_dark_theme_branding, icon_visual_identity_rationale [INFERRED 0.85]

## Communities (13 total, 3 thin omitted)

### Community 1 - "Parser dan Penamaan Bupot"
Cohesion: 0.19
Nodes (5): Ambil semua baris objek pajak dari teks satu PDF Bukti Potong., 4 3 6 1 ...' -> '4361...'. Formulir BPBS menulis angka per kotak., 3 1 dd 0 1 mm 2 0 2 4 yyyy' -> '31-01-2024'. Kotak kosong -> ''., Ambil baris objek pajak dari teks satu PDF Bukti Potong formulir BPBS. Berbeda…, main()

### Community 3 - "Struktur Formulir BPPU Coretax"
Cohesion: 0.22
Nodes (9): Bagian A - Identitas Wajib Pajak yang Dipotong, Bagian B - Pemotongan/Pemungutan PPh, Bagian C - Identitas Pemotong/Pemungut PPh, Bukti Pemotongan/Pemungutan PPh Unifikasi (BPPU) - contoh, Direktorat Jenderal Pajak (issuer), Dokumen Dasar (Surat Tagihan 10006302), Kode Objek Pajak 24-104-18 (Jasa Perantara/Keagenan), PPh Pasal 23 (+1 more)

### Community 4 - "Tumpukan Teknologi dan Fitur"
Cohesion: 0.22
Nodes (9): CustomTkinter, ExpCore (Toolkit PDF Coretax), Inno Setup, Kolom Folder Sumber, Modul Pajak Masukan, pandas + openpyxl, pdfplumber, Pemindaian Subfolder (+1 more)

### Community 6 - "Lisensi Apache 2.0"
Cohesion: 0.33
Nodes (6): Apache License, Version 2.0, Copyright 2026 Iyan Sanjaya, Disclaimer of Warranty and Limitation of Liability (Sections 7-8), Non-standard appendix note about Eclipse Public License, Grant of Patent License (Section 3), Redistribution Conditions (Section 4)

### Community 7 - "Build Nuitka dan Jebakannya"
Cohesion: 0.33
Nodes (6): Aturan Garis Miring pada Path, Aturan Path Venv Eksplisit, Nuitka, Nuitka Mem-bundle dari Interpreter Pemanggil, Verifikasi Import Venv (lengkap / siap build), windows-console-mode=disable

### Community 8 - "Dua Format Bukti Potong"
Cohesion: 0.33
Nodes (6): Modul Bukti Potong 2024, Modul Bukti Potong 2026, Coretax DJP, Formulir BPBS (pra-Coretax), Formulir BPPU (Coretax), Pembacaan Kolom Sifat dari Centang H.4/H.5

### Community 9 - "Penamaan Otomatis dan Audit"
Cohesion: 0.40
Nodes (5): Log Audit Penamaan (CSV Pratinjau/Penerapan), Pemrosesan Sepenuhnya Lokal, Penamaan Otomatis Bupot, Pratinjau Nama sebelum Terapkan Nama, test_expcore.py (Pemeriksaan Parser & Keamanan Nama File)

### Community 10 - "Jembatan Nyata Alur Penamaan"
Cohesion: 0.50
Nodes (4): Alur Penamaan Bupot sebagai Jembatan Nyata, _page_rename_bupot (betweenness 0.476), process_rename_bupot (betweenness 0.499), Pemakaian Ulang Helper Lintas Komunitas Penamaan-Parser

### Community 11 - "Temuan Analisis God Class"
Cohesion: 0.67
Nodes (4): Betweenness sebagai Artefak God Class, Caveat: Graph Undirected, Arah Edge Tidak Reliabel, Premis Jembatan Tunggal Dibantah, Uji Hapus-Node (Node Deletion Test)

### Community 12 - "Identitas Visual Ikon"
Cohesion: 0.67
Nodes (4): ExpCore Application Icon, Dark Navy / Periwinkle Brand Palette, Document-with-Chevron Export Glyph, Icon Visual Identity Choice

## Ambiguous Edges - Review These
- `Apache License, Version 2.0` → `Non-standard appendix note about Eclipse Public License`  [AMBIGUOUS]
  LICENSE.txt · relation: references

## Knowledge Gaps
- **22 isolated node(s):** `Copyright 2026 Iyan Sanjaya`, `Bagian A - Identitas Wajib Pajak yang Dipotong`, `Direktorat Jenderal Pajak (issuer)`, `Dokumen Dasar (Surat Tagihan 10006302)`, `Kode Objek Pajak 24-104-18 (Jasa Perantara/Keagenan)` (+17 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Apache License, Version 2.0` and `Non-standard appendix note about Eclipse Public License`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **Why does `ExpCore` connect `Shell Aplikasi dan Komponen UI` to `Parser dan Penamaan Bupot`, `Orkestrasi Proses dan Output Excel`, `Sidebar dan Navigasi`?**
  _High betweenness centrality (0.202) - this node is a cross-community bridge._
- **Why does `ExpCore (Toolkit PDF Coretax)` connect `Tumpukan Teknologi dan Fitur` to `Dua Format Bukti Potong`, `Penamaan Otomatis dan Audit`, `Temuan Analisis God Class`, `Build Nuitka dan Jebakannya`?**
  _High betweenness centrality (0.079) - this node is a cross-community bridge._
- **Why does `Penamaan Otomatis Bupot` connect `Penamaan Otomatis dan Audit` to `Jembatan Nyata Alur Penamaan`, `Tumpukan Teknologi dan Fitur`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._
- **What connects `Copyright 2026 Iyan Sanjaya`, `Bagian A - Identitas Wajib Pajak yang Dipotong`, `Direktorat Jenderal Pajak (issuer)` to the rest of the system?**
  _22 weakly-connected nodes found - possible documentation gaps or missing edges._