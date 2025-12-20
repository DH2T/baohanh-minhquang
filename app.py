import streamlit as st
import pandas as pd
import gspread
from streamlit_qrcode_scanner import qrcode_scanner

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="Tra Cứu Bảo Hành - Biến Áp Minh Quang", page_icon="⚡")
st.title("⚡ TRA CỨU BẢO HÀNH")

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

# --- 3. NHẬN DIỆN THÔNG TIN (QR & URL) ---

# A. Lấy mã QR từ Camera (Quét tự động)
#with st.expander("📷 Mở Camera quét mã QR", expanded=True):
    #qr_code_value = qrcode_scanner(key='qrcode_scanner')

# B. Lấy mã Serial từ Link URL (Nếu khách truy cập từ link có ?serial=...)
url_params = st.query_params
url_serial = url_params.get("serial", "")

# C. Quyết định giá trị hiển thị trong ô nhập liệu
# Thứ tự ưu tiên: 1. Vừa quét được > 2. Có sẵn trên Link > 3. Trống
#if qr_code_value:
    #initial_value = qr_code_value
if url_serial:
    initial_value = url_serial
else:
    initial_value = ""

# --- 4. GIAO DIỆN TRA CỨU ---
search_query = st.text_input(
    "Nhập Số Serial / Quét Mã QR:", 
    value=initial_value,
    placeholder="Đưa camera vào mã QR hoặc nhập tay tại đây..."
).strip()

# --- 5. HIỂN THỊ KẾT QUẢ ---
if search_query:
    if not df.empty:
        # Tìm kiếm trong danh sách
        result = df[df['Serial'] == search_query]
        
        if not result.empty:
            st.success(f"✅ Tìm thấy thông tin bảo hành cho mã: {search_query}")
            st.divider()
            
            data = result.iloc[0]
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Tên Khách Hàng", data.get('Ten_Khach_Hang', 'N/A'))
                st.metric("Ngày Mua", str(data.get('Ngay_Mua', 'N/A')))
            
            with col2:
                st.metric("Trạng Thái", data.get('Trang_Thai', 'N/A'))
                st.metric("Ngày Hết Hạn", str(data.get('Ngay_Het_Han', 'N/A')))
            
            st.divider()
            st.info("💡 Hotline hỗ trợ kỹ thuật: 0903.736.414")
            st.link_button("📞 Gọi ngay cho chúng tôi", "tel:0903736414")
        else:
            st.error(f"❌ Không tìm thấy mã máy '{search_query}' trong hệ thống.")
    else:
        st.warning("Dữ liệu chưa sẵn sàng. Vui lòng thử lại sau.")

# Nút quay lại website chính ở thanh bên
st.sidebar.page_link("https://bienapminhquang.com", label="Quay lại Website", icon="🏠")



