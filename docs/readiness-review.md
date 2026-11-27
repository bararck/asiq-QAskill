# Review kesiapan ASIQ 0.4.0

Skor di dokumen ini adalah pertimbangan reviewer atas kesiapan **paket**, bukan persentase keberhasilan agen, sertifikasi atau hasil benchmark. Reviewer juga mengembangkan paket ini; belum ada adjudikasi manusia independen. Gunakan bobot sama untuk lima aspek yang dipakai pada review awal, sehingga perbandingannya terlihat.

| Aspek | Awal | Setelah perbaikan | Dasar perubahan |
| --- | --- | --- | --- |
| Disiplin bukti/oracle | 9 | 9.5 | Binding v2 memeriksa byte bukti, inventory pack, snapshot skill dan konteks event; kejujuran reviewer tetap tidak otomatis diverifikasi |
| Mode kerja/status | 8 | 8.5 | Tier tetap proporsional; diagnosis crash tanpa bukti diselaraskan ke UNKNOWN, bukan atribusi infra otomatis |
| Routing skill | 8 | 8.5 | Kesiapan runtime dipisahkan dari file ditemukan; fallback Windows Git Bash dan batas context budget ditulis eksplisit |
| Tooling/runtime | 7 | 8 | Probe version/syntax bounded dengan negative controls; Git Bash lokal bekerja. Browser gstack belum siap, sehingga aspek ini dibatasi |
| Kesiapan evaluasi perilaku | 4 | 6 | Satu sesi Codex terpisah menjawab lima kasus pemahaman; artifact hasil disimpan. Harness binding diperkuat; full-pack/blind benchmark tetap belum dijalankan |
| **Rata-rata bobot sama** | **7.2/10** | **8.1/10** | **Skor review kesiapan, bukan skor efektivitas empiris** |

## Bukti dan batas

- Verifikasi paket lokal terakhir: `python -B scripts/verify.py` exit 0, **98 test lulus**, serta negative control **8 assertion failures** yang diharapkan. Semua 83 test sebelumnya dipertahankan, ditambah sembilan test binding dan enam test probe. Ini hasil paket/tooling, bukan 98 pengujian aplikasi.
- [Record smoke aktual](../benchmarks/results/instruction-smoke.json): sesi terpisah exit 0; lima kasus tentang crash, retry, tier Bolt, mandat lama dan instruksi log. Jawaban dinilai sesuai aturan oleh agen pengembang. Tidak ada aplikasi yang diuji dalam sesi itu.
- Upaya pertama dalam sandbox gagal koneksi; tidak dihitung sebagai hasil pemahaman. Jalur subagent bawaan menolak model terwaris. CLI read-only di luar batas jaringan sandbox kemudian berhasil; metadata model dan beberapa MCP startup memberi warning. Warning dan kegagalan tidak diubah menjadi PASS produk.
- Pemeriksaan pertama menemukan kontradiksi UNKNOWN/INFRASTRUCTURE. Setelah koreksi, sesi berikutnya tidak menemukan konflik substantif pada kelima kasus. Ini smoke review publik dengan konteks host, bukan desain kausal baseline/treatment.
- Heading work-modes diubah selama sesi berikutnya berjalan; respons masih menyebut heading lamanya. Klaim hasil dibatasi pada aturan lima kasus yang dibaca, bukan snapshot final seluruh paket. Raw stream lengkap/diagnostik host tidak dipublikasikan; record adalah ekstrak event terpilih, bukan log lengkap atau attestation.
- Probe aktual Git, Node, graphify dan Git Bash keluar 0; syntax-only preamble gstack valid. Pemeriksaan konfigurasi gstack dengan Git Bash juga berjalan. Tidak mengubah telemetry/pilihan pengguna.
- Browser gstack `browse.exe --help` keluar 1 karena `server.ts` tidak ditemukan pada paket terpasang. Jangan menyamakan shell siap dengan browser siap atau menyembunyikan kegagalan bootstrap ini. Perbaikan paket browser tetap gap tersendiri.
- Unit fixture binding/probe bersifat sintetis. Full-pack sepuluh kasus dengan sesi nyata, holdout independen, review manusia dan bukti aplikasi tetap belum tersedia.

## Kriteria berikutnya

Untuk menaikkan bukti efektivitas, jalankan protokol berpasangan dengan oracle tersembunyi dan penilai independen, pertahankan invalidasi/timeout serta jumlah pertanyaan dan durasi. Untuk kesiapan operasional penuh, selesaikan bootstrap browser dan uji satu flow lokal yang diotorisasi. Jangan menaikkan skor hanya karena menambah nama skill atau jumlah test.
