# Recorder eksekusi opsional

Dari root paket penuh ASIQ yang ditinjau:

    python -B scripts/record_run.py --cwd <checkout-git> --output <direktori-baru> --timeout 60 --acknowledge-sensitive-output -- <executable> <argumen>

Jalankan hanya command yang telah diperiksa side effect dan diizinkan user. Tool bukan sandbox: command memakai hak akses, environment dan jaringan user. shell=False menghindari interpretasi shell implisit; interpreter/shell yang dipilih eksplisit tetap dapat mengeksekusi instruksi. Tidak ada command yang dibaca dari JSON.

Output baru berisi record.json, stdout.bin dan stderr.bin. Recorder menyimpan HEAD, dirty flag sebelum eksekusi, argv, exit code, status, durasi monotonic dan SHA-256 stream. Exit nol berarti command selesai dengan exit nol, bukan PASS requirement. Exit bukan nol dan timeout tetap disimpan tanpa retry; timeout 124 dan gagal start 127. Error setup menghasilkan diagnostik statis serta exit bukan nol. Direktori existing tidak ditimpa. Path cwd/output dengan symlink/junction/reparse ancestor dan output di komponen .git ditolak.

Flag acknowledge adalah pengakuan bahwa raw stream, argv dan path lokal dapat mengandung rahasia. Tool tidak meredaksi konten dan tidak mencetak stream ke terminal. Jangan memberi credential lewat argv. Simpan output pada direktori privat dengan ACL yang diverifikasi pemilik; mode 0700 bukan jaminan ACL Windows. Jangan publish raw record/stream; buat salinan tersanitasi dengan hash/provenance baru dan review manusia.

Format asiq-execution-record-v1 berbeda dari schema qa_gate. Mapping ke ledger memerlukan baseline independen, oracle terverifikasi, konteks build/environment/config, inventory dan keputusan reviewer; tool tidak membuat oracle atau ledger PASS otomatis.

Batas: HEAD dan dirty flag bukan snapshot isi working tree/build atau bukti source immutable. Tidak ada timestamp terpercaya, attestation, pengikatan environment/build, redaksi otomatis, batas ukuran output atau pengawasan process tree. Timeout mengakhiri child langsung; descendants dapat tetap berjalan. Gunakan hanya command bounded tanpa descendant/background dan runner terisolasi/terkontrol. Hashing membaca stream setelah run; file besar memerlukan pembatasan resource di luar tool. Pemeriksaan path bukan perlindungan terhadap perubahan filesystem bersamaan oleh pihak bermusuhan. Output yang tidak lengkap setelah crash/error tidak boleh diterima sebagai bukti lengkap. Recorder belum merupakan adapter universal framework tes.
