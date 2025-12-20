import streamlit as st
import pandas as pd
import gspread
from streamlit_qrcode_scanner import qrcode_scanner
from urllib.parse import urlparse, parse_qs

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="Tra Cứu Bảo Hành - Biến Áp Minh Quang", page_icon="⚡")

# Hàm xử lý để lấy Serial từ chuỗi (hỗ trợ cả link URL và mã thô)
def extract_serial(input_string):
    if not input_string:
        return ""
    if "http" in input_string:
        try:
            parsed_url = urlparse(input_string)
            captured_params = parse_qs(parsed_url.query)
            # Lấy giá trị của tham số 'serial', nếu không có thì lấy toàn bộ chuỗi
            return captured_params.get("serial", [input_string])[0]
        except:
            return input_string
    return input_string

# --- 2. KẾT NỐI DỮ LIỆU ---
SHEET_ID = "1RSgJ18oLmNkK2oL-pImYGLLiPBwENaXSG2_XDc-_pPk"
SHEET_NAME = "SerialNumber"

@st.cache_data(ttl=300)
def load_data_securely():
    try:
        creds = st.secrets["gservice_account"]
        gc = gspread.service_account_from_dict(creds)
        worksheet = gc.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)
        df['Serial'] = df['Serial'].astype(str).str.strip()
        return df
    except Exception as e:
        st.error(f"Lỗi kết nối dữ liệu: {e}")
        return pd.DataFrame()

df = load_data_securely()

# --- 3. QUẢN LÝ TRẠNG THÁI ---
# Khởi tạo giá trị ban đầu nếu chưa có
if "search_done" not in st.session_state:
    st.session_state.search_done = False

# --- 4. NHẬN DIỆN THÔNG TIN ---
url_params = st.query_params
url_serial = url_params.get("serial", "")

# Giao diện quét/nhập (Chỉ hiện khi chưa tìm thấy hoặc nhấn tìm lại)
if not st.session_state.search_done:
    st.title("⚡ TRA CỨU BẢO HÀNH")
    
    with st.expander("📷 Mở Camera quét mã QR", expanded=True):
        raw_qr = qrcode_scanner(key='qrcode_scanner')
    
    # Xử lý chuỗi quét được hoặc từ URL
    processed_qr = extract_serial(raw_qr)
    initial_value = processed_qr if processed_qr else extract_serial(url_serial)

    search_query = st.text_input(
        "Nhập Số Serial / Quét Mã QR:", 
        value=initial_value,
        placeholder="Đưa camera vào mã QR hoặc nhập tay tại đây..."
    ).strip()

    if search_query:
        # Kiểm tra dữ liệu
        result = df[df['Serial'] == search_query] if not df.empty else pd.DataFrame()
        
        if not result.empty:
            st.session_state.search_done = True
            st.session_state.current_result = result.iloc[0]
            st.session_state.current_query = search_query
            st.rerun() # Làm mới để ẩn camera
        else:
            st.error(f"❌ Không tìm thấy mã máy '{search_query}'")

# --- 5. HIỂN THỊ KẾT QUẢ (Giao diện sạch sẽ) ---
if st.session_state.search_done:
    data = st.session_state.current_result
    
    st.success(f"✅ THÔNG TIN BẢO HÀNH: {st.session_state.current_query}")
    
    # Hiển thị dạng Card hoặc Columns
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Khách hàng:**\n### {data.get('Ten_Khach_Hang', 'N/A')}")
        st.caption(f"Ngày mua: {data.get('Ngay_Mua', 'N/A')}")
    
    with col2:
        status = data.get('Trang_Thai', 'N/A')
        color = "green" if "Hành" in status else "red"
        st.markdown(f"**Trạng thái:**\n### :{color}[{status}]")
        st.caption(f"Hết hạn: {data.get('Ngay_Het_Han', 'N/A')}")

    st.divider()
    
    # Nút bấm hành động
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🔍 Tra cứu mã khác", use_container_width=True):
            st.session_state.search_done = False
            st.rerun()
    with col_btn2:
        st.link_button("📞 Gọi hỗ trợ: 0903.736.414", "tel:0903736414", type="primary", use_container_width=True)

# Nút quay lại website chính ở thanh bên
st.sidebar.page_link("https://bienapminhquang.com", label="Quay lại Website", icon="🏠")
