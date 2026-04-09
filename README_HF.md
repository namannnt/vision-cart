---
title: VisionCart AI Backend
emoji: 🛒
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: mit
---

# 🛒 VisionCart - AI-Powered Smart Billing Backend

AI-powered product recognition system using YOLO11, CLIP, and DINOv2.

## Features

- 🤖 Real-time product detection
- 🎯 95-98% accuracy with coin-based size measurement
- ⚡ Adaptive voting (instant for unique products)
- 🔍 Hierarchical size-first matching
- 📦 Automatic inventory management

## API Endpoints

### Detection
- `POST /api/detect_frame` - Upload frame for detection
- `GET /api/status` - Get system status
- `WS /ws/cart` - WebSocket for real-time cart updates

### Registration
- `POST /api/register_frame` - Register new product

### Health
- `GET /health` - Health check

## Usage

```javascript
// Send frame for detection
const formData = new FormData();
formData.append('file', blob);

fetch('https://YOUR-SPACE.hf.space/api/detect_frame', {
  method: 'POST',
  body: formData
});
```

## Tech Stack

- FastAPI
- PyTorch
- YOLO11x-seg
- OpenAI CLIP
- Meta DINOv2
- OpenCV

## Repository

[GitHub](https://github.com/namannnt/vision-cart)
