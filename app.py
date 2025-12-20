import streamlit as st
import pandas as pd
import gspread
from streamlit_qrcode_scanner import qrcode_scanner
from urllib.parse import urlparse, parse_qs

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="Bảo Hành - Biến Áp Minh Quang", page_icon="⚡")

# --- 2. ẨN HOÀN TOÀN CÁC THÀNH PHẦN MẶC ĐỊNH (CSS SIÊU SẠCH) ---
st.markdown("""
    <style>
    /* Ẩn dấu 3 chấm góc trên bên phải */
    #MainMenu {visibility: hidden;}
    
    /* Ẩn dòng chữ Hosted with Streamlit ở dưới cùng bên phải */
    footer {visibility: hidden;}
    
    /* Ẩn thanh header màu trắng phía trên cùng */
    header {visibility: hidden;}
    
    /* Giảm bớt khoảng trắng ở phía trên màn hình cho đẹp */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)
# --- 2. KẾT NỐI DỮ LIỆU ---
@st.cache_data(ttl=300)
def load_data():
    try:
        creds = st.secrets["gservice_account"]
        gc = gspread.service_account_from_dict(creds)
        # Thay ID Sheet của bạn vào đây
        sh = gc.open_by_key("1RSgJ18oLmNkK2oL-pImYGLLiPBwENaXSG2_XDc-_pPk")
        df = pd.DataFrame(sh.worksheet("SerialNumber").get_all_records())
        df['Serial'] = df['Serial'].astype(str).str.strip()
        return df
    except Exception as e:
        st.error(f"Lỗi kết nối: {e}")
        return pd.DataFrame()

df = load_data()

# --- 3. XỬ LÝ CHUỖI QR ---
def get_serial(text):
    if not text: return ""
    if "http" in text:
        try:
            return parse_qs(urlparse(text).query).get("serial", [text.split('/')[-1]])[0]
        except: return text
    return text

# --- 4. GIAO DIỆN CHÍNH ---

# Dùng Session State để chuyển màn hình
if "found" not in st.session_state:
    st.session_state.found = False

if not st.session_state.found:
    st.header("⚡ TRA CỨU BẢO HÀNH")
    st.write("Biến Áp Minh Quang")
    
    # Khu vực Quét QR
    with st.expander("📷 MỞ CAMERA QUÉT MÃ", expanded=True):
        scanned_val = qrcode_scanner(key='scanner')
    
    # Lấy Serial từ URL nếu có
    url_val = st.query_params.get("serial", "")
    
    # Ưu tiên mã quét được -> mã từ URL
    input_default = get_serial(scanned_val) if scanned_val else get_serial(url_val)
    
    query = st.text_input("Mã Số Serial:", value=input_default, placeholder="Nhập hoặc quét mã...")

    if query:
        if not df.empty:
            match = df[df['Serial'] == query]
            if not match.empty:
                st.session_state.found = True
                st.session_state.data = match.iloc[0]
                st.session_state.query_id = query
                st.rerun()
            else:
                st.error(f"Không tìm thấy mã: {query}")
else:
    # MÀN HÌNH KẾT QUẢ (DÙNG THÀNH PHẦN CHUẨN)
    st.success(f"THÔNG TIN BẢO HÀNH: {st.session_state.query_id}")
    
    # Tạo khung bao quanh thông tin
    with st.container(border=True):
        st.subheader(st.session_state.data.get('Ten_Khach_Hang', 'Khách hàng mới'))
        st.divider()
        
        c1, c2 = st.columns(2)
        c1.metric("Ngày mua", str(st.session_state.data.get('Ngay_Mua', 'N/A')))
        c2.metric("Hết hạn", str(st.session_state.data.get('Ngay_Het_Han', 'N/A')))
        
        status = st.session_state.data.get('Trang_Thai', 'N/A')
        if "CÒN" in status:
            st.info(f"✅ Trạng thái: {status}")
        else:
            st.error(f"❌ Trạng thái: {status}")

    st.write("") # Khoảng cách
    
    # Nút bấm hành động
    if st.button("🔍 Tra cứu mã khác", use_container_width=True, type="secondary"):
        st.session_state.found = False
        st.rerun()
        
    st.link_button("📞 Gọi hỗ trợ: 0903.736.414", "tel:0903736414", use_container_width=True, type="primary")

# Sidebar
st.sidebar.page_link("https://bienapminhquang.com", label="Quay lại Website", icon="🏠")



