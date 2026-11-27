# Kedalaman QA dan tier Bolt

Pilih tier tertinggi yang dipicu dampak aktual. Durasi adalah budget yang disepakati, bukan janji waktu universal. Banyak baris berubah tidak otomatis berisiko tinggi; satu baris izin akses dapat memicu Tier 3.

| Tier / mode | Trigger | Artefak proporsional | Pemeriksaan utama |
| --- | --- | --- | --- |
| 1 / ringkas | Copy, styling atau komponen UI lokal tanpa perubahan state, kontrak, auth, data atau integrasi | Satu catatan: scope, alasan tier, oracle+sumber, actual+bukti+konteks, verdict, gap | Perubahan yang diminta, interaksi/fokus terkait, viewport relevan; tidak ada klaim cakupan penuh |
| 2 / standar | Perilaku fitur terbatas, validasi/form atau API satu layanan dengan dependency yang diketahui | Skenario, perubahan→flow→risiko→pilihan regresi, catatan attempt dan gap | Happy path, batas, negatif, regresi pemanggil/consumer yang terdampak |
| 3 / mendalam | Auth/izin, data sensitif, migrasi, uang, state/retry/replay, concurrency, kontrak lintas layanan, perubahan besar atau keputusan rilis berisiko tinggi | Inventory dan ledger lengkap dalam scope, oracle, dependency flow, attempt, evidence binding, risiko residual dan keputusan bila diminta | Invariant, kompatibilitas, isolasi, failure/recovery dan jalur risiko relevan |

Jika pengguna menentukan tier, hormati batas kerja yang diizinkan dan nyatakan gap jika tier itu tidak cukup untuk kesimpulan yang diminta. Jangan diam-diam memperluas target atau menyatakan GO dari audit ringkas.

## Pemakaian langsung pada Bolt

Bolt di sini berarti proyek yang dibuat/diedit melalui Bolt. Preview atau tampilan sukses belum membuktikan backend, persistence, auth atau integrasi. Periksa stack aktual sebelum memilih command; jangan menganggap runner atau database tertentu tersedia.

- Nyatakan `Tier N — alasan dampak` di awal. Tier 1 untuk label/styling lokal; Tier 2 untuk form/fitur satu layanan; Tier 3 untuk auth, persistence lintas layanan, pembayaran atau retry/stateful.
- Catat identitas preview/build dan konfigurasi yang teramati. Bila preview tidak memiliki identitas build yang bisa diverifikasi, tulis keterbatasan itu; jangan mengarang hash.
- Bedakan mock, local preview, staging dan deployed. Jangan mengklaim integrasi live dari data contoh. Gunakan mandat pengujian yang sudah diberikan; tidak perlu izin ulang untuk tindakan yang sama.
- Pilih tes dari risiko. Tidak perlu menjalankan Tier 1 lalu 2 lalu 3 sebagai ritual. Tier 3 mencakup pemeriksaan kecil yang relevan tanpa menggandakan laporan.

## Seleksi regresi dan aturan berhenti

Sebelum run buat tabel kecil; Tier 1 boleh satu kalimat ekuivalen.

| Perubahan | Flow terdampak | Risiko / oracle | Skenario | Dipilih? / alasan |
| --- | --- | --- | --- | --- |
| Validasi panjang nama | Simpan profil | Batas 80 dari AC-2 | SC-1: 80 diterima; SC-2: 81 ditolak | Ya: kontrak berubah |
| Tidak berubah | Ekspor profil | Format CSV | SC-3 | Tidak: di luar perubahan; gap eksplisit |

Prioritaskan dampak × kemungkinan dengan alasan dari sumber, lalu jalur pemanggil/consumer, invariant dan defect sebelumnya. Jangan menganggap yang tidak dipilih sudah PASS. Inventory resmi yang ada tetap menjadi denominator, bukan hanya test hasil discovery.

Catat budget waktu, attempt, akses dan kondisi berhenti. Selesai jika semua skenario terpilih selesai dan hasil direkonsiliasi. Berhenti lebih awal pada budget tercapai, target berubah, izin dicabut, data tidak aman atau oracle penting konflik. Blokir hanya pekerjaan yang bergantung pada hambatan tersebut; lanjutkan scope independen dalam budget. Retest memerlukan hipotesis/perbaikan atau alasan diagnostik; simpan setiap attempt. Setelah hijau, jangan memperluas pengujian tanpa risiko atau perubahan baru.

## Status eksekusi, verdict dan diagnosis

`execution` menjelaskan proses; `verdict` menjelaskan apakah bukti memenuhi oracle produk. `cause` menjelaskan penyebab yang diketahui/diduga, bukan pengganti bukti.

| Keadaan | execution | verdict | cause | Status skenario lama |
| --- | --- | --- | --- | --- |
| Belum dicoba | NOT_RUN | INCONCLUSIVE | NONE | NOT_RUN |
| Dependency tidak tersedia | BLOCKED | INCONCLUSIVE | DEPENDENCY | BLOCKED |
| Oracle konflik | BLOCKED | INCONCLUSIVE | ORACLE | BLOCKED |
| Runner crash sebelum assertion | ERROR | INCONCLUSIVE | INFRASTRUCTURE (jika terbukti; selain itu UNKNOWN) | INCONCLUSIVE |
| Exit 0, nol test | COMPLETED | INCONCLUSIVE | TEST_DISCOVERY | INCONCLUSIVE |
| Assertion aktual melanggar oracle verified | COMPLETED | FAIL | PRODUCT (atau UNKNOWN sampai triase) | FAIL |
| Actual memenuhi oracle dan bukti cocok | COMPLETED | PASS | NONE | PASS |
| Budget habis sebelum cukup bukti | BLOCKED | INCONCLUSIVE | LIMIT | INCONCLUSIVE |

Review statis tetap `STATIC_REVIEW` dan tidak menghasilkan PASS dinamis. Kegagalan assertion dapat berasal dari test salah; diagnosis produk memerlukan triase. Retry A1 FAIL → A2 PASS pada konteks sama tanpa diagnosis menghasilkan riwayat campuran dan verdict gabungan INCONCLUSIVE. Perbaikan terikat konteks baru boleh mendukung PASS kandidat setelah retest; A1 tetap tercatat.

Gate paket penuh versi 1 tetap memakai `status` lama. Jangan tambahkan field baru ke ledger v1 yang ketat: catat tiga sumbu di Markdown pendamping dan petakan melalui tabel ini. Mode ringkas tidak melonggarkan syarat clean gate formal. Skema ledger baru perlu migrasi berversi dan review terpisah.
