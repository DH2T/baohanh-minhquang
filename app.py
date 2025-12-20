import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Minh Quang Test")

st.title("Kiểm tra kết nối")

try:
    # 1. Khởi tạo kết nối
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # 2. Đọc dữ liệu (Thử đọc sheet đầu tiên, không chỉ định tên để tránh lỗi chính tả)
    df = conn.read() 
    
    st.success("Chúc mừng! Đã kết nối thành công với Google Sheet.")
    
    # 3. Hiển thị thử 5 dòng đầu
    st.write("Dữ liệu tìm thấy:")
    st.dataframe(df.head())

except Exception as e:
    st.error("Vẫn còn lỗi kết nối!")
    st.info("Cách xử lý: Bạn hãy kiểm tra đã nhấn 'Share' Google Sheet ở chế độ 'Anyone with the link' chưa?")
    st.exception(e) # Dòng này sẽ hiện chi tiết lỗi kỹ thuật để ta xử lý tiếp
