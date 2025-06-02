import cv2
import numpy as np
import math
import os
import pytesseract
# Versi Nuel

# --- Konfigurasi Tesseract (Tambahkan bagian ini) ---
tesseract_path_default = r"C:\Program Files\Tesseract-OCR\tesseract.exe" # Sesuaikan dengan path Anda
try:
    pytesseract.pytesseract.tesseract_cmd = os.environ.get('TESSERACT_CMD', tesseract_path_default)
    pytesseract.get_tesseract_version()
    print(f"✅ Tesseract OCR ditemukan di: {pytesseract.pytesseract.tesseract_cmd}")
    print(f"   Versi Tesseract: {pytesseract.get_tesseract_version()}")
except Exception as e:
    print(f"⚠️ Peringatan Tesseract: {e}")
    # Penanganan error path Tesseract bisa ditambahkan di sini seperti skrip Anda sebelumnya jika diperlukan
    # Untuk contoh ini, kita asumsikan path default benar atau environment variable TESSERACT_CMD sudah di-set.
    # Jika tidak, pytesseract akan gagal saat dipanggil.
    if not os.path.exists(pytesseract.pytesseract.tesseract_cmd):
        print(f"❌ Error: Tesseract OCR tidak ditemukan di path '{pytesseract.pytesseract.tesseract_cmd}'.")
        print("Pastikan Tesseract OCR terinstal dan path ke tesseract.exe sudah benar, atau set environment variable TESSERACT_CMD.")
        # Anda mungkin ingin keluar dari program di sini jika Tesseract adalah komponen krusial
        # exit()

