import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Konfigurasi Halaman & Tema Gelap Spruson
st.set_page_config(
    page_title="Spruson & Ferguson - Patent Glossary", 
    page_icon="⚖️", 
    layout="wide"
)

# --- CUSTOM CSS (SPRUSON BRANDING) ---
st.markdown("""
    <style>
    /* Mengatur background utama menjadi hitam/gelap */
    .stApp {
        background-color: #0E1117;
        color: #FFFFFF;
    }
    
    /* Judul dengan gradasi Oranye Spruson */
    .main-title {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        background: -webkit-linear-gradient(#FF4B2B, #FF8C00);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 42px;
        font-weight: 900;
        text-align: center;
        margin-bottom: 0px;
        letter-spacing: -1px;
    }
    
    .sub-title {
        color: #A0AEC0;
        text-align: center;
        font-size: 18px;
        margin-bottom: 35px;
        font-weight: 300;
    }

    /* Container Filter dengan nuansa Dark Mode */
    .filter-container {
        background-color: #1A202C;
        padding: 25px;
        border-radius: 12px;
        border-left: 6px solid #E24A2D; /* Aksen Oranye di samping */
        margin-bottom: 25px;
    }

    /* Input Fields Styling */
    .stTextInput > div > div > input {
        background-color: #2D3748;
        color: white;
        border: 1px solid #4A5568;
    }

    /* Tombol Oranye Khas Spruson */
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #E24A2D 0%, #FF8C00 100%);
        color: white;
        border-radius: 6px;
        border: none;
        padding: 12px 30px;
        font-weight: bold;
        transition: 0.3s;
    }
    
    div.stButton > button:first-child:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 15px rgba(226, 74, 45, 0.4);
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #000000;
        border-right: 1px solid #2D3748;
    }

    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

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
        st.markdown("<h1 class='main-title'>ACCESS PORTAL</h1>", unsafe_allow_html=True)
        col_log1, col_log2, col_log3 = st.columns([1,1,1])
        with col_log2:
            st.text_input("Username", on_change=password_entered, key="username")
            st.text_input("Password", type="password", on_change=password_entered, key="password")
            if "password_correct" in st.session_state and not st.session_state["password_correct"]:
                st.error("❌ Username or password incorrect.")
        return False
    return True

if check_password():
    # --- HEADER ---
    st.markdown("<h1 class='main-title'>PATENT GLOSSARY PORTAL</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>Spruson & Ferguson Indonesia • Technical Terminology Database</p>", unsafe_allow_html=True)
    
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

    # 4. AREA FILTER (SPRUSON DARK THEME)
    with st.container():
        st.markdown("<div class='filter-container'>", unsafe_allow_html=True)
        
        # Row 1
        col1_a, col1_b, col1_c = st.columns([1, 2, 1])
        with col1_a:
            cat1 = st.selectbox("Search by:", list(options.keys()), key="cat1")
        with col1_b:
            val1 = st.text_input(f"Enter {cat1} keyword...", placeholder="e.g. Apparatus, Method, or Device", key="val1")
        with col1_c:
            mode1 = st.radio("Search Mode:", ["Containing", "Exact Match"], horizontal=True, key="mode1")

        # Row 2
        col2_a, col2_b, col2_c = st.columns([1, 2, 1])
        with col2_a:
            cat2 = st.selectbox("Secondary filter:", list(options.keys()), index=1, key="cat2")
        with col2_b:
            val2 = st.text_input(f"Additional {cat2} keyword...", placeholder="Optional", key="val2")
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
        st.subheader(f"📊 {len(results)} Terminology matches found")
        
        if not results.empty:
            st.dataframe(results, use_container_width=True, hide_index=True)
            
            # Export Action
            csv = results.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Export Results to CSV",
                data=csv,
                file_name='spruson_glossary_export.csv',
                mime='text/csv',
            )
        else:
            st.warning("No matches found. Please adjust your keywords or search mode.")
    else:
        st.info("💡 **Translator Tip:** Use **Exact Match** for high-precision auditing of 'Device' vs 'Apparatus' terms.")
        
        # Stats Dashboard
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Total Terms", f"{len(df)}")
        with c2:
            st.metric("Total Applicants", f"{df['Nama Pemohon'].nunique()}")
        with c3:
            st.metric("System Status", "Live ✅")

    # 6. SIDEBAR
    with st.sidebar:
        st.title("Admin Tools")
        if st.button("🔄 Sync with Google Sheets"):
            st.cache_data.clear()
            st.success("Database Updated!")
            st.rerun()
        st.write("---")
        st.caption("Spruson & Ferguson Indonesia")
        st.caption("Patent Audit & Translation Portal v1.5")
