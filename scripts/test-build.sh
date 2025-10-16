#!/bin/bash
# Test build script for React frontend

echo "🚀 Testing React Frontend Build..."
echo "=================================="

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ package.json not found. Please run from frontend directory."
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Type check
echo "🔍 Running type check..."
npm run type-check

# Build the project
echo "🔨 Building project..."
npm run build

# Check if build was successful
if [ -d "build" ]; then
    echo "✅ Build successful!"
    echo "📊 Build size:"
    du -sh build/
    echo ""
    echo "🎯 Ready for deployment!"
    echo "Next steps:"
    echo "1. Deploy to Vercel: vercel --prod"
    echo "2. Or preview locally: npx serve -s build"
else
    echo "❌ Build failed!"
    exit 1
fi