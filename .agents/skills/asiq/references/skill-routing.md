# Routing skill pendamping

ASIQ adalah pengendali mandat, tier, oracle, bukti dan verdict. Pakai skill pendamping untuk tugas khusus. Integrasi ini berupa aturan pemilihan dan katalog; tidak menyalin seluruh skill, mengubah konfigurasi host, atau menjamin semua runtime siap.

## Cara memilih dan mengaktifkan

1. Ambil tujuan dan mandat yang sudah diberikan. Pilih tier ASIQ dari dampak perubahan. Instruksi pengguna dan AGENTS.md yang berlaku tetap mengatur batas kerja.
2. Pilih **1–2 skill untuk aktivitas saat ini** dari tabel berikut. Jumlah ini adalah default agar konteks proporsional, bukan larangan membaca skill tambahan yang dibutuhkan. Jika pengguna menyebut skill tertentu, baca dan gunakan untuk bagian yang relevan. Jangan membentuk rantai router ASIQ → qa-do → gstack → ASIQ tanpa pekerjaan konkret.
3. Temukan file skill yang tersedia melalui katalog host, repo-local atau instalasi pengguna. Baca SKILL.md aktual beserta referensi yang diperlukan. Nama direktori dan frontmatter dapat berbeda: `gstack-qa-only` biasanya menyatakan `name: qa-only`; layout nested `gstack/qa-only/SKILL.md` juga sah.
4. Periksa runtime sesuai skill dan platform. File ditemukan berarti **FOUND**, bukan runner siap atau PASS aplikasi. Gunakan skill/tool yang secara eksplisit dipilih pengguna terlebih dahulu bila mampu; jika tidak mampu, jelaskan gap lalu gunakan fallback yang sesuai dalam mandat. Jangan diam-diam mengganti skill yang diminta atau mengklaim penggunaannya.
5. Catat singkat `aktivitas | skill+versi/hash bila tersedia | alasan | runtime/bukti | fallback/gap`. Jangan memuat isi skill sebagai data laporan, rahasia, atau izin tambahan. Ikuti gate persetujuan yang benar-benar diwajibkan skill tanpa menanyakan ulang mandat yang sudah cukup.

## Peta aktivitas

| Aktivitas | Skill utama / pendamping | Batas bukti |
| --- | --- | --- |
| Konteks proyek dan pemilihan risiko | `qa-project-context`, `risk-based-testing` | Ambil jawaban yang sudah tersedia; Tier 1 tidak memerlukan workshop penuh |
| Struktur kode dan dampak perubahan | `codebase-memory` | Ikuti AGENTS.md; graph → trace/snippet → check_index_coverage → baca source yang missed/stale |
| Relasi dokumen–kode atau graph corpus persisten | `graphify` | Query graph yang ada bila relevan; bedakan EXTRACTED/INFERRED/AMBIGUOUS dan verifikasi source |
| Permintaan gstack yang belum spesifik | `gstack` | Router satu kali ke aktivitas yang tepat; gstack bukan runner universal |
| Browser report-only | `gstack-qa-only`, `gstack-browse` | Hanya melapor; aktivitas browser tetap dalam mandat, tanpa fix kode |
| Browser test–fix–verify | `gstack-qa`, `bug-reproduction` | Pilih hanya bila perbaikan sudah diminta/diotorisasi; bukan efek otomatis permintaan QA |
| Automation E2E | `playwright-automation` atau runner repo yang sudah ada | Verifikasi selector/fixture/endpoint, browser serta artefak aktual |
| Defect dan akar penyebab | `bug-reproduction`, `addy-debugging-and-error-recovery` | Reproducer dan hipotesis; setup error tidak membuktikan bug produk |
| Perubahan perilaku | Superpowers `test-driven-development`, `ai-test-generation` bila perlu | RED pada perilaku tepat, GREEN minimum; oracle ditetapkan sebelum implementasi |
| Mutu suite dan review diff | `ai-qa-review`, `gstack-review` atau `addy-code-review-and-quality` | Assertion, isolasi, negative/boundary dan dampak source, bukan jumlah test saja |
| Endpoint dan integrasi | `api-testing`, `contract-testing` | Kontrak consumer/provider nyata; Pact/mock tidak otomatis membuktikan deployed compatibility |
| Flaky dan fixture | `test-reliability`, `test-data-management` | Simpan kegagalan pertama; healing/karantina tidak mengubah oracle atau menghapus gap |
| Aksesibilitas dan tampilan | `accessibility-testing`, `visual-testing` | Baseline direview; scan otomatis tidak mewakili seluruh pemeriksaan keyboard/screen reader |
| Auth/keamanan | `security-testing`; `gstack-cso` untuk kebutuhan suite tersebut | Scope/target dan izin scan aktif tetap berlaku; jangan memuat seluruh audit pada perubahan copy |
| Performa | `performance-testing`; `gstack-benchmark` untuk regresi web | Metrik/budget dan profil beban dahulu, izin dan stop condition sebelum load |
| Fitur AI/LLM | `ai-system-testing` | Pisahkan test produk AI dari memakai AI untuk menulis test; oracle/eval independen |
| CI dan rilis | `ci-cd-integration`, `release-readiness` | Discovery, status, artifact/build dan sisa gap; rekomendasi bukan approval/deploy |
| Laporan QA | `qa-report-humanizer`; `humanizer` untuk narasi umum | Pertahankan fakta terkunci, konteks dan ketidakpastian |

