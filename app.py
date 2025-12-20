import streamlit as st
import pandas as pd
import gspread
from streamlit_qrcode_scanner import qrcode_scanner
from urllib.parse import urlparse, parse_qs

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="Bảo Hành - Biến Áp Minh Quang", page_icon="⚡")

# --- 2. PHẦN GIAO DIỆN (CSS) - TÁCH RIÊNG ĐỂ TRÁNH LỖI NGOẶC ---
# Chuỗi này KHÔNG có chữ 'f' ở đầu để tránh lỗi xung đột với Python
style_css = """
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding-top: 2rem;}

    .warranty-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        border-left: 8px solid #FF9800;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .card-label { color: #888; font-size: 0.8rem; text-transform: uppercase; margin-bottom: 2px; }
    .card-value { color: #1f1f1f; font-size: 1.1rem; font-weight: bold; margin-bottom: 12px; }
    .card-serial { color: #FF9800; font-size: 1.4rem; font-weight: bold; margin-bottom: 15px; }
    
    .status-badge {
        padding: 5px 12px;
        border-radius: 6px;
        font-weight: bold;
        font-size: 0.9rem;
        display: inline-block;
    }
    .status-valid { background-color: #e8f5e9; color: #2e7d32; }
    .status-expired { background-color: #ffebee; color: #d32f2f; }
</style>
"""
st.markdown(style_css, unsafe_allow_html=True)

# --- 3. CÁC HÀM HỖ TRỢ ---
def extract_serial(input_string):
    if not input_string: return ""
    if "http" in input_string:
        try:
            parsed_url = urlparse(input_string)
            return parse_qs(parsed_url.query).get("serial", [input_string.split('/')[-1]])[0]
        except: return input_string
    return input_string

@st.cache_data(ttl=300)
def load_data():
    try:
        creds = st.secrets["gservice_account"]
        gc = gspread.service_account_from_dict(creds)
        df = pd.DataFrame(gc.open_by_key("1RSgJ18oLmNkK2oL-pImYGLLiPBwENaXSG2_XDc-_pPk").worksheet("SerialNumber").get_all_records())
        df['Serial'] = df['Serial'].astype(str).str.strip()
        return df
    except: return pd.DataFrame()

df = load_data()

# --- 4. QUẢN LÝ TRẠNG THÁI ---
if "search_done" not in st.session_state:
    st.session_state.search_done = False

# --- 5. GIAO DIỆN CHÍNH ---

if not st.session_state.search_done:
    st.markdown("<h2 style='text-align: center; color: #FF9800;'>⚡ BIẾN ÁP MINH QUANG</h2>", unsafe_allow_html=True)
    
    with st.expander("📷 Nhấn để mở Camera quét mã QR", expanded=True):
        qr_raw = qrcode_scanner(key='qrcode_scanner')
    
    url_serial = st.query_params.get("serial", "")
    processed_qr = extract_serial(qr_raw)
    initial_val = processed_qr if processed_qr else extract_serial(url_serial)

    search_query = st.text_input("Hoặc nhập mã Serial:", value=initial_val).strip()

    if search_query:
        if not df.empty:
            res = df[df['Serial'] == search_query]
            if not res.empty:
                st.session_state.search_done = True
                st.session_state.current_res = res.iloc[0]
                st.session_state.current_query = search_query
                st.rerun()
            else:
                st.error(f"❌ Không tìm thấy mã: {search_query}")
else:
    # MÀN HÌNH KẾT QUẢ
    data = st.session_state.current_res
    status_text = data.get('Trang_Thai', 'N/A')
    # Kiểm tra trạng thái để gán màu
    status_class = "status-valid" if "Hành" in status_text else "status-expired"
    
    st.markdown("<h3 style='text-align: center;'>THÔNG TIN BẢO HÀNH</h3>", unsafe_allow_html=True)

    # Sử dụng HTML đơn giản, gọi các class đã định nghĩa ở style_css
    card_html = f"""
    <div class="warranty-card">
        <div class="card-label">Mã Serial sản phẩm</div>
        <div class="card-serial">{st.session_state.current_query}</div>
        
        <div class="card-label">Tên khách hàng</div>
        <div class="card-value">{data.get('Ten_Khach_Hang', 'N/A')}</div>
        
        <div style="display: flex; justify-content: space-between;">
            <div style="width: 48%;">
                <div class="card-label">Ngày mua</div>
                <div class="card-value" style="font-size: 1rem;">{data.get('Ngay_Mua', 'N/A')}</div>
            </div>
            <div style="width: 48%;">
                <div class="card-label">Hết hạn</div>
                <div class="card-value" style="font-size: 1rem;">{data.get('Ngay_Het_Han', 'N/A')}</div>
            </div>
        </div>
        
        <div class="card-label" style="margin-top: 10px;">Trạng thái hệ thống</div>
        <div class="status-badge {status_class}">{status_text}</div>
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)

    # Các nút bấm bên dưới thẻ
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔍 Tra cứu mã khác", use_container_width=True):
            st.session_state.search_done = False
            st.rerun()
    with col2:
        st.link_button("📞 Gọi hỗ trợ", "tel:0903736414", type="primary", use_container_width=True)

# Thanh bên
st.sidebar.page_link("https://bienapminhquang.com", label="Quay lại Website", icon="🏠")
