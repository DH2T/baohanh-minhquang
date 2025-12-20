import streamlit as st
import pandas as pd
import gspread
from streamlit_qrcode_scanner import qrcode_scanner
from urllib.parse import urlparse, parse_qs

# --- 1. CẤU HÌNH TRANG & ẨN GIAO DIỆN THỪA ---
st.set_page_config(page_title="Bảo Hành - Biến Áp Minh Quang", page_icon="⚡", layout="centered")

# CSS để ẩn Menu, Footer và Header của Streamlit + Làm đẹp Card
hide_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding-top: 2rem;}
    
    /* Style cho Thẻ Bảo Hành */
    .warranty-card {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 15px;
        border-left: 8px solid #FF9800; /* Màu cam ngành điện */
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        font-family: 'sans-serif';
    }
    .card-label { color: #666; font-size: 0.9rem; margin-bottom: 2px; }
    .card-value { color: #1f1f1f; font-size: 1.2rem; font-weight: bold; margin-bottom: 15px; }
    .status-valid { color: #2e7d32; font-weight: bold; background: #e8f5e9; padding: 4px 10px; border-radius: 5px; }
    .status-expired { color: #d32f2f; font-weight: bold; background: #ffebee; padding: 4px 10px; border-radius: 5px; }
    </style>
"""
st.markdown(hide_style, unsafe_allow_html=True)

# --- 2. XỬ LÝ DỮ LIỆU & URL ---
def extract_serial(input_string):
    if not input_string: return ""
    if "http" in input_string:
        try:
            parsed_url = urlparse(input_string)
            return parse_qs(parsed_url.query).get("serial", [input_string])[0]
        except: return input_string
    return input_string

SHEET_ID = "1RSgJ18oLmNkK2oL-pImYGLLiPBwENaXSG2_XDc-_pPk"
SHEET_NAME = "SerialNumber"

@st.cache_data(ttl=300)
def load_data():
    try:
        creds = st.secrets["gservice_account"]
        gc = gspread.service_account_from_dict(creds)
        df = pd.DataFrame(gc.open_by_key(SHEET_ID).worksheet(SHEET_NAME).get_all_records())
        df['Serial'] = df['Serial'].astype(str).str.strip()
        return df
    except: return pd.DataFrame()

df = load_data()

# --- 3. LOGIC GIAO DIỆN ---
if "search_done" not in st.session_state:
    st.session_state.search_done = False

# MÀN HÌNH 1: QUÉT MÃ & NHẬP LIỆU
if not st.session_state.search_done:
    st.markdown("<h2 style='text-align: center; color: #FF9800;'>⚡ BIẾN ÁP MINH QUANG</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Vui lòng quét mã QR trên sản phẩm để tra cứu</p>", unsafe_allow_html=True)
    
    with st.expander("📷 Mở Camera quét mã", expanded=True):
        raw_qr = qrcode_scanner(key='qrcode_scanner')
    
    url_serial = st.query_params.get("serial", "")
    processed_qr = extract_serial(raw_qr)
    initial_value = processed_qr if processed_qr else extract_serial(url_serial)

    search_query = st.text_input("Hoặc nhập mã Serial tay:", value=initial_value).strip()

    if search_query:
        result = df[df['Serial'] == search_query] if not df.empty else pd.DataFrame()
        if not result.empty:
            st.session_state.search_done = True
            st.session_state.current_result = result.iloc[0]
            st.session_state.current_query = search_query
            st.rerun()
        else:
            st.error("❌ Không tìm thấy thông tin mã này.")

# MÀN HÌNH 2: HIỂN THỊ KẾT QUẢ DẠNG CARD
else:
    data = st.session_state.current_result
    st.markdown(f"<h3 style='text-align: center;'>Kết Quả Tra Cứu</h3>", unsafe_allow_html=True)
    
    # Xác định trạng thái để tô màu
    status_text = data.get('Trang_Thai', 'N/A')
    status_class = "status-valid" if "Hành" in status_text else "status-expired"

    # Hiển thị Card HTML
    st.markdown(f"""
        <div class="warranty-card">
            <div class="card-label">Mã Serial sản phẩm</div>
            <div class="card-value" style="color: #FF9800;">{st.session_state.current_query}</div>
            
            <div class="card-label">Tên khách hàng</div>
            <div class="card-value">{data.get('Ten_Khach_Hang', 'N/A')}</div>
            
            <div style="display: flex; justify-content: space-between;">
                <div>
                    <div class="card-label">Ngày mua</div>
                    <div class="card-value" style="font-size: 1rem;">{data.get('Ngay_Mua', 'N/A')}</div>
                </div>
                <div>
                    <div class="card-label">Hết hạn bảo hành</div>
                    <div class="card-value" style="font-size: 1rem;">{data.get('Ngay_Het_Han', 'N/A')}</div>
                </div>
            </div>
            
            <div class="card-label">Trạng thái hệ thống</div>
            <span class="{status_class}">{status_text}</span>
        </div>
    """, unsafe_allow_html=True)

    # Nút bấm tương tác
    if st.button("🔍 Tra cứu mã khác", use_container_width=True):
        st.session_state.search_done = False
        st.rerun()
        
    st.link_button("📞 Gọi hỗ trợ kỹ thuật", "tel:0903736414", type="primary", use_container_width=True)

# Thanh bên tối giản
st.sidebar.markdown("### Liên hệ")
st.sidebar.info("CÔNG TY BIẾN ÁP MINH QUANG\n\nHotline: 0903.736.414")
