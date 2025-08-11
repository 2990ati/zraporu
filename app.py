import streamlit as st
import pandas as pd

st.set_page_config(page_title="Z Raporu Analizi", layout="wide")

st.title("📊 Z Raporu Excel Analizi")

uploaded_file = st.file_uploader("Excel dosyanızı yükleyin", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        st.success("✅ Dosya başarıyla yüklendi!")
        
        st.subheader("Önizleme")
        st.dataframe(df)

        # İstatistikler
        st.subheader("Temel İstatistikler")
        st.write(df.describe())

        # Kolon filtreleme
        st.subheader("Kolon Seçimi")
        selected_columns = st.multiselect("Görüntülenecek Kolonlar", df.columns.tolist(), default=df.columns.tolist())
        st.dataframe(df[selected_columns])

        # CSV indir
        st.subheader("Veriyi İndir")
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 CSV olarak indir", csv, "z_raporu.csv", "text/csv")

    except Exception as e:
        st.error(f"Hata oluştu: {e}")
