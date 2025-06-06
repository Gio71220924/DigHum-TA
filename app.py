import streamlit as st
import numpy as np
import cv2
import pytesseract
import os
from hough import koreksi_kemiringan
from PIL import Image

# --- Konfigurasi Tesseract
tesseract_path_default = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = os.environ.get("TESSERACT_CMD", tesseract_path_default)

st.set_page_config(page_title="Tugas Digital Humanities", layout="centered")
st.title("📄 Koreksi Kemiringan Gambar menggunakan Hough Line dan OCR dengan Tesseract")
st.markdown("Unggah gambar berisi teks miring untuk dikoreksi dan dibaca.")

uploaded_file = st.file_uploader("📤 Upload Gambar disini!", type=["png", "jpg", "jpeg"])
st.divider()
if uploaded_file is not None:
    # Baca citra sebagai numpy array
    image = Image.open(uploaded_file).convert("RGB")
    img_np = np.array(image)[:, :, ::-1]  # Convert PIL RGB ke BGR OpenCV

    # Koreksi kemiringan
    asli, terkoreksi, sudut, arah = koreksi_kemiringan(img_np)

    # Membuat dua kolom untuk menampilkan gambar asli dan terkoreksi
    col1, col2 = st.columns(2)  # <-- ini perbaikan dari st.container(2)

    with col1:
        st.image(asli, caption=f"Citra Asli || Sudut Kemiringan:{sudut:.2f}°", channels="BGR", use_container_width=True)
    with col2:
        if terkoreksi is not None:
            st.image(terkoreksi, caption=f"Citra Terkoreksi ||  Arah Koreksi: {arah})", channels="BGR", use_container_width=True)
        else:
            st.warning("❌ Tidak ada kemiringan yang perlu dikoreksi.")

    # OCR
    # if terkoreksi is not None:
    #     st.subheader("📖 Hasil OCR (Tesseract)")
    #     ocr_img = cv2.cvtColor(terkoreksi, cv2.COLOR_BGR2GRAY)
    #     _, ocr_img = cv2.threshold(ocr_img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    #     text = pytesseract.image_to_string(ocr_img, lang='eng+ind', config='--oem 3 --psm 6')
    #     st.code(text if text.strip() else "(Teks tidak terdeteksi)")