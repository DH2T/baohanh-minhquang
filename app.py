import streamlit as st
import pandas as pd
import gspread
from streamlit_qrcode_scanner import qrcode_scanner
from urllib.parse import urlparse, parse_qs

# --- 1. CẤU HÌNH TRANG & ẨN GIAO DIỆN THỪA ---
st.set_page_config(
    page_title="Bảo Hành - Biến Áp Minh Quang", 
    page_icon="⚡", 
    layout="centered"
)

# CSS để ẩn Menu, Footer, Header và làm đẹp giao diện
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding-top: 2rem; padding-bottom: 2rem;}
    
    /* Tùy chỉnh font chữ chung */
    html, body, [class*="css"] {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. HÀM HỖ TRỢ & KẾT NỐI DỮ LIỆU ---

def extract_serial(input_string):
    """Trích xuất mã Serial từ chuỗi thô hoặc từ URL link"""
    if not input_string:
        return ""
    if "http" in input_string:
        try:
            parsed_url = urlparse(input_string)
            captured_params = parse_qs(parsed_url.query)
            # Lấy giá trị tham số 'serial', nếu không có lấy phần cuối của path
            return captured_params.get("serial", [input_string.split('/')[-1]])[0]
        except:
            return input_string
    return input_string

@st.cache_data(ttl=300)
def load_data_securely():
    try:
        # Lấy thông tin từ Streamlit Secrets
        creds = st.secrets["gservice_account"]
        gc = gspread.service_account_from_dict(creds)
        
        SHEET_ID = "1RSgJ18oLmNkK2oL-pImYGLLiPBwENaXSG2_XDc-_pPk"
        SHEET_NAME = "SerialNumber"
        
        worksheet = gc.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)
        
        # Làm sạch dữ liệu cột Serial
        df['Serial'] = df['Serial'].astype(str).str.strip()
        return df
    except Exception as e:
        st.error(f"Lỗi kết nối dữ liệu: {e}")
        return pd.DataFrame()

# Tải dữ liệu
df = load_data_securely()

# --- 3. QUẢN LÝ TRẠNG THÁI (SESSION STATE) ---
if "search_done" not in st.session_state:
    st.session_state.search_done = False
if "current_result" not in st.session_state:
    st.session_state.current_result = None
if "current_query" not in st.session_state:
    st.session_state.current_query = ""

# --- 4. LOGIC XỬ LÝ MÀN HÌNH ---

# MÀN HÌNH 1: NHẬP LIỆU & QUÉT MÃ (Chỉ hiện khi chưa tìm thấy kết quả)
if not st.session_state.search_done:
    st.markdown("<h2 style='text-align: center; color: #FF9800;'>⚡ BIẾN ÁP MINH QUANG</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666;'>Hệ thống tra cứu bảo hành điện tử</p>", unsafe_allow_html=True)
    
    # 1. Quét QR từ Camera
    with st.expander("📷 Nhấn vào đây để mở Camera quét mã", expanded=True):
        qr_code_raw = qrcode_scanner(key='qrcode_scanner')
    
    # 2. Lấy từ URL tham số ?serial=...
    url_serial = st.query_params.get("serial", "")
    
    # Xử lý ưu tiên giá trị
    processed_qr = extract_serial(qr_code_raw)
    initial_value = processed_qr if processed_qr else extract_serial(url_serial)

    # 3. Ô nhập liệu tay
    search_query = st.text_input(
        "Nhập Số Serial sản phẩm:", 
        value=initial_value,
        placeholder="Ví dụ: MQ-2024-001..."
    ).strip()

    if search_query:
        if not df.empty:
            result = df[df['Serial'] == search_query]
            if not result.empty:
                st.session_state.search_done = True
                st.session_state.current_result = result.iloc[0]
                st.session_state.current_query = search_query
                st.rerun() # Làm mới trang để ẩn camera
            else:
                st.error(f"❌ Không tìm thấy mã máy '{search_query}' trong hệ thống.")
        else:
            st.warning("⚠️ Dữ liệu chưa sẵn sàng. Vui lòng kiểm tra kết nối Google Sheets.")

# MÀN HÌNH 2: HIỂN THỊ THẺ BẢO HÀNH (Chỉ hiện khi đã có kết quả)
else:
    data = st.session_state.current_result
    serial_no = st.session_state.current_query
    
    st.markdown("<h3 style='text-align: center; color: #333;'>KẾT QUẢ TRA CỨU</h3>", unsafe_allow_html=True)
    
    # Định dạng màu sắc trạng thái
    status_text = data.get('Trang_Thai', 'N/A')
    is_valid = "Hành" in status_text # Kiểm tra nếu chuỗi có chữ "Bảo Hành" hoặc "Còn Hành"
    status_color = "#2e7d32" if is_valid else "#d32f2f"
    status_bg = "#e8f5e9" if is_valid else "#ffebee"

    # HTML Giao diện Thẻ bảo hành
    card_html = f"""
    <div style="
        background-color: white; 
        padding: 25px; 
        border-radius: 20px; 
        border-left: 10px solid #FF9800; 
        box-shadow: 0 10px 25px rgba(0,0,0,0.1); 
        margin-top: 10px;
        margin-bottom: 25px;
    ">
        <div style="color: #888; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px;">Mã Serial sản phẩm</div>
        <div style="color: #FF9800; font-size: 1.5rem; font-weight: bold; margin-bottom: 15px;">{serial_no}</div>
        
        <div style="color: #888; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px;">Tên khách hàng</div>
        <div style="color: #1f1f1f; font-size: 1.2rem; font-weight: bold; margin-bottom: 20px;">{data.get('Ten_Khach_Hang', 'N/A')}</div>
        
        <div style="display: flex; justify-content: space-between; margin-bottom: 20px; flex-wrap: wrap; gap: 10px;">
            <div style="min-width: 120px;">
                <div style="color: #888; font-size: 0.8rem;">Ngày mua</div>
                <div style="color: #333; font-weight: 600;">{data.get('Ngay_Mua', 'N/A')}</div>
            </div>
            <div style="min-width: 120px;">
                <div style="color: #888; font-size: 0.8rem;">Ngày hết hạn</div>
                <div style="color: #333; font-weight: 600;">{data.get('Ngay_Het_Han', 'N/A')}</div>
            </div>
        </div>
        
        <hr style="border: 0; border-top: 1px solid #eee; margin-bottom: 15px;">
        
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <span style="color: #888; font-size: 0.9rem;">Trạng thái:</span>
            <span style="
                color: {status_color}; 
                background-color: {status_bg}; 
                padding: 6px 15px; 
                border-radius: 8px; 
                font-weight: bold; 
                font-size: 0.95rem;
            ">
                {status_text}
            </span>
        </div>
    </div>
    """
    
    # Hiển thị thẻ HTML
    st.markdown(card_html, unsafe_allow_html=True)

    # Nút bấm hành động
    col_1, col_2 = st.columns(2)
    with col_1:
        if st.button("🔍 Tra cứu mã khác", use_container_width=True):
            st.session_state.search_done = False
            st.session_state.current_result = None
            st.rerun()
    with col_2:
        st.link_button("📞 Gọi hỗ trợ ngay", "tel:0903736414", type="primary", use_container_width=True)

# --- 5. THANH BÊN (SIDEBAR) ---
with st.sidebar:
    st.markdown("### 🏠 MENU")
    st.page_link("https://bienapminhquang.com", label="Quay lại Trang chủ", icon="🌐")
    st.divider()
    st.markdown("**Hỗ trợ kỹ thuật:**")
    st.info("☎️ 0903.736.414\n\n📍 TP. Hồ Chí Minh")
