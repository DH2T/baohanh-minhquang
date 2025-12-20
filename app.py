# --- 5. HIỂN THỊ KẾT QUẢ DẠNG CARD ---
else:
    data = st.session_state.current_result
    st.markdown("<h3 style='text-align: center; color: #333;'>Kết Quả Tra Cứu</h3>", unsafe_allow_html=True)
    
    # Chuẩn bị dữ liệu
    serial_no = st.session_state.current_query
    customer = data.get('Ten_Khach_Hang', 'N/A')
    buy_date = data.get('Ngay_Mua', 'N/A')
    exp_date = data.get('Ngay_Het_Han', 'N/A')
    status_text = data.get('Trang_Thai', 'N/A')
    
    # Xác định màu sắc trạng thái
    status_color = "#2e7d32" if "Hành" in status_text else "#d32f2f"
    status_bg = "#e8f5e9" if "Hành" in status_text else "#ffebee"

    # Tạo chuỗi HTML an toàn (Sử dụng f-string cẩn thận)
    card_html = f"""
    <div style="
        background-color: white; 
        padding: 20px; 
        border-radius: 15px; 
        border-left: 8px solid #FF9800; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.1); 
        margin-bottom: 20px;
    ">
        <div style="color: #666; font-size: 0.85rem;">Mã Serial sản phẩm</div>
        <div style="color: #FF9800; font-size: 1.3rem; font-weight: bold; margin-bottom: 12px;">{serial_no}</div>
        
        <div style="color: #666; font-size: 0.85rem;">Tên khách hàng</div>
        <div style="color: #1f1f1f; font-size: 1.1rem; font-weight: bold; margin-bottom: 12px;">{customer}</div>
        
        <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
            <div style="width: 48%;">
                <div style="color: #666; font-size: 0.85rem;">Ngày mua</div>
                <div style="color: #1f1f1f; font-weight: 600;">{buy_date}</div>
            </div>
            <div style="width: 48%;">
                <div style="color: #666; font-size: 0.85rem;">Hết hạn</div>
                <div style="color: #1f1f1f; font-weight: 600;">{exp_date}</div>
            </div>
        </div>
        
        <div style="color: #666; font-size: 0.85rem; margin-bottom: 4px;">Trạng thái</div>
        <span style="
            color: {status_color}; 
            background-color: {status_bg}; 
            padding: 5px 12px; 
            border-radius: 6px; 
            font-weight: bold; 
            font-size: 0.9rem;
        ">
            {status_text}
        </span>
    </div>
    """
    
    # HIỂN THỊ HTML RA MÀN HÌNH
    st.markdown(card_html, unsafe_allow_html=True)

    # Nút bấm tương tác dưới Card
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🔍 Tra mã khác", use_container_width=True):
            st.session_state.search_done = False
            st.rerun()
    with col_b:
        st.link_button("📞 Gọi hỗ trợ", "tel:0903736414", type="primary", use_container_width=True)
