# Gate opsional bukti QA aplikasi

Gate ini terpisah dari verifikasi paket ASIQ. Lulus fixture repository **bukan**
lulus QA aplikasi. Cakupannya universal: pemilik aplikasi menentukan requirement,
risiko, skenario, oracle, serta bukti yang relevan, bukan nama produk tertentu.
Python 3.11+ dan standard library cukup; tanpa jaringan atau dependensi tambahan.

```sh
python -B scripts/qa_gate.py --ledger run/ledger.json --baseline approved/baseline.json --evidence-root run/evidence
python -B -m unittest discover -s tests -p test_qa_gate.py -v
```

Ketiga argumen wajib eksplisit. Exit 0 berarti struktur, binding, hash, hitungan,
dan kelengkapan memenuhi aturan; 1 berarti ditolak; 2 berarti argumen salah.
Tidak ada shell, command JSON, network call, atau perubahan file yang dijalankan.
Diagnostik hanya pesan statis, tanpa mencetak path, command, isi JSON, atau secret.
Jangan simpan credential di argv maupun evidence; redaksi sebelum hashing.

## Baseline independen, versi 1

Baseline disediakan terpisah oleh pemilik scope/reviewer/CI yang dipercaya,
bukan diturunkan dari daftar skenario yang kebetulan dijalankan.
Semua field berikut wajib; field tambahan ditolak di semua objek.

```json
{
  "version": 1,
  "context": {
    "source_revision": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "build_id": "build-1",
    "environment": "isolated-test",
    "config_sha256": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
  },
  "requirements": ["REQ-1"],
  "risks": ["RISK-1"],
  "scenarios": [
    {"id": "SC-1", "requirement_ids": ["REQ-1"], "risk_ids": ["RISK-1"]}
  ]
}
```

Nilai contoh adalah **placeholder sintetis, bukan hasil eksekusi**. Revision
harus hex lowercase 40 atau 64 karakter; digest SHA-256 harus 64 hex lowercase.
`build_id` dan `environment` adalah string tidak kosong. Context di baseline,
ledger, dan setiap attempt harus sama persis. Hash config menunjuk konfigurasi
yang sudah disanitasi/diarsipkan oleh pipeline; gate tidak membaca source/build
atau config secara langsung. Baseline harus disetujui untuk context run tersebut.

ID memakai huruf/angka awal, kemudian huruf/angka/underscore/titik/hyphen, maksimal
80 karakter. Inventory requirement, risk, dan scenario harus tidak kosong serta
unik. Setiap scenario harus menautkan minimal satu requirement dan risiko yang
ada. Semua requirement dan risiko harus tercakup. Ledger harus memuat **tepat**
semua ID baseline: penghapusan ID, ID tambahan, dan duplikasi ditolak.

## Ledger versi 1

Top-level wajib: `version` (integer 1, bukan boolean), `baseline_sha256` (hash byte
file baseline persis, termasuk whitespace), `context`, `scenarios`, dan `counts`.
Tidak ada coercion tipe, key JSON duplikat, NaN, atau field asing yang diterima.
Context sama dengan contoh baseline. Setiap entry `scenarios` berbentuk:

```json
{
  "id": "SC-1",
  "selected": true,
  "gap": "",
  "attempts": [
    {
      "id": "A-1",
      "context": {
        "source_revision": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "build_id": "build-1",
        "environment": "isolated-test",
        "config_sha256": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
      },
      "status": "PASS",
      "command": {"argv": ["runner", "--offline"], "exit_code": 0, "status": "completed"},
      "oracle": {"expected": "allowed", "observed": "allowed", "verified": true},
      "artifacts": [{"path": "result.txt", "sha256": "DIGEST_BYTE_BUKTI_WAJIB_DIGANTI"}],
      "resolves": [],
      "fix": ""
    }
  ]
}
```

Contoh fragmen di atas sengaja tidak bisa dipakai sebagai klaim PASS: ganti
placeholder digest dengan hash file bukti nyata. Fixture positif lengkap yang
membangun hash dari byte aktual tersedia di `tests/test_qa_gate.py`.

- `selected` boolean; `gap` string. Skenario tidak dipilih atau belum dijalankan
  tetap wajib ada, memakai `attempts: []` dan alasan `gap` tidak kosong. Keduanya
  dihitung `not_run`, **tetap memblokir gate**. Tidak ada status SKIP, waiver,
  atau skip baru yang diam-diam menurunkan denominator.
