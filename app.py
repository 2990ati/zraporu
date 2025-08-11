import streamlit as st
import pandas as pd
import pytesseract
from PIL import Image
import io
import re

st.set_page_config(page_title="Z Raporu Analizi & Fiş OCR", layout="wide")

st.title("📊 Z Raporu ve Fiş Analizi")

# Sekmeler
tab1, tab2 = st.tabs(["📑 Excel Analizi", "🧾 Fişten Excel'e OCR"])

# --- Tab 1: Excel Analizi ---
with tab1:
    st.subheader("Excel dosyanızı yükleyin")
    uploaded_file = st.file_uploader("Excel dosyası yükle (.xlsx)", type=["xlsx"], key="excel")

    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file)
            st.success("✅ Dosya yüklendi!")
            st.dataframe(df)

            st.subheader("📊 Temel İstatistikler")
            st.write(df.describe())

            st.subheader("🔍 Kolon Seçimi")
            kolonlar = st.multiselect("Görüntülenecek kolonları seçin", df.columns.tolist(), default=df.columns.tolist())
            st.dataframe(df[kolonlar])

        except Exception as e:
            st.error(f"❌ Hata: {e}")

# --- Tab 2: Fiş OCR ---
with tab2:
    st.subheader("Fiş fotoğrafını yükleyin")
    uploaded_image = st.file_uploader("Fiş resmi yükle (PNG, JPG)", type=["png", "jpg", "jpeg"], key="fis")

    if uploaded_image:
        try:
            # Görsel yükleme
            image = Image.open(uploaded_image)
            st.image(image, caption="Yüklenen Fiş", use_column_width=True)

            # OCR ile metin okuma
            text = pytesseract.image_to_string(image, lang="tur")
            st.subheader("📄 OCR ile Okunan Metin")
            st.text(text)

            # Bilgileri ayıklama
            tarih = re.search(r"\d{2}\.\d{2}\.\d{4}", text)
            saat = re.search(r"\d{2}:\d{2}", text)
            toplam = re.search(r"TOPLAM\s+([\d\.,]+)", text, re.IGNORECASE)

            # Ürün satırlarını ayıkla
            urunler = []
            for line in text.split("\n"):
                parts = line.split()
                if len(parts) >= 3 and parts[-1].replace(",", "").replace(".", "").isdigit():
                    urun_adi = " ".join(parts[:-2])
                    adet = parts[-2]
                    fiyat = parts[-1]
                    urunler.append([urun_adi, adet, fiyat])

            # DataFrame oluşturma
            df_fis = pd.DataFrame(urunler, columns=["Ürün Adı", "Adet", "Fiyat"])
            df_fis["Tarih"] = tarih.group(0) if tarih else ""
            df_fis["Saat"] = saat.group(0) if saat else ""
            df_fis["Toplam"] = toplam.group(1) if toplam else ""

            # Excel çıktısı oluşturma
            output = io.BytesIO()
            df_fis.to_excel(output, index=False)

            st.success("✅ Fişten veriler çıkarıldı!")
            st.dataframe(df_fis)

            # İndirme butonu
            st.download_button("📥 Excel Olarak İndir", output.getvalue(), file_name="fis_analizi.xlsx")

        except Exception as e:
            st.error(f"❌ OCR sırasında hata: {e}")
