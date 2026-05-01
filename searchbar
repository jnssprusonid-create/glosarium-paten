import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Konfigurasi Halaman
st.set_page_config(page_title="Portal Glosarium Paten", layout="wide")

# 2. Sistem Login Sederhana (Username & Password)
# Untuk produksi, gunakan library streamlit-authenticator agar lebih aman
def check_password():
    def password_entered():
        if st.session_state["username"] in st.secrets["passwords"] and \
           st.session_state["password"] == st.secrets["passwords"][st.session_state["username"]]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Hapus password dari session state
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Username", on_change=password_entered, key="username")
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Username", on_change=password_entered, key="username")
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        st.error("😕 User tidak dikenal atau password salah")
        return False
    else:
        return True

if check_password():
    st.title("🔍 Portal Glosarium Padanan Paten")
    st.write("Gunakan kolom pencarian di bawah untuk menemukan padanan istilah teknis.")

    # 3. Koneksi ke Google Sheets
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Ganti URL ini dengan URL Google Sheets Anda
    url = "https://docs.google.com/spreadsheets/d/1vTtYmM0axLBu2uvP7yuVFLv2-28DSdYRNl9etok7nFE/edit?gid=1743141232#gid=1743141232"
    df = conn.read(spreadsheet=url)

    # 4. Search Bar
    search_query = st.text_input("Cari istilah asing atau padanan...", "")

    # 5. Logika Filter
    if search_query:
        filtered_df = df[
            df['istilah_asing'].str.contains(search_query, case=False, na=False) |
            df['padanan'].str.contains(search_query, case=False, na=False)
        ]
    else:
        filtered_df = df

    # 6. Tampilan Visual
    st.subheader("Daftar Istilah")
    st.dataframe(
        filtered_df,
        column_config={
            "istilah_asing": "Istilah Asing",
            "padanan": "Padanan",
            "nama_pemohon": "Nama Pemohon",
            "nomor_permohonan": "Nomor Permohonan",
            "sumber": "Sumber"
        },
        use_container_width=True,
        hide_index=True
    )

    # Tombol Refresh Data
    if st.button("Refresh Database"):
        st.cache_data.clear()
        st.rerun()
