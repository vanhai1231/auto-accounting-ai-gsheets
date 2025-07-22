import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import tempfile
from ocr.tesseract_ocr import extract_text_from_pdf_tesseract
from llm_parser.groq_invoice_parser import parse_invoice_with_groq
from sheets.write_to_sheets import write_to_google_sheet
from config import settings
from utils.logger import get_logger
import time

logger = get_logger()

# Cấu hình trang
st.set_page_config(
    page_title="Auto Accounting AI", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS Compact Modern Design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main container */
    .stApp {
        background: #0a0a0a;
        padding: 0;
    }
    
    /* Hide Streamlit elements */
    #MainMenu, footer, header {visibility: hidden;}
    .css-1rs6os, .css-17ziqus {visibility: hidden;}
    
    /* Compact header */
    .compact-header {
        background: linear-gradient(90deg, #1a1a1a 0%, #2d2d2d 100%);
        padding: 15px 30px;
        margin: -1rem -1rem 1rem -1rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-bottom: 1px solid #333;
    }
    
    .header-left {
        display: flex;
        align-items: center;
        gap: 15px;
    }
    
    .logo-mini {
        width: 40px;
        height: 40px;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
    }
    
    .header-title {
        color: white;
        font-size: 20px;
        font-weight: 600;
        margin: 0;
    }
    
    .header-status {
        color: #888;
        font-size: 13px;
    }
    
    /* Main grid layout */
    .main-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px;
        padding: 0 20px;
        height: calc(100vh - 100px);
    }
    
    /* Card style */
    .card {
        background: #1a1a1a;
        border: 1px solid #2d2d2d;
        border-radius: 12px;
        padding: 20px;
        height: fit-content;
    }
    
    .card-title {
        color: white;
        font-size: 16px;
        font-weight: 600;
        margin-bottom: 15px;
        padding-bottom: 10px;
        border-bottom: 1px solid #2d2d2d;
    }
    
    /* Upload section */
    .upload-zone {
        background: #0f0f0f;
        border: 2px dashed #333;
        border-radius: 8px;
        padding: 30px;
        text-align: center;
        transition: all 0.2s;
        cursor: pointer;
    }
    
    .upload-zone:hover {
        border-color: #6366f1;
        background: #141414;
    }
    
    .stFileUploader > div > div {
        background: transparent !important;
        border: none !important;
    }
    
    /* Compact file info */
    .file-info {
        background: #0f0f0f;
        border-radius: 8px;
        padding: 12px;
        margin-top: 15px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .file-info-item {
        color: #888;
        font-size: 13px;
    }
    
    .file-info-value {
        color: white;
        font-weight: 500;
    }
    
    /* Processing status */
    .status-bar {
        background: #0f0f0f;
        border-radius: 8px;
        padding: 15px;
        margin: 15px 0;
        display: flex;
        align-items: center;
        gap: 15px;
    }
    
    .status-icon {
        width: 30px;
        height: 30px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;
    }
    
    .status-processing {
        background: #6366f1;
        animation: pulse 1.5s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 0.6; }
        50% { opacity: 1; }
    }
    
    .status-success {
        background: #10b981;
    }
    
    .status-error {
        background: #ef4444;
    }
    
    .status-text {
        color: white;
        font-size: 14px;
        flex: 1;
    }
    
    /* Results section */
    .result-stats {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 10px;
        margin-bottom: 15px;
    }
    
    .stat-box {
        background: #0f0f0f;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
    }
    
    .stat-value {
        color: #6366f1;
        font-size: 24px;
        font-weight: 700;
        margin: 0;
    }
    
    .stat-label {
        color: #666;
        font-size: 12px;
        margin-top: 5px;
        text-transform: uppercase;
    }
    
    /* Product list */
    .product-list {
        background: #0f0f0f;
        border-radius: 8px;
        padding: 15px;
        max-height: 300px;
        overflow-y: auto;
    }
    
    .product-item {
        display: flex;
        justify-content: space-between;
        padding: 10px;
        border-bottom: 1px solid #1a1a1a;
        color: white;
        font-size: 14px;
    }
    
    .product-item:last-child {
        border-bottom: none;
    }
    
    /* Action buttons */
    .action-buttons {
        display: flex;
        gap: 10px;
        margin-top: 15px;
    }
    
    .stButton > button {
        background: #6366f1;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 8px;
        font-weight: 500;
        font-size: 14px;
        transition: all 0.2s;
        width: 100%;
    }
    
    .stButton > button:hover {
        background: #4f46e5;
        transform: translateY(-1px);
    }
    
    /* Secondary button */
    .secondary-btn button {
        background: #2d2d2d !important;
    }
    
    .secondary-btn button:hover {
        background: #3d3d3d !important;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: #0f0f0f;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #333;
        border-radius: 3px;
    }
    
    /* Loading spinner */
    .spinner {
        width: 20px;
        height: 20px;
        border: 2px solid #333;
        border-top-color: #6366f1;
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    /* Expander customization */
    .streamlit-expanderHeader {
        background: #0f0f0f !important;
        color: #888 !important;
        font-size: 13px !important;
        padding: 8px 12px !important;
    }
    
    /* JSON viewer */
    .stJson {
        background: #0f0f0f !important;
        font-size: 12px !important;
        max-height: 250px !important;
        overflow-y: auto !important;
    }
</style>
""", unsafe_allow_html=True)

# Compact Header
st.markdown("""
<div class="compact-header">
    <div class="header-left">
        <div class="logo-mini">📄</div>
        <div>
            <h1 class="header-title">Auto Accounting AI</h1>
            <p class="header-status">Xử lý hóa đơn thông minh</p>
        </div>
    </div>
    <div class="header-status" id="current-time"></div>
</div>

<script>
function updateTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
    const dateString = now.toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric' });
    document.getElementById('current-time').innerHTML = dateString + ' • ' + timeString;
}
updateTime();
setInterval(updateTime, 1000);
</script>
""", unsafe_allow_html=True)

# Main layout with 2 columns
col1, col2 = st.columns(2)

# Left column - Upload & Processing
with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h3 class="card-title">📤 Tải lên & Xử lý</h3>', unsafe_allow_html=True)
    
    # Upload zone
    st.markdown("""
    <div class="upload-zone">
        <div style="font-size: 40px; margin-bottom: 10px;">📁</div>
        <div style="color: white; font-weight: 500; margin-bottom: 5px;">Kéo thả hoặc chọn file</div>
        <div style="color: #666; font-size: 13px;">PDF, JPG, PNG (Max: 10MB)</div>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("", type=["pdf", "jpg", "jpeg", "png"], label_visibility="collapsed")
    
    # File info & status
    if uploaded_file:
        st.markdown(f"""
        <div class="file-info">
            <span class="file-info-item">📄 <span class="file-info-value">{uploaded_file.name}</span></span>
            <span class="file-info-item">📊 <span class="file-info-value">{uploaded_file.size / 1024:.1f} KB</span></span>
            <span class="file-info-item">📋 <span class="file-info-value">{uploaded_file.type}</span></span>
        </div>
        """, unsafe_allow_html=True)
        
        # Status placeholder
        status_placeholder = st.empty()
        
    st.markdown('</div>', unsafe_allow_html=True)

# Right column - Results
with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h3 class="card-title">📊 Kết quả phân tích</h3>', unsafe_allow_html=True)
    
    result_placeholder = st.empty()
    
    if not uploaded_file:
        result_placeholder.markdown("""
        <div style="text-align: center; padding: 80px 20px; color: #666;">
            <div style="font-size: 60px; margin-bottom: 20px;">🤖</div>
            <p>Chờ tải file để bắt đầu phân tích</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Process file if uploaded
if uploaded_file:
    # Save temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix="." + uploaded_file.name.split(".")[-1]) as tmp_file:
        tmp_file.write(uploaded_file.read())
        temp_path = tmp_file.name
    
    try:
        # OCR Processing
        status_placeholder.markdown("""
        <div class="status-bar">
            <div class="status-icon status-processing"><div class="spinner"></div></div>
            <div class="status-text">Đang nhận dạng văn bản (OCR)...</div>
        </div>
        """, unsafe_allow_html=True)
        
        text = extract_text_from_pdf_tesseract(temp_path, lang="vie+eng")
        
        # AI Analysis
        status_placeholder.markdown("""
        <div class="status-bar">
            <div class="status-icon status-processing"><div class="spinner"></div></div>
            <div class="status-text">AI đang phân tích nội dung...</div>
        </div>
        """, unsafe_allow_html=True)
        
        result = parse_invoice_with_groq(text)
        items = result.get("items") if isinstance(result, dict) else result
        
        if not items:
            status_placeholder.markdown("""
            <div class="status-bar">
                <div class="status-icon status-error">❌</div>
                <div class="status-text">Không tìm thấy sản phẩm trong hóa đơn</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Success status
            status_placeholder.markdown("""
            <div class="status-bar">
                <div class="status-icon status-success">✓</div>
                <div class="status-text">Phân tích hoàn tất!</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Calculate stats
            total_items = len(items)
            total_amount = sum(item.get('total', 0) for item in items if isinstance(item, dict))
            avg_price = total_amount / total_items if total_items > 0 else 0
            
            # Display results
            with result_placeholder.container():
                # Stats
                st.markdown(f"""
                <div class="result-stats">
                    <div class="stat-box">
                        <p class="stat-value">{total_items}</p>
                        <p class="stat-label">Sản phẩm</p>
                    </div>
                    <div class="stat-box">
                        <p class="stat-value">{total_amount:,.0f}đ</p>
                        <p class="stat-label">Tổng tiền</p>
                    </div>
                    <div class="stat-box">
                        <p class="stat-value">{avg_price:,.0f}đ</p>
                        <p class="stat-label">Trung bình</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Product details with expander
                with st.expander("Chi tiết sản phẩm", expanded=True):
                    st.json(items)
                
                # Action buttons
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("📤 Xuất Google Sheets", use_container_width=True):
                        with st.spinner("Đang xuất..."):
                            write_to_google_sheet(
                                settings.GOOGLE_SHEET_ID,
                                settings.WORKSHEET_NAME,
                                items
                            )
                        st.success("✅ Đã xuất thành công!")
                
                with col_btn2:
                    st.markdown('<div class="secondary-btn">', unsafe_allow_html=True)
                    if st.button("🔄 Xử lý file mới", use_container_width=True):
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                    
    except Exception as e:
        status_placeholder.markdown(f"""
        <div class="status-bar">
            <div class="status-icon status-error">⚠️</div>
            <div class="status-text">Lỗi: {str(e)}</div>
        </div>
        """, unsafe_allow_html=True)
        logger.error(f"Error: {e}")