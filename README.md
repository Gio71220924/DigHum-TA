# DigHum-TA
📐 Koreksi Kemiringan Teks pada Citra Menggunakan Hough Line Transform (Python + OpenCV)
📄 Deskripsi Singkat
Skrip ini digunakan untuk mendeteksi dan mengoreksi kemiringan teks horizontal dalam citra dokumen menggunakan transformasi Hough Lines. Setelah mendeteksi sudut kemiringan dominan, gambar akan otomatis dirotasi agar teks menjadi lurus dan horizontal.

📦 Ketergantungan
Python 3.x

OpenCV (cv2)

NumPy

Install dependencies (jika belum):

bash
Copy
Edit
pip install opencv-python numpy
🧠 Alur Kerja Program
Membaca gambar masukan

Pra-pemrosesan:

Konversi ke grayscale

Deteksi tepi dengan Canny

Deteksi garis menggunakan cv2.HoughLinesP

Menghitung sudut kemiringan dominan (median dari sudut-sudut dalam rentang -45° sampai 45°)

Menentukan arah rotasi (kiri atau kanan)

Meluruskan teks dengan rotasi citra menggunakan cv2.getRotationMatrix2D

Menampilkan dan menyimpan hasil koreksi

🔧 Fungsi Utama
python
Copy
Edit
def koreksi_kemiringan(path_citra)
Parameter
Nama	Tipe	Deskripsi
path_citra	str	Path menuju file citra input

Return
Tuple berisi:

python
Copy
Edit
(citra_asli, citra_hasil_rotasi, sudut_kemiringan, arah_kemiringan)
Elemen	Tipe	Deskripsi
citra_asli	ndarray	Citra input sebelum dikoreksi
citra_hasil_rotasi	ndarray	Citra setelah diluruskan
sudut_kemiringan	float	Sudut kemiringan dominan dalam derajat
arah_kemiringan	str	Arah kemiringan: ke kiri, ke kanan, atau tegak lurus

▶️ Contoh Pemakaian
python
Copy
Edit
if __name__ == "__main__":
    daftar_citra_input = [
        "dataset/coba5.jpg",
        "dataset/coba6.png",
    ]

    for i, path_input in enumerate(daftar_citra_input):
        citra_asli, citra_terkoreksi, sudut, arah = koreksi_kemiringan(path_input)

        if citra_asli is not None:
            cv2.imshow(f"Citra Asli {i+1}", citra_asli)
            if citra_terkoreksi is not None:
                cv2.imshow(f"Citra Terkoreksi {i+1}", citra_terkoreksi)
                cv2.imwrite(f"hasil_koreksi_{i+1}.png", citra_terkoreksi)
🧪 Contoh Output
yaml
Copy
Edit
Citra: dataset/coba6.png
Sudut Kemiringan Terdeteksi: -2.15 derajat
Arah Kemiringan: Searah Jarum Jam (Rotasi ke Kiri)
Hasil koreksi disimpan sebagai: hasil_koreksi_2.png
📌 Catatan
Citra yang tidak memiliki teks horizontal yang jelas mungkin tidak bisa dideteksi dengan baik.

Parameter threshold, minLineLength, dan maxLineGap pada cv2.HoughLinesP() bisa disesuaikan untuk citra yang berbeda.

Kemiringan kecil (< 0.5 derajat) dianggap sudah tegak lurus.

Jika kamu ingin, dokumentasi ini juga bisa dibuat dalam format .md atau .pdf. Mau aku bantu ekspor?






You said:
buat versi Markdown nya untuk readme repository github saya 


ChatGPT said:
Berikut adalah versi dokumentasi dalam format Markdown untuk dijadikan sebagai README.md di repository GitHub:

markdown
Copy
Edit
# Deteksi dan Koreksi Kemiringan Teks Otomatis menggunakan OpenCV

Proyek ini bertujuan untuk mendeteksi dan mengoreksi kemiringan (skew) pada citra yang berisi teks menggunakan metode **Hough Line Transform** dari OpenCV. Program akan membaca citra teks, mendeteksi sudut kemiringan dominan, dan secara otomatis merotasi citra untuk membuat teks menjadi sejajar.

---

## 📂 Struktur Direktori

.
├── dataset/
│ ├── coba5.jpg
│ └── coba6.png
├── hasil_koreksi_1.png
├── hasil_koreksi_2.png
├── koreksi_kemiringan.py
└── README.md

yaml
Copy
Edit

---

## 🧠 Fitur Utama

- Deteksi garis pada citra teks menggunakan **Canny Edge** dan **HoughLinesP**.
- Estimasi sudut kemiringan dominan dari teks.
- Rotasi otomatis untuk meluruskan teks berdasarkan sudut yang terdeteksi.
- Identifikasi arah kemiringan:
  - 🔄 Searah jarum jam
  - 🔃 Berlawanan arah jarum jam
  - ⬆️ Tegak lurus / tanpa kemiringan signifikan

---

## 📌 Kebutuhan Sistem

- Python 3.x
- OpenCV
- NumPy

Instalasi dependensi:
```bash
pip install opencv-python numpy
🚀 Cara Menjalankan
Tempatkan citra yang ingin diperbaiki pada folder dataset/.

Jalankan program:

bash
Copy
Edit
python koreksi_kemiringan.py
Hasil rotasi akan ditampilkan di jendela baru dan juga disimpan sebagai file:

Copy
Edit
hasil_koreksi_1.png
hasil_koreksi_2.png
🔍 Contoh Output Terminal
yaml
Copy
Edit
Citra: dataset\coba5.jpg
Sudut Kemiringan Terdeteksi: -3.75 derajat
Arah Kemiringan: Searah Jarum Jam (Rotasi ke Kiri)
Hasil koreksi disimpan sebagai: hasil_koreksi_1.png
🧪 Catatan Teknis
Sudut dihitung berdasarkan median dari semua garis yang terdeteksi, setelah disaring dalam rentang -45 hingga 45 derajat.

Fungsi rotasi mempertimbangkan translasi agar seluruh bagian citra tetap terlihat setelah rotasi.

Jika tidak ada sudut kemiringan yang signifikan terdeteksi, citra akan dikembalikan dalam bentuk aslinya.

⚠️ Catatan
Pastikan teks dalam citra cukup kontras terhadap latar belakang agar tepi dapat terdeteksi dengan baik.

Anda bisa menyesuaikan parameter threshold, minLineLength, dan maxLineGap pada fungsi cv2.HoughLinesP() jika deteksi tidak optimal.

📄 Lisensi
Proyek ini tersedia secara bebas untuk pembelajaran dan penggunaan pribadi.

👨‍💻 Kontributor
Nama Anda

Silakan fork, gunakan, dan berkontribusi untuk meningkatkan akurasi dan fitur lainnya!

yaml
Copy
Edit

---

Silakan sesuaikan bagian seperti nama Anda, lisensi, atau link GitHub jika diperlukan. Jika Anda ingin saya bantu menambahkan gambar hasil koreksi (`hasil_koreksi_1.png`, dsb.) dalam README, beri tahu saja!
