import streamlit as st
import sqlite3
import pandas as pd
import sys
import os
import cv2
import numpy as np

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Get correct database path (relative to project root)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB = os.path.join(BASE_DIR, "database", "visioncart.db")

def get_inventory():
    """Get all products from database"""
    conn = sqlite3.connect(DB)
    df = pd.read_sql_query("SELECT product_id, price, stock FROM products", conn)
    conn.close()
    return df

def add_product(pid, price, stock):
    """Add or update product"""
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO products (product_id, price, stock, embedding)
        VALUES (?, ?, ?, ?)
    """, (pid, price, stock, b''))  # Empty embedding for manual entry
    conn.commit()
    conn.close()

def update_stock(pid, stock):
    """Update stock for existing product"""
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE products SET stock=?
        WHERE product_id=?
    """, (stock, pid))
    conn.commit()
    conn.close()

def delete_product(pid):
    """Delete product from database"""
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE product_id=?", (pid,))
    conn.commit()
    conn.close()

# Page config
st.set_page_config(
    page_title="VisionCart Admin",
    page_icon="🛒",
    layout="wide"
)

# Title
st.title("🛒 VisionCart Shopkeeper Dashboard")
st.markdown("Manage your inventory and products")
st.markdown("---")

# Sidebar menu
menu = st.sidebar.selectbox(
    "📋 Menu",
    ["View Inventory", "Register Product", "Update Stock", "Delete Product"]
)

st.sidebar.markdown("---")
st.sidebar.info("💡 Tip: Use AI Camera Registration for automatic product recognition")

# ---------------- VIEW INVENTORY ---------------- 
if menu == "View Inventory":
    
    st.header("📦 Inventory Status")
    
    try:
        df = get_inventory()
        
        if df.empty:
            st.warning("No products in inventory. Register products to get started!")
        else:
            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Products", len(df))
            
            with col2:
                total_value = (df['price'] * df['stock']).sum()
                st.metric("Inventory Value", f"₹{total_value:.2f}")
            
            with col3:
                low_stock_count = len(df[df['stock'] <= 3])
                st.metric("Low Stock Items", low_stock_count)
            
            with col4:
                out_of_stock = len(df[df['stock'] == 0])
                st.metric("Out of Stock", out_of_stock)
            
            st.markdown("---")
            
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
            
            # Low stock alert
            low_stock = df[df["stock"] <= 3]
            
            if not low_stock.empty:
                st.markdown("---")
                st.warning("⚠️ Low Stock Alert")
                st.dataframe(
                    low_stock[['product_id', 'price', 'stock']],
                    use_container_width=True,
                    hide_index=True
                )
    
    except Exception as e:
        st.error(f"Error loading inventory: {e}")

