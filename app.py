import streamlit as st
import pandas as pd
import gspread
from streamlit_qrcode_scanner import qrcode_scanner
from urllib.parse import urlparse, parse_qs

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="Bảo Hành - Biến Áp Minh Quang", 
    page_icon="⚡",
    layout="centered"
)

# --- 2. TỐI ƯU GIAO DIỆN (CSS) ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .main-title {
        font-size: 2rem !important; 
        color: #FF9800 !important;
        text-align: center !important;
        font-weight: bold !important;
        white-space: nowrap !important; 
        margin-top: 0px !important;
        margin-bottom: 5px !important;
        text-transform: uppercase !important;
        display: block !important;
        width: 100% !important;
    }
    
    .sub-title {
        text-align: center;
        color: #666;
        font-size: 0.9rem;
        margin-bottom: 20px;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. KẾT NỐI DỮ LIỆU ---
@st.cache_data(ttl=300)
def load_data():
    try:
        creds = st.secrets["gservice_account"]
        gc = gspread.service_account_from_dict(creds)
        sh = gc.open_by_key("1RSgJ18oLmNkK2oL-pImYGLLiPBwENaXSG2_XDc-_pPk")
        df = pd.DataFrame(sh.worksheet("SerialNumber").get_all_records())
        df['Serial'] = df['Serial'].astype(str).str.strip()
        return df
    except Exception as e:
        st.error(f"Lỗi kết nối dữ liệu: {e}")
        return pd.DataFrame()

df = load_data()

# --- 4. HÀM XỬ LÝ CHUỖI QR/URL ---
def get_serial(text):
    if not text: return ""
    if "http" in text:
        try:
            return parse_qs(urlparse(text).query).get("serial", [text.split('/')[-1]])[0]
        except: return text
    return text

# --- 5. QUẢN LÝ TRẠNG THÁI ---
if "found" not in st.session_state:
    st.session_state.found = False

# HÀM RESET KHI BẤM NÚT "TRA CỨU MÃ KHÁC"
def reset_search():
    st.session_state.found = False
    st.session_state.query_id = ""
    st.session_state.data = None
    # Xóa tham số trên URL để không bị tự động điền lại mã cũ
    st.query_params.clear()

# --- 6. GIAO DIỆN CHÍNH ---

if not st.session_state.found:
    # MÀN HÌNH TRA CỨU
    st.markdown('<p class="main-title">TRA CỨU BẢO HÀNH</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">BIẾN ÁP MINH QUANG-CÔNG TY DH2T</p>', unsafe_allow_html=True)
    
    with st.expander("📷 MỞ CAMERA QUÉT MÃ QR", expanded=True):
        scanned_val = qrcode_scanner(key='scanner')
    
    url_val = st.query_params.get("serial", "")
    input_default = get_serial(scanned_val) if scanned_val else get_serial(url_val)
    
    query = st.text_input("Nhập Số Serial sản phẩm:", value=input_default, placeholder="Nhập hoặc quét mã...")

    if query:
        if not df.empty:
            match = df[df['Serial'] == query]
            if not match.empty:
                st.session_state.found = True
                st.session_state.data = match.iloc[0]
                st.session_state.query_id = query
                st.rerun()
            else:
                st.error(f"❌ Không tìm thấy mã máy: {query}")
else:
    # MÀN HÌNH KẾT QUẢ
    st.markdown('<p class="main-title">THÔNG TIN BẢO HÀNH</p>', unsafe_allow_html=True)
    
    data = st.session_state.data
    
    with st.container(border=True):
        st.markdown(f"### 👤 {data.get('Ten_Khach_Hang', 'Khách hàng')}")
        st.caption(f"Số Serial: {st.session_state.query_id}")
        st.divider()
        
        c1, c2 = st.columns(2)
        c1.metric("Ngày mua", str(data.get('Ngay_Mua', 'N/A')))
        c2.metric("Hết hạn", str(data.get('Ngay_Het_Han', 'N/A')))
        
        status_raw = str(data.get('Trang_Thai', '')).strip()
        if "còn" in status_raw.lower():
            st.success(f"✅ **TRẠNG THÁI:** {status_raw}")
        else:
            st.error(f"❌ **TRẠNG THÁI:** {status_raw}")

    st.write("") 
    
    # NÚT RESET - ĐÃ ĐƯỢC FIX LỖI KHÔNG CHẠY
    st.button("🔍 Tra cứu mã khác", on_click=reset_search, use_container_width=True)
        
    st.link_button("📞 Gọi hỗ trợ kỹ thuật", "tel:0903736414", use_container_width=True, type="primary")

# Sidebar
st.sidebar.page_link("https://bienapminhquang.com", label="Quay lại Website", icon="🏠")








