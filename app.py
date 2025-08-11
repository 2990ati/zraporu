import streamlit as st
import pandas as pd
import pytesseract
import cv2
import numpy as np
from PIL import Image
import io

st.set_page_config(page_title="Z Raporu Otomasyon", layout="wide")

st.title("📄 Z Raporu Otomatik Excel Doldurma")
st.write("Fişleri yükle, otomatik olarak Excel şablonuna işlensin.")

uploaded_excel = st.file_uploader("📂 Excel Şablonu (örn: Kitap1.xlsx)", type=["xlsx"])
uploaded_receipts = st.file_uploader("🧾 Z Raporu Fiş(ler)i", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

def clean_text(text):
    return text.strip().replace("\n", " ")

def extract_info(image):
    img = np.array(image)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray, lang="tur")
    
    tarih = ""
    z_no = ""
    toplam = 0.0
    kdv_tutar = 0.0
    kdv_oran = ""
    kredi = 0.0
    
    for line in text.split("\n"):
        line_clean = line.strip()
        if "202" in line_clean and tarih == "":
            tarih = line_clean.split(" ")[0]
        if "Z" in line_clean and "NO" in line_clean.upper():
            z_no = ''.join([c for c in line_clean if c.isdigit()])
        if "TOPLAM" in line_clean.upper():
            try:
                toplam = float(line_clean.split()[-1].replace(",", "."))
            except:
                pass
        if "KDV" in line_clean.upper() and "%" in line_clean:
            parts = line_clean.split()
            try:
                kdv_oran = ''.join([c for c in parts[0] if c.isdigit()])
                kdv_tutar = float(parts[-1].replace(",", "."))
            except:
                pass
        if "K.KARTI" in line_clean.upper():
            try:
                kredi = float(line_clean.split()[-1].replace(",", "."))
            except:
                pass

    tutar = toplam - kdv_tutar
    return tarih, z_no, tutar, kdv_oran, kredi

if st.button("İşle ve Excel Oluştur"):
    if uploaded_excel and uploaded_receipts:
        df = pd.read_excel(uploaded_excel)
        for receipt in uploaded_receipts:
            img = Image.open(receipt)
            tarih, z_no, tutar, kdv_oran, kredi = extract_info(img)
            
            new_row = {
                "Defter Kayıt Tarihi": tarih,
                "Belge Tarihi": tarih,
                "Z No": z_no,
                "Tutar": tutar,
                "KDV Oranı": kdv_oran,
                "Kredi": kredi
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        
        output = io.BytesIO()
        df.to_excel(output, index=False)
        st.download_button("📥 Excel'i İndir", data=output.getvalue(), file_name="zraporu_cikti.xlsx")
    else:
        st.warning("Lütfen hem Excel şablonunu hem de fişleri yükleyin.")
