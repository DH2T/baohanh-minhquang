import streamlit as st
import pandas as pd
import gspread
from streamlit_qrcode_scanner import qrcode_scanner
from urllib.parse import urlparse, parse_qs

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="Bảo Hành - Biến Áp Minh Quang", page_icon="⚡")

# --- 2. TÁCH RIÊNG PHẦN GIAO DIỆN (CSS) ---
# Đưa toàn bộ định dạng vào đây để không bị lỗi xung đột code
st.markdown("""
    <style>
    /* Ẩn các thành phần thừa */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Định dạng Thẻ Bảo Hành */
    .warranty-card {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 15px;
        border-left: 10px solid #FF9800;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-top: 10px;
        margin-bottom: 20px;
        color: #333333;
    }
    .label { color: #888888; font-size: 0.8rem; text-transform: uppercase; margin-bottom: 2px; }
    .value { color: #1f1f1f; font-size: 1.2rem; font-weight: bold; margin-bottom: 15px; }
    .serial { color: #FF9800; font-size: 1.5rem; font-weight: bold; margin-bottom: 15px; }
    
    /* Trạng thái */
    .status-box {
        padding: 6px 15px;
        border-radius: 8px;
        font-weight: bold;
        display: inline-block;
    }
    .valid { background-color: #e8f5e9; color: #2e7d32; }
    .expired { background-color: #ffebee; color: #d32f2f; }
    </style>
    """, unsafe_allow_html=True)

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

# --- 4. XỬ LÝ TRẠNG THÁI ---
if "search_done" not in st.session_state:
    st.session_state.search_done = False

# --- 5. GIAO DIỆN CHÍNH ---

if not st.session_state.search_done:
    # MÀN HÌNH CHỜ QUÉT
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
    # MÀN HÌNH HIỂN THỊ THẺ (DÙNG CLASS CSS ĐÃ KHAI BÁO Ở TRÊN)
    data = st.session_state.current_res
    status_text = data.get('Trang_Thai', 'N/A')
    status_class = "valid" if "Hành" in status_text else "expired"
    
    st.markdown("<h3 style='text-align: center;'>THÔNG TIN BẢO HÀNH</h3>", unsafe_allow_html=True)

    # HTML sạch sẽ, chỉ chứa dữ liệu, không chứa dấu ngoặc CSS
    card_html = f"""
    <div class="warranty-card">
        <div class="label">Mã Serial sản phẩm</div>
        <div class="serial">{st.session_state.current_query}</div>
        
        <div class="label">Tên khách hàng</div>
        <div class="value">{data.get('Ten_Khach_Hang', 'N/A')}</div>
        
        <div style="display: flex; justify-content: space-between;">
            <div>
                <div class="label">Ngày mua</div>
                <div class="value" style="font-size: 1rem;">{data.get('Ngay_Mua', 'N/A')}</div>
            </div>
            <div>
                <div class="label">Hết hạn</div>
                <div class="value" style="font-size: 1rem;">{data.get('Ngay_Het_Han', 'N/A')}</div>
            </div>
        </div>
        
        <div class="label">Trạng thái bảo hành</div>
        <div class="status-box {status_class}">{status_text}</div>
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)

    # Nút bấm
    if st.button("🔍 Tra cứu mã khác", use_container_width=True):
        st.session_state.search_done = False
        st.rerun()
    
    st.link_button("📞 Gọi hỗ trợ kỹ thuật", "tel:0903736414", type="primary", use_container_width=True)

# Thanh bên
st.sidebar.page_link("https://bienapminhquang.com", label="Quay lại Website", icon="🏠")
