#!/bin/bash
# VisionCart - Automated Hugging Face Spaces Deployment

echo "🚀 VisionCart - Hugging Face Spaces Deployment"
echo "=============================================="
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git not found!"
    exit 1
fi

echo "✅ Git found"
echo ""

# Ask for HF username and space name
echo "Enter your Hugging Face username:"
read -p "Username: " HF_USERNAME

if [ -z "$HF_USERNAME" ]; then
    echo "❌ Username cannot be empty"
    exit 1
fi

echo ""
echo "Enter your Space name (e.g., visioncart-backend):"
read -p "Space name: " SPACE_NAME

if [ -z "$SPACE_NAME" ]; then
    echo "❌ Space name cannot be empty"
    exit 1
fi

echo ""
echo "📝 Instructions:"
echo "1. Go to https://huggingface.co/new-space"
echo "2. Create a new Space with:"
echo "   - Name: $SPACE_NAME"
echo "   - SDK: Docker"
echo "   - Hardware: CPU Basic (free)"
echo "3. Press Enter when done..."
read -p ""

echo ""
echo "📦 Preparing files for deployment..."

# Create temporary deployment directory
DEPLOY_DIR="hf_deploy_temp"
rm -rf $DEPLOY_DIR
mkdir -p $DEPLOY_DIR

# Copy required files
echo "Copying files..."
cp app.py $DEPLOY_DIR/
cp web_api_cloud.py $DEPLOY_DIR/
cp customer_checkout_backend.py $DEPLOY_DIR/
cp config.py $DEPLOY_DIR/
cp Dockerfile $DEPLOY_DIR/
cp requirements_hf.txt $DEPLOY_DIR/
cp README_HF.md $DEPLOY_DIR/README.md
cp yolo11x-seg.pt $DEPLOY_DIR/ 2>/dev/null || echo "⚠️  YOLO model not found - download it first"

# Copy directories
cp -r models $DEPLOY_DIR/
cp -r utils $DEPLOY_DIR/
cp -r database $DEPLOY_DIR/
cp -r data $DEPLOY_DIR/

echo "✅ Files prepared"
echo ""

# Clone the space
echo "🔗 Cloning your Hugging Face Space..."
cd $DEPLOY_DIR
git clone https://huggingface.co/spaces/$HF_USERNAME/$SPACE_NAME space_repo

if [ $? -ne 0 ]; then
    echo "❌ Failed to clone Space"
    echo ""
    echo "Make sure:"
    echo "1. You created the Space on Hugging Face"
    echo "2. Your username is correct: $HF_USERNAME"
    echo "3. Space name is correct: $SPACE_NAME"
    echo "4. You're logged in to Hugging Face (git credential helper)"
    echo ""
    exit 1
fi

# Copy files to space repo
echo "📋 Copying files to Space repository..."
cp -r * space_repo/ 2>/dev/null
cd space_repo

# Commit and push
echo ""
echo "📤 Pushing to Hugging Face..."
git add .
git commit -m "Deploy VisionCart backend"
git push

if [ $? -eq 0 ]; then
    echo ""
    echo "=============================================="
    echo "✅ Deployment Successful!"
    echo "=============================================="
    echo ""
    echo "Your backend is deploying at:"
    echo "https://huggingface.co/spaces/$HF_USERNAME/$SPACE_NAME"
    echo ""
    echo "Build will take ~5-10 minutes"
    echo ""
    echo "Your API URL will be:"
    echo "https://$HF_USERNAME-$SPACE_NAME.hf.space"
    echo ""
    echo "Next steps:"
    echo "1. Wait for build to complete"
    echo "2. Test: curl https://$HF_USERNAME-$SPACE_NAME.hf.space/health"
    echo "3. Deploy frontend with this URL"
    echo ""
else
    echo ""
    echo "❌ Push failed"
    echo ""
    echo "You may need to login to Hugging Face:"
    echo "  git config --global credential.helper store"
    echo "  git push (enter your HF token when prompted)"
    echo ""
    exit 1
fi

# Cleanup
cd ../..
rm -rf $DEPLOY_DIR
