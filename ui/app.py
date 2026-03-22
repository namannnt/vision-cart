import streamlit as st
import sqlite3
import pandas as pd
import time
from datetime import datetime

# Page config
st.set_page_config(
    page_title="VisionCart Smart Billing",
    page_icon="🛒",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .big-font {
        font-size:30px !important;
        font-weight: bold;
    }
    .alert-box {
        padding: 10px;
        background-color: #ff4b4b;
        color: white;
        border-radius: 5px;
        margin: 5px 0;
    }
    .success-box {
        padding: 10px;
        background-color: #00cc00;
        color: white;
        border-radius: 5px;
        margin: 5px 0;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title("🛒 VisionCart Smart Billing System")
st.markdown("---")

# Database connection
@st.cache_resource
def get_database_connection():
    return sqlite3.connect("database/visioncart.db", check_same_thread=False)

def load_inventory():
    """Load inventory from database"""
    conn = get_database_connection()
    df = pd.read_sql_query("SELECT product_id, price, stock FROM products", conn)
    return df

def load_bill():
    """Load current bill (mock data for now)"""
    # This will be replaced with actual billing data
    return []

# Sidebar - Inventory Alerts
st.sidebar.title("📊 Inventory Alerts")
st.sidebar.markdown("---")

try:
    df = load_inventory()
    
    # Low stock items
    low_stock = df[df["stock"] <= 3]
    
    if not low_stock.empty:
        st.sidebar.warning(f"⚠️ {len(low_stock)} Low Stock Items")
        for _, row in low_stock.iterrows():
            st.sidebar.markdown(f"""
            <div class="alert-box">
                <b>{row['product_id']}</b><br>
                Stock: {row['stock']} units
            </div>
            """, unsafe_allow_html=True)
    else:
        st.sidebar.success("✅ All items in stock")
    
    # Out of stock items
    out_of_stock = df[df["stock"] == 0]
    if not out_of_stock.empty:
        st.sidebar.error(f"❌ {len(out_of_stock)} Out of Stock")
        for _, row in out_of_stock.iterrows():
            st.sidebar.write(f"- {row['product_id']}")

except Exception as e:
    st.sidebar.error("Database not found. Please register products first.")

# Main content - Two columns
col1, col2 = st.columns([1, 1])

# Left column - Current Bill
with col1:
    st.header("💳 Current Bill")
    
    bill = load_bill()
    
    if len(bill) == 0:
        st.info("No items in cart. Start scanning products!")
    else:
        # Display bill items
        for i, item in enumerate(bill, 1):
            st.write(f"{i}. **{item['product_id']}** — ₹{item['price']:.2f}")
        
        st.markdown("---")
        total = sum(item['price'] for item in bill)
        st.markdown(f"<p class='big-font'>Total: ₹{total:.2f}</p>", unsafe_allow_html=True)
        
        # Action buttons
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🗑️ Clear Cart", use_container_width=True):
                st.success("Cart cleared!")
        with col_btn2:
            if st.button("✅ Checkout", use_container_width=True):
                st.success("Payment successful!")

# Right column - Inventory Status
with col2:
    st.header("📦 Inventory Status")
    
    try:
        df = load_inventory()
        
        if df.empty:
            st.warning("No products registered yet.")
        else:
            # Add status column
            def get_status(stock):
                if stock == 0:
                    return "❌ Out of Stock"
                elif stock <= 3:
                    return "⚠️ Low Stock"
                else:
                    return "✅ In Stock"
            
            df['Status'] = df['stock'].apply(get_status)
            
            # Display table
            st.dataframe(
                df[['product_id', 'price', 'stock', 'Status']],
                use_container_width=True,
                hide_index=True
            )
            
            # Summary metrics
            st.markdown("---")
            metric_col1, metric_col2, metric_col3 = st.columns(3)
            
            with metric_col1:
                st.metric("Total Products", len(df))
            
            with metric_col2:
                total_value = (df['price'] * df['stock']).sum()
                st.metric("Inventory Value", f"₹{total_value:.2f}")
            
            with metric_col3:
                low_count = len(df[df['stock'] <= 3])
                st.metric("Low Stock Items", low_count)
    
    except Exception as e:
        st.error(f"Error loading inventory: {e}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>VisionCart Smart Billing System | Powered by YOLO + CLIP + DINOv2</p>
</div>
""", unsafe_allow_html=True)

# Auto-refresh (optional)
# st.rerun()  # Uncomment for live updates
