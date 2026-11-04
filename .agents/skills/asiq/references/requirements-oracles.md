# Kebutuhan, penemuan scope, dan oracle

## Inventaris awal

Catat aktor, tujuan pengguna, alur utama, kegagalan paling mahal, integrasi, batas data, lingkungan, dan pemilik keputusan. Cari bukti hanya dalam sumber yang diizinkan: acceptance criteria, spesifikasi versi aktif, kontrak API, konfigurasi, dan keputusan pemilik. Catat lokasi, revisi/tanggal, relevansi terhadap build, serta siapa yang dapat menyelesaikan konflik. Jangan menyalin data sensitif ke laporan.

Tanyakan hal yang mengubah keputusan: apa arti berhasil; variasi input yang sah; perilaku saat timeout/duplikasi; hak akses per peran; dan batas nonfungsional. Jangan mengasumsikan mata uang, aturan pembulatan, transaksi, yurisdiksi, atau pola domain tertentu.

## Ledger oracle

Buat tabel `requirement_id | perilaku | sumber+revisi | otoritas | status | skenario terkait | pertanyaan/pemilik`.

- `VERIFIED`: sumber otoritatif untuk scope/build ini telah diperiksa; tulis aturan expected yang dapat dibandingkan.
- `PROVISIONAL`: hipotesis atau konvensi yang belum disahkan; boleh memandu eksplorasi aman, tidak boleh menghasilkan verdict produk PASS/FAIL.
- `CONFLICTED`: sumber bertentangan; catat keduanya, jangan memilih diam-diam.
- `MISSING`: tidak ditemukan aturan; minta keputusan pemilik.

Perilaku implementasi saat ini bukan bukti bahwa perilaku tersebut benar. Test lama, output model, dan pola pesaing bukan otoritas otomatis. Property/metamorphic oracle (misalnya round-trip) hanya sah jika properti itu benar-benar sesuai kontrak; tulis asumsi dan ruang berlakunya.

## Ketidakpastian terlokalisasi

Petakan dependency tiap skenario ke oracle, data, akses, dan lingkungan. Blokir hanya node yang bergantung pada prasyarat yang belum selesai. Contoh: aturan pembulatan belum disahkan tidak harus menghentikan pemeriksaan navigasi dengan oracle independen. Jangan menandai kebutuhan keseluruhan PASS jika sebagian cakupannya belum diputuskan.

Selesai ketika setiap prioritas memiliki expected terverifikasi atau blocker eksplisit beserta pemiliknya, bukan ketika semua pertanyaan disembunyikan dalam asumsi.
