# ExpCore — Desktop workspace

Desain terinspirasi selera editorial Awesomic: zinc yang tenang, hierarki tegas,
permukaan membulat, dan aksen oranye sebagai penanda. Disesuaikan untuk aplikasi
desktop pengolahan dokumen, dengan informasi dan tindakan yang mudah ditemukan.

## Token visual

| Peran | Nilai |
| --- | --- |
| Kanvas | `#f4f4f5` |
| Kartu / sidebar | `#ffffff` |
| Teks utama / aksi utama | `#09090b` |
| Panel gelap | `#18181b` |
| Teks pendukung | `#52525b` |
| Metadata | `#71717a` |
| Garis pemisah | `#e4e4e7` |
| Aksen badge / fokus keyboard | `#ff5a00` |
| Font | Segoe UI, tersedia secara native di Windows |
| Judul beranda | 34–40 px, bold |
| Judul alat | 36 px, bold |
| Judul kartu | 20 px, bold |
| Teks antarmuka | 12–14 px |
| Radius kartu | 28 px |
| Radius kontrol | 14 px |

Warna ditetapkan sekali di `Workspace.C`; metadata keempat alat di
`Workspace.MODULES`. Segoe UI menghindari pengunduhan font dan tetap bekerja
offline. Kartu memakai garis tipis tanpa drop shadow. Status memakai teks,
sehingga warna bukan satu-satunya pembeda.

## Struktur dan interaksi

- Beranda berisi pengantar, panduan tiga langkah, dan akses ke empat alat.
- Sidebar menetap; setiap alat menyimpan folder, aktivitas, dan hasilnya sendiri
  selama sesi. Jalur folder dapat diketik atau dipilih melalui dialog native.
- Konten dapat digulir pada jendela pendek. Tombol pemrosesan menetap di bawah.
  Komposisi pengantar beranda ditumpuk pada area konten sempit.
- Handler layout responsif ditambahkan dengan `bind(..., add="+")` agar tidak
  menimpa pembaruan `scrollregion` bawaan CustomTkinter. Scrollbar berkontras jelas;
  roda mouse bekerja di atas kartu, label, tombol, dan isian folder.
- Log panjang digulir secara mandiri. Saat log kosong atau mencapai ujung, roda
  mouse diteruskan ke halaman. Satu gerakan hanya menggulir satu area.
- Reflow dan pembungkusan teks memperhitungkan skala widget. Panduan beranda menjadi
  baris ringkas di layar sempit; kartu menjadi satu kolom bila ruangnya tidak cukup.
- Badge oranye memakai teks gelap untuk meningkatkan kontras teks kecil.
- Field folder dan tombol pemilih memiliki tinggi 44 px. Field memakai radius
  14 px dan border 2 px dengan renderer polygon canvas untuk mencegah sambungan
  sudut dari glyph font terlihat pada DPI pecahan; perubahan warna fokus tidak
  mengubah ukuran kontrol. Teks bantuan BPPU menjelaskan format untuk alat aktif.
- Ukuran awal menyesuaikan layar dan DPI. Ukuran minimum: 960 × 620 logical px.
- Kontrol folder dan pemrosesan dikunci selama satu pekerjaan berjalan;
  navigasi tetap aktif. Progres dan log dikirim lewat queue ke thread Tk.
- Hasil selesai ditampilkan inline, dengan tombol membuka Excel/CSV dan salin
  log. Folder yang berubah membatalkan tautan hasil dan status pratinjau lama.
- Penamaan memerlukan pratinjau selesai sebelum tombol penerapan aktif.
  Konfirmasi menjelaskan bahwa penerapan memindai ulang kondisi folder terkini.
- Mengganti rekap yang sudah ada memerlukan konfirmasi. Menutup aplikasi saat
  proses berjalan ditahan sampai hasil dan log selesai ditulis.
- PDF yang gagal dibaca dicatat dan dilewati; dokumen lain tetap diproses.

## Keyboard

| Tombol | Tindakan |
| --- | --- |
| `Tab` / `Shift+Tab` | Pindah fokus kontrol |
| `Enter` / `Space` pada tombol | Aktifkan tombol |
| `Ctrl+O` | Pilih folder pada alat aktif |
| `Alt+0` | Beranda |
| `Alt+1`–`Alt+4` | Alat sesuai urutan sidebar |
| `Page Up` / `Page Down` | Gulir halaman saat fokus berada di luar editor teks |

## Pemeriksaan

`test_expcore.py` mencakup parser, penamaan, ekspor tiga modul, subfolder, dan
kelanjutan batch saat PDF rusak. Opsi `--pdf-samples` memeriksa 151 PDF lokal
tanpa mengubah dokumen. `test_expcore_ui.py` memeriksa input roda mouse nyata melalui
event Tk, klik scrollbar, keyboard, log bersarang, resize dua arah, posisi aksi
utama, isolasi worker, pemulihan kesalahan, hasil, dan konfirmasi. Gunakan
`--scale 1.25` atau `--scale 1.5` untuk verifikasi pembesaran 125% / 150%.

Pemeriksa update membaca metadata rilis publik GitHub di worker terpisah. PDF tetap
diproses lokal; tidak ada unggahan dokumen atau token akun. Banner update tidak
memblokir pekerjaan, dapat ditutup dengan **Nanti**, dan membuka halaman rilis resmi
melalui **Unduh update**. Kegagalan otomatis tetap diam; hasil pengecekan manual
ditampilkan lewat dialog. Versi UI dan installer bersumber dari `VERSION`.

UI tidak memakai font jarak jauh atau dependensi baru. Sumber
antarmuka berada di `expcore_ui.py`, sedangkan parser dan ekspor di `ExpCore.py`.

### Hasil verifikasi perbaikan scroll

Pada 8 September 2026, versi akhir diuji dua putaran setelah perbaikan, masing-masing
pada skala 100%, 125%, dan 150%. Keenam eksekusi lulus. Setiap eksekusi mencakup
kelima halaman, roda mouse di atas kartu/kontrol, klik scrollbar, Page Up/Down,
log kosong/panjang/ujung log/ruang tepi log, resize dua arah, dan pengamanan proses.
Tes parser, penamaan, dan ekspor ketiga modul juga lulus.

Pemeriksaan langsung di Windows membuktikan beranda dapat digulir hingga keempat
kartu dan tombolnya terlihat; roda mouse di tepi log Pajak Masukan juga mencapai
bagian bawah dengan tombol aksi utama tetap di tempatnya. Tes baru sebelumnya
dibuktikan gagal pada dua penyebab: `scrollregion` beranda kosong dan tepi log yang
tidak meneruskan event roda mouse.
