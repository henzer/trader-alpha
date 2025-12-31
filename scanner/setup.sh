#!/bin/bash

echo "Setting up scanner environment..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r ../requirements.txt
pip install -r requirements.txt

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo ""
    echo "⚠️  Please edit scanner/.env and add your Supabase credentials:"
    echo "   SUPABASE_URL=https://xxxxx.supabase.co"
    echo "   SUPABASE_KEY=eyJhbGc..."
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To activate the environment:"
echo "  source venv/bin/activate"
echo ""
echo "To test Supabase connection:"
echo "  python test_supabase.py"
echo ""
echo "To run the scanner:"
echo "  cd src && python daily_scan.py"