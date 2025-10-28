
**deploy.sh** (for easy deployment)
```bash
#!/bin/bash

echo "🚀 Deploying Crypto Screener to Streamlit Cloud"

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found!"
    exit 1
fi

echo "✅ All files are ready for deployment!"
echo "📝 Deployment Steps:"
echo "1. Push this code to GitHub"
echo "2. Go to https://share.streamlit.io"
echo "3. Connect your GitHub repository"
echo "4. Set main file to: app/main.py"
echo "5. Click Deploy!"
echo ""
echo "🌐 Your app will be live at: https://your-app-name.streamlit.app"