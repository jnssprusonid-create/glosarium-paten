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
    
    # Membersihkan nama kolom dari spasi liar
    df.columns = [c.strip() for c in df.columns]

    # Mapping label ke nama kolom asli di Google Sheets
    options = {
        "Istilah Asing": "istilah_asing",
        "Padanan": "padanan",
        "Nama Pemohon": "nama_pemohon",
        "Nomor Permohonan": "nomor_permohonan",
        "Sumber": "sumber"
    }

    # 4. UI Filter
    st.write("---")
    st.subheader("1. Filter Utama")
    
    # Baris pertama: Sejajar (Horizontal)
    col1_a, col1_b = st.columns([1, 2]) # Rasio 1:2 agar kolom input lebih lebar
    
    with col1_a:
        cat1 = st.selectbox("Cari berdasarkan:", list(options.keys()), key="cat1")
    
    with col1_b:
        val1 = st.text_input(f"Masukkan kata kunci {cat1}...", placeholder=f"Ketik {cat1} di sini...", key="val1")

    # Baris kedua: Di bawahnya (Vertical)
    st.subheader("2. Filter Tambahan (Opsional)")
    cat2 = st.selectbox("Filter lebih lanjut dengan:", list(options.keys()), index=1, key="cat2")
    val2 = st.text_input(f"Masukkan kata kunci {cat2} tambahan...", placeholder="Kosongkan jika tidak diperlukan", key="val2")

    # 5. Logika Pencarian & Trigger Tabel
    results = df.copy()

    # Tabel HANYA muncul jika Filter Utama diisi
    if val1:
        # Terapkan filter pertama
        results = results[results[options[cat1]].astype(str).str.contains(val1, case=False, na=False)]
        
        # Terapkan filter kedua jika ada isinya
        if val2:
            results = results[results[options[cat2]].astype(str).str.contains(val2, case=False, na=False)]

        st.write("---")
        st.subheader(f"📊 Hasil Pencarian ({len(results)} ditemukan)")
        
        if not results.empty:
            st.dataframe(
                results,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning("Ups! Data tidak ditemukan. Coba kata kunci lain.")
    else:
        # Pesan awal saat tabel masih tersembunyi
        st.info("💡 **Tips:** Masukkan kata kunci pada **Filter Utama** di atas untuk menampilkan daftar istilah.")

    # Tombol Refresh di Sidebar
    if st.sidebar.button("🔄 Update Data dari Sheets"):
        st.cache_data.clear()
        st.rerun()
