import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Konfigurasi Halaman & Branding Spruson
st.set_page_config(
    page_title="Spruson & Ferguson - Patent Glossary", 
    page_icon="⚖️", 
    layout="wide"
)

# --- CUSTOM CSS (SPRUSON BRANDING) ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    .main-title {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        background: -webkit-linear-gradient(#FF4B2B, #FF8C00);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 42px; font-weight: 900; text-align: center; margin-bottom: 0px;
    }
    .sub-title { color: #A0AEC0; text-align: center; font-size: 18px; margin-bottom: 35px; }
    .filter-container {
        background-color: #1A202C; padding: 25px; border-radius: 12px;
        border-left: 6px solid #E24A2D; margin-bottom: 25px;
    }
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #E24A2D 0%, #FF8C00 100%);
        color: white; border-radius: 6px; border: none; padding: 12px 30px; font-weight: bold; width: 100%;
    }
    [data-testid="stSidebar"] { background-color: #000000; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 2. Sistem Login dengan TOMBOL (st.form)
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if not st.session_state["password_correct"]:
        col_log1, col_log2, col_log3 = st.columns([1,1,1])
        with col_log2:
            st.markdown("<h1 class='main-title'>LOGIN</h1>", unsafe_allow_html=True)
            with st.form("login_form"):
                user = st.text_input("Username")
                pw = st.text_input("Password", type="password")
                submit_button = st.form_submit_button("LOGIN")
                
                if submit_button:
                    if user in st.secrets["passwords"] and pw == st.secrets["passwords"][user]:
                        st.session_state["password_correct"] = True
                        st.rerun()
                    else:
                        st.error("❌ Username atau password salah.")
        return False
    return True

if check_password():
    # --- HEADER ---
    st.markdown("<h1 class='main-title'>PATENT GLOSSARY PORTAL</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>Spruson & Ferguson Indonesia • Technical Terminology Database</p>", unsafe_allow_html=True)
    
    # 3. Koneksi Data & Pembersihan Kolom (Anti-KeyError)
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(spreadsheet=st.secrets["connections"]["gsheets"]["spreadsheet"])
        
        # Membersihkan header: huruf kecil semua dan hapus spasi di awal/akhir
        df.columns = [c.strip().lower() for c in df.columns]
        
        # Mapping label visual ke nama kolom yang sudah dibersihkan
        options = {
            "Istilah Asing": "istilah_asing",
            "Padanan": "padanan",
            "Nama Pemohon": "nama_pemohon",
            "Nomor Permohonan": "nomor_permohonan",
            "Sumber": "sumber"
        }

        # 4. AREA FILTER
        with st.container():
            st.markdown("<div class='filter-container'>", unsafe_allow_html=True)
            # Baris 1
            col1_a, col1_b, col1_c = st.columns([1, 2, 1])
            with col1_a:
                cat1 = st.selectbox("Search by:", list(options.keys()), key="cat1")
            with col1_b:
                val1 = st.text_input(f"Enter {cat1} keyword...", key="val1")
            with col1_c:
                mode1 = st.radio("Search Mode:", ["Containing", "Exact Match"], horizontal=True, key="mode1")

            # Baris 2
            col2_a, col2_b, col2_c = st.columns([1, 2, 1])
            with col2_a:
                cat2 = st.selectbox("Secondary filter:", list(options.keys()), index=1, key="cat2")
            with col2_b:
                val2 = st.text_input(f"Additional {cat2} keyword...", key="val2")
            with col2_c:
                mode2 = st.radio("Filter Mode:", ["Containing", "Exact Match"], horizontal=True, key="mode2")
            st.markdown("</div>", unsafe_allow_html=True)

        # 5. LOGIKA PENCARIAN
        def filter_data(data, category, value, mode):
            if not value: return data
            column_name = options[category]
            if mode == "Exact Match":
                return data[data[column_name].astype(str).str.fullmatch(value, case=False, na=False)]
            else:
                return data[data[column_name].astype(str).str.contains(value, case=False, na=False)]

        results = df.copy()

        if val1:
            results = filter_data(results, cat1, val1, mode1)
            if val2:
                results = filter_data(results, cat2, val2, mode2)

            st.markdown("---")
            st.subheader(f"📊 {len(results)} Matches Found")
            
            if not results.empty:
                st.dataframe(results, use_container_width=True, hide_index=True)
                csv = results.to_csv(index=False).encode('utf-8')
                st.download_button(label="📥 Export Results to CSV", data=csv, file_name='glossary_export.csv', mime='text/csv')
            else:
                st.warning("No matches found.")
        else:
            st.info("💡 **Tip:** Use 'Exact Match' for precise auditing of terms like 'Alat' vs 'Peralatan'.")
            
            # Dashboard Stats
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Terms", f"{len(df)}")
            # Menggunakan kolom yang sudah dibersihkan (nama_pemohon)
            c2.metric("Applicants", f"{df['nama_pemohon'].nunique()}")
            c3.metric("Status", "Online ✅")

    except Exception as e:
        st.error(f"Error loading database. Please check your Google Sheets headers. Details: {e}")

    # 6. SIDEBAR
    with st.sidebar:
        st.title("Admin Tools")
        if st.button("🔄 Sync Database"):
            st.cache_data.clear()
            st.rerun()
        st.write("---")
        st.caption("Spruson & Ferguson Indonesia")