- Attempt tersusun menurut urutan kejadian; ID unik dalam scenario. Simpan
  **seluruh** attempt, termasuk FAIL pertama. Context tidak boleh berubah dalam
  ledger; run dengan build/context baru memerlukan ledger dan baseline tersendiri,
  dengan arsip run lama tetap dipertahankan di sistem bukti eksternal.
- Status attempt hanya PASS/FAIL. Command mencatat argv array string tidak kosong,
  integer exit_code, dan status completed/timeout/error. PASS wajib completed,
  exit 0, expected/observed tidak kosong, `verified: true`, serta minimal satu
  artifact yang hash-nya cocok. FAIL tetap wajib menyimpan command, oracle dan
  artifact. Exit 0 sendiri bukan oracle. Expected dan observed tidak dibandingkan
  sebagai string: oracle dapat memeriksa batas, toleransi, atau properti lain;
  reviewer harus memeriksa kebenaran penilaian `verified`.
- FAIL tidak hilang hanya karena retry terakhir PASS. Retest PASS wajib menautkan
  ID FAIL sebelumnya lewat `resolves`, disertai `fix` tidak kosong (referensi dan
  deskripsi perbaikan). Link unknown/forward/self/duplikat atau ke FAIL yang sudah
  ditutup ditolak. Semua FAIL harus terselesaikan, attempt terakhir harus PASS.
  Tanpa link, `fix` wajib string kosong. Bukti dan hash attempt lama tetap dicek.
- `counts` wajib tepat `total`, `selected`, `passed`, `failed`, `not_run`, semua
  integer nonnegatif. `failed` mencakup scenario dengan FAIL belum terselesaikan
  atau attempt terakhir FAIL. Gate menghitung ulang semua angka; hanya seluruh
  scenario baseline terpilih dan PASS tanpa gap yang dapat lulus.

## Containment evidence

Path artifact memakai slash relatif, komponen ASCII dimulai huruf/angka/underscore/
hyphen dan dilanjutkan huruf/angka/underscore/hyphen/titik. Komponen kosong,
titik tunggal/ganda, trailing titik, absolute/drive/UNC, backslash, ADS/colon,
dan traversal ditolak. File harus reguler, bukan direktori/device/pipe. Symlink
serta Windows reparse point/junction ditolak pada artifact, direktori perantara,
evidence root, **dan semua ancestor root** sebelum resolve/open. Hash dibaca
streaming. File hilang, tak terbaca, atau digest salah menggagalkan gate.

## Batas keamanan dan keputusan release

Containment anti-link di atas berlaku untuk artifact/evidence, bukan path input
JSON baseline dan ledger. Kedua JSON dapat dibaca melalui symlink/junction;
caller wajib memilih snapshot input terpercaya dan melindunginya dengan ACL.
Jangan menganggap gate menegakkan kebijakan seluruh input bebas link.

Ini pemeriksaan konsistensi, **bukan autentikasi atau attestation eksekusi**.
SHA-256 tidak membuktikan siapa yang menjalankan command, siapa yang menulis
oracle, apakah source benar-benar dibuild, apakah baseline lengkap, atau apakah
attempt lama sengaja dihapus sebelum input diberikan. Seseorang yang dapat
mengubah baseline dan ledger bersama-sama dapat mengecilkan scope dan menghitung
ulang digest. Gate tidak dapat mendeteksi itu tanpa baseline/histori terpercaya.
Simpan baseline terproteksi, persetujuan reviewer, ledger append-only, identitas
runner, provenance build dan bukti run di penyimpanan independen/CI terkontrol.

Pemeriksaan filesystem ini bukan sandbox terhadap penyerang lokal yang mengubah
file/link secara bersamaan (TOCTOU), bukan deteksi hardlink, dan bukan pengganti
ACL. Jalankan pada snapshot evidence immutable di workspace terpercaya; batasi
ukuran input dan resource di runner. Jangan gunakan direktori evidence yang dapat
ditulis pihak lain selama validasi. Passing gate tidak membuktikan kelengkapan
cakupan bisnis, keamanan produk, atau kesiapan release tanpa review manusia.
