# ☁️ VisionCart Cloud Deployment Guide

Complete guide to deploy VisionCart on Hugging Face Spaces + Vercel

---

## 🎯 Architecture

```
Mobile/Desktop Browser (Camera)
         ↓
    Capture Frame (JavaScript)
         ↓
    Send to Backend API
         ↓
Hugging Face Spaces (FastAPI)
         ↓
YOLO + CLIP + DINO Processing
         ↓
    Return Detection Result
         ↓
    Update Frontend (Vercel)
```

---

## 📦 What Changed?

### ❌ Removed:
- `cv2.VideoCapture()` - No more backend camera
- Camera thread - No background processing
- `/video_feed` endpoint - No MJPEG stream

### ✅ Added:
- `/api/detect_frame` - Accept frames from frontend
- Browser camera capture - JavaScript MediaDevices API
- Frame upload logic - FormData POST request

---

## 🚀 Step 1: Deploy Backend to Hugging Face Spaces

### 1.1 Create Hugging Face Account
1. Go to [huggingface.co](https://huggingface.co)
2. Sign up (free)
3. Verify email

### 1.2 Create New Space
1. Click "New Space"
2. Settings:
   - **Name**: `visioncart-backend`
   - **License**: MIT
   - **SDK**: Docker
   - **Hardware**: CPU Basic (free) or T4 GPU ($0.60/hr)
3. Click "Create Space"

### 1.3 Upload Files

Upload these files to your Space:

**Required Files:**
```
app.py                    # Entry point
web_api_cloud.py          # Cloud backend (camera-less)
customer_checkout_backend.py
config.py
requirements_hf.txt       # Dependencies
Dockerfile               # Container config
README_HF.md            # Space description
```

**Required Folders:**
```
models/
  ├── clip/
  ├── dinov2/
  └── yolo/
utils/
  ├── all utility files
database/
  ├── __init__.py
  ├── setup_db.py
  └── visioncart.db
data/
  ├── registered_products/
  └── embeddings/
```

### 1.4 Upload via Git (Recommended)

```bash
# Clone your space
git clone https://huggingface.co/spaces/YOUR_USERNAME/visioncart-backend
cd visioncart-backend

# Copy files from VisionCart
cp ../VisionCart/app.py .
cp ../VisionCart/web_api_cloud.py .
cp ../VisionCart/customer_checkout_backend.py .
cp ../VisionCart/config.py .
cp ../VisionCart/requirements_hf.txt .
cp ../VisionCart/Dockerfile .
cp ../VisionCart/README_HF.md README.md

# Copy folders
cp -r ../VisionCart/models .
cp -r ../VisionCart/utils .
cp -r ../VisionCart/database .
cp -r ../VisionCart/data .

# Add YOLO model
cp ../VisionCart/yolo11x-seg.pt .

# Commit and push
git add .
git commit -m "Initial deployment"
git push
```

### 1.5 Wait for Build

- Hugging Face will build your Docker container
- Check logs for errors
- Build time: ~5-10 minutes
- Once "Running", your backend is live!

### 1.6 Test Backend

```bash
# Health check
curl https://YOUR_USERNAME-visioncart-backend.hf.space/health

# Expected response:
{
  "status": "healthy",
  "products_loaded": 4,
  "cart_size": 0
}
```

---

## 🌐 Step 2: Update Frontend for Cloud

### 2.1 Update Environment Variables

Create `.env.local` in `vision-cart-web/`:

```env
# Hugging Face backend URL
NEXT_PUBLIC_API_URL=https://YOUR_USERNAME-visioncart-backend.hf.space

# WebSocket URL (same as API)
NEXT_PUBLIC_WS_URL=wss://YOUR_USERNAME-visioncart-backend.hf.space
```

### 2.2 Update Billing Page

The billing page needs to:
1. Access browser camera
2. Capture frames
3. Send to backend
4. Display results

**Key changes in `billing/page.tsx`:**

```typescript
// Add camera capture
const videoRef = useRef<HTMLVideoElement>(null);
const canvasRef = useRef<HTMLCanvasElement>(null);

// Start camera
useEffect(() => {
  navigator.mediaDevices.getUserMedia({ 
    video: { 
      width: 640, 
      height: 480,
      facingMode: 'environment' // Use back camera on mobile
    } 
  })
  .then(stream => {
    if (videoRef.current) {
      videoRef.current.srcObject = stream;
    }
  })
  .catch(err => console.error('Camera error:', err));
}, []);

// Capture and send frames
useEffect(() => {
  const interval = setInterval(() => {
    if (!videoRef.current || !canvasRef.current) return;
    
    const canvas = canvasRef.current;
    const video = videoRef.current;
    const ctx = canvas.getContext('2d');
    
    if (!ctx) return;
    
    // Draw video frame to canvas
    canvas.width = 320;
    canvas.height = 320;
    ctx.drawImage(video, 0, 0, 320, 320);
    
    // Convert to blob
    canvas.toBlob(blob => {
      if (!blob) return;
      
      // Send to backend
      const formData = new FormData();
      formData.append('file', blob, 'frame.jpg');
      
      fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/detect_frame`, {
        method: 'POST',
        body: formData
      })
      .then(res => res.json())
      .then(data => console.log('Detection:', data))
      .catch(err => console.error('Detection error:', err));
      
    }, 'image/jpeg', 0.6); // 60% quality for speed
    
  }, 1000); // Send frame every 1 second
  
  return () => clearInterval(interval);
}, []);
```

**Replace video feed:**

```tsx
{/* OLD: Backend camera stream */}
<img src="http://127.0.0.1:8000/video_feed" alt="Camera" />

