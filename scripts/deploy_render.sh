#!/bin/bash
# Render deployment script
set -e

echo "🚀 Deploying to Render..."
echo "=========================="

# Check if we're in the right directory
if [ ! -f "Dockerfile" ]; then
    echo "❌ Dockerfile not found. Please run from backend directory."
    exit 1
fi

# Build and test Docker image locally first
echo "🔨 Building Docker image locally..."
docker build -t doctor-appointment-system .

echo "🧪 Testing Docker image..."
docker run --rm -d -p 8000:8000 --name test-appointment doctor-appointment-system

# Wait for container to start
sleep 10

# Test health endpoint
if curl -f http://localhost:8000/health; then
    echo "✅ Health check passed"
else
    echo "❌ Health check failed"
    docker stop test-appointment
    exit 1
fi

# Stop test container
docker stop test-appointment

echo "🎯 Docker image ready for Render deployment"
echo ""
echo "📋 Next steps:"
echo "1. Push your code to GitHub"
echo "2. Connect your GitHub repo to Render"
echo "3. Use the render.yaml blueprint for configuration"
echo "4. Set environment variables in Render dashboard:"
echo "   - GROQ_API_KEY"
echo "   - OPENAI_API_KEY"
echo "   - ALLOWED_ORIGINS (include your Streamlit app URL)"
echo ""
echo "🌐 Your backend will be available at:"
echo "   https://your-app-name.onrender.com"