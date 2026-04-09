# 🔧 Vercel Deployment Fix

## ❌ Problem
Bundle size (5401 MB) exceeds Vercel's limit because:
- Python backend files included
- YOLO model (119 MB)
- PyTorch dependencies

## ✅ Solution
Deploy **frontend only** to Vercel, **backend separately** to Hugging Face.

---

## 🚀 Correct Deployment Steps

### Step 1: Delete Failed Vercel Project

1. Go to [vercel.com/dashboard](https://vercel.com/dashboard)
2. Find `vision-cart-9ofa` project
3. Settings → Delete Project

### Step 2: Deploy Frontend Only (Correct Way)

#### Option A: Via Vercel Dashboard (Easiest)

1. Go to [vercel.com](https://vercel.com)
2. Click "Add New Project"
3. Import `namannnt/vision-cart`
4. **IMPORTANT**: Configure these settings:
   - **Root Directory**: `vision-cart-web` ← This is the key!
   - **Framework Preset**: Next.js (auto-detected)
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`
5. **Environment Variables**:
   - Name: `NEXT_PUBLIC_API_URL`
   - Value: `http://localhost:8000` (temporary)
6. Click "Deploy"

#### Option B: Via Vercel CLI

```bash
cd vision-cart-web

# Install dependencies
npm install

# Build locally first (to test)
npm run build

# Deploy
vercel --prod

# When prompted:
# - Set up and deploy? Yes
# - Which scope? Your account
# - Link to existing project? No
# - Project name? vision-cart
# - Directory? ./ (current directory)
# - Override settings? No
```

### Step 3: Deploy Backend to Hugging Face

1. Go to [huggingface.co/new-space](https://huggingface.co/new-space)
2. Create Space:
   - **Name**: `visioncart-backend`
   - **License**: MIT
   - **SDK**: Docker
   - **Hardware**: CPU Basic (free)
3. Click "Create Space"

4. **Upload Files** (Files tab in your Space):
   
   **Root files:**
   ```
   app.py
   web_api_cloud.py
   customer_checkout_backend.py
   config.py
   Dockerfile
   requirements_hf.txt
   README_HF.md
   yolo11x-seg.pt
   ```
   
   **Folders** (click "Add folder" button):
   ```
   models/
   utils/
   database/
   data/
   ```

5. Wait for build (~5-10 minutes)

6. Test: `https://YOUR_USERNAME-visioncart-backend.hf.space/health`

### Step 4: Connect Frontend to Backend

1. Go to Vercel dashboard
2. Your project → Settings → Environment Variables
3. Edit `NEXT_PUBLIC_API_URL`
4. Change to: `https://YOUR_USERNAME-visioncart-backend.hf.space`
5. Save
6. Deployments tab → Latest deployment → "..." → Redeploy

---

## 🎯 Why This Works

### Before (Wrong):
```
Vercel trying to deploy:
├── vision-cart-web/ (frontend)
├── models/ (119 MB YOLO)
├── *.py (backend)
└── venv/ (Python packages)
Total: 5401 MB ❌
```

### After (Correct):
```
Vercel deploys:
└── vision-cart-web/ (frontend only)
    ├── src/
    ├── public/
    └── package.json
Total: ~50 MB ✅

Hugging Face deploys:
├── app.py
├── models/
├── *.py
└── yolo11x-seg.pt
Total: Unlimited ✅
```

---

## 📝 Quick Checklist

### Vercel Deployment:
- [ ] Root Directory set to `vision-cart-web`
- [ ] Framework detected as Next.js
- [ ] Build succeeds locally (`npm run build`)
- [ ] No Python files included
- [ ] Environment variable added

### Hugging Face Deployment:
- [ ] Space created with Docker SDK
- [ ] All files uploaded
- [ ] Build completes successfully
- [ ] Health endpoint works
- [ ] Products loaded

### Connection:
- [ ] Frontend has correct backend URL
- [ ] CORS configured in backend
- [ ] WebSocket connects
- [ ] Camera works in browser

---

## 🆘 Still Getting Errors?

### Error: "Application Preset: Python"
**Fix**: You selected wrong root directory
- Delete project
- Recreate with Root Directory: `vision-cart-web`

### Error: "Bundle size exceeds limit"
**Fix**: Python files still included
- Check Root Directory is `vision-cart-web`
- Not root of repository

### Error: "Build failed"
**Fix**: Missing dependencies
```bash
cd vision-cart-web
rm -rf node_modules package-lock.json
npm install
npm run build
```

---

## ✅ Expected Result

After correct deployment:

**Vercel (Frontend)**:
- URL: `https://vision-cart-9ofa.vercel.app`
- Size: ~50 MB
- Build time: ~2 minutes
- Status: ✅ Deployed

**Hugging Face (Backend)**:
- URL: `https://USERNAME-visioncart-backend.hf.space`
- Size: ~5 GB (no limit on HF)
- Build time: ~10 minutes
- Status: ✅ Running

---

## 🎉 Success!

Once both are deployed:
1. Visit Vercel URL
2. Login as staff/staff123
3. Go to billing page
4. Allow camera
5. Show product → Detected! ✅

---

**Need help? Check the screenshots in this guide or ask!**
