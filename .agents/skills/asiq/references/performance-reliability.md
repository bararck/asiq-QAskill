# Kinerja dan reliabilitas dengan otorisasi

Analisis konfigurasi/hasil lama boleh read-only sesuai akses. Load, soak, stress, restart, fault injection, pengisian storage, dan gangguan jaringan adalah tindakan aktif; jangan menjalankannya dari permintaan QA umum.

## Gerbang izin

Sebelum tindakan aktif, dapatkan persetujuan eksplisit: hostname/lingkungan, pemilik layanan, tenant/data uji, dependensi pihak ketiga, waktu, model traffic, batas request/concurrency/durasi/biaya, metrik penghentian, kanal eskalasi, dan pelaksana rollback. Hindari produksi secara default. Persetujuan lingkungan staging bukan izin membebani layanan pembayaran/email atau layanan bersama di belakangnya. Jika batas belum ada, keluarkan rencana dan blocker, bukan generator beban.

## Rancangan

- Sahkan SLI/SLO dan profil workload: komposisi operasi, distribusi input, arrival rate atau concurrency, warmup, ramp, durasi steady state, dan cache. Jangan mengarang target latency.
- Rekam versi aplikasi, kapasitas, konfigurasi, dataset, lokasi generator, clock, baseline, dan sampling. Bedakan throughput yang diminta, yang tercapai, error, timeout, serta latency p50/p95/p99 dengan satuan dan jendela pengukuran. Jangan melaporkan percentile dari rata-rata.
- Pastikan generator tidak menjadi bottleneck. Hasil sampel kecil atau lingkungan tak setara harus diberi batas interpretasi; jangan mengekstrapolasi kapasitas produksi sebagai fakta.
- Untuk recovery, tetapkan fault yang disetujui, expected degradations, timeout/retry/backoff, idempotensi, dan batas kehilangan/pemulihan data yang disahkan. Uji failover bukan sekadar proses hidup kembali; verifikasi integritas serta pemulihan layanan.

## Penghentian dan penutupan

Hentikan ketika batas error/latency/resource/biaya yang disepakati terlewati, monitoring hilang, atau target berubah. Jangan menaikkan beban untuk mengejar hasil menarik. Simpan bukti sebelum cleanup; verifikasi cleanup dan pulihnya health dalam izin. Laporkan tindakan, actual terhadap threshold, residual impact, dan apa yang belum teruji. Tanpa bukti pemulihan, status penutupan tetap terbuka.
