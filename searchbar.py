import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Konfigurasi Halaman
st.set_page_config(
    page_title="Spruson & Ferguson - Patent Glossary", 
    page_icon="⚖️", 
    layout="wide"
)

# --- CUSTOM CSS ---
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
    </style>
    """, unsafe_allow_html=True)

# 2. Sistem Login
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
                        st.error("❌ Username or password incorrect.")
        return False
    return True

if check_password():
    # --- HEADER ---
    st.markdown("<h1 class='main-title'>PATENT GLOSSARY PORTAL</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>Spruson & Ferguson Indonesia • Terminology Search</p>", unsafe_allow_html=True)
    
    # 3. Koneksi Data
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(spreadsheet=st.secrets["connections"]["gsheets"]["spreadsheet"])
    df.columns = [c.strip().lower() for c in df.columns]

    # Master list of options
    master_options = {
        "Foregin Term": "istilah_asing",
        "ID Equivalent": "padanan",
        "Client": "nama_pemohon",
        "ID Application": "nomor_permohonan",
        "Source of Information": "sumber"
    }

    st.write("---")

    # 4. AREA FILTER ADAPTIF
    with st.container():
        st.markdown("<div class='filter-container'>", unsafe_allow_html=True)
        
        # --- BARIS 1 (FILTER UTAMA) ---
        col1_a, col1_b, col1_c = st.columns([1, 2, 1])
        with col1_a:
            cat1 = st.selectbox("Search by:", list(master_options.keys()), key="cat1")
        with col1_b:
            val1 = st.text_input(f"Enter {cat1} keyword...", key="val1")
        with col1_c:
            mode1 = st.radio("Search Mode:", ["Containing", "Exact Match"], horizontal=True, key="mode1")

        # --- LOGIKA ADAPTIF ---
        # Membuat list baru untuk filter kedua yang mengecualikan pilihan di filter pertama
        remaining_options = [opt for opt in master_options.keys() if opt != cat1]

        # --- BARIS 2 (FILTER TAMBAHAN) ---
        col2_a, col2_b, col2_c = st.columns([1, 2, 1])
        with col2_a:
            # Pilihan di sini akan berubah otomatis jika cat1 berubah
            cat2 = st.selectbox("Secondary filter:", remaining_options, key="cat2")
        with col2_b:
            val2 = st.text_input(f"Additional {cat2} keyword...", placeholder="Optional", key="val2")
        with col2_c:
            mode2 = st.radio("Filter Mode:", ["Containing", "Exact Match"], horizontal=True, key="mode2")

        st.markdown("</div>", unsafe_allow_html=True)

    # 5. LOGIKA PENCARIAN
    def filter_data(data, category, value, mode):
        if not value: return data
        column_name = master_options[category]
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
            st.warning("No matches found. Try changing your search mode.")
    else:
        st.info("💡 **Translator Tip:** This adaptive filter prevents searching the same column twice.")

    # 6. SIDEBAR
    with st.sidebar:
                if st.button("🔄 Sync Database"):
            st.cache_data.clear()
            st.rerun()
        st.write("---")
        st.caption("Spruson & Ferguson Indonesia")

# --- FORM KOMUNIKASI ---
    st.write("---")
    with st.expander("✉️ Contact Admin / Ask a Question About Terms"):
        st.write("Use this form if you have questions about terminology or would like to suggest a new translation.")
        
        with st.form("email_form", clear_on_submit=True):
            user_email = st.text_input("Your email address (for a reply):")
            subject = st.selectbox("Category:", ["Proposed New Terms", "Correction", "Technical Questions"])
            message = st.text_area("Message / Question Details:")
            
            submit_email = st.form_submit_button("Send Message")
            
            if submit_email:
                if user_email and message:
                    try:
                        # Logika Pengiriman Email
                        import smtplib
                        from email.mime.text import MIMEText
                        
                        # Data dari Secrets
                        sender_email = st.secrets["email"]["user"]
                        sender_password = st.secrets["email"]["password"]
                        target_email = "glossarysfid@gmail.com" 
                        
                        # Format Email
                        email_body = f"Dari: {user_email}\nKategori: {subject}\n\nPesan:\n{message}"
                        msg = MIMEText(email_body)
                        msg['Subject'] = f"[Glosarium Portal] {subject}"
                        msg['From'] = sender_email
                        msg['To'] = target_email
                        
                        # Kirim menggunakan SMTP Gmail
                        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                            server.login(sender_email, sender_password)
                            server.sendmail(sender_email, target_email, msg.as_string())
                        
                        st.success("✅ Your message has been sent to the Admin team. Thank you!")
                    except Exception as e:
                        st.error(f"❌ Failed to send the message. Make sure your SMTP settings are correct. Error: {e}")
                else:
                    st.warning("Please provide your email address and message.")
