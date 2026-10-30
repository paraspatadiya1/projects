#!/usr/bin/env bash
# ==============================================================================
# PythonAnywhere Automated Setup & Deployment Script
# ==============================================================================
# Usage in PythonAnywhere Bash Console:
#   cd ~/apiproject
#   bash deploy_pythonanywhere.sh
# ==============================================================================

set -e

echo "🚀 Starting Aura SIS Deployment on PythonAnywhere..."

# 1. Detect Python version (prefer Python 3.10, 3.11, or 3.12)
if command -v python3.12 &>/dev/null; then
    PY_BIN="python3.12"
elif command -v python3.11 &>/dev/null; then
    PY_BIN="python3.11"
elif command -v python3.10 &>/dev/null; then
    PY_BIN="python3.10"
else
    PY_BIN="python3"
fi

echo "🐍 Using Python binary: $PY_BIN"

# 2. Setup Virtual Environment in ~/.virtualenvs/apienv if not already active
VENV_DIR="$HOME/.virtualenvs/apienv"

if [ -z "$VIRTUAL_ENV" ]; then
    if [ ! -d "$VENV_DIR" ]; then
        echo "📦 Creating virtual environment at $VENV_DIR..."
        $PY_BIN -m venv "$VENV_DIR"
    fi
    echo "⚡ Activating virtual environment..."
    source "$VENV_DIR/bin/activate"
else
    echo "✅ Already running inside virtualenv: $VIRTUAL_ENV"
fi

# 3. Upgrade pip and install dependencies
echo "📥 Installing production requirements..."
pip install --upgrade pip
pip install -r requirements.txt

# 4. Apply Database Migrations
echo "🗄️ Running database migrations..."
python manage.py migrate

# 5. Collect Static Files for WhiteNoise & PythonAnywhere static mapping
echo "🎨 Collecting static files..."
python manage.py collectstatic --noinput

# 6. Optional Demo Data
echo "📊 Checking demo database state..."
python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apiproject.settings')
django.setup()
from apiapp.models import Course, Studinfo
if Course.objects.count() == 0:
    print('🌱 No courses found, seeding sample demo data...')
    from django.core.management import call_command
    call_command('seed_data')
else:
    print(f'✅ Found {Course.objects.count()} courses and {Studinfo.objects.count()} students in database.')
"

# 7. Final System Check
echo "🔍 Running Django production check..."
python manage.py check --deploy || python manage.py check

echo ""
echo "======================================================================"
echo "🎉 DEPLOYMENT PREPARATION COMPLETE!"
echo "======================================================================"
echo "Next step in your PythonAnywhere Web Tab:"
echo "1. Go to Web tab: https://www.pythonanywhere.com/user/$USER/webapps/"
echo "2. Set Virtualenv directory: $VENV_DIR"
echo "3. Open 'WSGI configuration file' link and paste contents of 'wsgi_pythonanywhere.py'"
echo "   (Make sure USERNAME is set to: $USER)"
echo "4. In Static Files section, add:"
echo "   URL: /static/"
echo "   Directory: $HOME/apiproject/staticfiles"
echo "5. Click the green 'Reload' button at the top!"
echo "======================================================================"

