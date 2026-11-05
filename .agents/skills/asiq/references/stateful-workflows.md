# Workflow stateful dan rekonsiliasi

Gunakan hanya bila source/requirement menunjukkan state, retry, otorisasi, sinkronisasi, atau proyeksi data yang relevan. Ini pola investigasi lintas produk, bukan aturan bisnis universal. Review pasif boleh sesuai mandat; concurrency, fault injection, pesan dan mutasi membutuhkan izin spesifik.

## Peta dampak dan reuse

Petakan aturan bersumber → transisi state → data/consumer → risiko → ID skenario → bukti. Tandai edge sebagai terkonfirmasi atau hipotesis beserta lokasi source. Identifikasi consumer lain dari simbol dan pemakaian aktual, bukan nama fitur saja. Pertahankan ID canonical; role/state/tenant menjadi varian bernama, bukan alasan menghapus coverage. Catat regresi terpilih dan alasan area tidak dipilih. Inventory resmi tetap denominator, bukan hanya test yang berhasil ditemukan runner.

## Bedakan produk dari fixture

Simpan identitas run dan resource yang dibuat, snapshot awal, clock/seed serta konfigurasi. Periksa prasyarat fixture sebelum mengaitkan selisih ke bug produk. Fixture lama, benturan tenant, timezone dan cleanup gagal adalah hipotesis tersendiri. Bandingkan run bersih terisolasi dengan reproduksi awal tanpa menghapus bukti pertama. Cleanup hanya resource milik run sesuai izin dan verifikasi readback; jangan menghapus data lain atau mengubah expected agar hijau. Klasifikasikan produk, fixture, infrastruktur, atau belum pasti dengan bukti pembeda.

## Otorisasi sepanjang lifecycle

Gambarkan create → claim → execute → commit → callback/reconcile sesuai kontrak. Periksa perubahan role, tenant, kepemilikan, izin dan pembatalan antara fase, termasuk setelah claim sebelum efek eksternal. Tentukan titik otorisasi dan atomisitas yang diwajibkan requirement. Pemeriksaan login saja tidak membuktikan izin masih valid saat efek terjadi. Uji scope resource, stale token/cache, lease kedaluwarsa, dan competing worker bila relevan; jangan menganggap recheck sederhana menyelesaikan race check-versus-use.

## Acknowledgment ambigu dan replay

Pisahkan bukti ACCEPTED/DELIVERED, REJECTED definitif, dan UNKNOWN. Timeout atau 503 tidak selalu membuktikan tidak ada efek; kontrak provider menentukan apakah permintaan mungkin sudah diterima. Jangan mengubah UNKNOWN menjadi gagal definitif atau otomatis mengirim ulang. Temukan correlation/idempotency key, status lookup, webhook, batas deduplikasi dan mekanisme rekonsiliasi yang benar-benar tersedia. Uji replay identik, payload berbeda dengan key sama, callback duplikat/tidak berurutan, crash sebelum/sesudah commit dan manual recovery sesuai izin. Tidak ada jaminan exactly-once hanya karena fungsi memakai lock.

## Rekonsiliasi dan snapshot historis

Telusuri lineage sumber → transformasi → proyeksi → UI/API/report. Bangun expected secara independen dari fungsi yang diuji: sumber aturan, dataset sintetis, satuan, rounding, cutoff/timezone dan versi aturan. Untuk keuangan gunakan representasi desimal yang sesuai kontrak, bukan float tanpa alasan. Perubahan harga/role/aturan hari ini tidak otomatis boleh mengubah snapshot historis; cek kontrak efektif waktunya. Nyatakan batas integrasi: mock provider, database lokal, dan layanan nyata adalah lapisan bukti berbeda.

## Pertanyaan penutupan

- Transisi dan invariant mana teramati, mana baru direview statis?
- Apakah fixture terisolasi dan cleanup terverifikasi?
- Apakah izin dicabut di tengah lifecycle dan outcome ambigu ditangani sesuai kontrak?
- Apakah replay/concurrency diuji deterministik tanpa sleep sebagai koordinasi?
- Apakah build, konfigurasi, data dan sumber oracle konsisten pada setiap attempt?
- Apakah kegagalan pertama, perbaikan dan retest tetap dapat ditelusuri?

Suite hijau tidak mengisi requirement yang belum dipetakan atau membuktikan integrasi live yang belum dijalankan.