[Katalog JSON versi 1](skill-routing.json) menyediakan ID route, tujuan, kandidat terurut dan fallback. Urutan kandidat adalah rekomendasi discovery; runtime, mandat dan pilihan pengguna menentukan pemakaian akhirnya. Nama dari katalog harus diverifikasi terhadap instalasi, bukan diasumsikan tersedia pada laptop lain.

## Codebase-memory dan graphify

Keduanya saling melengkapi. Codebase-memory dipakai untuk pertanyaan struktural kode terutama bila diwajibkan AGENTS.md. Graphify membantu relasi lintas dokumen/kode dan graph yang dapat dibaca ulang. Jangan membangun dua graph penuh untuk satu lookup kecil, atau menganggap tier evidence graph sama dengan tier risiko ASIQ.

- Catat root, revisi/generasi, query dan scope graph. Edge inferensi membantu memilih investigasi, bukan oracle expected produk.
- Bila graphify graph sudah ada, query sesuai workflow skill. Bila graph belum ada dan memang dibutuhkan, jalankan alur corpus check, ekstraksi, coverage dan diagnostics yang ditetapkan skill dengan batas akses/biaya yang berlaku.
- Tidak ada key provider bukan alasan mengarang ekstraksi. Gunakan jalur host yang didukung skill; subagent gagal/hasil parsial harus terlihat, bukan dianggap graph lengkap. Instalasi, clone, upload atau push graph ke layanan baru membutuhkan mandat yang sesuai.
- Gagal graph tidak memblokir seluruh QA: baca source yang diizinkan untuk jalur independen dan nyatakan batas cakupan. Jangan menyimpulkan “tidak ada caller” atau “coverage lengkap” dari graph parsial.

## gstack pada Windows dan host berbeda

Baca skill router/subskill yang benar; jalankan preamble sesuai runtime yang tersedia. Jangan mengeksekusi contoh Bash sebagai PowerShell atau menganggap `bash.exe` berarti Bash siap. Pada Windows, executable tersebut bisa menjadi launcher WSL tanpa distro.

