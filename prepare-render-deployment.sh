#!/bin/bash

# Script to prepare NotesHub for Render deployment
# This ensures all files are ready before pushing to GitHub

echo "=================================================="
echo "  NotesHub - Render Deployment Preparation"
echo "=================================================="
echo ""

# Check if we're in the right directory
if [ ! -f "render-deployment.yaml" ]; then
    echo "❌ Error: render-deployment.yaml not found!"
    echo "   Please run this script from the /app directory"
    exit 1
fi

echo "✅ Found render-deployment.yaml"
echo ""

# Check for required files
echo "Checking required files..."
FILES=(
    "backend/server.py"
    "backend/requirements.txt"
    "frontend/package.json"
    "frontend/vite.config.ts"
    "RENDER_DEPLOYMENT_GUIDE.md"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file - MISSING!"
    fi
done

echo ""
echo "=================================================="
echo "  Next Steps:"
echo "=================================================="
echo ""
echo "1. 📋 Read the deployment guide:"
echo "   cat /app/RENDER_DEPLOYMENT_GUIDE.md"
echo ""
echo "2. 🗄️ Set up MongoDB Atlas (follow guide Part 1)"
echo "   https://www.mongodb.com/cloud/atlas/register"
echo ""
echo "3. 📦 Push your code to GitHub:"
echo "   git init"
echo "   git add ."
echo "   git commit -m 'Ready for Render deployment'"
echo "   git remote add origin https://github.com/YOUR_USERNAME/noteshub-app.git"
echo "   git push -u origin main"
echo ""
echo "4. 🚀 Deploy to Render:"
echo "   - Go to https://dashboard.render.com"
echo "   - Click 'New +' → 'Blueprint'"
echo "   - Select your GitHub repository"
echo "   - Configure environment variables"
echo "   - Click 'Apply'"
echo ""
echo "5. 🎉 Your app will be live in 5-10 minutes!"
echo ""
echo "=================================================="
echo "  Important URLs to bookmark:"
echo "=================================================="
echo ""
echo "  📚 Full Guide: /app/RENDER_DEPLOYMENT_GUIDE.md"
echo "  🔧 Render Dashboard: https://dashboard.render.com"
echo "  🗄️ MongoDB Atlas: https://cloud.mongodb.com"
echo ""
echo "Need help? Check the guide or visit Render docs:"
echo "https://render.com/docs"
echo ""
