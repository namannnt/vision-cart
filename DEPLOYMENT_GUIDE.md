# 🚀 VisionCart Deployment Guide

Complete guide to deploy VisionCart to production.

---

## 📋 Deployment Overview

VisionCart consists of two components:

1. **Frontend (Next.js)** - Web interface for admin, billing, inventory
2. **Backend (FastAPI + Python)** - AI detection, camera processing, API

### Deployment Options

| Component | Recommended | Alternative |
|-----------|-------------|-------------|
| **Frontend** | Vercel (Free) | Netlify, AWS Amplify |
| **Backend** | Local Server | VPS (DigitalOcean, AWS EC2) |

---

## 🎯 Quick Deploy (Recommended)

### Option 1: Frontend on Vercel + Backend Local

**Best for**: Small stores, testing, development

**Pros**: 
- Free frontend hosting
- Easy setup
- Fast deployment

**Cons**: 
- Backend must run locally
- Requires port forwarding for remote access

---

## 📦 Frontend Deployment (Vercel)

### Prerequisites
- GitHub account
- Vercel account (free)
- Code pushed to GitHub

### Step 1: Prepare for Deployment

1. **Update API endpoint** for production:

```bash
cd VisionCart/vision-cart-web
```

Create `.env.local` file:
```env
NEXT_PUBLIC_API_URL=http://YOUR_SERVER_IP:8000
```

2. **Build test locally**:
```bash
npm run build
```

### Step 2: Deploy to Vercel

#### Method A: Vercel Dashboard (Easiest)

