import streamlit as st
import numpy as np
import cv2
import requests
from hough import koreksi_kemiringan
from PIL import Image
from io import BytesIO

# URL backend OCR yang sudah dideploy
BACKEND_URL = "https://deploy-railway-production-1030.up.railway.app/ocr"

def perform_ocr_via_backend(image_pil):
    # Konversi PIL Image ke bytes untuk di-upload ke backend
    buffered = BytesIO()
    image_pil.save(buffered, format="PNG")
    buffered.seek(0)
    
    files = {'image': ('image.png', buffered, 'image/png')}
    try:
        response = requests.post(BACKEND_URL, files=files)
        response.raise_for_status()
        data = response.json()
        return data.get('text', '(Tidak ada teks terdeteksi)')
    except Exception as e:
        return f"Error saat memanggil backend OCR: {e}"

st.markdown("""
<h1 style='text-align: center;'>🧾 Deteksi dan Koreksi Kemiringan</h1>
<h3 style='text-align: center; color: gray;'>Deteksi kemiringan + OCR otomatis berbasis Hough Transform</h3>
""", unsafe_allow_html=True)

# Upload gambar
st.markdown("### 📤 Upload Gambar disini!")
uploaded_files = st.file_uploader("Unggah satu atau beberapa gambar", accept_multiple_files=True, type=["png", "jpg", "jpeg"])

if st.button("🚀 Jalankan Koreksi dan OCR"):
    if uploaded_files:
        for idx, uploaded_file in enumerate(uploaded_files):
            st.divider()
            st.subheader(f"Gambar ke-{idx + 1}: {uploaded_file.name}")

            # Baca gambar sebagai array numpy (OpenCV BGR)
            image = Image.open(uploaded_file).convert("RGB")
            img_np = np.array(image)[:, :, ::-1]

            # Koreksi kemiringan
            asli, terkoreksi, sudut, arah, visual_hough = koreksi_kemiringan(img_np)

            # Tampilkan gambar
            col1, col2, col3 = st.columns(3)
            with col1:
                st.image(asli, caption=f"Citra Asli || Sudut kemiringan: {sudut:.2f}°", channels="BGR", use_container_width=True)
            with col2:
                if terkoreksi is not None:
                    st.image(terkoreksi, caption=f"Citra Terkoreksi || Arah koreksi: {arah}", channels="BGR", use_container_width=True)
                    terkoreksi_rgb = cv2.cvtColor(terkoreksi, cv2.COLOR_BGR2RGB)
                    img_pil = Image.fromarray(terkoreksi_rgb)

                    # Simpan ke buffer untuk download
                    img_buffer = BytesIO()
                    img_pil.save(img_buffer, format="PNG")
                    img_buffer.seek(0)

                    st.download_button(
                        label="⬇️ Download Citra Terkoreksi",
                        data=img_buffer,
                        file_name=f"terkoreksi_{uploaded_file.name.rsplit('.', 1)[0]}.png",
                        mime="image/png",
                        use_container_width=True
                    )
                else:
                    st.warning("❌ Tidak ada kemiringan signifikan yang perlu dikoreksi.")
            with col3:
                st.image(visual_hough, caption="Visualisasi Garis Hough", channels="BGR", use_container_width=True)

            # OCR via backend
            st.markdown(f"### 📄 Hasil OCR untuk gambar ke-{idx + 1}")
            if terkoreksi is not None:
                with st.spinner("Sedang memproses OCR..."):
                    text = perform_ocr_via_backend(img_pil)
            else:
                text = "(Tidak ada kemiringan signifikan yang perlu dikoreksi)"

            st.text_area("Teks:", value=text if text else "(Teks tidak terdeteksi)", height=250, key=f"ocr_{idx}")
    else:
        st.warning("⚠️ Silakan unggah setidaknya satu gambar terlebih dahulu.")

st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>🚧 Dibuat oleh Kelompok 6 Digital Humanities • 2025</p>", unsafe_allow_html=True)