def koreksi_kemiringan(path_citra):
    """
    Membaca citra teks, mendeteksi sudut kemiringan menggunakan Hough Transform,
    mengidentifikasi arah kemiringan, dan melakukan rotasi untuk meluruskan teks.

    Args:
        path_citra (str): Path menuju file citra input.

    Returns:
        tuple: Berisi (citra_asli, citra_hasil_rotasi, sudut_kemiringan, arah_kemiringan)
               atau None jika tidak ada garis yang terdeteksi.
    """
    # 1. Baca citra
    citra = cv2.imread(path_citra)
    if citra is None:
        print(f"Error: Tidak dapat membaca citra dari {path_citra}")
        return None, None, None, None

    citra_asli = citra.copy()

    # 2. Pra-pemrosesan
    # Konversi ke grayscale
    gray = cv2.cvtColor(citra, cv2.COLOR_BGR2GRAY)
    # Invert gambar jika teks lebih terang dari background (opsional, tergantung citra)
    # gray = cv2.bitwise_not(gray)
    # Deteksi tepi menggunakan Canny
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)

    # 3. Terapkan Hough Line Transform
    # Parameter HoughLinesP:
    # - edges: output dari detektor tepi.
    # - 1: resolusi rho dalam piksel.
    # - np.pi / 180: resolusi theta dalam radian.
    # - threshold: jumlah minimum irisan untuk mendeteksi garis.
    # - minLineLength: panjang minimum garis dalam piksel.
    # - maxLineGap: celah maksimum antara segmen garis yang akan dianggap sebagai satu garis.
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=80, minLineLength=50, maxLineGap=10)

    if lines is None:
        print(f"Tidak ada garis yang terdeteksi di {path_citra}. Coba sesuaikan parameter Hough.")
        return citra_asli, None, 0, "Tidak terdeteksi"

    angles = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        # Hitung sudut garis
        # Perhatikan: atan2 mengembalikan sudut dalam radian, antara -pi dan pi.
        # Sudut dihitung relatif terhadap sumbu x positif.
        angle = math.atan2(y2 - y1, x2 - x1) * 180.0 / np.pi
        angles.append(angle)

    # 4. Tentukan sudut kemiringan dominan
    # Kita bisa menggunakan median atau modus dari sudut-sudut yang terdeteksi.
    # Median lebih robust terhadap outlier.
    # Filter sudut yang masuk akal untuk kemiringan teks (misalnya antara -45 dan 45 derajat)
    # karena Hough Transform bisa mendeteksi garis vertikal juga.
    filtered_angles = [angle for angle in angles if -45 < angle < 45 and angle != 0]

    if not filtered_angles:
        print(f"Tidak ada sudut kemiringan teks yang signifikan terdeteksi di {path_citra}.")
        return citra_asli, citra_asli, 0, "Tidak signifikan" # Kembalikan citra asli jika tidak ada kemiringan

    sudut_kemiringan = np.median(filtered_angles)

    # 5. Identifikasi arah kemiringan
    arah_kemiringan = "Tidak ada"
    if sudut_kemiringan > 0.5: # Tambahkan sedikit toleransi
        arah_kemiringan = "Berlawanan Arah Jarum Jam (Rotasi ke Kanan)"
    elif sudut_kemiringan < -0.5: # Tambahkan sedikit toleransi
        arah_kemiringan = "Searah Jarum Jam (Rotasi ke Kiri)"
    else:
        arah_kemiringan = "Tegak Lurus / Kemiringan Sangat Kecil"


    print(f"Citra: {path_citra}")
    print(f"Sudut Kemiringan Terdeteksi: {sudut_kemiringan:.2f} derajat")
    print(f"Arah Kemiringan: {arah_kemiringan}")

    # 6. Rotasi citra untuk meluruskan
    (h, w) = citra.shape[:2]
    center = (w // 2, h // 2)

    # Matriks rotasi
    # Perhatikan: OpenCV melakukan rotasi berlawanan arah jarum jam untuk sudut positif.
    # Jadi, jika sudut_kemiringan adalah X, kita perlu merotasi sebesar -X.
    M = cv2.getRotationMatrix2D(center, sudut_kemiringan, 1.0) # Koreksi sudut rotasi
    
    # Hitung dimensi baru gambar setelah rotasi agar seluruh gambar terlihat
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])
    
    new_w = int((h * sin) + (w * cos))
    new_h = int((h * cos) + (w * sin))
    
    # Sesuaikan matriks rotasi untuk memperhitungkan translasi
    M[0, 2] += (new_w / 2) - center[0]
    M[1, 2] += (new_h / 2) - center[1]
    
    citra_hasil_rotasi = cv2.warpAffine(citra, M, (new_w, new_h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)


    return citra_asli, citra_hasil_rotasi, sudut_kemiringan, arah_kemiringan

if __name__ == "__main__":
    # Ganti dengan path ke citra-citra input kalian
    daftar_citra_input = [
        "dataset\coba7.png"
    ]

     # <<< GANTI BAHASA OCR DI SINI JIKA PERLU >>>
    ocr_language = 'eng+ind' # Contoh: Inggris dan Indonesia

    # <<< SET OPSI THRESHOLDING SEBELUM OCR (OPSIONAL TAPI DIREKOMENDASIKAN) >>>
    apply_ocr_preprocessing_thresholding = True
    # Pilih INV jika teks lebih gelap dari latar belakang pada gambar grayscale setelah koreksi
    ocr_threshold_type = cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    

    for i, path_input in enumerate(daftar_citra_input):
        print(f"\n--- Memproses Citra {i+1}: {path_input} ---")
        citra_asli, citra_terkoreksi, sudut, arah = koreksi_kemiringan(path_input)

        if citra_asli is not None:
            cv2.imshow(f"Citra Asli {i+1}", citra_asli)
            if citra_terkoreksi is not None:
                cv2.imshow(f"Citra Terkoreksi {i+1} (Sudut: {sudut:.2f}, Arah: {arah})", citra_terkoreksi)
                # Simpan hasil (opsional)
                # nama_file_output = f"hasil_koreksi_{i+1}.png"
                # cv2.imwrite(nama_file_output, citra_terkoreksi)
                # print(f"Hasil koreksi disimpan sebagai: {nama_file_output}")
                 # --- Langkah OCR dengan Tesseract ---
                print("\n  Melakukan OCR pada citra terkoreksi...")
                img_for_ocr = citra_terkoreksi.copy()

                if apply_ocr_preprocessing_thresholding:
                    print("    Menerapkan thresholding tambahan sebelum OCR...")
                    if len(img_for_ocr.shape) == 3: # Jika berwarna
                        ocr_gray = cv2.cvtColor(img_for_ocr, cv2.COLOR_BGR2GRAY)
                    else: # Jika sudah grayscale
                        ocr_gray = img_for_ocr
                    
                    # Terapkan thresholding
                    _, ocr_thresholded = cv2.threshold(ocr_gray, 0, 255, ocr_threshold_type)
                    img_for_ocr = ocr_thresholded # Gambar untuk OCR sekarang adalah hasil threshold
                    cv2.imshow(f"Thresholded untuk OCR {i+1}", img_for_ocr)


                try:
                    # Pytesseract dapat menerima citra BGR, RGB, atau Grayscale (NumPy array).
                    # Jika sudah di-threshold menjadi biner/grayscale, tidak perlu konversi BGR2RGB.
                    custom_config = r'--oem 3 --psm 6' # Contoh konfigurasi, sesuaikan jika perlu
                    dikenali_teks = pytesseract.image_to_string(img_for_ocr, lang=ocr_language, config=custom_config)
                    
                    print(f"\n  Teks yang Dikenali dari Citra {i+1} ({ocr_language}):")
                    print("  ------------------------------------")
                    print(dikenali_teks if dikenali_teks.strip() else "  (Tidak ada teks yang dikenali atau teks kosong)")
                    print("  ------------------------------------")

                except pytesseract.TesseractNotFoundError:
                    print("❌ Error Tesseract: Path ke tesseract.exe tidak ditemukan atau salah.")
                    print("   Pastikan Tesseract OCR terinstal dan path sudah dikonfigurasi dengan benar.")
                except Exception as e_ocr:
                    print(f"❌ Error saat melakukan OCR pada citra {i+1}: {e_ocr}")
                    if "Failed loading language" in str(e_ocr):
                        print(f"   Pastikan language pack untuk '{ocr_language}' sudah terinstal di Tesseract.")

            else:
                print(f"Tidak dapat melakukan koreksi untuk citra {path_input}")
            print("-" * 30)

    cv2.waitKey(0)
    cv2.destroyAllWindows()
