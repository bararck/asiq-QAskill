# Keputusan rilis <build/revisi>

- Lingkungan/konfigurasi/data, cakupan perubahan:
- Tanggal+zona, pemilik keputusan, mandat:
- Kriteria penerimaan dan oracle beserta sumber/revisi:
- Rekomendasi QA: GO / NO_GO / CONDITIONAL / INSUFFICIENT_EVIDENCE
- Keputusan pemilik: BELUM DIPUTUSKAN

| Skenario/risiko | Status | Bukti + waktu/build | Gap / pemilik |
| --- | --- | --- | --- |
| <ID> | NOT_RUN | Belum ada | <isi> |

## Rekonsiliasi

- Jumlah skenario dalam scope:
- NOT_RUN / BLOCKED / PASS / FAIL / INCONCLUSIVE (jumlah harus cocok total):
- Review statis (terpisah; tidak ditambahkan sebagai PASS dinamis):
- Skip, retry, discovery/infrastruktur error dan implikasinya:
- Cakupan di luar scope dan alasan:
- Bukti basi atau berbeda lingkungan; dampak terhadap keputusan:
- Revisi/hash baseline inventory, ID hilang/tambahan dan skip baru:
- Hasil gate ledger/bukti atau kontrol manual bila tool tidak tersedia:
- Fixture/infrastruktur versus defect produk; integrasi mock/lokal/live yang terbukti:

## Dasar keputusan

- Teramati dan terverifikasi:
- Asumsi / belum diketahui:
- Bug terbuka, severity, risiko residual dan pemilik penerimaan:
- Syarat sebelum rilis, pemilik, tenggat dan bukti pemenuhannya:
- Monitoring, batas rollback, pelaksana dan izin tindakan:
- Persetujuan eksplisit pemilik (identitas/peran, waktu, scope):

Tidak ada GO otomatis dari skor, model, atau jumlah test. Syarat yang belum terpenuhi tetap terbuka; jangan menyatakan rilis aman tanpa batasan.
