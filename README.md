# ASIQ — edisi publik baru

Skill agen QA berbahasa Indonesia untuk kebutuhan, eksplorasi, regresi, CI, kinerja/reliabilitas, keamanan dan keputusan rilis berbasis bukti. Tidak mengunci domain bisnis atau framework. Mulai dari [SKILL.md](.agents/skills/asiq/SKILL.md).

## Status distribusi

Edisi ini disusun baru dengan bantuan AI, bukan salinan atau pengganti yang terbukti setara dengan edisi sebelumnya. Tidak membawa skor, inventaris benchmark, atau klaim test lama. Lihat [PROVENANCE.md](PROVENANCE.md). Pemilik telah menyetujui publikasi dengan lisensi [MIT](LICENSE) dan pemberitahuan copyright `2026 bararck`. Otorisasi pemilik ini bukan audit legal atau jaminan bebas hak pihak lain; batas asal-usul tetap berlaku.

## Pemasangan repo-local tanpa overwrite

1. Unduh atau salin paket ke direktori baru yang tidak berisi pekerjaan lain. Tidak perlu instalasi global, dependensi eksternal, atau akses jaringan untuk verifier.
2. Dalam repo tujuan, periksa apakah `.agents/skills/asiq` sudah ada. Jika ada, **berhenti**; jangan merge/replace otomatis. Pemilik harus memilih lokasi lain atau meninjau perubahan secara manual, dengan cadangan yang dibuat sendiri.
3. Jika belum ada, salin hanya direktori `.agents/skills/asiq` dari paket ini ke `.agents/skills/asiq` di repo tujuan menggunakan pengelola file. Pertahankan `references/` dan `templates/`. Sertakan salinan LICENSE sebagai `.agents/skills/asiq/LICENSE` untuk mempertahankan pemberitahuan copyright dan izin MIT; jangan menimpa LICENSE repo tujuan. Jangan menyalin konfigurasi CI paket ke repo tujuan tanpa review.
4. Pastikan agen yang digunakan mendukung discovery skill repo-local pada lokasi tersebut; bila tidak, muat `SKILL.md` secara eksplisit sesuai dokumentasi agen. Tidak ada klaim semua host memuatnya otomatis. Minta agen menyebut aturan read-only dan oracle sebelum memberi akses tindakan.
5. Untuk menghapus, hapus hanya folder skill yang baru disalin setelah memastikan tidak ada perubahan lokal yang ingin disimpan. Ini tidak menghapus artefak pengujian aplikasi.

## Validasi paket

Prasyarat: Python 3.11 atau 3.12. Dari root paket jalankan command yang sama di Windows/Linux:

```text
python scripts/verify.py
```

Verifier memakai stdlib, tanpa jaringan. Memeriksa metadata subset yang sengaja ketat, file wajib, teks MIT dan copyright pemilik, tautan Markdown lokal inline, path privat, lalu menjalankan unittest termasuk fixture negatif. Gate gagal jika tidak ada test, skip, unexpected success, error, kegagalan, penghentian runner (`shouldStop`), atau jumlah test berbeda dari deklarasi. Pengujian menulis fixture sementara melalui `tempfile` dan membersihkannya; bytecode dinonaktifkan. Traversal memangkas hanya direktori `.git` dan `__pycache__`; folder source lain, termasuk folder tersembunyi, tetap diperiksa. Symlink tidak diikuti dan ditolak. Verifier tidak mengeksekusi aplikasi target, tidak membuktikan keamanan, dan bukan pembuktian legal asal-usul. Tautan daring tidak diakses. Format tautan reference-style/HTML tidak digunakan dan tidak didukung pemeriksa.

CI: [workflow](.github/workflows/verify.yml) mendeklarasikan Windows/Linux dan Python 3.11/3.12. Menjalankan verifier lokal tidak membuktikan seluruh matriks CI telah berjalan. Jangan menyebut hasil CI sebelum memeriksa run nyata untuk revisi tersebut.

## Penggunaan

Berikan tujuan, sumber kebutuhan dalam scope, target/lingkungan, risiko, dan batas izin. Skill memulai secara read-only, menemukan stack aktual, memverifikasi oracle, lalu memilih jalur dan template. Tindakan aktif perlu persetujuan spesifik. Tidak ada PASS dari penilaian model atau eksekusi yang tidak terjadi. Keputusan rilis milik pemilik yang berwenang.

Laporkan masalah keamanan melalui [SECURITY.md](SECURITY.md), bukan issue publik berisi rahasia.