1. Go to [vercel.com](https://vercel.com)
2. Click "Add New Project"
3. Import your GitHub repository
4. Configure:
   - **Framework Preset**: Next.js
   - **Root Directory**: `VisionCart/vision-cart-web`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`
5. Add Environment Variable:
   - Key: `NEXT_PUBLIC_API_URL`
   - Value: `http://YOUR_SERVER_IP:8000`
6. Click "Deploy"

#### Method B: Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
cd VisionCart/vision-cart-web
vercel

# Follow prompts:
# - Link to existing project? No
# - Project name: vision-cart
# - Directory: ./
# - Override settings? No

# Deploy to production
vercel --prod
```

### Step 3: Configure Custom Domain (Optional)

1. In Vercel dashboard, go to your project
2. Settings → Domains
3. Add your domain (e.g., `visioncart.yourdomain.com`)
4. Follow DNS configuration instructions

---

## 🖥️ Backend Deployment

### Option 1: Local Server (Recommended for Start)

**Best for**: Single store, local network access

#### Setup

1. **Ensure backend is running**:
```bash
cd VisionCart
venv\Scripts\activate
python web_api.py
```

2. **Configure firewall** (Windows):
```powershell
# Allow port 8000
netsh advfirewall firewall add rule name="VisionCart API" dir=in action=allow protocol=TCP localport=8000
```

3. **Get your local IP**:
```bash
ipconfig
# Look for IPv4 Address (e.g., 192.168.1.100)
```

4. **Update frontend** to use this IP:
```env
NEXT_PUBLIC_API_URL=http://192.168.1.100:8000
```

5. **Access from other devices** on same network:
```
http://192.168.1.100:8000
```

#### Keep Backend Running

Create `start_backend.bat`:
```batch
@echo off
cd /d "%~dp0"
call venv\Scripts\activate
python web_api.py
pause
```

**For 24/7 operation**, use Windows Task Scheduler:
1. Open Task Scheduler
2. Create Basic Task
3. Trigger: At startup
4. Action: Start program → `start_backend.bat`

---

### Option 2: Cloud VPS (Production)

**Best for**: Multiple stores, remote access, scalability

#### Recommended Providers

| Provider | Price | Specs | Best For |
|----------|-------|-------|----------|
| **DigitalOcean** | $6/mo | 1GB RAM, 1 CPU | Small stores |
| **AWS EC2** | $8/mo | t3.micro | Enterprise |
| **Linode** | $5/mo | 1GB RAM | Budget |
| **Hetzner** | €4/mo | 2GB RAM | Europe |

#### Deploy to Ubuntu VPS

1. **Create VPS** (Ubuntu 22.04 LTS)

2. **Connect via SSH**:
```bash
ssh root@YOUR_SERVER_IP
```

3. **Install dependencies**:
```bash
# Update system
apt update && apt upgrade -y

# Install Python 3.12
apt install python3.12 python3.12-venv python3-pip -y

# Install system dependencies
apt install libgl1-mesa-glx libglib2.0-0 -y

# Install camera support (if using USB camera)
apt install v4l-utils -y
```

4. **Upload project**:
```bash
# On your local machine
scp -r VisionCart root@YOUR_SERVER_IP:/root/
```

Or use Git:
```bash
# On VPS
cd /root
git clone https://github.com/namannnt/vision-cart.git
cd vision-cart
```

5. **Setup Python environment**:
```bash
cd /root/vision-cart
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

6. **Configure camera** (if using USB):
```bash
# List cameras
v4l2-ctl --list-devices

# Test camera
python3 find_camera.py
```

7. **Run backend**:
```bash
python web_api.py
```

8. **Setup systemd service** (auto-start):

Create `/etc/systemd/system/visioncart.service`:
```ini
[Unit]
Description=VisionCart Backend API
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/vision-cart
Environment="PATH=/root/vision-cart/venv/bin"
ExecStart=/root/vision-cart/venv/bin/python web_api.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
systemctl daemon-reload
systemctl enable visioncart
systemctl start visioncart
systemctl status visioncart
```

9. **Configure firewall**:
```bash
ufw allow 8000/tcp
ufw enable
```

10. **Setup Nginx reverse proxy** (optional, for HTTPS):

```bash
apt install nginx certbot python3-certbot-nginx -y
```

Create `/etc/nginx/sites-available/visioncart`:
```nginx
server {
    listen 80;
    server_name YOUR_DOMAIN.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

Enable:
```bash
ln -s /etc/nginx/sites-available/visioncart /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

Get SSL certificate:
```bash
certbot --nginx -d YOUR_DOMAIN.com
```

---

## 🔐 Security Configuration

### 1. Environment Variables

Create `.env` file in backend:
```env
# Database
DATABASE_PATH=database/visioncart.db

# Security
SECRET_KEY=your-secret-key-here
ALLOWED_ORIGINS=https://your-frontend.vercel.app

# Camera
CAMERA_INDEX=0
```

### 2. Update CORS in `web_api.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-frontend.vercel.app",
        "http://localhost:3000"  # For development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3. Add Authentication (Optional)

Install:
```bash
pip install python-jose[cryptography] passlib[bcrypt]
```

Add JWT authentication to protect admin routes.

---

## 📊 Monitoring & Maintenance

### 1. Check Backend Status

```bash
# On VPS
systemctl status visioncart

# View logs
journalctl -u visioncart -f
```

### 2. Monitor Resources

```bash
# CPU and memory
htop

# Disk space
df -h

# Camera status
v4l2-ctl --list-devices
```

### 3. Backup Database

```bash
# Create backup script
cat > /root/backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
cp /root/vision-cart/database/visioncart.db /root/backups/visioncart_$DATE.db
# Keep only last 7 days
find /root/backups -name "visioncart_*.db" -mtime +7 -delete
EOF

chmod +x /root/backup.sh

# Add to crontab (daily at 2 AM)
crontab -e
# Add: 0 2 * * * /root/backup.sh
```

---

## 🌐 Domain & SSL Setup

### 1. Get Domain

Purchase from:
- Namecheap
- GoDaddy
- Google Domains
- Cloudflare

### 2. Configure DNS

Add A records:
```
Type: A
Name: @
Value: YOUR_SERVER_IP

Type: A
Name: api
Value: YOUR_SERVER_IP
```

### 3. SSL Certificate

Using Certbot (free):
```bash
certbot --nginx -d yourdomain.com -d api.yourdomain.com
```

Auto-renewal:
```bash
certbot renew --dry-run
```

---

## 🧪 Testing Deployment

### 1. Test Frontend

```bash
# Visit your Vercel URL
https://your-project.vercel.app

# Check:
- Login page loads
- Can login as admin/staff
- All pages accessible
```

### 2. Test Backend

```bash
# Health check
curl http://YOUR_SERVER_IP:8000/health

# Get products
curl http://YOUR_SERVER_IP:8000/api/products

# WebSocket (use browser console)
const ws = new WebSocket('ws://YOUR_SERVER_IP:8000/ws');
ws.onmessage = (e) => console.log(e.data);
```

### 3. Test Camera

```bash
# On server
python find_camera.py

# Check video feed
http://YOUR_SERVER_IP:8000/video_feed
```

---

## 🚨 Troubleshooting

### Frontend Issues

**Build fails on Vercel**:
```bash
# Check locally first
npm run build

# Common fixes:
npm install
rm -rf .next node_modules
npm install
npm run build
```

**API not connecting**:
- Check `NEXT_PUBLIC_API_URL` environment variable
- Verify backend is running
- Check firewall rules
- Test API directly: `curl http://YOUR_SERVER_IP:8000/health`

### Backend Issues

**Camera not detected**:
```bash
# List cameras
ls /dev/video*

# Test camera
python find_camera.py

# Check permissions
sudo usermod -a -G video $USER
```

**Service won't start**:
```bash
# Check logs
journalctl -u visioncart -n 50

# Common issues:
- Python path incorrect
- Missing dependencies
- Camera not available
- Port already in use
```

**High CPU usage**:
- Reduce camera FPS in `web_api.py`
- Use smaller YOLO model
- Enable GPU acceleration

---

## 💰 Cost Estimate

### Minimal Setup (Local)
- Frontend: Free (Vercel)
- Backend: Free (local server)
- Domain: $12/year (optional)
- **Total: $0-12/year**

### Production Setup (VPS)
- Frontend: Free (Vercel)
- Backend: $6/month (DigitalOcean)
- Domain: $12/year
- SSL: Free (Let's Encrypt)
- **Total: ~$84/year**

### Enterprise Setup
- Frontend: $20/month (Vercel Pro)
- Backend: $40/month (AWS EC2 t3.medium)
- Domain: $12/year
- CDN: $10/month (Cloudflare)
- **Total: ~$852/year**

---

## 📈 Scaling

### Horizontal Scaling

1. **Multiple cameras**: Run multiple backend instances
2. **Load balancer**: Nginx or AWS ALB
3. **Database**: PostgreSQL instead of SQLite
4. **Redis**: Cache product embeddings

### Vertical Scaling

1. **GPU**: Add NVIDIA GPU for 10x faster detection
2. **More RAM**: Handle more concurrent requests
3. **SSD**: Faster database access

---

## ✅ Post-Deployment Checklist

- [ ] Frontend deployed and accessible
- [ ] Backend running and healthy
- [ ] Camera working and detected
- [ ] Database backed up
- [ ] SSL certificate installed
- [ ] Monitoring setup
- [ ] Firewall configured
- [ ] Admin credentials changed
- [ ] Test all features
- [ ] Document server details

---

## 📞 Support

For deployment issues:
1. Check logs: `journalctl -u visioncart -f`
2. Test components individually
3. Review this guide
4. Check GitHub issues

---

## 🎉 Success!

Your VisionCart is now deployed and ready for production use!

**Next steps**:
1. Register your products
2. Train staff on the system
3. Monitor performance
4. Collect feedback
5. Iterate and improve

---

**Last Updated**: 2026-04-10
**Version**: 2.0
**Status**: Production Ready ✅
