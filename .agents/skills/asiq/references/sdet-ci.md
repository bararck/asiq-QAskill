# Regresi SDET dan CI

## Discovery sebelum command

Identifikasi manifest/lockfile, runtime, runner, pola penemuan test, setup/teardown, layanan eksternal, konfigurasi CI dan filter test dari file dalam scope. Verifikasi command yang ada; jangan menciptakan command berdasarkan nama framework. Membaca konfigurasi tidak sama dengan membuktikan runner tersedia. Instalasi dependensi, perubahan file, dan menjalankan hook memerlukan izin yang sesuai.

## Rancangan yang dapat dipelihara

- Hubungkan test ke risiko dan oracle. Pilih unit untuk aturan lokal, integrasi untuk batas komponen, kontrak untuk kompatibilitas, E2E untuk alur kritis; jangan memakai E2E untuk semua variasi.
- Gunakan data sintetis terisolasi per test, clock/seed terkendali bila relevan, cleanup terbatas pada resource yang dibuat test. Jangan menghapus resource berdasarkan pola nama luas.
- Assertion membandingkan actual ke oracle terverifikasi, bukan hanya status sukses atau screenshot baseline yang belum direview. Mock membuktikan interaksi model, bukan integrasi nyata.
- Untuk perubahan yang diizinkan, demonstrasikan test gagal karena perilaku yang tepat, bukan setup rusak; perbaiki minimal lalu jalankan ulang cakupan terkait. Jangan mengubah expected hanya agar test hijau.

## Gate yang tidak menutupi kegagalan

Catat commit/build, environment, command, filter, jumlah ditemukan/dijalankan, status tiap test, exit code dan artefak tersanitasi. Nol test, discovery error, skip tak disetujui, unexpected success, runner error, atau artefak hilang harus membuat gate gagal/terblokir, bukan lulus diam-diam. Daftar pengecualian eksplisit harus memiliki alasan, pemilik, expiry, dan dampak; jangan menganggap seluruh skip aman.

Simpan kegagalan percobaan pertama dan jumlah retry. Karantina flaky harus terlihat, terbatas waktunya, dan tidak dihitung sebagai cakupan hijau. Laporan CI harus mengikat artefak ke build yang diputuskan; badge hijau dari branch/build lain bukan bukti rilis ini. Jangan mengunggah environment dump, token, atau raw data pengguna ke artefak.

Selesai ketika test yang disepakati benar-benar berjalan, jumlah/status direkonsiliasi, dan keputusan atas gap tercatat. Menguji verifier paket skill hanya memvalidasi paket, bukan sistem pengguna.

## Inventory dan evidence ledger

Bekukan daftar ID resmi secara independen sebelum eksekusi, beserta kebutuhan, risiko, oracle dan pilihan regresi. Cocokkan ledger terhadap baseline tersebut, bukan hanya angka total: test berbeda dengan jumlah sama tetap perubahan coverage. Varian tetap dapat ditelusuri ke skenario canonical. Item tidak dipilih tetap terlihat NOT_RUN dengan alasan; skip baru atau ID hilang tidak boleh memperoleh clean gate.

Catat konteks per attempt: source revision/hash, build, environment, konfigurasi/data, command/filter, waktu dan zona, status, exit code, actual, artifact tersanitasi dan hash. Jangan menyatukan log dari build berbeda sebagai bukti satu build. Perbaikan yang mengubah source membutuhkan konteks baru dan tautan eksplisit ke kegagalan sebelumnya. Lindungi baseline dan bukti pada CI/access control yang dikelola tim; hash tanpa trust anchor hanya mendeteksi perbedaan byte.

Untuk state, fixture, replay, izin berubah dan hasil provider ambigu, gunakan [workflow stateful](stateful-workflows.md). Pisahkan diagnosis produk dari fixture/infrastruktur, dan hasil mock dari integrasi nyata. Tooling ledger opsional tersedia pada paket ASIQ penuh; jangan menganggap salinan skill menyertakannya atau memasangnya ke repo konsumen otomatis.
