# Audit integrasi skill lokal — 27 November 2026

Scope: discovery folder skill pengguna dan repo ASIQ, pemeriksaan metadata/petunjuk awal skill terkait, serta probe runtime terbatas. Ini bukan audit keamanan semua skill terpasang atau bukti seluruh workflow berhasil.

## Hasil yang teramati

- Katalog ASIQ memetakan **27 aktivitas**. Doctor menemukan file kandidat untuk seluruh 27 route di lingkungan pengembangan ini, termasuk Superpowers TDD dari cache plugin. Hasil ini spesifik instalasi saat pemeriksaan; jalankan doctor lagi setelah perubahan instalasi.
- gstack, gstack qa/qa-only/browse/review/investigate, graphify, codebase-memory, keluarga Addy dan skill QA spesialis yang dipetakan tersedia sebagai file. Katalog memilih kandidat, bukan mengeksekusi semuanya.
- `graphify --version` exit 0, versi **0.9.119**. Interpreter `python` default tidak memiliki modul graphify; CLI terpasang terpisah. Gunakan interpreter yang diselesaikan workflow graphify, jangan memasang ulang hanya karena import pada Python default gagal. Belum dibangun graphify corpus untuk validasi integrasi ini.
- Preamble gstack melalui `bash` exit 1: launcher WSL melaporkan tidak ada distro terpasang. Tidak ada handshake sehat; onboarding/consent/telemetry tidak dijalankan sebagai sesi sehat. Bun tidak ditemukan oleh pemeriksaan command yang dilakukan. Ini gap runtime, bukan bukti bug produk atau kegagalan seluruh skill gstack.
- Skill ASIQ global sebelumnya **0.3.0**, lalu diperbarui ke kandidat **0.4.0** sesuai permintaan pengguna. **17 file skill** disalin dan hash source/tujuan dicocokkan satu per satu; LICENSE disertakan. Versi sebelumnya dicadangkan di direktori backup pengguna di luar direktori discovery skill. Ini pemasangan panduan/routing, bukan pemasangan ulang seluruh runtime pendamping.

## Integrasi yang ditambahkan

[Aturan routing](../.agents/skills/asiq/references/skill-routing.md) membedakan tujuan graph, QA laporan/fix, kebutuhan runtime dan fallback. [Katalog JSON](../.agents/skills/asiq/references/skill-routing.json) bersifat portabel tanpa path privat. [Doctor](../scripts/skill_doctor.py) membaca file dan hash tanpa menjalankan instruksi skill atau menginstal dependency.

Prioritas berikut untuk meningkatkan mutu ASIQ:

1. **Evaluasi agen aktual:** jalankan kasus konformansi dan holdout independen dengan event tool, reviewer dan baseline/treatment. Ukur verdict, bukti, pelanggaran scope, pertanyaan berulang dan durasi QA kecil. Grader hijau belum membuktikan agen patuh.
2. **Runtime yang dapat direproduksi:** pilih runtime gstack yang didukung laptop, siapkan dalam tugas berizin, lalu smoke-test tool browser yang dipakai. Hindari memasang semua framework QA sekaligus.
3. **Schema ledger berversi:** terbitkan schema scenario/attempt/oracle/evidence beserta migrasi dari v1 dan fixture valid/tidak valid. Jangan mengubah ledger ketat diam-diam.
4. **Validasi proyek nyata terbatas:** satu flow UI, satu API/kontrak dan satu state/retry pada lingkungan uji berizin, dengan oracle independen. Pilih tambahan skill berdasarkan gap yang muncul.

Pelajaran operasional yang disimpan: executable Bash pada Windows dapat berupa launcher WSL tanpa distro; CLI Python yang diinstal terisolasi dapat bekerja meski import pada Python default gagal. Keduanya perlu diperiksa terpisah dari keberadaan SKILL.md.

Validasi pengembangan lokal: `python -B scripts/verify.py` selesai dengan 83 test lulus dan negative control 8 assertion failures yang diharapkan. Test doctor melewati baseline gagal lalu implementasi hijau; hasil tersebut memvalidasi discovery, bukan kepatuhan agen atau mutu aplikasi. Evaluasi agen aktual tetap NOT_RUN.

## Pembaruan sesudah review

Git Bash lokal ditemukan melalui lokasi Git dan dapat menjalankan shell/config gstack; penggunaan launcher WSL di PATH sebelumnya tidak mencakup instalasi ini. Doctor kini memiliki opt-in version/syntax probe yang memakai Git Bash tersebut. Graphify CLI tetap tersedia. Browser gstack mencoba bootstrap dan gagal karena source server tidak ditemukan; browser belum dinyatakan siap.

Satu [smoke pemahaman aktual](../benchmarks/results/instruction-smoke.json) melalui sesi Codex read-only terpisah kini tersedia untuk lima kasus publik. Ini menggantikan status “belum ada sesi pemahaman sama sekali”, namun full-pack/efektivitas berpasangan tetap NOT_RUN. [Review kesiapan](readiness-review.md) memuat skor dengan batas yang eksplisit.
