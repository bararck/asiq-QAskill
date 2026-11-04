# Keamanan, bukti, dan privasi

## Batas keamanan

Review pasif hanya dalam scope baca yang diberikan. Scanner aktif, probing auth, fuzzing, exploit, perubahan izin, dan akses lintas tenant memerlukan otorisasi eksplisit atas target serta metode. Bukti kerentanan bukan izin eksploitasi lebih jauh. Jika data pihak lain terlihat, berhenti, minimalkan paparan, dan eskalasi lewat kanal privat yang disepakati; jangan menyalinnya sebagai demonstrasi.

Susun threat checklist dari trust boundary aktual: autentikasi/session, matriks peran dan objek, validasi input/output, dependency/configuration, logging, serta alur data. Gunakan identitas dan objek sintetis yang disetujui untuk pemeriksaan otorisasi. Jangan melewati login atau mengumpulkan kredensial. Keamanan tidak cukup dibuktikan oleh status HTTP; cocokkan dengan efek pada resource dan aturan izin yang disahkan.

## Kontrak bukti minimum

Satu bukti memuat ID, sumber/tool, timestamp+zona, revisi/build, lingkungan, identitas peran tanpa rahasia, langkah/perintah, expected bersumber, actual, dan batas interpretasi. Catat observasi mentah yang aman secara terpisah dari dugaan root cause. Catat perubahan konteks yang membuat bukti basi; jangan memakai hasil sebelum perbaikan sebagai hasil retest.

Minimalkan data sebelum capture: hindari header autentikasi, cookie, token URL, isi profil, connection string, dan environment dump. Redaksi di salinan aman; jangan menimpa bukti asli kecuali sesuai kebijakan retensi. Jika bukti asli sensitif, jangan membuatnya di workspace umum; tentukan penyimpanan terbatas, akses, retensi dan penghapusan bersama pemilik terlebih dahulu. Nama file dan metadata screenshot juga dapat membocorkan identitas.

Publikasi bug menggunakan reproduksi sintetis dan dampak terbatas yang sudah diamati. Jangan mengunggah log mentah, payload berbahaya, detail target rentan, atau rahasia ke issue publik. Dugaan paparan rahasia dilaporkan tanpa nilai rahasianya; rotasi dilakukan pemilik melalui prosedur resmi, bukan oleh agen tanpa izin.

Selesai ketika bukti dapat diaudit tanpa membuka data sensitif, gap terlabel, dan pemilik menerima tindak lanjut yang relevan. Laporan statis bukan sertifikasi keamanan.
