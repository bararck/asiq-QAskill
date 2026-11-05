# Review dependensi, desain dan logika lintas repo

## Mandat dan penemuan

Mulai dari root, revisi dan scope repo utama. Inventaris manifest/lockfile, workspace/submodule, kontrak API/event, migration, entry point, pemanggil dan consumer. Dependency package bukan otomatis repo terpisah; bedakan library runtime, dev/test tool, layanan remote, generated client dan kode workspace. Manifest menyatakan dependency, bukan bukti dependency aktif dipakai atau versi deployed.

Untuk setiap dependensi relevan catat ID, tipe, versi resolved/commit, sumber declaration, simbol pemakai dan alasan dampak. Periksa pemanggilan aktual dan konfigurasi nonsecret, bukan hanya diagram/README. Jangan membuka credential file atau menyalin payload sensitif. Jangan menjalankan install/build/hook untuk sekadar memahami stack.

Repo lain hanya dibaca bila path/URL dan izin baca memang tercakup mandat. Permintaan analisis lintas dependency tidak memberikan izin ke semua repo organisasi, clone private repo, mengambil kredensial, memanggil layanan live atau memindahkan kode perusahaan ke tool eksternal. Gunakan checkout read-only yang tersedia atau kontrak tersanitasi yang diberikan pemilik. Repo yang belum tersedia berstatus UNAVAILABLE; tulis kontrak/aspek yang tidak dapat dibuktikan. Jangan menebak implementasi atau menyatakan integrasi PASS berdasarkan mock.

## Telusuri satu vertical slice

1. Mulai dari aksi aktor dan requirement terverifikasi. Catat precondition, role/tenant, input, expected outcome dan owner oracle.
2. Telusuri UI/route → validasi → service/domain → persistensi/transaksi → event/job/provider → consumer/proyeksi/UI. Hanya masukkan edge yang punya bukti source/kontrak. Edge dugaan berlabel ASSUMED, bukan CONFIRMED.
3. Untuk tiap edge cocokkan kontrak producer dan consumer: nama/type/nullability, unit/mata uang/timezone, enum/state, versi, auth, timeout, idempotency dan error semantics. Baca kedua sisi pada revisi yang dicatat; melihat satu sisi tidak membuktikan kompatibilitas.
4. Petakan batas transaksi dan side effect: kapan commit, claim, permission check, pengiriman, retry, kompensasi dan audit terjadi. Bedakan state tersimpan, state ditampilkan dan acknowledgment eksternal. Catat failure window antar langkah.
5. Bandingkan requirement/desain yang disetujui dengan implementasi aktual dan perilaku teramati. Diagram tidak boleh menjadi oracle tunggal bila draft, kedaluwarsa atau konflik dengan kontrak yang lebih otoritatif. Konflik memerlukan pemilik keputusan; jangan memilih source terbaru sekadar karena tanggal.
6. Pilih regresi berdasarkan edge/state yang berubah dan consumer terdampak. Kaitkan canonical scenario dan varian existing; jangan menghapus inventory resmi. Dependency tidak terdampak boleh tidak dipilih hanya dengan alasan dan gap yang terlihat.

## Pencocokan desain dan logic

Desain UX: actor/action, navigasi, role visibility, loading/empty/error/success, validasi input, aksesibilitas, dan konsistensi status. Komponen yang sesuai screenshot belum membuktikan aturan bisnis benar. Tanpa akses UI/desain final, beri STATIC_REVIEW/BLOCKED untuk bagian terkait; jangan mengarang screenshot atau visual PASS.

Desain arsitektur: ownership data, boundary modul/layanan, arah dependency, konsistensi sinkron/asinkron, versioning, dan jalur gagal. Dependency cycle bukan otomatis defect; jelaskan dampak konkret pada kontrak, perubahan atau reliabilitas.

Logic: invariant, kalkulasi dengan oracle independen, pembulatan/boundary, state transition terlarang, tenant isolation, perubahan permission setelah claim, concurrency, replay, ambiguous acknowledgment dan historical snapshot. Gunakan [workflow stateful](stateful-workflows.md) jika relevan. Jangan memaksa seluruh checklist ke aplikasi yang tidak memiliki flow tersebut.

## Matriks keluaran

Gunakan [template flow](../templates/dependency-flow.md). Pisahkan:

- DESIGN_GAP: desain/requirement belum menjelaskan kontrak, bukan bug terkonfirmasi.
- IMPLEMENTATION_MISMATCH: bukti source menyimpang dari oracle; label STATIC_REVIEW sampai diverifikasi secara dinamis bila dibutuhkan.
- OBSERVED_DEFECT: eksekusi berizin mereproduksi pelanggaran oracle, dengan actual/expected dan bukti.
- COMPATIBILITY_UNKNOWN: sisi consumer/producer, versi deployed atau konfigurasi belum diperiksa.

Setiap finding memiliki path:symbol/line dan revisi kedua sisi bila tersedia, sumber oracle, confidence, skenario verifikasi dan pemilik. Untuk dependency map laporkan jumlah CONFIRMED/ASSUMED/UNAVAILABLE tanpa menyamakan semua edge tercakup. Jumlah edge bukan coverage bisnis. Keputusan rilis tetap menyebut gap dan siapa yang boleh menerima risiko.

## Contoh sintetis

Requirement: pembatalan reservasi sebelum pengiriman mengembalikan satu unit stok tepat sekali. Repo UI memanggil POST cancel; repo service mengubah state dan menerbitkan event; consumer stok memakai event_id untuk deduplikasi. Ini contoh hipotetis, bukan struktur aplikasi target.

Bukti minimum: requirement yang disetujui; route dan service pada revisi A; schema event pada revisi A; handler consumer pada revisi B; skenario cancel ulang/concurrent, event duplikat, izin dicabut dan publish gagal setelah commit jika kontrak memang mendukungnya. Bila repo consumer tidak tersedia, tulis COMPATIBILITY_UNKNOWN dan minta kontrak/pemilik—jangan menyimpulkan stok benar dari respons HTTP 200.
