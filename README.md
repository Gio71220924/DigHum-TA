# Deteksi Kemiringan dengan Hough Transform 
Projek Akhir Mata Kuliah Digital Humanities (https://dighum-ta.streamlit.app/)


Daftar Anggota kelompok:
  1. 71220856	Vincen Imanuel
  2. 71220924   Giovanka Steviano H.P.
  3. 71220925	Anjelita Haninuna
  4. 71220927	Imanuel Putra Anugerah Faot
  5. 71220928	Natanael


## Deskripsi Singkat
📐 Koreksi Kemiringan Teks pada Citra Menggunakan Hough Line Transform (Python + OpenCV) 📄 Skrip ini digunakan untuk mendeteksi dan mengoreksi kemiringan teks horizontal dalam citra dokumen menggunakan transformasi Hough Lines. Setelah mendeteksi sudut kemiringan dominan, gambar akan otomatis dirotasi agar teks menjadi lurus dan horizontal.

## Fitur
- Deteksi garis pada teks menggunakan **Canny Edge Detection** dan **HoughLinesP**.
- Estimasi sudut kemiringan dominan.
- Rotasi otomatis berdasarkan sudut kemiringan.
- Deteksi arah kemiringan:
  - 🔄 Searah jarum jam
  - 🔃 Berlawanan arah jarum jam
  - ⬆️ Tidak miring / tegak lurus


## Library yang digunakan
```
opencv-python-headless	 
Numpy
Tesseract OCR
streamlit	
Pillow
```
## Instalasi

```
pip install opencv-python-headless
pip install numpy
pip install pytesseract
pip install streamlit
pip install Pillow
```
## Cara menginstall Tesseract OCR
- [Download disini](https://github.com/tesseract-ocr/tesseract/releases/download/5.5.0/tesseract-ocr-w64-setup-5.5.0.20241111.exe).
- Klik dua kali file .exe untuk menjalankan instalasi.
- Pilih opsi "Additional language data" saat instalasi, centang bahasa yang kamu butuhkan (misalnya ind untuk Indonesia).
- Install di direktori default, biasanya: ```C:\Program Files\Tesseract-OCR\```
- Klik "OK", lalu tunggu proses instalasi.
  
