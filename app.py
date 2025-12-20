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

# --- 5. HIỂN THỊ KẾT QUẢ DẠNG CARD ---
else:
    data = st.session_state.current_result
    st.markdown("<h3 style='text-align: center; color: #333;'>Kết Quả Tra Cứu</h3>", unsafe_allow_html=True)
    
    # Chuẩn bị dữ liệu
    serial_no = st.session_state.current_query
    customer = data.get('Ten_Khach_Hang', 'N/A')
    buy_date = data.get('Ngay_Mua', 'N/A')
    exp_date = data.get('Ngay_Het_Han', 'N/A')
    status_text = data.get('Trang_Thai', 'N/A')
    
    # Xác định màu sắc trạng thái
    status_color = "#2e7d32" if "Hành" in status_text else "#d32f2f"
    status_bg = "#e8f5e9" if "Hành" in status_text else "#ffebee"

    # Tạo chuỗi HTML an toàn (Sử dụng f-string cẩn thận)
    card_html = f"""
    <div style="
        background-color: white; 
        padding: 20px; 
        border-radius: 15px; 
        border-left: 8px solid #FF9800; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.1); 
        margin-bottom: 20px;
    ">
        <div style="color: #666; font-size: 0.85rem;">Mã Serial sản phẩm</div>
        <div style="color: #FF9800; font-size: 1.3rem; font-weight: bold; margin-bottom: 12px;">{serial_no}</div>
        
        <div style="color: #666; font-size: 0.85rem;">Tên khách hàng</div>
        <div style="color: #1f1f1f; font-size: 1.1rem; font-weight: bold; margin-bottom: 12px;">{customer}</div>
        
        <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
            <div style="width: 48%;">
                <div style="color: #666; font-size: 0.85rem;">Ngày mua</div>
                <div style="color: #1f1f1f; font-weight: 600;">{buy_date}</div>
            </div>
            <div style="width: 48%;">
                <div style="color: #666; font-size: 0.85rem;">Hết hạn</div>
                <div style="color: #1f1f1f; font-weight: 600;">{exp_date}</div>
            </div>
        </div>
        
        <div style="color: #666; font-size: 0.85rem; margin-bottom: 4px;">Trạng thái</div>
        <span style="
            color: {status_color}; 
            background-color: {status_bg}; 
            padding: 5px 12px; 
            border-radius: 6px; 
            font-weight: bold; 
            font-size: 0.9rem;
        ">
            {status_text}
        </span>
    </div>
    """
    
    # HIỂN THỊ HTML RA MÀN HÌNH
    st.markdown(card_html, unsafe_allow_html=True)

    # Nút bấm tương tác dưới Card
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🔍 Tra mã khác", use_container_width=True):
            st.session_state.search_done = False
            st.rerun()
    with col_b:
        st.link_button("📞 Gọi hỗ trợ", "tel:0903736414", type="primary", use_container_width=True)
