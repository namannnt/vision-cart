@echo off
echo ========================================
echo   VisionCart - Deploy to Vercel
echo ========================================
echo.

cd vision-cart-web

echo [1/4] Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed!
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)
echo ✓ Node.js found

echo.
echo [2/4] Installing dependencies...
call npm install
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo ✓ Dependencies installed

echo.
echo [3/4] Building project...
call npm run build
if errorlevel 1 (
    echo ERROR: Build failed
    echo Please check the error messages above
    pause
    exit /b 1
)
echo ✓ Build successful

echo.
echo [4/4] Deploying to Vercel...
echo.
echo IMPORTANT: Make sure you have:
echo 1. Created a Vercel account at https://vercel.com
echo 2. Installed Vercel CLI: npm install -g vercel
echo 3. Logged in: vercel login
echo.
echo Press any key to continue with deployment...
pause >nul

call vercel --prod
if errorlevel 1 (
    echo.
    echo ERROR: Deployment failed
    echo.
    echo If you haven't installed Vercel CLI, run:
    echo   npm install -g vercel
    echo   vercel login
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   ✓ Deployment Complete!
echo ========================================
echo.
echo Your VisionCart frontend is now live!
echo.
echo Next steps:
echo 1. Note your deployment URL from above
echo 2. Update CORS in web_api.py with your URL
echo 3. Start the backend: run_web_api.bat
echo 4. Test your deployment
echo.
pause
