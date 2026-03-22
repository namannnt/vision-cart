# 🚀 VisionCart - Quick Run Guide

## ⚠️ IMPORTANT: Always Activate Virtual Environment First!

Your system check shows you're running Python 3.14 from system instead of the venv where all packages are installed.

### Step 1: Activate Virtual Environment

```cmd
cd VisionCart
venv\Scripts\activate
```

You should see `(venv)` prefix in your terminal.

### Step 2: Verify Installation

```cmd
python system_check.py
```

All libraries should show ✅ now.

---

## 📋 Available Applications

### 1️⃣ Register New Products (Camera-based AI Registration)

```cmd
python register_product_app.py
```

**Instructions:**
- Show product clearly in front of camera
- Press `R` to register product
- Enter product details (ID, price, stock)
- Press `Q` to quit

**Features:**
- ✅ YOLO segmentation
- ✅ Background removal
- ✅ CLIP + DINOv2 embeddings
- ✅ Duplicate detection (>0.95 similarity)
- ✅ 5-rule validation system

---

### 2️⃣ Live Product Recognition

```cmd
python live_recognition.py
```

**Features:**
- ✅ Real-time product detection
- ✅ Multi-frame voting (5 frames)
- ✅ Embedding smoothing (3 frames)
- ✅ Top-K matching (top 3)
- ✅ Brightness normalization
- Shows: Product name, price, stock, confidence

---

### 3️⃣ Live Billing System

```cmd
python live_billing.py
```

**Features:**
- ✅ Automatic product detection
- ✅ Cart management
- ✅ Stock tracking
- ✅ Bill generation
- Press `C` to checkout

---

### 4️⃣ Auto Billing Counter (Hands-free)

```cmd
python auto_billing_counter.py
```

**Features:**
- ✅ Continuous scanning
- ✅ Auto-add to cart (3-second cooldown)
- ✅ Low stock alerts
- ✅ Automatic checkout

---

### 5️⃣ Streamlit Admin Panel

```cmd
streamlit run ui/admin_panel.py
```

**Features:**
- 📦 View inventory
- ➕ Register products (manual or AI camera)
- 🔄 Update stock
- 🗑️ Delete products

---

### 6️⃣ Streamlit Billing Counter UI

```cmd
streamlit run ui/billing_counter.py
```

**Features:**
- 🛒 Live billing interface
- 📊 Real-time stats
- 💰 Cart management
- 🧾 Bill generation

---

### 7️⃣ Advanced Analytics Dashboard

```cmd
streamlit run ui/dashboard_advanced.py
```

**Features:**
- 📈 Sales analytics
- 📊 Stock charts
- 💹 Revenue tracking
- 🎯 Performance metrics

---

## 🔧 Troubleshooting

### Issue: "No module named 'cv2'" or similar errors

**Solution:** You forgot to activate venv!
```cmd
venv\Scripts\activate
```

### Issue: "Could not open camera"

**Solution:** Check camera index in code:
- Default webcam: `cv2.VideoCapture(0)`
- iVCam: `cv2.VideoCapture(2)`
- DroidCam: `cv2.VideoCapture(1)`

### Issue: "No products in database"

**Solution:** Register products first:
```cmd
python register_product_app.py
```

### Issue: CUDA not available (slow performance)

**Current:** PyTorch CPU version installed
**For GPU (RTX 4060):** Install CUDA version:
```cmd
pip uninstall torch torchvision
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

---

## 📊 Current System Status

✅ **Database:** 4 products registered
- controller: ₹1000 (Stock: 1)
- controller A: ₹500 (Stock: 2)
- sanitizer: ₹60 (Stock: 3)
- medicine: ₹60 (Stock: 1)

✅ **YOLO Model:** yolo11x-seg.pt (119.3 MB)
✅ **Directory Structure:** All folders created
⚠️ **GPU:** Not enabled (using CPU - slower but works)

---

## 🎯 Recommended Workflow

1. **First Time Setup:**
   ```cmd
   venv\Scripts\activate
   python system_check.py
   ```

2. **Register Products:**
   ```cmd
   python register_product_app.py
   ```

3. **Test Recognition:**
   ```cmd
   python live_recognition.py
   ```

4. **Start Billing:**
   ```cmd
   python auto_billing_counter.py
   ```

5. **Manage Inventory:**
   ```cmd
   streamlit run ui/admin_panel.py
   ```

---

## 💡 Tips

- **Best Lighting:** Natural daylight or bright white light
- **Background:** Plain white or light-colored surface
- **Distance:** Hold product 30-50cm from camera
- **Orientation:** Front-facing, centered
- **Stability:** Keep product still for 1-2 seconds

---

## 🔍 Pipeline Overview

```
Camera Frame
    ↓
YOLO11x-seg Detection (conf > 0.6)
    ↓
Segmentation & Background Removal
    ↓
5-Rule Validation
    ↓
CLIP Embedding (512D) + DINOv2 Embedding (768D)
    ↓
Embedding Fusion (1280D)
    ↓
Accuracy Boosts (voting, smoothing, top-K)
    ↓
Cosine Similarity Matching (threshold > 0.85)
    ↓
Product Identified ✅
```

---

**Need Help?** Check `DEMO_SCRIPT.md` and `TESTING_GUIDE.md` for detailed instructions.
