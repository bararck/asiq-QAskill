# Eksplorasi manual berbasis risiko

1. Urutkan risiko dengan alasan: dampak pengguna/bisnis, kemungkinan, perubahan terbaru, kemampuan mendeteksi, dan luas paparan. Hindari angka presisi tanpa dasar. Prioritas tinggi bukan izin melewati batas keselamatan.
2. Susun charter berbatas waktu: area, pertanyaan, persona, oracle, data sintetis, izin tindakan, durasi, dan kondisi berhenti. Satu charter menjawab satu hipotesis, bukan menjanjikan cakupan penuh.
3. Pilih variasi relevan: normal, batas, kosong, invalid, perubahan state, navigasi balik, refresh, interupsi, aksesibilitas keyboard/fokus, ukuran layar, locale, dan peran. Pilih dari risiko/stack aktual; jangan memaksakan matriks perangkat yang tidak tersedia.
4. Catat urutan aksi dan state awal. Pisahkan catatan observasi dari interpretasi. Untuk UI, simpan teks aktual, urutan fokus, dan bukti tersanitasi; screenshot tanpa konteks tidak cukup mereproduksi masalah.
5. Saat anomali muncul, minimalkan reproduksi tanpa merusak bukti awal. Periksa apakah masalah berasal dari produk, data, jaringan, atau tool. Jangan mengulang mutasi yang dapat menggandakan efek; minta izin bila perlu.
6. Debrief: apa yang dicoba, yang tidak dicoba, waktu, temuan, pertanyaan, dan charter lanjutan. Ubah temuan bernilai menjadi kandidat regresi, bukan otomatis menambah semua eksperimen sebagai test permanen.

Kriteria selesai: charter ditutup dengan bukti dan sisa risiko; tidak ada klaim bahwa sesi eksplorasi membuktikan ketiadaan cacat.
