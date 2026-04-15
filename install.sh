#!/bin/bash
set -e

REPO_URL="${REPO_URL:-https://github.com/cingulumtech/unifi-dashboard.git}"
INSTALL_DIR="${INSTALL_DIR:-/opt/unifi-dashboard}"
USG_HOST="${USG_HOST:-192.168.1.1}"
USG_USER="${USG_USER:-Comtex}"
USG_PASSWORD="${USG_PASSWORD:-}"

echo "UniFi Network Dashboard - Deployment Script"
echo ""

if [ "$EUID" -ne 0 ]; then 
   echo "Please run as root or with sudo"
   exit 1
fi

if [ -z "$USG_PASSWORD" ]; then
    echo "USG Configuration"
    read -p "USG IP [192.168.1.1]: " input_host
    USG_HOST=${input_host:-192.168.1.1}
    
    read -p "USG Username [Comtex]: " input_user
    USG_USER=${input_user:-Comtex}
    
    read -s -p "USG Password: " USG_PASSWORD
    echo ""
fi

echo ""
echo "Installing dependencies..."
apt-get update
apt-get install -y docker.io docker-compose git curl

systemctl enable docker
systemctl start docker

echo ""
echo "Cloning repository..."
if [ -d "$INSTALL_DIR" ]; then
    mv "$INSTALL_DIR" "${INSTALL_DIR}.backup.$(date +%Y%m%d%H%M%S)"
fi

git clone "$REPO_URL" "$INSTALL_DIR"
cd "$INSTALL_DIR"

echo ""
echo "Configuring environment..."

cat > .env << EOF
USG_HOST=$USG_HOST
USG_USER=$USG_USER
USG_PASSWORD=$USG_PASSWORD
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=cingulum$(openssl rand -hex 4)
DOMAIN=${DOMAIN:-}
LETSENCRYPT_EMAIL=${LETSENCRYPT_EMAIL:-}
EOF

echo "Configuration saved to .env"

echo ""
echo "Starting services..."
docker-compose pull
docker-compose up -d

echo ""
echo "Waiting for services to initialize..."
sleep 10

echo ""
echo "Enabling SNMP on USG..."
sshpass -p "$USG_PASSWORD" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 "${USG_USER}@${USG_HOST}" "configure\nset service snmp community public client 100.87.5.16\ncommit\nsave\nexit" 2>/dev/null || echo "SNMP configuration requires manual setup"

echo ""
echo "Deployment Complete!"
echo ""
echo "Access URLs:"
echo "  Control Panel: http://$(hostname -I | awk '{print $1}'):8080"
echo "  Prometheus:    http://$(hostname -I | awk '{print $1}'):9090"
echo "  Grafana:       http://$(hostname -I | awk '{print $1}'):3000"
echo ""
echo "Grafana Login: admin / $(grep GRAFANA_ADMIN_PASSWORD .env | cut -d= -f2)"
echo ""
echo "Management Commands:"
echo "  cd $INSTALL_DIR"
echo "  docker-compose logs -f"
echo "  docker-compose restart"
echo ""
