#!/bin/bash
# ConnectPro — Local Development Startup Script
set -e

echo "================================"
echo "  ConnectPro — Starting Up"
echo "================================"

# Copy .env if not present
if [ ! -f .env ]; then
  cp .env.example .env
  echo "[INFO] Created .env from .env.example — please edit it with your values."
fi

# Install dependencies
echo "[1/4] Installing dependencies..."
pip install -r requirements.txt -q --break-system-packages

# Run migrations
echo "[2/4] Running migrations..."
python manage.py migrate --noinput

# Collect static files
echo "[3/4] Collecting static files..."
python manage.py collectstatic --noinput -v 0

# Create superuser if needed
echo "[4/4] Checking superuser..."
python manage.py shell -c "
from apps.accounts.models import User
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin@connectpro.com', 'admin', 'admin123')
    print('  Superuser created: admin@connectpro.com / admin123')
else:
    print('  Superuser already exists.')
"

echo ""
echo "================================"
echo "  ConnectPro is ready!"
echo "  Visit: http://127.0.0.1:8000"
echo "  Admin:  http://127.0.0.1:8000/admin"
echo "================================"
echo ""

# Start development server
python manage.py runserver
