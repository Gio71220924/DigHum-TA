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

import requests

# app.py
def run_ocr_local(image_path):
    with open(image_path, "rb") as img:
        # Key "image" di sini sudah benar
        response = requests.post("http://localhost:5000/ocr", files={"image": img})
        print("Hasil OCR:", response.json()["text"])

# Contoh panggil fungsi
run_ocr_local("dataset/coba1.png")

st.markdown("""
<h1 style='text-align: center;'>🧾 Deteksi dan  Koreksi Kemiringan</h1>
<h3 style='text-align: center; color: gray;'>Deteksi kemiringan + OCR otomatis berbasis Hough Transform</h3>
""", unsafe_allow_html=True)

# --- Upload multiple files
st.markdown("### 📤 Upload Gambar disini!")
uploaded_files = st.file_uploader("Unggah satu atau beberapa gambar", accept_multiple_files=True, type=["png", "jpg", "jpeg"])

if st.button("🚀 Jalankan Koreksi dan OCR"):
    if uploaded_files:
        for idx, uploaded_file in enumerate(uploaded_files):
            st.divider()
            st.subheader(f"Gambar ke-{idx + 1}: {uploaded_file.name}")

            # Baca gambar sebagai array numpy
            image = Image.open(uploaded_file).convert("RGB")
            img_np = np.array(image)[:, :, ::-1]  # Convert PIL RGB ke BGR (OpenCV)

            # Koreksi kemiringan
            asli, terkoreksi, sudut, arah, visual_hough = koreksi_kemiringan(img_np)

            # Tampilkan gambar
            col1, col2, col3 = st.columns(3)
            with col1:
                st.image(asli, caption=f"Citra Asli || Sudut kemiringan: {sudut:.2f}°", channels="BGR", use_container_width=True)
            with col2:
                if terkoreksi is not None:
                    st.image(terkoreksi, caption=f"Citra Terkoreksi || Arah koreksi: {arah}", channels="BGR", use_container_width=True)
                    # Konversi citra BGR ke RGB untuk disimpan
                    terkoreksi_rgb = cv2.cvtColor(terkoreksi, cv2.COLOR_BGR2RGB)
                    img_pil = Image.fromarray(terkoreksi_rgb)

                    # Simpan ke buffer
                    from io import BytesIO
                    img_buffer = BytesIO()
                    img_pil.save(img_buffer, format="PNG")
                    img_buffer.seek(0)

                    # Tombol download gambar terkoreksi
                    download_name = f"terkoreksi_{uploaded_file.name.rsplit('.', 1)[0]}.png"
                    st.download_button(
                        label="⬇️ Download Citra Terkoreksi",
                        data=img_buffer,
                        file_name=download_name,
                        mime="image/png",
                        use_container_width=True
                    )
                else:
                    st.warning("❌ Tidak ada kemiringan signifikan yang perlu dikoreksi.")
            with col3:
                st.image(visual_hough, caption="Visualisasi Garis Hough", channels="BGR", use_container_width=True)

        # OCR jika berhasil dikoreksi
        # if terkoreksi is not None:
        #     st.markdown("**📖 OCR (Tesseract) Output**")
        #     ocr_img = cv2.cvtColor(terkoreksi, cv2.COLOR_BGR2GRAY)
        #     _, ocr_img = cv2.threshold(ocr_img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        #     text = pytesseract.image_to_string(ocr_img, lang='eng+ind', config='--oem 3 --psm 6')
        #     st.code(text.strip() if text.strip() else "(Teks tidak terdeteksi)")


st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>🚧 Dibuat oleh Kelompok 6 Digital Humanities • 2025</p>", unsafe_allow_html=True)
