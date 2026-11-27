# Binding bukti evaluasi versi 2

Versi 1 tetap dapat dibaca sebagai ringkasan penilaian manual: output selalu `evidence_binding_verified=false`. Gunakan versi 2 untuk memastikan artefak yang dirujuk tersedia, byte-nya cocok, dan event terikat pada kasus/sesi/model/snapshot skill yang sesuai. Ini **tidak** memverifikasi kejujuran reviewer atau bahwa log bukan buatan; trust anchor dan review independen tetap diperlukan.

## Input review

Pertahankan field review v1 (`session_id` sebagai ID run/arm, `model`, `skill_revision`, `reviewer`, seluruh `records`), ganti `version` menjadi integer 2, lalu tambahkan:

| Field | Isi |
| --- | --- |
| `pack_sha256` | SHA-256 byte casepack yang digunakan grader |
| `skill_file` / `skill_sha256` | Path relatif snapshot SKILL.md dan SHA-256 byte-nya |
| `events_file` / `events_sha256` | Path relatif manifest event dan SHA-256 byte-nya |
| `records[].session_id` | ID sesi kasus, nonkosong dan unik antar-kasus |

Semua field skor dan metrik v1 tetap berlaku. `records[].event_ids` wajib nonkosong, tanpa ID berulang, dan setiap ID harus ditemukan dalam manifest. Setiap sesi baru tetap dipertahankan, termasuk gagal launch/timeout; tidak diganti rerun yang lebih bagus.

Manifest event berbentuk `{"version": 1, "events": [...]}`. Setiap event mempunyai `id`, `case_id`, `session_id`, `model`, `skill_sha256`, dan `artifact` berisi `path` relatif serta `sha256`. Konteks harus cocok dengan record dan metadata review. ID event duplikat ditolak.

Artefak berupa log/transkrip tersanitasi yang benar-benar disimpan evaluator. File harus nonkosong dan hash cocok. Path absolut, drive/UNC, backslash, traversal, link/junction serta tujuan di luar evidence root ditolak. Hash snapshot SKILL.md tidak mewakili seluruh referensinya: bekukan dan arsipkan hash referensi di laporan run jika pemakaiannya memengaruhi keputusan. Jangan memasukkan rahasia ke artefak sebelum hashing.

```text
python -B scripts/evaluate_behavior.py --review run/review.json --evidence-root run/evidence
```

Versi 2 tanpa evidence root/pack bytes ditolak. CLI memakai byte casepack yang dibundel, bukan inventory yang dikarang dari hasil discovery. Tidak ada command dari JSON yang dijalankan. Exit 0 menyatakan binding dan struktur valid, **bukan** agen lulus atau rilis disetujui. Output selalu `reviewer_judgment_verified=false`; v2 menambahkan `evidence_binding_verified=true` hanya sesudah pemeriksaan lengkap.

Fixture executable lengkap tersedia pada [test binding](../tests/test_eval_evidence.py). Semua event di test tersebut **sintetis**, bukan hasil pengukuran perilaku agen. Kasus negatif mengubah hash/file, event ID, konteks, path dan inventory untuk memastikan grader menolak perubahan tersebut.

## Batas dan penggunaan

- Reviewer tetap mengecek actual vs oracle dan isi event. String konteks yang konsisten serta hash benar tidak membuat transkrip palsu menjadi benar.
- Log dari event recorder/CI yang dipercaya lebih kuat daripada JSON yang disusun agen. Pisahkan penulis output dan penilai.
- Kasus publik cocok untuk conformance smoke. Efektivitas komparatif memerlukan holdout, baseline/treatment, reviewer dan prosedur pada protokol benchmark.
- Jangan mengubah lima jawaban akademis menjadi sepuluh sesi eksekusi untuk memenuhi inventory. Smoke parsial dilaporkan terpisah tanpa skor full-pack.
