"""
VisionCart Customer Checkout Counter
Professional customer-facing dashboard with auto-detection and billing
"""
import streamlit as st
import cv2
import torch
import numpy as np
from PIL import Image
import time
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ultralytics import YOLO
from torchvision import transforms

# Page config
st.set_page_config(
    page_title="VisionCart Checkout",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 48px;
        font-weight: bold;
        color: #4CAF50;
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 30px;
    }
    .cart-item {
        font-size: 24px;
        padding: 15px;
        margin: 10px 0;
        background-color: #f0f0f0;
        border-radius: 8px;
        border-left: 5px solid #4CAF50;
    }
    .total-amount {
        font-size: 42px;
        font-weight: bold;
        color: #4CAF50;
        text-align: center;
        padding: 20px;
        background-color: #e8f5e9;
        border-radius: 10px;
        margin: 20px 0;
    }
    .status-ready {
        color: #4CAF50;
        font-size: 24px;
        font-weight: bold;
    }
    .status-scanning {
        color: #FF9800;
        font-size: 24px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'cart' not in st.session_state:
    st.session_state.cart = []
if 'last_detected' not in st.session_state:
    st.session_state.last_detected = None
if 'last_detection_time' not in st.session_state:
    st.session_state.last_detection_time = 0


# Header
st.markdown('<div class="main-header">🛒 VisionCart Smart Checkout</div>', unsafe_allow_html=True)

# Layout
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 📸 Scanning Area")
    
    # Camera feed placeholder
    camera_placeholder = st.empty()
    status_placeholder = st.empty()
    
    # Instructions
    st.info("""
    **📋 Instructions:**
    1. Place items in scanning area
    2. Wait for auto-detection
    3. Review your cart
    4. Click CONFIRM & PAY
    """)

with col2:
    st.markdown("### 🛍️ Your Cart")
    
    cart_placeholder = st.empty()
    total_placeholder = st.empty()
    
    # Action buttons
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    
    with col_btn1:
        if st.button("✅ CONFIRM & PAY", type="primary", use_container_width=True):
            if len(st.session_state.cart) > 0:
                st.session_state.show_payment = True
            else:
                st.warning("Cart is empty!")
    
    with col_btn2:
        if st.button("❌ REMOVE LAST", use_container_width=True):
            if len(st.session_state.cart) > 0:
                removed = st.session_state.cart.pop()
                st.success(f"Removed: {removed['name']}")
                st.rerun()
    
    with col_btn3:
        if st.button("🔄 CLEAR CART", use_container_width=True):
            st.session_state.cart = []
            st.success("Cart cleared!")
            st.rerun()

# Display cart
with cart_placeholder.container():
    if len(st.session_state.cart) == 0:
        st.info("🛒 Cart is empty. Start scanning items!")
    else:
        for i, item in enumerate(st.session_state.cart, 1):
            st.markdown(f"""
            <div class="cart-item">
                {i}. {item['name']} - ₹{item['price']:.2f}
                <span style="float: right; color: #666;">
                    Conf: {item['confidence']:.0%}
                </span>
            </div>
            """, unsafe_allow_html=True)

# Display total
total = sum(item['price'] for item in st.session_state.cart)
with total_placeholder.container():
    st.markdown(f'<div class="total-amount">TOTAL: ₹{total:.2f}</div>', unsafe_allow_html=True)
    st.markdown(f"**Items:** {len(st.session_state.cart)}")

# Payment screen
if 'show_payment' in st.session_state and st.session_state.show_payment:
    with st.container():
        st.markdown("---")
        st.markdown("### 💳 Payment")
        
        payment_method = st.radio(
            "Select Payment Method:",
            ["💵 Cash", "💳 Card", "📱 UPI"],
            horizontal=True
        )
        
        if st.button("✅ COMPLETE PAYMENT", type="primary", use_container_width=True):
            # Update inventory
            import sqlite3
            conn = sqlite3.connect("database/visioncart.db")
            cursor = conn.cursor()
            
            for item in st.session_state.cart:
                cursor.execute("""
                    UPDATE products 
                    SET stock = stock - 1 
                    WHERE product_id = ?
                """, (item['name'],))
            
            conn.commit()
            conn.close()
            
            # Generate bill
            bill_text = f"""
            ═══════════════════════════════
            🛒 VISIONCART RECEIPT
            ═══════════════════════════════
            Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            
            Items:
            """
            
            for i, item in enumerate(st.session_state.cart, 1):
                bill_text += f"\n{i}. {item['name']:<20} ₹{item['price']:>8.2f}"
            
            bill_text += f"""
            
            ───────────────────────────────
            TOTAL:                ₹{total:>8.2f}
            ───────────────────────────────
            Payment: {payment_method}
            
            Thank you for shopping!
            ═══════════════════════════════
            """
            
            st.success("✅ Payment Successful!")
            st.code(bill_text)
            st.balloons()
            
            # Reset
            time.sleep(3)
            st.session_state.cart = []
            st.session_state.show_payment = False
            st.rerun()
