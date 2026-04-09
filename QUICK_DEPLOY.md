# ⚡ Quick Deploy Guide

Get VisionCart live in 10 minutes!

---

## 🎯 Fastest Path to Deployment

### Step 1: Deploy Frontend (2 minutes)

#### Option A: Vercel (Recommended - Free)

1. **Push to GitHub** (if not already):
```bash
cd VisionCart
git add .
git commit -m "Ready for deployment"
git push origin master
```

2. **Deploy to Vercel**:
   - Go to [vercel.com](https://vercel.com)
   - Click "Add New Project"
   - Import `namannnt/vision-cart`
   - Set Root Directory: `vision-cart-web`
   - Click "Deploy"
   - Done! ✅

Your frontend is now live at: `https://your-project.vercel.app`

---

### Step 2: Start Backend (1 minute)

#### On Your Local Machine:

1. **Double-click**: `run_web_api.bat`

2. **Get your local IP**:
```bash
ipconfig
# Look for IPv4 Address (e.g., 192.168.1.100)
```

3. **Allow firewall** (Windows will prompt - click "Allow")

Backend is now running at: `http://192.168.1.100:8000`

---

### Step 3: Connect Frontend to Backend (2 minutes)

1. **Go to Vercel Dashboard**
   - Select your project
   - Settings → Environment Variables

2. **Add variable**:
   - Name: `NEXT_PUBLIC_API_URL`
   - Value: `http://YOUR_LOCAL_IP:8000`
   - Click "Save"

3. **Redeploy**:
   - Go to Deployments tab
   - Click "..." on latest deployment
   - Click "Redeploy"

---

### Step 4: Test (1 minute)

1. **Open your Vercel URL**: `https://your-project.vercel.app`

2. **Login**:
   - Username: `admin`
   - Password: `admin123`

3. **Test features**:
   - ✅ Admin dashboard loads
   - ✅ Inventory page shows products
   - ✅ Billing page shows camera feed

---

## 🎉 You're Live!

Your VisionCart is now deployed and accessible from anywhere!

### Access URLs:
- **Frontend**: `https://your-project.vercel.app`
- **Backend**: `http://YOUR_LOCAL_IP:8000` (local network only)

---

## 🔧 Quick Fixes

### "Cannot connect to backend"

**Fix 1**: Check backend is running
```bash
# Should see: "Uvicorn running on http://0.0.0.0:8000"
```

**Fix 2**: Check firewall
```bash
# Windows: Allow port 8000
netsh advfirewall firewall add rule name="VisionCart" dir=in action=allow protocol=TCP localport=8000
```

**Fix 3**: Verify IP address
```bash
ipconfig
# Use the IPv4 Address shown
```

### "Camera not working"

**Fix**: Update camera index in `web_api.py`:
```python
# Try different values: 0, 1, or 2
cap = cv2.VideoCapture(1)  # Change this number
```

### "Build failed on Vercel"

**Fix**: Build locally first
```bash
cd vision-cart-web
npm install
npm run build
# If successful, push to GitHub and redeploy
```

---

## 🌐 Access from Other Devices

### Same Network (Free)
- Use your local IP: `http://192.168.1.100:8000`
- Works on: Phones, tablets, other computers on same WiFi

### Internet Access (Requires Setup)
- Option 1: Port forwarding on router
- Option 2: Deploy backend to VPS (see DEPLOYMENT_GUIDE.md)
- Option 3: Use ngrok for testing

---

## 📱 Mobile Access (Same Network)

1. **Get your PC's IP**: `ipconfig`
2. **On phone/tablet**, open browser
3. **Visit**: `https://your-project.vercel.app`
4. **Backend auto-connects** to `http://192.168.1.100:8000`

---

## 🚀 Next Steps

### For Testing:
- ✅ You're done! Start using VisionCart

### For Production:
1. Deploy backend to VPS (see DEPLOYMENT_GUIDE.md)
2. Get custom domain
3. Setup SSL certificate
4. Configure backups

---

## 💡 Pro Tips

### Keep Backend Running 24/7

**Method 1**: Windows Task Scheduler
1. Open Task Scheduler
2. Create Basic Task
3. Trigger: At startup
4. Action: `run_web_api.bat`

**Method 2**: Run as Windows Service
```bash
# Install NSSM (Non-Sucking Service Manager)
# Then create service pointing to run_web_api.bat
```

### Improve Performance

1. **Use GPU** (if available):
```bash
pip uninstall torch torchvision
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

2. **Reduce camera resolution** in `web_api.py`:
```python
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
```

---

## 📊 Deployment Status

After deployment, you should see:

### Frontend (Vercel):
- ✅ Build successful
- ✅ Deployment live
- ✅ Environment variables set
- ✅ Custom domain (optional)

### Backend (Local):
- ✅ Server running on port 8000
- ✅ Camera detected
- ✅ Products loaded
- ✅ WebSocket active

---

## 🆘 Need Help?

1. **Check logs**:
   - Frontend: Vercel dashboard → Logs
   - Backend: Terminal window running web_api.py

2. **Test components**:
   - Backend health: `http://localhost:8000/health`
   - API products: `http://localhost:8000/api/products`
   - Camera feed: `http://localhost:8000/video_feed`

3. **Review guides**:
   - Full deployment: `DEPLOYMENT_GUIDE.md`
   - Troubleshooting: `README.md`

---

## ⏱️ Time Breakdown

- Frontend deploy: 2 minutes
- Backend start: 1 minute
- Connect them: 2 minutes
- Testing: 1 minute
- **Total: ~6 minutes** ⚡

---

## 🎯 Success Checklist

- [ ] Frontend deployed to Vercel
- [ ] Backend running locally
- [ ] Environment variable set
- [ ] Can access frontend URL
- [ ] Can login to admin panel
- [ ] Camera feed visible on billing page
- [ ] Products showing in inventory
- [ ] Can detect products

---

**Congratulations! Your VisionCart is now live! 🎉**

For advanced deployment options, see `DEPLOYMENT_GUIDE.md`

---

**Last Updated**: 2026-04-10
**Deployment Time**: ~6 minutes
**Difficulty**: Easy ⭐
