import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Konfigurasi Halaman
st.set_page_config(page_title="Portal Glosarium Paten", layout="wide")

# 2. Sistem Login
def check_password():
    def password_entered():
        if st.session_state["username"] in st.secrets["passwords"] and \
           st.session_state["password"] == st.secrets["passwords"][st.session_state["username"]]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.title("🔐 Login Portal Glosarium")
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
    
    # 3. Koneksi Data
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(spreadsheet=st.secrets["connections"]["gsheets"]["spreadsheet"])
    df.columns = [c.strip() for c in df.columns]

    options = {
        "Istilah Asing": "istilah_asing",
        "Padanan": "padanan",
        "Nama Pemohon": "nama_pemohon",
        "Nomor Permohonan": "nomor_permohonan",
        "Sumber": "sumber"
    }

    st.write("---")

    # 4. Filter Baris 1 (Utama) - Menggunakan 3 Kolom
    col1_a, col1_b, col1_c = st.columns([1, 2, 1])
    with col1_a:
        cat1 = st.selectbox("Cari berdasarkan:", list(options.keys()), key="cat1")
    with col1_b:
        val1 = st.text_input(f"Masukkan kata kunci {cat1}...", placeholder="Contoh: Device atau Transmitting", key="val1")
    with col1_c:
        mode1 = st.radio("Mode Pencarian:", ["Containing", "Exact Match"], horizontal=True, key="mode1")

    # 5. Filter Baris 2 (Tambahan) - Menggunakan 3 Kolom
    col2_a, col2_b, col2_c = st.columns([1, 2, 1])
    with col2_a:
        cat2 = st.selectbox("Filter tambahan dengan:", list(options.keys()), index=1, key="cat2")
    with col2_b:
        val2 = st.text_input(f"Masukkan kata kunci {cat2} tambahan...", placeholder="Kosongkan jika tidak diperlukan", key="val2")
    with col2_c:
        mode2 = st.radio("Mode Filter:", ["Containing", "Exact Match"], horizontal=True, key="mode2")

    # 6. Logika Pencarian Berdasarkan Mode
    results = df.copy()

    def filter_data(data, category, value, mode):
        if not value:
            return data
        
        column_name = options[category]
        if mode == "Exact Match":
            # Mencari yang benar-benar sama persis (case insensitive)
            return data[data[column_name].astype(str).str.fullmatch(value, case=False, na=False)]
        else:
            # Mencari yang mengandung kata tersebut
            return data[data[column_name].astype(str).str.contains(value, case=False, na=False)]

    if val1:
        # Terapkan filter pertama
        results = filter_data(results, cat1, val1, mode1)
        
        # Terapkan filter kedua
        if val2:
            results = filter_data(results, cat2, val2, mode2)

        st.write("---")
        st.subheader(f"📊 Hasil: {len(results)} ditemukan")
        
        if not results.empty:
            st.dataframe(results, use_container_width=True, hide_index=True)
        else:
            st.warning("Data tidak ditemukan. Coba ubah mode ke 'Containing' jika hasil terlalu spesifik.")
    else:
        st.info("💡 **Tips:** Gunakan **Exact Match** jika ingin hasil yang sama persis (misal: hanya mencari 'Alat' tanpa 'Peralatan').")

    # Sidebar
    if st.sidebar.button("🔄 Update Database"):
        st.cache_data.clear()
        st.rerun()
