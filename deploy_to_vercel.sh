#!/bin/bash
# VisionCart - Automated Vercel Deployment

echo "🚀 VisionCart - Vercel Deployment"
echo "=================================="
echo ""

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found!"
    echo ""
    echo "Install it with:"
    echo "  npm install -g vercel"
    echo ""
    exit 1
fi

echo "✅ Vercel CLI found"
echo ""

# Check if logged in
echo "Checking Vercel login status..."
vercel whoami &> /dev/null
if [ $? -ne 0 ]; then
    echo "❌ Not logged in to Vercel"
    echo ""
    echo "Please login first:"
    echo "  vercel login"
    echo ""
    exit 1
fi

echo "✅ Logged in to Vercel"
echo ""

# Navigate to frontend directory
cd vision-cart-web

echo "📦 Installing dependencies..."
npm install

echo ""
echo "🔨 Building project..."
npm run build

if [ $? -ne 0 ]; then
    echo "❌ Build failed!"
    exit 1
fi

echo ""
echo "✅ Build successful"
echo ""

# Ask for backend URL
echo "Enter your Hugging Face Space URL:"
echo "(e.g., https://username-visioncart-backend.hf.space)"
read -p "URL: " HF_URL

if [ -z "$HF_URL" ]; then
    echo "❌ URL cannot be empty"
    exit 1
fi

echo ""
echo "🚀 Deploying to Vercel..."
echo ""

# Deploy with environment variable
vercel --prod -e NEXT_PUBLIC_API_URL="$HF_URL"

if [ $? -eq 0 ]; then
    echo ""
    echo "=================================="
    echo "✅ Deployment Successful!"
    echo "=================================="
    echo ""
    echo "Your VisionCart frontend is now live!"
    echo ""
    echo "Next steps:"
    echo "1. Visit your Vercel URL"
    echo "2. Login as staff/staff123"
    echo "3. Test the billing page"
    echo ""
else
    echo ""
    echo "❌ Deployment failed"
    echo "Check the error messages above"
    exit 1
fi
