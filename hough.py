# hough.py
import cv2
import numpy as np
import math

def koreksi_kemiringan(citra):
    """
    Menerima citra (numpy array), mendeteksi sudut kemiringan menggunakan Hough Transform,
    dan melakukan rotasi untuk meluruskan teks.

    Returns:
        tuple: (citra_asli, citra_terkoreksi, sudut_kemiringan, arah_kemiringan)
    """
    citra_asli = citra.copy()
    #GrayScale Citra
    gray = cv2.cvtColor(citra, cv2.COLOR_BGR2GRAY)

    # Kurangi noise dengan Gaussian Blur
    blurred = cv2.GaussianBlur(gray, (5, 9), 2)

    #Batas atas dan Batas Bawah untuk menghitung tepi
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    #Garis Hough
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=80, minLineLength=50, maxLineGap=10)

    if lines is None:
        return citra_asli, None, 0, "Tidak terdeteksi"
    #Hitung sudut kemiringan
    angles = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        angle = math.atan2(y2 - y1, x2 - x1) * 180.0 / np.pi
        angles.append(angle)

    filtered_angles = [a for a in angles if -45 < a < 45 and a != 0]
    if not filtered_angles:
        return citra_asli, citra_asli, 0, "Tidak signifikan"

    sudut_kemiringan = np.median(filtered_angles)
    arah = "Tegak Lurus / Kecil"
    if sudut_kemiringan > 0.5:
        arah = "Berlawanan Arah Jarum Jam (Rotasi ke kiri)"
    elif sudut_kemiringan < -0.5:
        arah = "Searah Jarum Jam (Rotasi ke kanan)"
    else:
        arah = "Tegak Lurus / Kemiringan Sangat Kecil"

    (h, w) = citra.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, sudut_kemiringan, 1.0)

    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])
    #Lebar & Tinggi Citra Baru (Citra Terkoreksi)
    new_w = int((h * sin) + (w * cos))
    new_h = int((h * cos) + (w * sin))

    M[0, 2] += (new_w / 2) - center[0]
    M[1, 2] += (new_h / 2) - center[1]

    # Koreksi citra dengan rotasi
    citra_terkoreksi = cv2.warpAffine(citra, M, (new_w, new_h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return citra_asli, citra_terkoreksi, sudut_kemiringan, arah