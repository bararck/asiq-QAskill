# Dependency dan flow review

- Mandat/owner/izin baca dan eksekusi:
- Repo utama: root, revision, dirty state, area yang dibaca:
- Requirement/desain: ID, sumber/revisi, status approval, konflik dan owner:
- Scope yang tidak diperiksa:

## Dependency inventory

| ID | Jenis | Versi resolved/commit | Declaration | Pemakai aktual | Lokasi berizin | Status akses |
|---|---|---|---|---|---|---|

Status akses: AVAILABLE / UNAVAILABLE. Jangan isi versi deployed dari lockfile saja.

## Flow dan kontrak

| Edge ID | Aktor/state awal | Producer path:symbol @revision | Consumer path:symbol @revision | Input/output/error contract | State/side effect | CONFIRMED / ASSUMED / UNAVAILABLE | Bukti |
|---|---|---|---|---|---|---|---|

## Requirement → desain → logic → regresi

| Requirement ID | Desain/flow disetujui | Invariant/oracle independen | Implementasi aktual | Scenario canonical/varian | Dipilih/alasan | Status dan bukti/gap |
|---|---|---|---|---|---|---|

## Temuan

| ID | DESIGN_GAP / IMPLEMENTATION_MISMATCH / OBSERVED_DEFECT / COMPATIBILITY_UNKNOWN | Oracle | Actual + lokasi/revisi | Confidence | Verifikasi berikutnya | Owner |
|---|---|---|---|---|---|---|

## Keputusan

- Edge CONFIRMED / ASSUMED / UNAVAILABLE dan cara menghitung:
- Scenario selected / executed / not-run; baseline resmi dan gap:
- Review desain visual vs logic vs integrasi: bukti terpisah:
- Perubahan fix → revision/build baru → retest dan referensi FAIL awal:
- Residual risk, blocker, owner acceptance:

Template ini struktur laporan manual; bukan schema qa_gate dan tidak otomatis divalidasi olehnya. STATIC_REVIEW tidak menjadi PASS dinamis. Field yang belum diketahui tetap eksplisit, bukan diisi asumsi agar tabel lengkap.
