import cv2
import numpy as np
from scipy.ndimage import interpolation as inter
import pytesseract
import os # Untuk mempermudah penanganan path

# --- Konfigurasi Tesseract ---
# (Bagian ini tetap sama)
tesseract_path_default = r"C:\Program Files\Tesseract-OCR\tesseract.exe" # Contoh path
try:
    pytesseract.pytesseract.tesseract_cmd = os.environ.get('TESSERACT_CMD', tesseract_path_default)
    pytesseract.get_tesseract_version()
    print(f"✅ Tesseract OCR ditemukan di: {pytesseract.pytesseract.tesseract_cmd}")
    print(f"   Versi Tesseract: {pytesseract.get_tesseract_version()}")
except Exception as e:
    print(f"⚠️ Peringatan Tesseract: {e}")
    user_tesseract_path = input(f"Tesseract tidak otomatis terdeteksi atau ada masalah. Masukkan path ke tesseract.exe (atau biarkan kosong untuk mencoba '{tesseract_path_default}'): ").strip()
    if user_tesseract_path:
        pytesseract.pytesseract.tesseract_cmd = user_tesseract_path
    elif not os.path.exists(tesseract_path_default):
        print(f"❌ Error: Tesseract OCR tidak ditemukan di path default ('{tesseract_path_default}') dan tidak ada path yang dimasukkan.")
        print("Silakan install Tesseract OCR dan/atau set path yang benar dalam script atau sebagai environment variable TESSERACT_CMD.")
        exit()
    else:
         pytesseract.pytesseract.tesseract_cmd = tesseract_path_default

    try:
        pytesseract.get_tesseract_version()
        print(f"✅ Tesseract OCR berhasil dikonfigurasi ke: {pytesseract.pytesseract.tesseract_cmd}")
        print(f"   Versi Tesseract: {pytesseract.get_tesseract_version()}")
    except Exception as e_inner:
        print(f"❌ Error: Gagal menggunakan path Tesseract yang dimasukkan atau default: {e_inner}")
        print("Pastikan Tesseract OCR terinstal dan path ke tesseract.exe sudah benar.")
        exit()


# --- Fungsi Deteksi Rotasi Besar (OSD) ---
# (Bagian ini tetap sama)
def detect_major_rotation_osd(image):
    try:
        osd_data = pytesseract.image_to_osd(image, output_type=pytesseract.Output.DICT, lang='eng+ind')
        rotation = osd_data['rotate']
        direction_map = {
            0: "✅ Orientasi Sudah Benar (0°)",
            90: "🔄 Orientasi Perlu Diputar 90° Searah Jarum Jam untuk Lurus",
            180: "🔄 Orientasi Perlu Diputar 180° untuk Lurus",
            270: "🔄 Orientasi Perlu Diputar 90° Berlawanan Arah Jarum Jam untuk Lurus"
        }
        direction_message = direction_map.get(rotation, f"❓ Orientasi Tidak Diketahui (Rotasi OSD: {rotation}°)")
        return rotation, direction_message
    except Exception as e:
        print(f"⚠️ Gagal melakukan OSD: {e}. Mengasumsikan rotasi 0 derajat.")
        return 0, "⚠️ OSD Gagal, Asumsi 0°"

# --- Fungsi Rotasi Gambar ---
# (Bagian ini tetap sama)
def rotate_image(image, angle_degrees, border_color=(255,255,255)):
    if image is None:
        return None
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle_degrees, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT, borderValue=border_color)
    return rotated

# --- Fungsi Deteksi dan Koreksi Kemiringan Halus (Proyeksi Profil) ---
# (Bagian ini tetap sama)
def correct_fine_skew(image, delta=0.5, limit=15):
    if image is None:
        print("Error: Gambar input untuk correct_fine_skew adalah None.")
        return None, 0, "Tidak Diketahui"
    if len(image.shape) == 2:
        gray = image
    else:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    def find_score(arr, angle):
        data = inter.rotate(arr, angle, reshape=False, order=0, cval=0)
        hist = np.sum(data, axis=1)
        score = np.sum((hist[1:] - hist[:-1]) ** 2)
        return score
    angles = np.arange(-limit, limit + delta, delta)
    scores = [find_score(thresh, angle) for angle in angles]
    best_angle = angles[np.argmax(scores)]
    direction = "Tidak Diketahui"
    angle_threshold = 0.05
    if best_angle > angle_threshold:
        direction = "Berlawanan Arah Jarum Jam (Perlu Rotasi CCW)"
    elif best_angle < -angle_threshold:
        direction = "Searah Jarum Jam (Perlu Rotasi CW)"
    else:
        direction = "Tegak Lurus (atau kemiringan sangat kecil)"
    corrected_img = rotate_image(image, best_angle)
    return corrected_img, best_angle, direction


