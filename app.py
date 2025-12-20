import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="Bảo Hành Minh Quang", page_icon="⚡", layout="centered")

# CSS làm đẹp giao diện Mobile
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .warranty-card {
        background-color: white;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        text-align: center;
        border-top: 5px solid #007bff;
        margin-top: 20px;
    }
    .product-title { 
        color: #2c3e50; 
        font-weight: 800; 
        font-size: 1.4rem; 
        margin-bottom: 5px; 
    }
    .serial-badge {
        background-color: #e9ecef;
        color: #495057;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 15px;
    }
    .status-box {
        font-size: 1.2rem;
        font-weight: bold;
        padding: 10px;
        border-radius: 8px;
        margin: 15px 0;
    }
    .status-ok { background-color: #d4edda; color: #155724; }
    .status-fail { background-color: #f8d7da; color: #721c24; }
    .info-row {
        display: flex;
        justify-content: space-between;
        border-bottom: 1px dashed #dee2e6;
        padding: 8px 0;
        text-align: left;
    }
    .info-label { color: #6c757d; font-weight: 500; }
    .info-value { color: #212529; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# --- 2. HÀM KẾT NỐI GOOGLE SHEETS ---
@st.cache_data(ttl=60) # Tự động cập nhật dữ liệu sau mỗi 60 giây
def load_data():
    # Tạo kết nối
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Đọc dữ liệu từ Sheet có tên chính xác là "Serial Number"
    # Dùng usecols để chỉ lấy các cột cần thiết nhằm tăng tốc độ
    # Cột A=0, B=1, F=5, G=6, H=7, I=8, J=9
    df = conn.read(
        worksheet="Serial Number",
        usecols=[1, 5, 6, 7, 8, 9], 
        header=0  # Hàng đầu tiên là tiêu đề
    )
    
    # Đảm bảo cột SerialNumber là dạng chuỗi để so sánh chính xác
    df['SerialNumber'] = df['SerialNumber'].astype(str)
    return df

# --- 3. XỬ LÝ LOGIC ---
st.image("https://bienapminhquang.com/wp-content/uploads/2023/your-logo.png", width=120)
st.title("Tra Cứu Bảo Hành")

# Lấy tham số ID từ QR Code (URL)
query_params = st.query_params
search_serial = query_params.get("id", "")

# Nếu không có QR thì hiện ô nhập tay
if not search_serial:
    search_serial = st.text_input("Nhập số Serial:", placeholder="VD: 2412001").strip()

if search_serial:
    try:
        with st.spinner('Đang tìm dữ liệu...'):
            df = load_data()
            
            # Lọc dữ liệu theo cột F (SerialNumber)
            # Dùng strip() để xóa khoảng trắng thừa nếu có
            result = df[df['SerialNumber'].str.strip() == search_serial]

        if not result.empty:
            # Lấy dòng dữ liệu đầu tiên tìm thấy
            item = result.iloc[0]
            
            # Gán biến từ các cột (Lưu ý: Tên cột phải khớp chính xác trong Sheet)
            prod_name = item.get('ProductID', 'Sản phẩm Minh Quang') # Cột B
            cust_name = item.get('Ten_Khach_Hang', 'Khách lẻ')       # Cột G
            date_buy = item.get('Ngay_Mua', '---')                   # Cột H
            date_end = item.get('Ngay_Het_Han', '---')               # Cột I
            status = item.get('Trang_Thai', '')                      # Cột J

            # Xác định màu sắc trạng thái
            # Giả sử cột Trang_Thai bạn ghi là "Còn hạn" hoặc "Hết hạn"
            # Hoặc Logic: Nếu ngày hết hạn > ngày nay
            status_class = "status-ok"
            icon = "✅"
            if "hết" in str(status).lower() or "expired" in str(status).lower():
                status_class = "status-fail"
                icon = "⚠️"

            # --- 4. HIỂN THỊ KẾT QUẢ ---
            html = f"""
            <div class="warranty-card">
                <div class="product-title">{prod_name}</div>
                <div class="serial-badge">S/N: {search_serial}</div>
                
                <div class="status-box {status_class}">
                    {icon} {status}
                </div>

                <div class="info-row">
                    <span class="info-label">Khách hàng:</span>
                    <span class="info-value">{cust_name}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Ngày mua:</span>
                    <span class="info-value">{date_buy}</span>
                </div>
                <div class="info-row" style="border-bottom: none;">
                    <span class="info-label">Hết hạn BH:</span>
                    <span class="info-value" style="color: #d63384;">{date_end}</span>
                </div>
            </div>
            """
            st.markdown(html, unsafe_allow_html=True)
            
            st.caption("Cảm ơn quý khách đã tin dùng sản phẩm Biến áp Minh Quang.")
            
            # Nút liên hệ nhanh
            c1, c2 = st.columns(2)
            c1.link_button("🌐 Website", "https://bienapminhquang.com", use_container_width=True)
            c2.link_button("💬 Zalo Hỗ Trợ", "https://zalo.me/YOUR_PHONE_NUMBER", use_container_width=True)

        else:
            st.error(f"❌ Không tìm thấy thông tin cho Serial: **{search_serial}**")
            st.warning("Vui lòng kiểm tra lại mã trên tem hoặc liên hệ bộ phận CSKH.")

    except Exception as e:
        st.error("⚠️ Có lỗi kết nối dữ liệu. Vui lòng thử lại sau.")
        # Dòng dưới này chỉ hiện khi bạn debug, khách hàng không nên thấy lỗi chi tiết
        # st.code(e)
