import streamlit as st
import pandas as pd
import gspread
from streamlit_qrcode_scanner import qrcode_scanner

# Cấu hình trang
st.set_page_config(page_title="Tra Cứu Bảo Hành - Biến Áp Minh Quang", page_icon="⚡", layout="centered")

# CSS để làm giao diện đẹp hơn
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .status-active { color: #28a745; font-weight: bold; }
    .status-expired { color: #dc3545; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("⚡ HỆ THỐNG BẢO HÀNH")
st.info("Hướng dẫn: Đưa camera vào mã QR dán trên thân máy để tra cứu nhanh.")

# --- KẾT NỐI DỮ LIỆU ---
SHEET_ID = "1RSgJ18oLmNkK2oL-pImYGLLiPBwENaXSG2_XDc-_pPk"
SHEET_NAME = "Serial Number"

@st.cache_data(ttl=300)
def load_data():
    try:
        creds = st.secrets["gservice_account"]
        gc = gspread.service_account_from_dict(creds)
        worksheet = gc.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
        df = pd.DataFrame(worksheet.get_all_records())
        df['SerialNumber'] = df['SerialNumber'].astype(str).str.strip()
        return df
    except Exception as e:
        st.error("Không thể kết nối dữ liệu.")
        return pd.DataFrame()

df = load_data()

# --- QUÉT MÃ QR ---
with st.expander("📷 Mở Camera Quét Mã", expanded=True):
    qr_code_value = qrcode_scanner(key='scanner')

# --- TRA CỨU VÀ HIỂN THỊ ---
search_query = st.text_input("Hoặc nhập Số Serial thủ công:", value=qr_code_value if qr_code_value else "")

if search_query:
    result = df[df['SerialNumber'] == search_query.strip()]
    
    if not result.empty:
        data = result.iloc[0]
        st.success(f"✅ Đã tìm thấy Serial: {search_query}")
        
        # Hiển thị thông tin dạng Card
        st.markdown("### 📋 Thông tin chi tiết")
        
        # Chia cột hiển thị
        c1, c2 = st.columns(2)
        with c1:
            st.metric("👤 Khách hàng", data['Ten_Khach_Hang'])
            st.metric("📅 Ngày mua", str(data['Ngay_Mua']))
            
        with c2:
            # Xử lý màu sắc cho trạng thái
            trang_thai = data['Trang_Thai']
            st.metric("🛡️ Trạng thái", trang_thai)
            st.metric("⏳ Hết hạn", str(data['Ngay_Het_Han']))

        # Nút liên hệ nhanh
        st.divider()
        st.markdown(f"""
            <div style="text-align: center;">
                <p>Cần hỗ trợ về sản phẩm này?</p>
                <a href="tel:0903736414" style="background-color: #ff4b4b; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none; font-weight: bold;">
                    📞 Gọi Hotline: 0903 736 414
                </a>
            </div>
        """, unsafe_allow_html=True)
        
    else:
        st.error("❌ Không tìm thấy thông tin cho mã này. Vui lòng thử lại.")
