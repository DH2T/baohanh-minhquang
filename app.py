import streamlit as st
import pandas as pd

# Cấu hình trang
st.set_page_config(page_title="Tra Cứu Bảo Hành - Biến Áp Minh Quang", page_icon="⚡")

# Tiêu đề và Logo (Bạn có thể chèn link ảnh logo thật của bạn vào)
st.image("https://bienapminhquang.com/wp-content/uploads/2020/06/logo-minh-quang.png", width=200)
st.title("Hệ Thống Tra Cứu Bảo Hành Điện Tử")
st.markdown("---")

# Hàm tải dữ liệu từ Google Sheet (Thay LINK_CUA_BAN bằng link CSV export)
# Để lấy link CSV: Thay đoạn cuối link Google Sheet từ /edit#gid=0 thành /export?format=csv
@st.cache_data
def load_data():
    sheet_id = "115NEuESwsu4YeFWlcoLh_1t04_7CdPtGPkMmKvZFSeo" # Lấy ID từ URL của sheet
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    return pd.read_csv(url)

try:
    df = load_data()
    
    # Chuyển đổi cột dữ liệu sang dạng chuỗi để tìm kiếm chính xác
    df['Ma_May'] = df['Ma_May'].astype(str)

    # Giao diện tìm kiếm
    search_query = st.text_input("Nhập Số Serial / Mã Máy (ghi trên thân máy):", "")
    
    if st.button("Tra cứu ngay"):
        if search_query:
            # Tìm kiếm trong database
            result = df[df['Ma_May'] == search_query]
            
            if not result.empty:
                st.success("✅ Tìm thấy thông tin bảo hành!")
                st.write("---")
                
                # Hiển thị thông tin chi tiết
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Tên Khách Hàng", result.iloc[0]['Ten_Khach_Hang'])
                    st.metric("Ngày Mua", result.iloc[0]['Ngay_Mua'])
                
                with col2:
                    st.metric("Trạng Thái", result.iloc[0]['Trang_Thai'])
                    st.metric("Ngày Hết Hạn", result.iloc[0]['Ngay_Het_Han'])
                
                st.info("Nếu cần hỗ trợ kỹ thuật, vui lòng liên hệ hotline: 09xxx...")
            else:
                st.error("❌ Không tìm thấy mã máy này trong hệ thống. Vui lòng kiểm tra lại.")
        else:
            st.warning("Vui lòng nhập mã máy để tra cứu.")

except Exception as e:
    st.error(f"Lỗi kết nối dữ liệu. Vui lòng thử lại sau. ({e})")

# Footer
st.markdown("---")
st.caption("© 2024 Biến Áp Minh Quang. All Rights Reserved.")