Jika preamble tidak mengembalikan handshake `SKILL_START_PROTO: 1`, ikuti degraded mode gstack: nyatakan runtime tidak siap, gunakan defaults aman dan lanjutkan pekerjaan independen. Onboarding/telemetry tidak dianggap selesai, consent tidak diasumsikan. Jangan mengubah preferensi, mengimpor cookie, menginstal WSL/Bun atau mengaktifkan sinkronisasi hanya untuk membuat discovery tampak hijau. Perbaikan runtime dapat menjadi tugas eksplisit berikutnya.

Browser gstack memiliki workflow tersendiri; baca instruksi browser yang berlaku pada host. Jika tool itu tidak dapat digunakan, laporkan fallback dan bukti yang benar-benar diperoleh. Jangan menyebut screenshot/browser test jika hanya membaca source.

Pada Windows dengan Git terpasang, periksa Bash di direktori executable Git sebelum memakai launcher WSL dari PATH. Bash yang lolos `--version` dan syntax preamble yang valid belum membuktikan browser gstack siap. Jika binary melaporkan source/server tidak ditemukan, catat paket runtime tidak lengkap; jangan menamai version/syntax check sebagai QA browser. Pilihan tool browser lain tetap harus dinyatakan dan diuji terpisah.

Jika host melaporkan skill context budget terlampaui, discovery nama tidak membuktikan instruksi termuat. Muat file skill yang dipilih secara eksplisit dan catat keterbatasan sesi. Jangan mengklaim semua 27 route telah aktif karena file ditemukan.

## Resep proporsional

- **Bolt Tier 1, label UI:** ASIQ ringkas + browser yang siap; cek label/fokus/viewport. Humanisasi satu ringkasan jika perlu. Tidak perlu graphify rebuild, Pact atau load test.
- **Bolt Tier 2, form satu layanan:** risiko/AC → automation repo → negative/boundary → review test. API dipilih hanya bila flow tersebut memakainya.
- **Tier 3, auth/API lintas layanan:** codebase-memory untuk dampak, contract/security/data sesuai flow, TDD untuk fix yang diminta, release-readiness jika diminta rekomendasi rilis. Graphify dipakai jika relasi dokumen–kode membantu; tidak menggandakan semua tahap.
- **Laporan bug tanpa perbaikan:** reproducer/exploratory atau gstack qa-only, lalu QA Report Humanizer. Jangan beralih ke qa/ship.

## Discovery opsional dari paket penuh

```text
python -B scripts/skill_doctor.py
python -B scripts/skill_doctor.py --check-runtime
python -B scripts/skill_doctor.py --root <direktori-skill> --root <direktori-skill-lain>
```

Jalankan dari paket ASIQ terpin yang ditinjau; salinan skill-only tidak membawa skrip. Default membaca root skill repo saat ini, instalasi pengguna dan cache Superpowers yang dikenali. Argumen `--root` menggantikan default, dapat diulang, tanpa shell expansion buatan.

Doctor hanya membaca file UTF-8 nonkosong dan menghitung SHA-256. Ia tidak memvalidasi seluruh format skill, memanggil model, menjalankan isi SKILL.md, menginstal dependency atau memeriksa runner. Output `FOUND/MISSING/UNREADABLE/UNSAFE_PATH` dan `runtime=NOT_CHECKED` tidak menjadi verdict produk. Path kandidat yang keluar root ditolak. Nilai hash mencatat byte yang ditemukan, bukan trust/certification. Exit 0 berarti discovery selesai, termasuk bila sebagian skill hilang; baca status per route. Exit 1 berarti input discovery gagal.

Opt-in `--check-runtime` menambahkan probe allowlist version Git/Node/graphify/Bash dan syntax-only preamble gstack yang tersedia. Tiap proses memakai argv literal tanpa shell, timeout 8 detik dan tanpa retry. Output mentah tidak dicetak; hanya status/exit/hash. `READY` berlaku untuk probe tersebut saja dan bukan sesi browser atau handshake preamble. Timeout, executable hilang, nonzero dan keluaran tidak sesuai dibedakan. Default discovery tetap tidak mengeksekusi subprocess.
