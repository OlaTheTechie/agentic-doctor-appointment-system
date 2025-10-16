#!/bin/bash
# Production deployment script

set -e

echo "🚀 Deploying Doctor Appointment System"
echo "======================================"

# Configuration
APP_NAME="doctor-appointment-system"
APP_USER="appointment"
APP_DIR="/opt/$APP_NAME"
SERVICE_NAME="appointment-system"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (use sudo)"
    exit 1
fi

# Create application user
if ! id "$APP_USER" &>/dev/null; then
    echo "Creating application user..."
    useradd -r -s /bin/false -d "$APP_DIR" "$APP_USER"
fi

# Create application directory
echo "Setting up application directory..."
mkdir -p "$APP_DIR"
mkdir -p "$APP_DIR/logs"
mkdir -p "$APP_DIR/data"

# Copy application files
echo "Copying application files..."
cp -r src/ "$APP_DIR/"
cp -r ui/ "$APP_DIR/"
cp main.py "$APP_DIR/"
cp requirements.txt "$APP_DIR/"
cp logging.conf "$APP_DIR/"
cp .env.template "$APP_DIR/"

# Set permissions
chown -R "$APP_USER:$APP_USER" "$APP_DIR"
chmod -R 755 "$APP_DIR"

# Install Python dependencies
echo "Installing Python dependencies..."
cd "$APP_DIR"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Create systemd service
echo "Creating systemd service..."
cat > "/etc/systemd/system/$SERVICE_NAME.service" << EOF
[Unit]
Description=Doctor Appointment System
After=network.target

[Service]
Type=simple
User=$APP_USER
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
ExecStart=$APP_DIR/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create nginx configuration (if nginx is installed)
if command -v nginx &> /dev/null; then
    echo "Creating nginx configuration..."
    cat > "/etc/nginx/sites-available/$APP_NAME" << EOF
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

    ln -sf "/etc/nginx/sites-available/$APP_NAME" "/etc/nginx/sites-enabled/"
    nginx -t && systemctl reload nginx
fi

# Enable and start service
echo "Starting services..."
systemctl daemon-reload
systemctl enable "$SERVICE_NAME"
systemctl start "$SERVICE_NAME"

echo ""
echo "Deployment complete!"
echo ""
echo "Service status:"
systemctl status "$SERVICE_NAME" --no-pager -l
echo ""
echo "Next steps:"
echo "1. Configure your domain in nginx"
echo "2. Set up SSL certificate"
echo "3. Configure environment variables in $APP_DIR/.env"
echo "4. Monitor logs: journalctl -u $SERVICE_NAME -f"
echo ""