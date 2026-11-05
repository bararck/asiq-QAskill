# Pilot tim sebelum adopsi company

ASIQ adalah baseline proses, bukan sertifikasi aplikasi atau pengganti reviewer independen. Feedback pemakaian eksternal adalah input desain yang dilaporkan pengguna; bukan hasil eksekusi company yang direproduksi oleh maintainer. Pengembangan ini tidak mengakses layanan atau data company.

## Pemilik dan batas

Tetapkan QA lead sebagai pemilik inventory/oracle, engineering sebagai pemilik runner/build, pemilik layanan sebagai pemberi izin tindakan, dan reviewer independen sebagai adjudicator bukti. Gunakan akun/data sintetis. Mulai read-only; otorisasi aplikasi non-production secara terpisah dari instalasi skill. Jangan menyimpan token, data personal, raw provider trace atau environment dump pada ledger maupun artefak publik.

## Lapisan adopsi

1. Skill-only: pasang hanya konten skill dan lisensi seperti README; enforcement tetap manual dan harus dinyatakan.
2. Paket tooling: tinjau dan pin source ASIQ penuh di lokasi terpisah, gunakan gate opsional dengan input/bukti eksplisit. Jangan menimpa scripts/CI aplikasi atau mengubah AGENTS.md otomatis.
3. Integrasi CI: setelah pilot, tim memetakan output runner sebenarnya ke ledger. Simpan baseline resmi dan artefak pada penyimpanan yang memiliki kontrol akses/retensi. Gate tidak boleh membaca credential atau menjalankan command dari ledger. Adaptor runner belum universal; validasi parser tiap stack sebelum menjadikannya wajib.

## Acceptance pilot

- Setiap requirement in-scope memiliki risiko, skenario atau gap eksplisit dengan pemilik. ID resmi tidak hilang; skip baru menahan gate.
- Expected berasal dari oracle terpisah; versi aturan, rounding/timezone dan lineage data dapat ditelusuri bila relevan.
- Bukti terikat source/build, environment/config/data dan attempt yang benar. Kegagalan awal dipertahankan; retest punya penjelasan perubahan.
- Pemisahan defect produk, fixture, infrastruktur dan belum pasti dapat diperiksa reviewer. Mock/lokal/live dilaporkan terpisah.
- Instalasi tidak mengubah file aplikasi/global; update/rollback direview dan diuji manual sebelum penggunaan tim.
- Negative controls (ID hilang, hash berubah, konteks berbeda, retry menutupi FAIL) harus benar-benar ditolak.
- Aktivitas aktif hanya dalam izin; cleanup dan efeknya diverifikasi. Keputusan rilis tetap milik pemilik berwenang.

## Ukur efektivitas, bukan skor subjektif

Gunakan protokol benchmark paket untuk tugas identik dengan/tanpa skill, sesi terpisah dan penilaian independen. Rekam defect yang terkonfirmasi, false positive, gap risiko kritis, kepatuhan izin serta waktu/biaya aktual. Tetapkan threshold pilot sebelum melihat hasil; jangan memilih threshold agar hasil tampak baik. Hasil lab sintetis hanya membuktikan kontrak lab, bukan efektivitas model atau integrasi aplikasi company.

## Update, rollback dan dukungan

Pin commit/hash paket yang direview; jangan mengikuti latest otomatis. Simpan versi lama di luar discovery agent. Bila tujuan sudah ada, hentikan; review diff dan simpan perubahan lokal sebelum pemilik memindahkan folder lama dan menyalin kandidat baru. Verifikasi file kandidat, lisensi, discovery host dan prompt smoke test pada sesi baru. Rollback dengan menghentikan sesi, mengarantina kandidat dan mengembalikan folder lama setelah memastikan tujuan kosong. Tidak ada merge/force overwrite otomatis. Prosedur manual belum membuktikan ketahanan power-loss atau concurrent writer.

Format ledger/tooling memiliki versi sendiri; perubahan incompatible harus memakai versi schema baru. Pilot ini menargetkan Python 3.11/3.12 untuk tooling stdlib; host discovery dan stack aplikasi harus diuji sendiri. Catat pemilik support, kanal security privat dan prosedur eskalasi sebelum menjadikan ASIQ gate organisasi.