{/* NEW: Browser camera */}
<video 
  ref={videoRef}
  autoPlay
  playsInline
  muted
  style={{
    width: '100%',
    height: '100%',
    objectFit: 'cover'
  }}
/>
<canvas ref={canvasRef} style={{ display: 'none' }} />
```

---

## 🚀 Step 3: Deploy Frontend to Vercel

### 3.1 Update Vercel Environment Variables

1. Go to Vercel dashboard
2. Select your project
3. Settings → Environment Variables
4. Add:
   - `NEXT_PUBLIC_API_URL`: `https://YOUR_USERNAME-visioncart-backend.hf.space`
   - `NEXT_PUBLIC_WS_URL`: `wss://YOUR_USERNAME-visioncart-backend.hf.space`

### 3.2 Deploy

```bash
cd vision-cart-web
vercel --prod
```

Or push to GitHub and Vercel will auto-deploy.

---

## 🧪 Step 4: Test Complete System

### 4.1 Open Frontend
```
https://your-project.vercel.app
```

### 4.2 Login
- Username: `staff`
- Password: `staff123`

### 4.3 Go to Billing Page

### 4.4 Allow Camera Access
- Browser will ask for camera permission
- Click "Allow"

### 4.5 Test Detection
- Show registered product to camera
- Wait 1-2 seconds
- Product should be detected and added to cart

---

## 📊 Performance Optimization

### Frame Rate
```javascript
// Adjust detection frequency
setInterval(() => {
  captureAndSend();
}, 1000); // 1 second = 1 FPS (recommended)

// For faster detection (uses more bandwidth)
}, 500); // 0.5 seconds = 2 FPS
```

### Image Quality
```javascript
canvas.toBlob(blob => {
  // ...
}, 'image/jpeg', 0.6); // 0.6 = 60% quality

// Lower quality = faster upload
}, 'image/jpeg', 0.4); // 40% quality

// Higher quality = better accuracy
}, 'image/jpeg', 0.8); // 80% quality
```

### Image Size
```javascript
// Smaller = faster
canvas.width = 320;
canvas.height = 320;

// Larger = better accuracy
canvas.width = 640;
canvas.height = 480;
```

---

## 💰 Cost Breakdown

### Free Tier (Recommended for Testing)
- **Hugging Face**: CPU Basic (free, but slow)
- **Vercel**: Free tier (100GB bandwidth/month)
- **Total**: $0/month

### Production Tier
- **Hugging Face**: T4 GPU ($0.60/hour = ~$432/month for 24/7)
- **Vercel**: Pro ($20/month)
- **Total**: ~$452/month

### Cost Optimization
- **Pause Space when not in use**: $0 when paused
- **Use CPU for low traffic**: Free or $0.03/hour
- **Upgrade to GPU only during business hours**: ~$7/day

---

## 🔧 Troubleshooting

### Backend Issues

**Space won't build:**
```bash
# Check Dockerfile syntax
# Verify all files are uploaded
# Check logs in HF Space
```

**Out of memory:**
```bash
# Upgrade to larger hardware
# Or reduce model size (use smaller YOLO)
```

**Slow detection:**
```bash
# Upgrade to GPU (T4 or A10G)
# Or reduce image size in frontend
```

### Frontend Issues

**Camera not working:**
```javascript
// Check HTTPS (camera requires secure context)
// Check browser permissions
// Try different browser
```

**CORS errors:**
```python
# In web_api_cloud.py, update CORS:
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-project.vercel.app",
        "http://localhost:3000"
    ],
    # ...
)
```

**WebSocket not connecting:**
```javascript
// Check WSS (not WS) for HTTPS sites
const ws = new WebSocket('wss://your-space.hf.space/ws/cart');
```

---

## 🎯 Production Checklist

- [ ] Backend deployed to Hugging Face
- [ ] Backend health check passes
- [ ] Frontend deployed to Vercel
- [ ] Environment variables set
- [ ] Camera access works
- [ ] Frame upload works
- [ ] Detection works
- [ ] WebSocket connects
- [ ] Cart updates in real-time
- [ ] Checkout works
- [ ] Products registered
- [ ] Database backed up

---

## 📈 Scaling

### Horizontal Scaling
- Deploy multiple HF Spaces
- Use load balancer (Cloudflare)
- Distribute traffic

### Vertical Scaling
- Upgrade to A10G GPU (faster)
- Increase memory
- Use Redis for caching

### Edge Deployment
- Deploy to Cloudflare Workers
- Use edge functions
- Reduce latency

---

## 🆘 Support

### Hugging Face Issues
- [HF Community Forum](https://discuss.huggingface.co/)
- [HF Discord](https://discord.gg/hugging-face)

### Vercel Issues
- [Vercel Docs](https://vercel.com/docs)
- [Vercel Discord](https://vercel.com/discord)

### VisionCart Issues
- [GitHub Issues](https://github.com/namannnt/vision-cart/issues)

---

## 🎉 Success!

Your VisionCart is now fully cloud-deployed and accessible from anywhere!

**URLs:**
- Frontend: `https://your-project.vercel.app`
- Backend: `https://your-username-visioncart-backend.hf.space`

**Next Steps:**
1. Register your products
2. Train your team
3. Start billing!

---

**Last Updated**: 2026-04-10
**Version**: 3.0 (Cloud Edition)
**Status**: Production Ready ☁️
