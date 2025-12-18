import streamlit as st
import pandas as pd
import gspread # Thêm thư viện gspread

# Cấu hình trang (giữ nguyên)
st.set_page_config(page_title="Tra Cứu Bảo Hành - Biến Áp Minh Quang", page_icon="⚡")
st.title("TRA CỨU BH")

# ID của Google Sheet (Lấy từ URL, ví dụ: https://docs.google.com/spreadsheets/d/ID_CUA_SHEET_O_DAY/edit)
SHEET_ID = "1RSgJ18oLmNkK2oL-pImYGLLiPBwENaXSG2_XDc-_pPk"
SHEET_NAME = "Serial Number" # Tên của sheet chứa dữ liệu

@st.cache_data(ttl=600) # Dữ liệu được cache và tự động tải lại sau 600 giây (10 phút)
def load_data_securely():
    try:
        # --- BƯỚC XÁC THỰC BẢO MẬT ---
        # Đọc thông tin xác thực từ Streamlit Secrets
        creds = st.secrets["gservice_account"]
        gc = gspread.service_account_from_dict(creds)
        
        # Mở Sheet và Worksheet
        worksheet = gc.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
        
        # Lấy tất cả dữ liệu và chuyển thành DataFrame
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)
        
        # Chuyển đổi cột Mã Máy sang dạng chuỗi
        df['SerialNumber'] = df['SerialNumber'].astype(str)
        return df

    except Exception as e:
        st.error(f"Lỗi bảo mật hoặc kết nối dữ liệu: {e}. Vui lòng kiểm tra lại Google Sheet ID và Service Account.")
        return pd.DataFrame() # Trả về DataFrame rỗng nếu thất bại

# Gọi hàm tải dữ liệu bảo mật
df = load_data_securely()

# --- Phần giao diện tra cứu (Giữ nguyên) ---
if not df.empty:
    search_query = st.text_input("Nhập Số Serial / Quét Mã QR (Dán trên Biến Áp):", "")
    
    if st.button("Tra cứu ngay"):
        if search_query:
            # Tìm kiếm (Thêm .str.strip() để loại bỏ khoảng trắng thừa)
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
                
                st.info("Nếu cần hỗ trợ kỹ thuật, vui lòng liên hệ hotline: 0903736414")
            else:
                st.error("❌ Không tìm thấy mã máy này trong hệ thống. Vui lòng kiểm tra lại.")
        else:
            st.warning("Vui lòng nhập Số Serial để tra cứu.")











