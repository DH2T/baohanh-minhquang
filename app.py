import streamlit as st
import pandas as pd
import gspread
from streamlit_qrcode_scanner import qrcode_scanner # Thư viện mới

st.set_page_config(page_title="Tra Cứu Bảo Hành - Biến Áp Minh Quang", page_icon="⚡")
st.title("⚡ TRA CỨU BẢO HÀNH")

SHEET_ID = "1RSgJ18oLmNkK2oL-pImYGLLiPBwENaXSG2_XDc-_pPk"
SHEET_NAME = "Serial Number"

@st.cache_data(ttl=600)
def load_data_securely():
    try:
        creds = st.secrets["gservice_account"]
        gc = gspread.service_account_from_dict(creds)
        worksheet = gc.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)
        df['SerialNumber'] = df['SerialNumber'].astype(str)
        return df
    except Exception as e:
        st.error(f"Lỗi kết nối: {e}")
        return pd.DataFrame()

df = load_data_securely()

# --- PHẦN QUÉT MÃ QR ---
st.subheader("Quét mã QR tại đây")
# QR_code_scanner sẽ trả về chuỗi văn bản sau khi quét thành công
qr_code_value = qrcode_scanner(key='qrcode_scanner')

# --- PHẦN GIAO DIỆN TRA CỨU ---
if not df.empty:
    # Nếu quét được QR, giá trị đó sẽ được mặc định điền vào text_input
    search_query = st.text_input(
        "Số Serial (Tự động điền khi quét QR):", 
        value=qr_code_value if qr_code_value else ""
    )
    
    # Logic tự động kích hoạt tra cứu nếu có search_query
    if search_query:
        result = df[df['SerialNumber'].str.strip() == search_query.strip()] 
        
        if not result.empty:
            st.success("✅ Tìm thấy thông tin bảo hành!")
            st.write("---")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Tên Khách Hàng", result.iloc[0]['Ten_Khach_Hang'])
                st.metric("Ngày Mua", result.iloc[0]['Ngay_Mua'])
            
            with col2:
                st.metric("Trạng Thái", result.iloc[0]['Trang_Thai'])
                st.metric("Ngày Hết Hạn", result.iloc[0]['Ngay_Het_Han'])
            
            st.info("Hotline hỗ trợ: 0903736414")
        else:
            st.error("❌ Không tìm thấy mã máy này.")
