import streamlit as st
import pandas as pd
import gspread
import cv2
import numpy as np

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="Tra Cứu Bảo Hành - Biến Áp Minh Quang", page_icon="⚡", layout="centered")

# CSS tùy chỉnh để giao diện chuyên nghiệp hơn
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .main-card { background-color: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
    .status-box { padding: 10px; border-radius: 8px; text-align: center; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- KẾT NỐI DỮ LIỆU ---
SHEET_ID = "1RSgJ18oLmNkK2oL-pImYGLLiPBwENaXSG2_XDc-_pPk"
SHEET_NAME = "Serial Number"

@st.cache_data(ttl=300)
def load_data():
    try:
        creds = st.secrets["gservice_account"]
        gc = gspread.service_account_from_dict(creds)
        worksheet = gc.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)
        df['SerialNumber'] = df['SerialNumber'].astype(str).str.strip()
        return df
    except Exception as e:
        st.error(f"Lỗi kết nối dữ liệu: {e}")
        return pd.DataFrame()

df = load_data()

# --- GIAO DIỆN CHÍNH ---
st.title("⚡ TRA CỨU BẢO HÀNH")
st.write("CÔNG TY BIẾN ÁP MINH QUANG")

# Bước 1: Quét mã QR
st.markdown("### 📷 Bước 1: Quét mã QR")
qr_img = st.camera_input("Đưa camera vào mã QR dán trên máy và nhấn Chụp")

qr_result = ""
if qr_img:
    # Chuyển đổi ảnh chụp sang định dạng OpenCV
    file_bytes = np.asarray(bytearray(qr_img.read()), dtype=np.uint8)
    opencv_image = cv2.imdecode(file_bytes, 1)
    
    # Giải mã QR
    detector = cv2.QRCodeDetector()
    data, points, _ = detector.detectAndDecode(opencv_image)
    
    if data:
        qr_result = data
        st.success(f"Đã nhận diện mã: {qr_result}")
    else:
        st.warning("Không tìm thấy mã QR. Hãy thử chụp lại rõ nét hơn.")

# Bước 2: Hiển thị kết quả
st.markdown("---")
st.markdown("### 🔍 Bước 2: Kết quả tra cứu")

# Lấy tham số từ URL nếu có (dành cho link quét trực tiếp)
url_params = st.query_params
url_serial = url_params.get("serial", "")

# Ô nhập liệu (tự động điền nếu quét được hoặc có trên link)
search_query = st.text_input(
    "Số Serial máy:", 
    value=qr_result if qr_result else url_serial
).strip()

if search_query:
    if not df.empty:
        result = df[df['SerialNumber'] == search_query]
        
        if not result.empty:
            data = result.iloc[0]
            
            with st.container():
                st.markdown('<div class="main-card">', unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Tên Khách Hàng", data['Ten_Khach_Hang'])
                    st.metric("Ngày Mua", str(data['Ngay_Mua']))
                
                with col2:
                    st.metric("Trạng Thái", data['Trang_Thai'])
                    st.metric("Ngày Hết Hạn", str(data['Ngay_Het_Han']))
                
                st.markdown('</div>', unsafe_allow_html=True)
                
            # Nút liên hệ
            st.write("")
            st.info("💡 Nếu thông tin chưa chính xác, vui lòng liên hệ Hotline: 0903736414")
            st.link_button("📞 Gọi hỗ trợ ngay", "tel:0903736414")
        else:
            st.error(f"❌ Không tìm thấy thông tin cho Serial: {search_query}")
    else:
        st.warning("Dữ liệu đang trống, vui lòng kiểm tra Google Sheet.")

# Chân trang
st.markdown("---")
st.caption("© 2024 Biến Áp Minh Quang - Hệ thống tra cứu tự động")