# --- Fungsi Utama dengan Path Gambar Langsung ---
if __name__ == "__main__":
    # <<< GANTI PATH GAMBAR DI SINI >>>
    image_file_path = r"D:\Kuliah\SEMESTER 6\DigHum\Projek Akhir\test\coba5.png"

    # <<< GANTI BAHASA OCR DI SINI JIKA PERLU >>>
    ocr_language = 'eng'

    # <<< SET OPSI THRESHOLDING SEBELUM OCR >>>
    apply_ocr_preprocessing_thresholding = True # Set ke True untuk menerapkan, False untuk tidak
    # Jika True, jenis thresholding yang akan digunakan (contoh: Otsu)
    # Anda bisa juga memilih cv2.THRESH_BINARY (+ nilai manual) atau cv2.adaptiveThresholdMeanC/GaussianC
    ocr_threshold_type = cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU # Teks hitam di latar putih (THRESH_BINARY) atau Teks putih di latar hitam (THRESH_BINARY_INV)
                                                                 # Pilih INV jika teks Anda lebih gelap dari latar belakang pada gambar grayscale

    print(f"Memproses gambar: {image_file_path}")
    print(f"Bahasa OCR yang digunakan: {ocr_language}")
    print(f"Thresholding tambahan sebelum OCR: {'Aktif' if apply_ocr_preprocessing_thresholding else 'Tidak Aktif'}")

    if not os.path.exists(image_file_path):
        print(f"❌ Error: File tidak ditemukan di '{image_file_path}'. Mohon periksa path.")
        exit()

    original_img = cv2.imread(image_file_path)

    if original_img is None:
        print(f"❌ Gagal membaca gambar: {image_file_path}")
        exit()

    # 1. Deteksi dan Koreksi Orientasi Besar (OSD)
    print("  Tahap 1: Deteksi Orientasi Besar (OSD)...")
    osd_correction_angle, osd_direction_msg = detect_major_rotation_osd(original_img)
    print(f"    Sudut Rotasi OSD yang dibutuhkan: {osd_correction_angle}° ({osd_direction_msg})")

    img_after_osd = rotate_image(original_img, osd_correction_angle)
    if img_after_osd is None:
        print(f"❌ Gagal melakukan rotasi OSD pada {image_file_path}. Menggunakan gambar asli untuk tahap selanjutnya.")
        img_after_osd = original_img.copy()

    # 2. Deteksi dan Koreksi Kemiringan Halus (Proyeksi Profil)
    print("  Tahap 2: Deteksi Kemiringan Halus (Proyeksi Profil)...")
    img_final_corrected, fine_skew_angle, fine_skew_direction_msg = correct_fine_skew(img_after_osd, delta=0.2, limit=15)

    if img_final_corrected is None:
        print(f"❌ Gagal melakukan koreksi kemiringan halus pada {image_file_path}. Menampilkan gambar setelah OSD (jika ada).")
        img_final_corrected = img_after_osd.copy()

    print(f"    Sudut Kemiringan Halus Terdeteksi (koreksi): {fine_skew_angle:.2f}°")
    print(f"    Arah Kemiringan Halus Asli: {fine_skew_direction_msg}")

    # 3. Pengenalan Teks (OCR) dari Gambar yang Sudah Dikoreksi Sepenuhnya
    print("  Tahap 3: Pengenalan Teks (OCR)...")
    recognized_text = ""
    img_for_ocr = img_final_corrected.copy() # Mulai dengan gambar yang sudah dikoreksi

    if apply_ocr_preprocessing_thresholding:
        print("    Menerapkan thresholding tambahan sebelum OCR...")
        # Konversi ke grayscale jika belum
        if len(img_for_ocr.shape) == 3: # Jika berwarna
            ocr_gray = cv2.cvtColor(img_for_ocr, cv2.COLOR_BGR2GRAY)
        else: # Jika sudah grayscale
            ocr_gray = img_for_ocr

        # Terapkan thresholding
        # Untuk THRESH_OTSU, nilai threshold (parameter kedua) tidak digunakan (bisa diisi 0)
        _, ocr_thresholded = cv2.threshold(ocr_gray, 0, 255, ocr_threshold_type)
        img_for_ocr = ocr_thresholded # Gambar untuk OCR sekarang adalah hasil threshold
        
        # Opsional: tampilkan gambar hasil thresholding untuk OCR
        # cv2.imshow("Gambar Thresholded untuk OCR", img_for_ocr)

    try:
        # Jika tidak menerapkan thresholding di atas, Tesseract akan menggunakan
        # gambar berwarna (img_final_corrected) atau grayscale (jika sudah dikonversi sebelumnya)
        # Pytesseract dapat menangani gambar BGR, RGB, atau Grayscale (NumPy array).
        # Konversi ke RGB adalah praktik umum jika inputnya BGR, tapi jika sudah di-threshold jadi biner/grayscale, itu tidak perlu.
        if not apply_ocr_preprocessing_thresholding and len(img_for_ocr.shape) == 3: # Jika berwarna dan tidak di-threshold
             img_to_pass_to_tesseract = cv2.cvtColor(img_for_ocr, cv2.COLOR_BGR2RGB)
        else: # Jika sudah grayscale/biner dari thresholding, atau sudah grayscale
             img_to_pass_to_tesseract = img_for_ocr

        recognized_text = pytesseract.image_to_string(img_to_pass_to_tesseract, lang=ocr_language)
        print(f"    Teks yang Dikenali ({ocr_language}):")
        print("    ------------------------------------")
        print(recognized_text if recognized_text.strip() else "    (Tidak ada teks yang dikenali atau teks kosong)")
        print("    ------------------------------------")
    except Exception as e:
        print(f"❌ Error saat melakukan OCR: {e}")
        if "TesseractNotFoundError" in str(e):
             print("   Pastikan Tesseract terinstal dan path-nya sudah benar.")
        elif "Failed loading language" in str(e):
             print(f"   Pastikan language pack untuk '{ocr_language}' sudah terinstal di Tesseract.")

    # Tampilkan gambar
    try:
        cv2.imshow(f"Asli: {os.path.basename(image_file_path)}", original_img)
        if osd_correction_angle != 0 :
            cv2.imshow(f"Setelah OSD ({osd_correction_angle}°): {os.path.basename(image_file_path)}", img_after_osd)
        # Tampilkan juga gambar yang di-threshold untuk OCR jika diterapkan
        if apply_ocr_preprocessing_thresholding:
            cv2.imshow(f"Thresholded untuk OCR: {os.path.basename(image_file_path)}", img_for_ocr) # img_for_ocr adalah hasil threshold di sini
        
        cv2.imshow(f"Final Dikoreksi (Sebelum OCR): {os.path.basename(image_file_path)}", img_final_corrected)


        print(f"\n  Menampilkan gambar untuk: {os.path.basename(image_file_path)}. Tekan tombol apa saja di jendela gambar untuk menutup...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    except Exception as e:
        print(f"  ⚠️ Tidak bisa menampilkan gambar: {e}. Pastikan Anda memiliki GUI environment.")

    # # Simpan gambar yang sudah dikoreksi
    # try:
    #     base_name = os.path.basename(image_file_path)
    #     name, ext = os.path.splitext(base_name)
    #     output_filename = f"corrected_ocr_thresholded_{name}{ext}" if apply_ocr_preprocessing_thresholding else f"corrected_ocr_{name}{ext}"
    #     cv2.imwrite(output_filename, img_final_corrected) # Simpan gambar hasil koreksi skew, bukan yang di-threshold untuk OCR
    #     print(f"  ✅ Gambar yang dikoreksi (sebelum OCR thresholding) disimpan sebagai: {output_filename}")
    #     if apply_ocr_preprocessing_thresholding:
    #         output_filename_ocr_prep = f"ocr_input_thresholded_{name}{ext}"
    #         cv2.imwrite(output_filename_ocr_prep, img_for_ocr) # img_for_ocr adalah hasil thresholding
    #         print(f"  ✅ Gambar yang di-threshold untuk OCR disimpan sebagai: {output_filename_ocr_prep}")

    # except Exception as e:
    #     print(f"  ❌ Gagal menyimpan {output_filename}: {e}")

    print("\n--- Pemrosesan Selesai ---")
    # (Bagian ringkasan tetap sama)
    print(f"File: {image_file_path}")
    print(f"  OSD: Rotasi {res['osd_angle']}° ({res['osd_direction']})") # Seharusnya res tidak ada di sini, pakai variabel langsung
    print(f"  OSD: Rotasi {osd_correction_angle}° ({osd_direction_msg})")
    print(f"  Skew Halus: Koreksi {fine_skew_angle:.2f}° ({fine_skew_direction_msg})")
    if recognized_text.strip():
        print(f"  Teks Dikenali: Ditampilkan di atas.")
    else:
        print(f"  Teks Dikenali: Tidak ada teks yang signifikan terdeteksi.")