# ---------------- REGISTER PRODUCT ---------------- 
elif menu == "Register Product":
    
    st.header("➕ Register New Product")
    
    # Registration method selection
    reg_method = st.radio(
        "Registration Method",
        ["📝 Manual Entry", "📷 AI Camera Registration"],
        horizontal=True
    )
    
    st.markdown("---")
    
    if reg_method == "📝 Manual Entry":
        st.subheader("Manual Product Entry")
        
        with st.form("register_form"):
            pid = st.text_input("Product Name / ID", placeholder="e.g., Lays Blue")
            price = st.number_input("Price (₹)", min_value=0.0, step=1.0)
            stock = st.number_input("Initial Stock", min_value=0, step=1)
            
            submitted = st.form_submit_button("Register Product")
            
            if submitted:
                if pid.strip() == "":
                    st.error("Product name cannot be empty!")
                else:
                    try:
                        add_product(pid, price, stock)
                        st.success(f"✅ Product '{pid}' registered successfully!")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Error: {e}")
    
    else:  # AI Camera Registration
        st.subheader("📷 AI-Powered Camera Registration")
        
        # Registration mode selection
        reg_mode = st.radio(
            "Select Registration Mode:",
            ["📸 Single View (Fast)", "🔄 Multi-View (Better Accuracy)"],
            help="Multi-view recommended for cylindrical objects and similar products"
        )
        
        st.info("🤖 Click button below to open camera window")
        
        if reg_mode == "📸 Single View (Fast)":
            if st.button("📷 Open Camera & Capture Product", type="primary", use_container_width=True):
                with st.spinner("Opening camera..."):
                    try:
                        from utils.camera_capture import capture_and_process_product
                        
                        success, product_data, error_msg = capture_and_process_product()
                        
                        if not success:
                            st.error(f"❌ {error_msg}")
                        else:
                            st.success("✅ Product captured and processed!")
                            
                            # Show captured product
                            cropped_rgb = cv2.cvtColor(product_data['crop'], cv2.COLOR_BGR2RGB)
                            st.image(cropped_rgb, caption="Captured Product", width=300)
                            
                            # Store in session state
                            st.session_state['captured_product'] = product_data
                            st.session_state['capture_done'] = True
                    
                    except Exception as e:
                        st.error(f"Error: {e}")
                        import traceback
                        st.code(traceback.format_exc())
        
        else:  # Multi-View
            st.warning("📋 Multi-View Registration: You'll capture 3 views of the same product")
            st.info("""
            **Instructions:**
            1. View 1: Front label facing camera
            2. View 2: Rotate product 45° LEFT
            3. View 3: Rotate product 45° RIGHT
            
            All 3 views will be averaged for better recognition!
            """)
            
            if st.button("📷 Start Multi-View Capture", type="primary", use_container_width=True):
                with st.spinner("Opening camera for multi-view capture..."):
                    try:
                        # Import multi-view capture function
                        import subprocess
                        import sys
                        
                        # Run multi-view registration script
                        st.info("🎥 Camera window opened! Follow on-screen instructions...")
                        
                        # This will open the multi-view registration in a separate window
                        result = subprocess.run(
                            [sys.executable, "register_bottle_multiview.py"],
                            capture_output=True,
                            text=True
                        )
                        
                        if result.returncode == 0:
                            st.success("✅ Multi-view registration completed!")
                            st.balloons()
                            st.info("Product registered successfully with 3 views!")
                        else:
                            st.error(f"❌ Registration failed: {result.stderr}")
                    
                    except Exception as e:
                        st.error(f"Error: {e}")
                        import traceback
                        st.code(traceback.format_exc())
        
        # If product captured, show registration form
        if st.session_state.get('capture_done', False):
            st.markdown("---")
            st.subheader("📝 Enter Product Details")
            
            pid = st.text_input("Product Name / ID", placeholder="e.g., Lays Blue", key="ai_pid")
            price = st.number_input("Price (₹)", min_value=0.0, step=1.0, key="ai_price")
            stock = st.number_input("Initial Stock", min_value=0, step=1, key="ai_stock")
            
            if st.button("💾 Register Product", type="primary"):
                if pid.strip() == "":
                    st.error("Product name cannot be empty!")
                else:
                    try:
                        with st.spinner("🔍 Checking for duplicates..."):
                            from utils.register_product import register_product as register_with_embedding, is_duplicate, get_all_embeddings
                            import cv2
                            
                            product_data = st.session_state['captured_product']
                            fused_embedding = product_data['embedding']
                            
                            # Check duplicates
                            existing_embeddings = get_all_embeddings()
                            if len(existing_embeddings) > 0:
                                if is_duplicate(fused_embedding, existing_embeddings, threshold=0.95):
                                    st.error("❌ DUPLICATE DETECTED! This product is already registered.")
                                    st.stop()
                            
                            st.success("✅ No duplicates found!")
                        
                        with st.spinner("💾 Saving product..."):
                            # Save image
                            image_path = f"data/registered_products/{pid}.jpg"
                            cv2.imwrite(image_path, product_data['crop'])
                            
                            # Register
                            success, message = register_with_embedding(pid, price, stock, fused_embedding)
                            
                            if success:
                                st.success(f"✅ {message}")
                                st.success(f"📸 Image saved: {image_path}")
                                st.balloons()
                                
                                # Clear session state
                                st.session_state['capture_done'] = False
                                st.session_state['captured_product'] = None
                            else:
                                st.error(f"❌ {message}")
                    
                    except Exception as e:
                        st.error(f"Error: {e}")
                        import traceback
                        st.code(traceback.format_exc())

# ---------------- UPDATE STOCK ---------------- 
elif menu == "Update Stock":
    
    st.header("🔄 Update Stock")
    
    try:
        df = get_inventory()
        
        if df.empty:
            st.warning("No products available.")
        else:
            with st.form("update_form"):
                pid = st.selectbox("Select Product", df["product_id"].tolist())
                current_stock = df[df['product_id'] == pid]['stock'].values[0]
                st.info(f"Current Stock: {current_stock} units")
                new_stock = st.number_input("New Stock", min_value=0, step=1, value=int(current_stock))
                
                if st.form_submit_button("Update Stock"):
                    update_stock(pid, new_stock)
                    st.success(f"✅ Stock updated for '{pid}'!")
                    st.rerun()
    
    except Exception as e:
        st.error(f"Error: {e}")

# ---------------- DELETE PRODUCT ---------------- 
elif menu == "Delete Product":
    
    st.header("🗑️ Delete Product")
    st.warning("⚠️ This action cannot be undone!")
    
    try:
        df = get_inventory()
        
        if df.empty:
            st.warning("No products available.")
        else:
            with st.form("delete_form"):
                pid = st.selectbox("Select Product", df["product_id"].tolist())
                product_info = df[df['product_id'] == pid].iloc[0]
                st.info(f"Price: ₹{product_info['price']} | Stock: {product_info['stock']}")
                confirm = st.checkbox("I confirm deletion")
                
                if st.form_submit_button("Delete", type="primary"):
                    if confirm:
                        delete_product(pid)
                        st.success(f"✅ Deleted '{pid}'!")
                        st.rerun()
                    else:
                        st.error("Please confirm!")
    
    except Exception as e:
        st.error(f"Error: {e}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>VisionCart Admin Panel | AI-Powered Smart Store</p>
</div>
""", unsafe_allow_html=True)
