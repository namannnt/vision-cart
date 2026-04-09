# 🚀 VisionCart - Easy Deployment Instructions

Choose your method:

---

## 🎯 Method 1: Automated Scripts (Easiest)

### Prerequisites
```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Login to Hugging Face (for git)
git config --global credential.helper store
```

### Deploy Backend (Hugging Face)
```bash
# 1. Create Space on huggingface.co first
#    - Name: visioncart-backend
#    - SDK: Docker
#    - Hardware: CPU Basic

# 2. Run deployment script
bash deploy_to_hf.sh

# Follow the prompts
```

### Deploy Frontend (Vercel)
```bash
# Run deployment script
bash deploy_to_vercel.sh

# Enter your HF Space URL when prompted
```

**Done!** ✅

---

## 🎯 Method 2: Manual (5 Minutes)

### Step 1: Deploy to Vercel (2 min)

1. Go to [vercel.com](https://vercel.com)
2. Sign in with GitHub
3. Click "Add New Project"
4. Import `namannnt/vision-cart`
5. Configure:
   - Root Directory: `vision-cart-web`
   - Framework: Next.js
6. Add Environment Variable:
   - `NEXT_PUBLIC_API_URL` = `http://localhost:8000` (temporary)
7. Click "Deploy"

### Step 2: Deploy to Hugging Face (3 min)

1. Go to [huggingface.co/new-space](https://huggingface.co/new-space)
2. Create Space:
   - Name: `visioncart-backend`
   - SDK: Docker
   - Hardware: CPU Basic (free)
3. Upload files (drag & drop):
   ```
   app.py
   web_api_cloud.py
   customer_checkout_backend.py
   config.py
   Dockerfile
   requirements_hf.txt
   README_HF.md
   yolo11x-seg.pt
   models/ (folder)
   utils/ (folder)
   database/ (folder)
   data/ (folder)
   ```
4. Wait for build (~5 min)

### Step 3: Connect (30 sec)

1. Copy your HF Space URL: `https://USERNAME-visioncart-backend.hf.space`
2. Go to Vercel → Your Project → Settings → Environment Variables
3. Edit `NEXT_PUBLIC_API_URL` to your HF Space URL
4. Redeploy

**Done!** ✅

---

## 🎯 Method 3: Using Vercel CLI

### Deploy Frontend
```bash
cd vision-cart-web

# Install dependencies
npm install

# Build
npm run build

# Deploy
vercel --prod

# Add environment variable
vercel env add NEXT_PUBLIC_API_URL production
# Enter: https://YOUR_USERNAME-visioncart-backend.hf.space

# Redeploy
vercel --prod
```

---

## 🎯 Method 4: Using Git (For HF Spaces)

```bash
# Clone your space
git clone https://huggingface.co/spaces/YOUR_USERNAME/visioncart-backend
cd visioncart-backend

# Copy files
cp ../VisionCart/app.py .
cp ../VisionCart/web_api_cloud.py .
cp ../VisionCart/customer_checkout_backend.py .
cp ../VisionCart/config.py .
cp ../VisionCart/Dockerfile .
cp ../VisionCart/requirements_hf.txt .
cp ../VisionCart/README_HF.md README.md
cp ../VisionCart/yolo11x-seg.pt .
cp -r ../VisionCart/models .
cp -r ../VisionCart/utils .
cp -r ../VisionCart/database .
cp -r ../VisionCart/data .

# Commit and push
git add .
git commit -m "Deploy VisionCart"
git push
```

---

## ✅ Verification

### Test Backend
```bash
curl https://YOUR_USERNAME-visioncart-backend.hf.space/health
```

Expected response:
```json
{
  "status": "healthy",
  "products_loaded": 4,
  "cart_size": 0
}
```

### Test Frontend
1. Visit your Vercel URL
2. Login: staff / staff123
3. Go to Billing page
4. Allow camera access
5. Show product → Should detect!

---

## 🆘 Troubleshooting

### Vercel Build Fails
```bash
# Build locally first
cd vision-cart-web
npm install
npm run build

# If successful, push to GitHub and redeploy
```

### HF Space Build Fails
- Check Dockerfile syntax
- Verify all files uploaded
- Check build logs in HF Space

### Camera Not Working
- Must use HTTPS (Vercel provides this)
- Allow camera permissions in browser
- Try different browser

### CORS Errors
Update `web_api_cloud.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-project.vercel.app",
        "http://localhost:3000"
    ],
    # ...
)
```

---

## 💰 Cost

### Free Tier
- Vercel: Free (100GB bandwidth)
- HF Spaces: CPU Basic (free, slow)
- **Total: $0/month**

### Production
- Vercel: Pro ($20/month)
- HF Spaces: T4 GPU ($0.60/hour)
- **Total: ~$452/month for 24/7**

### Smart Option
- Pause HF Space when not in use
- Only run during business hours (8 hours)
- **Cost: ~$7/day**

---

## 📞 Need Help?

1. Read: `CLOUD_DEPLOYMENT_GUIDE.md` (detailed guide)
2. Check: GitHub Issues
3. Ask: In the repository discussions

---

**Good luck! 🚀**
