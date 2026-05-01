import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Konfigurasi Halaman
st.set_page_config(page_title="Portal Glosarium Paten", layout="centered") # 'centered' lebih enak dilihat untuk layout atas-bawah

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
    st.write("Cari padanan istilah teknis untuk menjaga konsistensi dokumen.")

    # 3. Koneksi Data
    conn = st.connection("gsheets", type=GSheetsConnection)
    # Pastikan URL sheet ada di Secrets
    df = conn.read(spreadsheet=st.secrets["connections"]["gsheets"]["spreadsheet"])
    
    # Membersihkan nama kolom
    df.columns = [c.strip() for c in df.columns]

    options = {
        "Istilah Asing": "istilah_asing",
        "Padanan": "padanan",
        "Nama Pemohon": "nama_pemohon",
        "Nomor Permohonan": "nomor_permohonan",
        "Sumber": "sumber"
    }

    # 4. UI Filter Atas-Bawah
    st.markdown("---")
    
    # Bagian Filter Utama
    st.subheader("1. Filter Utama")
    cat1 = st.selectbox("Cari berdasarkan:", list(options.keys()), key="cat1")
    val1 = st.text_input(f"Masukkan kata kunci {cat1}...", placeholder="Contoh: Device atau Transmitting", key="val1")

    # Bagian Filter Tambahan
    st.subheader("2. Filter Tambahan (Opsional)")
    cat2 = st.selectbox("Filter lebih lanjut dengan:", list(options.keys()), index=1, key="cat2")
    val2 = st.text_input(f"Masukkan kata kunci {cat2} tambahan...", placeholder="Opsional", key="val2")

    # 5. Logika Pencarian & Tampilan Tabel
    results = df.copy()

    # Trigger: Tabel hanya muncul jika Filter Utama (val1) diisi
    if val1:
        # Filter pertama
        results = results[results[options[cat1]].astype(str).str.contains(val1, case=False, na=False)]
        
        # Filter kedua (hanya jika diisi)
        if val2:
            results = results[results[options[cat2]].astype(str).str.contains(val2, case=False, na=False)]

        st.markdown("---")
        st.subheader(f"✅ Hasil Pencarian ({len(results)} data)")
        
        if not results.empty:
            st.dataframe(
                results,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning("Data tidak ditemukan. Pastikan kata kunci sudah benar.")
    else:
        st.info("Silakan masukkan kata kunci pada **Filter Utama** di atas untuk menampilkan hasil.")

    # Tombol Refresh di Sidebar agar tidak mengganggu layout utama
    if st.sidebar.button("🔄 Refresh Database"):
        st.cache_data.clear()
        st.rerun()
