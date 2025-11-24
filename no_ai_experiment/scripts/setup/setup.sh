#!/bin/bash
# Setup script for AI Memory Experiment Multi-Language Support

echo "================================================"
echo "AI Memory Experiment - Multi-Language Setup"
echo "================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""

# Create directories if they don't exist
echo "📁 Creating directories..."
mkdir -p templates
mkdir -p static
mkdir -p experiment_data

echo "✓ Directories created"
echo ""

# Check if language_selection.html exists
if [ ! -f "templates/language_selection.html" ]; then
    echo "⚠️  language_selection.html not found in templates/"
    echo "   Please copy language_selection.html to templates/ folder"
else
    echo "✓ language_selection.html found"
fi

echo ""

# Check if app.py exists
if [ ! -f "app.py" ]; then
    echo "⚠️  app.py not found in current directory"
    echo "   Please make sure app.py is in the root directory"
else
    echo "✓ app.py found"
fi

echo ""
echo "================================================"
echo "Setup Complete!"
echo "================================================"
echo ""
echo "To start the experiment server, run:"
echo "  python3 app.py"
echo ""
echo "Then open your browser to:"
echo "  http://127.0.0.1:8080"
echo ""
echo "Supported languages:"
echo "  • English (en)"
echo "  • 中文 (zh)"
echo ""
echo "To change language manually:"
echo "  http://127.0.0.1:8080/set_lang/en"
echo "  http://127.0.0.1:8080/set_lang/zh"
echo ""
