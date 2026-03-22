import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Page config
st.set_page_config(
    page_title="VisionCart Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title
st.title("🛒 VisionCart - Advanced Dashboard")
st.markdown("Real-time inventory and billing analytics")
st.markdown("---")

# Database connection
def get_inventory():
    conn = sqlite3.connect("database/visioncart.db")
    df = pd.read_sql_query("SELECT * FROM products", conn)
    conn.close()
    return df

# Sidebar
st.sidebar.title("📊 System Status")
st.sidebar.markdown("---")

try:
    df = get_inventory()
    
    # Metrics
    total_products = len(df)
    low_stock_count = len(df[df['stock'] <= 3])
    out_of_stock_count = len(df[df['stock'] == 0])
    total_inventory_value = (df['price'] * df['stock']).sum()
    
    st.sidebar.metric("Total Products", total_products)
    st.sidebar.metric("Low Stock Items", low_stock_count, delta=f"-{low_stock_count}" if low_stock_count > 0 else "0")
    st.sidebar.metric("Out of Stock", out_of_stock_count, delta=f"-{out_of_stock_count}" if out_of_stock_count > 0 else "0")
    st.sidebar.metric("Inventory Value", f"₹{total_inventory_value:.2f}")
    
    st.sidebar.markdown("---")
    
    # Alerts
    st.sidebar.subheader("⚠️ Alerts")
    
    if low_stock_count > 0:
        low_stock_items = df[df['stock'] <= 3]
        for _, row in low_stock_items.iterrows():
            st.sidebar.warning(f"**{row['product_id']}**: {row['stock']} units left")
    
    if out_of_stock_count > 0:
        out_of_stock_items = df[df['stock'] == 0]
        for _, row in out_of_stock_items.iterrows():
            st.sidebar.error(f"**{row['product_id']}**: OUT OF STOCK")
    
    if low_stock_count == 0 and out_of_stock_count == 0:
        st.sidebar.success("✅ All items well stocked!")

except Exception as e:
    st.sidebar.error("Database not initialized")

# Main dashboard
tab1, tab2, tab3 = st.tabs(["📦 Inventory", "📊 Analytics", "💳 Billing"])

# Tab 1: Inventory
with tab1:
    st.header("Inventory Management")
    
    try:
        df = get_inventory()
        
        if df.empty:
            st.warning("No products in database. Please register products first.")
        else:
            # Add status
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
    
    except Exception as e:
        st.error(f"Error: {e}")

# Tab 2: Analytics
with tab2:
    st.header("Inventory Analytics")
    
    try:
        df = get_inventory()
        
        if not df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # Stock distribution
                fig1 = px.bar(
                    df,
                    x='product_id',
                    y='stock',
                    title='Stock Levels by Product',
                    labels={'stock': 'Units', 'product_id': 'Product'},
                    color='stock',
                    color_continuous_scale='RdYlGn'
                )
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                # Price distribution
                fig2 = px.pie(
                    df,
                    values='price',
                    names='product_id',
                    title='Price Distribution'
                )
                st.plotly_chart(fig2, use_container_width=True)
            
            # Inventory value
            df['total_value'] = df['price'] * df['stock']
            fig3 = px.bar(
                df,
                x='product_id',
                y='total_value',
                title='Inventory Value by Product',
                labels={'total_value': 'Value (₹)', 'product_id': 'Product'}
            )
            st.plotly_chart(fig3, use_container_width=True)
    
    except Exception as e:
        st.error(f"Error: {e}")

# Tab 3: Billing
with tab3:
    st.header("Current Bill")
    
    # Mock bill data (will be replaced with actual data)
    st.info("Connect live billing system to see real-time cart updates")
    
    # Sample bill display
    st.subheader("Cart Items")
    st.write("No items in cart")
    
    st.markdown("---")
    st.markdown("### Total: ₹0.00")
    
    col1, col2 = st.columns(2)
    with col1:
        st.button("🗑️ Clear Cart", use_container_width=True)
    with col2:
        st.button("✅ Checkout", use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>VisionCart Dashboard v1.0 | AI-Powered Smart Billing</p>
</div>
""", unsafe_allow_html=True)
