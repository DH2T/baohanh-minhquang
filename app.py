import streamlit as st
import pandas as pd
import gspread
from streamlit_qrcode_scanner import qrcode_scanner
from urllib.parse import urlparse, parse_qs

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="Bảo Hành - Biến Áp Minh Quang", page_icon="⚡")

# Cách ẩn footer đơn giản nhất (Không dùng dấu ngoặc nhọn trong Python để tránh lỗi)
st.markdown("<style>footer {display: none !important;} #MainMenu {display: none !important;} header {display: none !important;}</style>", unsafe_allow_html=True)

# --- 2. KẾT NỐI DỮ LIỆU ---
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
        st.error(f"Lỗi kết nối: {e}")
        return pd.DataFrame()

df = load_data()

# --- 3. HÀM XỬ LÝ SERIAL ---
def get_serial(text):
    if not text: return ""
    if "http" in text:
        try:
            return parse_qs(urlparse(text).query).get("serial", [text.split('/')[-1]])[0]
        except: return text
    return text

# --- 4. QUẢN LÝ TRẠNG THÁI (SESSION STATE) ---
if "found" not in st.session_state:
    st.session_state.found = False
if "reset_trigger" not in st.session_state:
    st.session_state.reset_trigger = 0

# --- 5. GIAO DIỆN CHÍNH ---

if not st.session_state.found:
    st.header("⚡ TRA CỨU BẢO HÀNH")
    st.write("Biến Áp Minh Quang - CTy DH2T")
    
    # Khu vực Quét QR - Sử dụng reset_trigger để làm mới scanner khi tra mã khác
    with st.expander("📷 MỞ CAMERA QUÉT MÃ", expanded=True):
        scanned_val = qrcode_scanner(key=f'scanner_{st.session_state.reset_trigger}')
    
    # Lấy mã từ URL
    url_val = st.query_params.get("serial", "")
    
    # Xử lý ưu tiên
    input_default = get_serial(scanned_val) if scanned_val else get_serial(url_val)
    
    # Ô nhập liệu
    query = st.text_input("Mã Số Serial:", value=input_default, placeholder="Nhập hoặc quét mã...")

    if query:
        if not df.empty:
            match = df[df['Serial'] == query]
            if not match.empty:
                st.session_state.found = True
                st.session_state.data = match.iloc[0]
                st.session_state.query_id = query
                st.rerun()
            elif scanned_val or query != "": # Chỉ báo lỗi nếu người dùng đã nhập/quét gì đó
                st.error(f"Không tìm thấy mã: {query}")
else:
    # MÀN HÌNH KẾT QUẢ
    data = st.session_state.data
    st.success(f"THÔNG TIN BẢO HÀNH: {st.session_state.query_id}")
    
    with st.container(border=True):
        st.markdown(f"### 👤 {data.get('Ten_Khach_Hang', 'Khách hàng')}")
        st.divider()
        
        col1, col2 = st.columns(2)
        col1.metric("Ngày mua", str(data.get('Ngay_Mua', 'N/A')))
        col2.metric("Hết hạn", str(data.get('Ngay_Het_Han', 'N/A')))
        
        status_raw = str(data.get('Trang_Thai', '')).strip()
        if "còn" in status_raw.lower():
            st.info(f"✅ **TRẠNG THÁI:** {status_raw}")
        else:
            st.error(f"❌ **TRẠNG THÁI:** {status_raw}")

    st.write("")
    
    # NÚT TRA CỨU MÃ KHÁC (Đã sửa lỗi)
    if st.button("🔍 Tra cứu mã khác", use_container_width=True):
        # Reset toàn bộ trạng thái
        st.session_state.found = False
        st.session_state.data = None
        st.session_state.query_id = ""
        st.session_state.reset_trigger += 1 # Thay đổi key của scanner để nó khởi động lại
        st.query_params.clear() # Xóa mã cũ trên thanh địa chỉ URL
        st.rerun()
        
    st.link_button("📞 Gọi hỗ trợ: 0903.736.414", "tel:0903736414", use_container_width=True, type="primary")

st.sidebar.page_link("https://bienapminhquang.com", label="Quay lại Website", icon="🏠")


