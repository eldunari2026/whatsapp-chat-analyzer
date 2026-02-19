#!/usr/bin/env bash
# Oracle Cloud Always-Free ARM VM setup script
# Run as root (or with sudo) on a fresh Ubuntu 22.04+ ARM instance
set -euo pipefail

echo "=== WhatsApp Chat Analyzer - Oracle Cloud Setup ==="

# ── 1. System updates ──
echo "[1/6] Updating system packages..."
apt-get update && apt-get upgrade -y
apt-get install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx git tesseract-ocr curl

# ── 2. Install Ollama ──
echo "[2/6] Installing Ollama..."
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama and pull the model
systemctl enable ollama
systemctl start ollama
sleep 5

echo "[2/6] Pulling llama3.1:8b model (~4.7GB)..."
ollama pull llama3.1:8b

# ── 3. Clone project ──
echo "[3/6] Setting up project..."
APP_DIR="/opt/whatsapp-analyzer"
mkdir -p "$APP_DIR"

# If running from the repo, copy files; otherwise clone
if [ -d "/tmp/ai-agent" ]; then
    cp -r /tmp/ai-agent/* "$APP_DIR/"
else
    echo "  Copy your project files to $APP_DIR"
    echo "  Or: git clone <your-repo-url> $APP_DIR"
fi

# ── 4. Python environment ──
echo "[4/6] Setting up Python environment..."
cd "$APP_DIR"
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt

# ── 5. Systemd service ──
echo "[5/6] Creating systemd service..."
cp deploy/systemd/whatsapp-api.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable whatsapp-api
systemctl start whatsapp-api

# ── 6. Nginx reverse proxy ──
echo "[6/6] Configuring Nginx..."
cp deploy/nginx.conf /etc/nginx/sites-available/whatsapp-api
ln -sf /etc/nginx/sites-available/whatsapp-api /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

echo ""
echo "=== Setup complete! ==="
echo "API running on port 8000 (behind Nginx on port 80)"
echo ""
echo "Next steps:"
echo "  1. Point your domain to this VM's public IP"
echo "  2. Run: certbot --nginx -d your-domain.com"
echo "  3. Set VITE_API_URL=https://your-domain.com in your Netlify frontend"
echo ""
echo "Test: curl http://localhost/api/health"
