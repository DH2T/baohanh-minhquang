import streamlit as st
import pandas as pd
import gspread # Thêm thư viện gspread

# Cấu hình trang (giữ nguyên)
st.set_page_config(page_title="Tra Cứu Bảo Hành - Biến Áp Minh Quang", page_icon="⚡")
st.title("Hệ Thống Tra Cứu Bảo Hành Điện Tử")

# ID của Google Sheet (Lấy từ URL, ví dụ: https://docs.google.com/spreadsheets/d/ID_CUA_SHEET_O_DAY/edit)
SHEET_ID = "115NEuESwsu4YeFWlcoLh_1t04_7CdPtGPkMmKvZFSeo"
SHEET_NAME = "dulieu_baohanh" # Tên của sheet chứa dữ liệu

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
        df['Ma_May'] = df['Ma_May'].astype(str)
        return df

    except Exception as e:
        st.error(f"Lỗi bảo mật hoặc kết nối dữ liệu: {e}. Vui lòng kiểm tra lại Google Sheet ID và Service Account.")
        return pd.DataFrame() # Trả về DataFrame rỗng nếu thất bại

# Gọi hàm tải dữ liệu bảo mật
df = load_data_securely()

# --- Phần giao diện tra cứu (Giữ nguyên) ---
if not df.empty:
    search_query = st.text_input("Nhập Số Serial / Mã Máy (ghi trên thân máy):", "")
    
    if st.button("Tra cứu ngay"):
        if search_query:
            # Tìm kiếm (Thêm .str.strip() để loại bỏ khoảng trắng thừa)
            result = df[df['Ma_May'].str.strip() == search_query.strip()] 
            
            if not result.empty:
                st.success("✅ Tìm thấy thông tin bảo hành!")
                # ... (Phần hiển thị kết quả giữ nguyên)
                
            # ... (Phần còn lại của code giữ nguyên)

