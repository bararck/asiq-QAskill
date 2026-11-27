# Contoh terisi — seluruh hasil berikut sintetis

Contoh ini bahan belajar, **bukan pengujian yang dijalankan**. ID, waktu, build, path bukti dan observasi hanyalah ilustrasi; jangan menyalinnya menjadi ledger PASS aplikasi. Rekomendasi tidak menggantikan persetujuan pemilik.

## Tier 1 — perubahan label UI di Bolt

**Scope:** tombol Simpan pada editor profil preview `ui-b12`, browser desktop, 27 November 2026 10:00 +07:00. Tier 1 karena hanya copy lokal; tidak ada perubahan handler/data/auth. Mandat: permintaan pengguna untuk memperbaiki label dan memeriksa preview lokal masih berlaku. Batas: 10 menit, tanpa deployment.

**Oracle:** AC-UI-7 revisi 2 menetapkan label “Simpan profil”, aktivasi keyboard tetap memanggil handler yang sama. Oracle verified pada konteks ilustrasi.

**Ilustrasi hasil:** SC-UI-1, `execution=COMPLETED / verdict=PASS / cause=NONE`. Actual: label “Simpan profil”; Tab memfokuskan tombol dan Enter menjalankan aksi sekali. Bukti contoh `evidence/ui-b12-label.png` dan `evidence/ui-b12-keyboard.txt`, waktu/build/browser yang sama. SC-UI-2 viewport 360px: label terbaca, tombol tidak terpotong. Ini bukti UI pada preview, bukan integrasi backend.

**Gap:** persistence backend dan mobile browser asli belum diuji; tidak relevan dengan perubahan copy dan tidak mendapat PASS. Scope terpilih selesai, run berhenti. Tidak perlu ledger lengkap atau keputusan rilis formal untuk pemeriksaan ini.

## Tier 3 — perubahan API lintas layanan, consumer tidak tersedia

**Scope:** producer orders revisi `orders-r24`, kontrak API v3 approved, consumer fulfillment revisi belum diketahui. Tier 3 karena kontrak lintas layanan. Izin: test lokal producer dengan fixture sintetis; tidak mencakup clone repo, akses layanan baru atau deployment. Batas 30 menit.

| Perubahan → flow | Risiko / oracle | Pilihan | Hasil ilustrasi |
| --- | --- | --- | --- |
| Field optional `delivery_note` → create order | Payload lama tetap diterima, API v3 §4 | SC-API-1 dipilih | COMPLETED/PASS/NONE; unit producer, bukan E2E |
| Field baru → serializer → fulfillment | Consumer menerima payload baru, kontrak consumer belum tersedia | SC-API-2 dipilih | BLOCKED/INCONCLUSIVE/DEPENDENCY |
| Tidak berubah → ekspor CSV | Di luar perubahan | SC-API-3 tidak dipilih | NOT_RUN; gap dicatat |

**Bukti contoh:** A1 command `python -m unittest tests.test_orders`, exit 0, ditemukan/dijalankan 2/2; `evidence/orders-r24.txt`, waktu 27 November 2026 10:20 +07:00, local fixture config C2. Bukti hanya mengikat producer tersebut. Consumer tidak diimplementasikan berdasarkan tebakan; mock lokal tidak membuktikan kompatibilitas deployed.

**Laporan:** “Dua pemeriksaan producer memenuhi kontrak v3. Kompatibilitas fulfillment belum dapat disimpulkan karena source/kontrak consumer tidak tersedia. Pemeriksaan producer selesai; integrasi tetap BLOCKED. Rekomendasi rilis: INSUFFICIENT_EVIDENCE; pemilik integrasi perlu menyediakan revisi consumer dan bukti kontraknya.”

## Tier 3 — retry/stateful, kegagalan pertama dipertahankan

**Scope:** pengiriman job staging sintetis `worker-b9`, oracle JOB-3 menyatakan replay key yang sama hanya menghasilkan satu delivery. Izin bounded replay pada fixture `job-demo-21`, maksimal 3 attempt/15 menit; tidak memakai data pengguna.

| Attempt | Konteks | Expected / actual ilustrasi | execution / verdict / cause |
| --- | --- | --- | --- |
| A1 | worker-b9 / fixture F1 | 1 delivery / 2 delivery | COMPLETED / FAIL / PRODUCT (duplikasi teramati; akar penyebab belum diketahui) |
| A2 retry diagnostik | worker-b9 / fixture baru F2, perubahan data dicatat | 1 delivery / 1 delivery | COMPLETED / PASS / NONE |

**Keputusan ilustrasi:** hasil gabungan INCONCLUSIVE; A2 tidak menyelesaikan A1 tanpa diagnosis. Bukti contoh `evidence/A1-deliveries.json` dan `evidence/A2-deliveries.json` tetap tersimpan terpisah dengan timestamp, fixture, build, konfigurasi dan command. Tidak disebut “semua hijau”. Batas habis, berhenti dan laporkan bug duplikasi dengan langkah reproduksi A1.

Jika perbaikan idempotency dibuat pada `worker-b10`, tautkan perubahan dan A3 retest ke A1; kumpulkan bukti baru. Jangan menggabungkan bukti b9/b10 menjadi satu run seolah konteks sama.

## Runner rusak dan humanisasi laporan

Sumber ilustrasi: “Runner timeout sebelum assertion. Diduga fixture infrastructure. 3 NOT_RUN. Produk belum teruji. Build b22.”

Laporan yang mempertahankan fakta: “Build b22 belum dapat dinilai: runner timeout sebelum assertion dan 3 skenario masih NOT_RUN. Penyebab diduga pada fixture infrastructure. `execution=ERROR, verdict=INCONCLUSIVE, cause=INFRASTRUCTURE (dugaan)`. Periksa setup fixture, lalu jalankan kembali skenario yang tertahan dalam mandat.”

Jangan mengubahnya menjadi “3 test produk gagal” atau memberi GO karena kegagalan dianggap hanya infra.
