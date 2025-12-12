#!/bin/bash
# TermScan VPS Deployment Script
# Hostinger VPS: 72.61.76.62

set -e

echo "🔍 TermScan Deployment Script"
echo "============================="

# Configuration
APP_DIR="/var/www/termscan"
DOMAIN="termscan.candysonic.com"  # Update if different

# Step 1: Install Python 3.11+ if not present
echo ""
echo "📦 Step 1: Checking Python installation..."
if ! command -v python3.11 &> /dev/null; then
    echo "Installing Python 3.11..."
    apt update
    apt install -y python3.11 python3.11-venv python3.11-dev
fi

python3.11 --version

# Step 2: Create app directory
echo ""
echo "📁 Step 2: Setting up application directory..."
mkdir -p $APP_DIR
cd $APP_DIR

# Step 3: Clone/pull the repository
echo ""
echo "📥 Step 3: Getting latest code..."
if [ -d ".git" ]; then
    git pull origin main
else
    git clone https://github.com/candysonic/termscan.git .
fi

# Step 4: Create virtual environment
echo ""
echo "🐍 Step 4: Setting up Python virtual environment..."
python3.11 -m venv venv
source venv/bin/activate

# Step 5: Install dependencies
echo ""
echo "📦 Step 5: Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Step 6: Create .env if not exists
echo ""
echo "⚙️ Step 6: Checking environment configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "⚠️  Please edit .env and add your API keys!"
    echo "    nano $APP_DIR/.env"
fi

# Step 7: Create systemd service
echo ""
echo "🔧 Step 7: Setting up systemd service..."
cat > /etc/systemd/system/termscan.service << EOF
[Unit]
Description=TermScan API
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable termscan
systemctl restart termscan

# Step 8: Configure Nginx reverse proxy
echo ""
echo "🌐 Step 8: Configuring Nginx..."
cat > /etc/nginx/sites-available/termscan << EOF
server {
    listen 80;
    server_name $DOMAIN;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
        proxy_read_timeout 300s;
        proxy_connect_timeout 300s;
    }
}
EOF

# Enable site
ln -sf /etc/nginx/sites-available/termscan /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

# Step 9: Set up SSL with Let's Encrypt
echo ""
echo "🔒 Step 9: Setting up SSL..."
if command -v certbot &> /dev/null; then
    certbot --nginx -d $DOMAIN --non-interactive --agree-tos -m admin@candysonic.com || true
else
    echo "⚠️  Certbot not installed. Install with: apt install certbot python3-certbot-nginx"
fi

echo ""
echo "✅ Deployment Complete!"
echo ""
echo "📊 Service Status:"
systemctl status termscan --no-pager

echo ""
echo "🌐 Your API is available at:"
echo "   http://$DOMAIN (or https:// if SSL configured)"
echo ""
echo "📚 API Docs: http://$DOMAIN/docs"
echo ""
echo "⚠️  Don't forget to:"
echo "   1. Edit .env with your Groq API key: nano $APP_DIR/.env"
echo "   2. Add DNS record for $DOMAIN pointing to this server"
echo "   3. Restart service after .env changes: systemctl restart termscan"
