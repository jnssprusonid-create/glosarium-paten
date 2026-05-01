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
    
    # Membersihkan nama kolom
    df.columns = [c.strip() for c in df.columns]

    options = {
        "Istilah Asing": "istilah_asing",
        "Padanan": "Padanan",
        "Nama Pemohon": "Nama Pemohon",
        "Nomor Permohonan": "Nomor Permohonan",
        "Sumber": "Sumber"
    }

    st.write("---")

    # 4. Filter Baris 1 (Utama)
    col1_a, col1_b = st.columns([1, 2])
    with col1_a:
        cat1 = st.selectbox("Cari berdasarkan:", list(options.keys()), key="cat1")
    with col1_b:
        val1 = st.text_input(f"Masukkan kata kunci {cat1}...", placeholder=f"Contoh: Device atau Transmitting", key="val1")

    # 5. Filter Baris 2 (Tambahan)
    col2_a, col2_b = st.columns([1, 2])
    with col2_a:
        cat2 = st.selectbox("Filter tambahan dengan:", list(options.keys()), index=1, key="cat2")
    with col2_b:
        val2 = st.text_input(f"Masukkan kata kunci {cat2} tambahan...", placeholder="Kosongkan jika tidak diperlukan", key="val2")

    # 6. Logika Pencarian & Trigger
    results = df.copy()

    if val1:
        # Filter pertama
        results = results[results[options[cat1]].astype(str).str.contains(val1, case=False, na=False)]
        
        # Filter kedua (jika ada isinya)
        if val2:
            results = results[results[options[cat2]].astype(str).str.contains(val2, case=False, na=False)]

        st.write("---")
        st.subheader(f"📊 Hasil: {len(results)} ditemukan")
        
        if not results.empty:
            st.dataframe(
                results,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning("Data tidak ditemukan. Coba cek kembali ejaan atau pilih kategori lain.")
    else:
        st.info("💡 **Tips:** Portal ini membantu menjaga konsistensi istilah (misal: penggunaan **'Alat'** untuk *Device*). Masukkan kata kunci di atas untuk memulai.")

    # Sidebar Refresh
    if st.sidebar.button("🔄 Update Database"):
        st.cache_data.clear()
        st.rerun()
