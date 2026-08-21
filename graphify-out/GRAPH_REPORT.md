# Graph Report - ExpCore-1  (2026-08-21)

## Corpus Check
- Corpus is ~26,394 words - fits in a single context window. You may not need a graph.

## Summary
- 92 nodes · 165 edges · 10 communities (5 shown, 5 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 1% AMBIGUOUS · INFERRED: 16 edges (avg confidence: 0.83)
- Token cost: 113,087 input · 0 output

## Community Hubs (Navigation)
- Domain Pajak Coretax
- Build dan Distribusi
- Shell Aplikasi dan Logging
- Lisensi dan Kepemilikan
- Sidebar dan Navigasi
- Penamaan Otomatis Bupot
- Orkestrasi Proses Ekstraksi
- Parser Bukti Potong
- Identitas Visual Ikon

## God Nodes (most connected - your core abstractions)
1. `ExpCore` - 38 edges
2. `Modul Bukti Potong` - 10 edges
3. `Penamaan Otomatis Bupot` - 7 edges
4. `main()` - 6 edges
5. `ExpCore` - 6 edges
6. `ExpCore.py (UI dan logika aplikasi)` - 6 edges
7. `Apache License, Version 2.0` - 6 edges
8. `Bukti Pemotongan/Pemungutan PPh Unifikasi (BPPU) - contoh` - 6 edges
9. `Modul Pajak Masukan` - 5 edges
10. `Nuitka standalone build` - 5 edges

## Surprising Connections (you probably didn't know these)
- `Tarif PPN tetap 12%` --semantically_similar_to--> `Kode Objek Pajak 24-104-18 (Jasa Perantara/Keagenan)`  [INFERRED] [semantically similar]
  README.md → contoh_pdf.pdf
- `Modul Bukti Potong` --shares_data_with--> `Bagian B - Pemotongan/Pemungutan PPh`  [INFERRED]
  README.md → contoh_pdf.pdf
- `Modul Bukti Potong` --shares_data_with--> `Bagian C - Identitas Pemotong/Pemungut PPh`  [INFERRED]
  README.md → contoh_pdf.pdf
- `Modul Bukti Potong` --shares_data_with--> `Bukti Pemotongan/Pemungutan PPh Unifikasi (BPPU) - contoh`  [INFERRED]
  README.md → contoh_pdf.pdf
- `Penamaan Otomatis Bupot` --shares_data_with--> `Bukti Pemotongan/Pemungutan PPh Unifikasi (BPPU) - contoh`  [INFERRED]
  README.md → contoh_pdf.pdf

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Pipeline build dan distribusi ExpCore** — readme_expcore_py, readme_nuitka, readme_verifikasi_hasil_build, readme_expcore_iss, readme_inno_setup [EXTRACTED 1.00]
- **Aturan yang mencegah hampir semua masalah build** — readme_venv_python_eksplisit, readme_path_garis_miring, readme_nuitka_bundle_dari_interpreter, readme_windows_console_mode_disable, readme_isolasi_masalah_kode_vs_build [EXTRACTED 1.00]
- **Alur ekstraksi Bupot dari PDF Coretax ke Excel** — contoh_pdf_bagian_a_identitas_dipotong, contoh_pdf_bagian_b_pemotongan_pph, contoh_pdf_bagian_c_identitas_pemotong, readme_bukti_potong, readme_hasil_rekap_bupot_xlsx, readme_kolom_folder_sumber [INFERRED 0.95]
- **ExpCore Brand Identity System** — icon_app_icon, icon_document_export_glyph, icon_dark_theme_branding, icon_visual_identity_rationale [INFERRED 0.85]

## Communities (10 total, 5 thin omitted)

### Community 0 - "Domain Pajak Coretax"
Cohesion: 0.13
Nodes (21): Bagian A - Identitas Wajib Pajak yang Dipotong, Bagian B - Pemotongan/Pemungutan PPh, Bagian C - Identitas Pemotong/Pemungut PPh, Bukti Pemotongan/Pemungutan PPh Unifikasi (BPPU) - contoh, Direktorat Jenderal Pajak (issuer), Dokumen Dasar (Surat Tagihan 10006302), Kode Objek Pajak 24-104-18 (Jasa Perantara/Keagenan), PPh Pasal 23 (+13 more)

### Community 1 - "Build dan Distribusi"
Cohesion: 0.13
Nodes (15): CustomTkinter (GUI), ExpCore.iss (konfigurasi installer), ExpCore.py (UI dan logika aplikasi), Inno Setup installer, Membedakan masalah kode dan masalah build, Nuitka standalone build, Nuitka mem-bundle dari interpreter yang menjalankannya, openpyxl (+7 more)

### Community 4 - "Lisensi dan Kepemilikan"
Cohesion: 0.25
Nodes (9): Apache License, Version 2.0, Copyright 2026 Iyan Sanjaya, Disclaimer of Warranty and Limitation of Liability (Sections 7-8), Non-standard appendix note about Eclipse Public License, Grant of Patent License (Section 3), Redistribution Conditions (Section 4), Lisensi Apache 2.0 (README), ExpCore (+1 more)

### Community 9 - "Identitas Visual Ikon"
Cohesion: 0.67
Nodes (4): ExpCore Application Icon, Dark Navy / Periwinkle Brand Palette, Document-with-Chevron Export Glyph, Icon Visual Identity Choice

## Ambiguous Edges - Review These
- `Apache License, Version 2.0` → `Non-standard appendix note about Eclipse Public License`  [AMBIGUOUS]
  LICENSE.txt · relation: references

## Knowledge Gaps
- **15 isolated node(s):** `Output Excel Terformat`, `!Hasil_Rekap_Bupot.xlsx`, `Hasil_Pajak_Masukan.xlsx`, `CustomTkinter (GUI)`, `pandas` (+10 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Apache License, Version 2.0` and `Non-standard appendix note about Eclipse Public License`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **Why does `ExpCore` connect `Shell Aplikasi dan Logging` to `Komponen UI Reusable`, `Sidebar dan Navigasi`, `Penamaan Otomatis Bupot`, `Orkestrasi Proses Ekstraksi`, `Parser Bukti Potong`?**
  _High betweenness centrality (0.170) - this node is a cross-community bridge._
- **Why does `ExpCore` connect `Lisensi dan Kepemilikan` to `Domain Pajak Coretax`, `Build dan Distribusi`?**
  _High betweenness centrality (0.124) - this node is a cross-community bridge._
- **Why does `ExpCore.py (UI dan logika aplikasi)` connect `Build dan Distribusi` to `Lisensi dan Kepemilikan`?**
  _High betweenness centrality (0.110) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `Modul Bukti Potong` (e.g. with `Bagian B - Pemotongan/Pemungutan PPh` and `Bagian C - Identitas Pemotong/Pemungut PPh`) actually correct?**
  _`Modul Bukti Potong` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `Penamaan Otomatis Bupot` (e.g. with `Bukti Pemotongan/Pemungutan PPh Unifikasi (BPPU) - contoh` and `Modul Bukti Potong`) actually correct?**
  _`Penamaan Otomatis Bupot` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Output Excel Terformat`, `!Hasil_Rekap_Bupot.xlsx`, `Hasil_Pajak_Masukan.xlsx` to the rest of the system?**
  _15 weakly-connected nodes found - possible documentation gaps or missing edges._