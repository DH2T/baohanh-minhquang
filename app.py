import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Cấu hình trang
st.set_page_config(page_title="Bảo Hành Minh Quang", page_icon="⚡")

# --- HÀM TẢI DỮ LIỆU ---
@st.cache_data(ttl=10) # Để 10 giây để bạn cập nhật Sheet là web thấy ngay
def load_data():
    conn = st.connection("gsheets", type=GSheetsConnection)
    # Đọc toàn bộ Sheet để tránh lỗi lệch cột
    df = conn.read(worksheet="SerialNumber")
    return df

# --- XỬ LÝ LẤY MÃ TỪ LINK QR ---
# Sửa lỗi: Streamlit bản mới dùng st.query_params thay cho query_params()
if "id" in st.query_params:
    st.session_state.serial_input = st.query_params["id"]

st.title("Tra Cứu Bảo Hành")

# Ô nhập mã (Nếu có id từ QR nó sẽ tự điền vào đây)
search_serial = st.text_input(
    "Nhập số Serial:", 
    value=st.session_state.get("serial_input", ""),
    key="main_input"
).strip()

if search_serial:
    df = load_data()
    
    # CHỈNH SỬA QUAN TRỌNG: 
    # Ép kiểu cột SerialNumber về chuỗi và xóa khoảng trắng để so sánh chính xác
    df['SerialNumber'] = df['SerialNumber'].astype(str).str.strip()
    
    # Tìm kiếm
    result = df[df['SerialNumber'] == str(search_serial)]

    if not result.empty:
        item = result.iloc[0]
        # Hiển thị kết quả (Dùng bảng đơn giản để chắc chắn không lỗi giao diện)
        st.success(f"Tìm thấy thông tin cho mã: {search_serial}")
        
        st.write(f"**Sản phẩm:** {item['ProductID']}")
        st.write(f"**Khách hàng:** {item['Ten_Khach_Hang']}")
        st.write(f"**Hạn bảo hành:** {item['Ngay_Het_Han']}")
        st.write(f"**Trạng thái:** {item['Trang_Thai']}")
    else:
        st.error(f"Không tìm thấy mã: {search_serial}")
        # Dòng này để bạn kiểm tra xem dữ liệu trong Sheet đang load lên là gì
        with st.expander("Nhấn vào đây để xem danh sách mã đang có trong hệ thống"):
            st.write(df['SerialNumber'].tolist())

