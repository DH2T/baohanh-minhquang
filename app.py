import streamlit as st
import pandas as pd
import gspread
import cv2
import av
import numpy as np
from streamlit_webrtc import webrtc_streamer, WebRtcMode, VideoTransformerBase
from urllib.parse import urlparse, parse_qs
import threading

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="Bảo Hành Minh Quang", page_icon="⚡", layout="centered")

# --- 2. CSS TỐI ƯU ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .main-title { font-size: 1.8rem; color: #FF9800; text-align: center; font-weight: bold; margin-bottom: 0px; }
    .sub-title { text-align: center; color: #666; font-size: 0.8rem; margin-bottom: 20px; }
    /* Ẩn nút Select Device xấu xí của webrtc, mặc định dùng camera sau */
    </style>
    """, unsafe_allow_html=True)

# --- 3. KẾT NỐI DỮ LIỆU ---
@st.cache_data(ttl=300)
def load_data():
    try:
        creds = st.secrets["gservice_account"]
        gc = gspread.service_account_from_dict(creds)
        sh = gc.open_by_key("1RSgJ18oLmNkK2oL-pImYGLLiPBwENaXSG2_XDc-_pPk")
        df = pd.DataFrame(sh.worksheet("SerialNumber").get_all_records())
        df['Serial'] = df['Serial'].astype(str).str.strip()
        return df
    except: return pd.DataFrame()

df = load_data()

# --- 4. XỬ LÝ QR REAL-TIME (CỐT LÕI) ---
# Biến toàn cục để lưu mã QR tìm thấy tạm thời
lock = threading.Lock()
class QRTransformer(VideoTransformerBase):
    def __init__(self):
        self.found_qr = None

    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        
        # 1. Xử lý ảnh để tăng độ nhạy (Chuyển xám)
        # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 
        # detector = cv2.QRCodeDetector()
        # data, bbox, _ = detector.detectAndDecode(img)
        
        # Dùng OpenCV detect
        detector = cv2.QRCodeDetector()
        data, bbox, _ = detector.detectAndDecode(img)

        if data:
            with lock:
                self.found_qr = data
            # Vẽ khung xanh quanh mã QR để báo hiệu đã nhận
            if bbox is not None:
                n = len(bbox)
                for j in range(n):
                    cv2.line(img, tuple(bbox[j][0].astype(int)), tuple(bbox[(j+1) % n][0].astype(int)), (0, 255, 0), 3)
            
        return img

# --- 5. HÀM HỖ TRỢ ---
def get_serial(text):
    if not text: return ""
    if "https" in text:
        try: return parse_qs(urlparse(text).query).get("serial", [text.split('/')[-1]])[0]
        except: return text
    return text

def reset_search():
    st.session_state.found = False
    st.session_state.query_id = ""
    st.session_state.data = None
    st.session_state.scanned_code = None # Reset mã quét
    st.query_params.clear()

# --- 6. QUẢN LÝ TRẠNG THÁI ---
if "found" not in st.session_state: st.session_state.found = False
if "scanned_code" not in st.session_state: st.session_state.scanned_code = None

# --- 7. GIAO DIỆN CHÍNH ---
if not st.session_state.found:
    st.markdown('<p class="main-title">TRA CỨU BẢO HÀNH</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">BIẾN ÁP MINH QUANG-CÔNG TY DH2T</p>', unsafe_allow_html=True)

    # --- KHU VỰC CAMERA REAL-TIME ---
    # Nếu chưa quét được mã thì hiện Camera
    if st.session_state.scanned_code is None:
        with st.expander("📷 MỞ MÁY QUÉT (AUTO)", expanded=True):
            ctx = webrtc_streamer(
                key="example",
                mode=WebRtcMode.SENDRECV,
                video_transformer_factory=QRTransformer,
                media_stream_constraints={"video": {"facingMode": "environment"}}, # Ưu tiên Camera sau
                async_processing=True,
            )

        # Kiểm tra liên tục xem Transformer đã bắt được mã chưa
        if ctx.video_transformer:
            if ctx.video_transformer.found_qr:
                # Đã tìm thấy! Lưu vào session và reload để tắt cam
                st.session_state.scanned_code = ctx.video_transformer.found_qr
                st.rerun()
    
    # --- XỬ LÝ DỮ LIỆU ---
    url_val = st.query_params.get("serial", "")
    # Ưu tiên mã quét từ Camera -> rồi đến URL
    detected_serial = st.session_state.scanned_code if st.session_state.scanned_code else url_val
    final_input = get_serial(detected_serial)

    query = st.text_input("Mã sản phẩm:", value=final_input, placeholder="Đang chờ quét...")

    # Tự động tra cứu nếu có mã (từ camera hoặc nhập tay)
    if query:
        if not df.empty:
            match = df[df['Serial'] == query]
            if not match.empty:
                st.session_state.found = True
                st.session_state.data = match.iloc[0]
                st.session_state.query_id = query
                st.rerun()
            else:
                st.error(f"❌ Không tìm thấy: {query}")
        else:
            st.warning("Chưa kết nối dữ liệu.")

else:
    # --- MÀN HÌNH KẾT QUẢ ---
    st.markdown('<p class="main-title">THÔNG TIN BẢO HÀNH</p>', unsafe_allow_html=True)
    data = st.session_state.data
    
    with st.container(border=True):
        st.success(f"✅ {data.get('Trang_Thai', 'Trạng thái')}")
        st.markdown(f"**Khách hàng:** {data.get('Ten_Khach_Hang', 'N/A')}")
        st.markdown(f"**Serial:** `{st.session_state.query_id}`")
        st.divider()
        c1, c2 = st.columns(2)
        c1.metric("Ngày mua", str(data.get('Ngay_Mua', '-')))
        c2.metric("Hết hạn", str(data.get('Ngay_Het_Han', '-')))

    st.button("🔍 Tra cứu mã khác", on_click=reset_search, use_container_width=True)
    st.link_button("📞 Gọi hỗ trợ", "tel:0903736414", use_container_width=True, type="primary")

# Sidebar
st.sidebar.page_link("https://bienapminhquang.com", label="Website Chính", icon="🏠")
