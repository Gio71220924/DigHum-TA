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

st.set_page_config(page_title="Batch Koreksi Kemiringan Gambar", layout="centered")
st.title("📄 Batch Koreksi Kemiringan + OCR dengan Hough Transform")
st.markdown("Unggah satu atau beberapa gambar berisi teks miring untuk dikoreksi dan dibaca.")

# --- Upload multiple files
uploaded_files = st.file_uploader("📤 Upload Gambar disini!", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

if uploaded_files:
    for idx, uploaded_file in enumerate(uploaded_files):
        st.divider()
        st.subheader(f"Gambar ke-{idx + 1}: {uploaded_file.name}")

        # Baca gambar sebagai array numpy
        image = Image.open(uploaded_file).convert("RGB")
        img_np = np.array(image)[:, :, ::-1]  # Convert PIL RGB ke BGR (OpenCV)

        # Koreksi kemiringan
        asli, terkoreksi, sudut, arah = koreksi_kemiringan(img_np)

        # Tampilkan gambar
        col1, col2 = st.columns(2)
        with col1:
            st.image(asli, caption=f"Asli || Sudut: {sudut:.2f}°", channels="BGR", use_container_width=True)
        with col2:
            if terkoreksi is not None:
                st.image(terkoreksi, caption=f"Terkoreksi || Arah: {arah}", channels="BGR", use_container_width=True)
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

        # OCR jika berhasil dikoreksi
        # if terkoreksi is not None:
        #     st.markdown("**📖 OCR (Tesseract) Output**")
        #     ocr_img = cv2.cvtColor(terkoreksi, cv2.COLOR_BGR2GRAY)
        #     _, ocr_img = cv2.threshold(ocr_img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        #     text = pytesseract.image_to_string(ocr_img, lang='eng+ind', config='--oem 3 --psm 6')
        #     st.code(text.strip() if text.strip() else "(Teks tidak terdeteksi)")
