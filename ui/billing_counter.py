import streamlit as st
import sqlite3
import pandas as pd
import sys
import os
import time
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Get correct paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB = os.path.join(BASE_DIR, "database", "visioncart.db")

# Page config
st.set_page_config(
    page_title="VisionCart Billing",
    page_icon="🛒",
    layout="wide"
)

# Initialize session state
if 'cart' not in st.session_state:
    st.session_state.cart = []
if 'scanning_active' not in st.session_state:
    st.session_state.scanning_active = False

def get_product_info(product_id):
    """Get product details from database"""
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("SELECT product_id, price, stock FROM products WHERE product_id=?", (product_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def update_stock(product_id, quantity=-1):
    """Update stock after purchase"""
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET stock = stock + ? WHERE product_id=?", (quantity, product_id))
    conn.commit()
    conn.close()

def add_to_cart(product_id, price):
    """Add item to cart"""
    # Check if already in cart
    for item in st.session_state.cart:
        if item['product_id'] == product_id:
            return False  # Already in cart
    
    st.session_state.cart.append({
        'product_id': product_id,
        'price': price,
        'time': datetime.now().strftime("%H:%M:%S")
    })
    return True

def clear_cart():
    """Clear all items from cart"""
    st.session_state.cart = []

def get_total():
    """Calculate total amount"""
    return sum(item['price'] for item in st.session_state.cart)

# Custom CSS
st.markdown("""
<style>
    .big-font {
        font-size: 40px !important;
        font-weight: bold;
        color: #00cc00;
    }
    .cart-item {
        padding: 10px;
        margin: 5px 0;
        background-color: #f0f0f0;
        border-radius: 5px;
        border-left: 4px solid #00cc00;
    }
    .total-box {
        padding: 20px;
        background-color: #00cc00;
        color: white;
        border-radius: 10px;
        text-align: center;
        font-size: 30px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("🛒 VisionCart - Billing Counter")
st.markdown("---")

# Two columns layout
col1, col2 = st.columns([2, 1])

# Left column - Camera & Scanning
with col1:
    st.header("📷 Product Scanner")
    
    # Scanning controls
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        if st.button("🎥 Start Scanning", type="primary", use_container_width=True):
            st.session_state.scanning_active = True
            st.rerun()
    
    with col_btn2:
        if st.button("⏹️ Stop Scanning", use_container_width=True):
            st.session_state.scanning_active = False
    
    st.markdown("---")
    
    if st.session_state.scanning_active:
        st.info("🔄 Scanner is running in background. Place products in front of camera.")
        st.warning("⚠️ Note: This will open a separate camera window. Check your desktop!")
        
        if st.button("🔍 Scan Product Now", type="primary", use_container_width=True):
            with st.spinner("📸 Capturing and processing..."):
                try:
                    from utils.camera_capture import capture_and_process_product
                    from utils.load_database import load_database
                    from utils.accuracy_boost import top_k_matching
                    
                    # Capture product
                    success, product_data, error_msg = capture_and_process_product()
                    
                    if not success:
                        st.error(f"❌ {error_msg}")
                    else:
                        # Load database
                        product_ids, db_embeddings, prices, stocks = load_database()
                        
                        if len(product_ids) == 0:
                            st.error("❌ No products in database!")
                        else:
                            # Match product
                            query_emb = product_data['embedding']
                            idx, score, is_known, top_k_labels = top_k_matching(
                                query_emb, db_embeddings, product_ids, k=3, threshold=0.85
                            )
                            
                            if is_known:
                                product_id = product_ids[idx]
                                price = prices[idx]
                                stock = stocks[idx]
                                
                                if stock <= 0:
                                    st.error(f"❌ {product_id} is OUT OF STOCK!")
                                else:
                                    # Add to cart
                                    if add_to_cart(product_id, price):
                                        st.success(f"✅ Added: {product_id} - ₹{price:.2f}")
                                        st.balloons()
                                        time.sleep(1)
                                        st.rerun()
                                    else:
                                        st.warning(f"ℹ️ {product_id} already in cart!")
                            else:
                                st.error(f"❌ Unknown product! (Confidence: {score:.2f})")
                
                except Exception as e:
                    st.error(f"Error: {e}")
                    import traceback
                    st.code(traceback.format_exc())
    else:
        st.info("👆 Click 'Start Scanning' to begin")
        st.image("https://via.placeholder.com/600x400?text=Camera+Feed+Here", use_container_width=True)

# Right column - Cart & Billing
with col2:
    st.header("🛍️ Shopping Cart")
    
    if len(st.session_state.cart) == 0:
        st.info("Cart is empty. Scan products to add items.")
    else:
        # Display cart items
        for i, item in enumerate(st.session_state.cart, 1):
            st.markdown(f"""
            <div class="cart-item">
                <b>{i}. {item['product_id']}</b><br>
                ₹{item['price']:.2f} | Added: {item['time']}
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Total
        total = get_total()
        st.markdown(f"""
        <div class="total-box">
            TOTAL: ₹{total:.2f}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Action buttons
        col_action1, col_action2 = st.columns(2)
        
        with col_action1:
            if st.button("🗑️ Clear Cart", use_container_width=True):
                clear_cart()
                st.rerun()
        
        with col_action2:
            if st.button("💳 Checkout", type="primary", use_container_width=True):
                # Update stock for all items
                for item in st.session_state.cart:
                    update_stock(item['product_id'], -1)
                
                # Generate bill
                st.success("✅ Payment Successful!")
                st.balloons()
                
                # Print bill
                st.markdown("---")
                st.subheader("📄 Bill Receipt")
                st.text(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                st.text("="*40)
                
                for i, item in enumerate(st.session_state.cart, 1):
                    st.text(f"{i}. {item['product_id']:<20} ₹{item['price']:>8.2f}")
                
                st.text("="*40)
                st.text(f"{'TOTAL':<20} ₹{total:>8.2f}")
                st.text("="*40)
                st.text("Thank you for shopping with VisionCart!")
                
                # Clear cart after checkout
                time.sleep(3)
                clear_cart()
                st.rerun()

# Sidebar - Quick Stats
st.sidebar.title("📊 Quick Stats")
st.sidebar.markdown("---")

try:
    conn = sqlite3.connect(DB)
    df = pd.read_sql_query("SELECT COUNT(*) as count FROM products", conn)
    total_products = df['count'].values[0]
    
    df = pd.read_sql_query("SELECT COUNT(*) as count FROM products WHERE stock <= 3", conn)
    low_stock = df['count'].values[0]
    
    conn.close()
    
    st.sidebar.metric("Products in DB", total_products)
    st.sidebar.metric("Low Stock Items", low_stock)
    st.sidebar.metric("Items in Cart", len(st.session_state.cart))
    st.sidebar.metric("Cart Total", f"₹{get_total():.2f}")

except Exception as e:
    st.sidebar.error("Database not found")

st.sidebar.markdown("---")
st.sidebar.info("💡 Tip: Keep products close to camera for best results")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>VisionCart Billing System | AI-Powered Smart Checkout</p>
</div>
""", unsafe_allow_html=True)
