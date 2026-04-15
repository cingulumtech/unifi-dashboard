# UniFi Network Dashboard

A complete monitoring and management solution for UniFi networks without requiring the UniFi Controller.

## Features

- **Web Control Panel**: SSH-based management interface with pre-configured commands
- **Prometheus Monitoring**: Metrics collection and storage
- **Grafana Dashboards**: Visualization and alerting
- **SQM Persistence**: Automated traffic shaping configuration
- **Controller-Independent**: Works even when UniFi Controller is disabled

## Quick Start

### Prerequisites

- Ubuntu/Debian server
- Docker and Docker Compose
- SSH access to UniFi USG

### Automated Installation

```bash
# Download and run the installer
curl -fsSL https://raw.githubusercontent.com/cingulumtech/unifi-dashboard/main/install.sh | sudo bash
```

Or manually:

```bash
# Clone the repository
git clone https://github.com/cingulumtech/unifi-dashboard.git
cd unifi-dashboard

# Copy environment file and configure
cp .env.example .env
# Edit .env with your USG credentials

# Deploy
sudo docker-compose up -d
```

## Configuration

Edit `.env` file:

```env
USG_HOST=192.168.1.1
USG_USER=Comtex
USG_PASSWORD=your_password
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=your_secure_password
```

## Access URLs

After deployment, access the dashboard at:

- **Control Panel**: http://your-server-ip:8080
- **Grafana**: http://your-server-ip:3000
- **Prometheus**: http://your-server-ip:9090

## Architecture

```
┌─────────────────────────────────────────┐
│  UniFi USG (192.168.1.1)               │
│  ├── PPPoE Connection                  │
│  ├── SQM (HTB/fq_codel)               │
│  └── SSH Access                       │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│  UniFi Dashboard Server                  │
│  ┌──────────────┐  ┌──────────────┐    │
│  │ Control      │  │ Grafana      │    │
│  │ Panel :8080  │  │ :3000        │    │
│  └──────────────┘  └──────────────┘    │
│  ┌──────────────┐                       │
│  │ Prometheus   │                       │
│  │ :9090        │                       │
│  └──────────────┘                       │
└─────────────────────────────────────────┘
```

## Control Panel Commands

Pre-configured SSH commands:

- **Network Status**: `show interfaces`
- **SQM Status**: Traffic shaping verification
- **PPPoE Status**: Connection details
- **System Resources**: CPU, memory, uptime

## SQM Persistence

The solution includes automatic SQM configuration that persists across reboots:

```bash
# Located on USG at:
/config/scripts/post-config.d/apply-sqm.sh
```

This applies 90/36 Mbps shaping on boot.

## Management Commands

```bash
# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Update images
docker-compose pull && docker-compose up -d

# Backup data
tar czf backup-$(date +%Y%m%d).tar.gz grafana/data prometheus/data
```

## Security Notes

- Change default Grafana password
- Use `.env` file for sensitive credentials
- Restrict access to port 8080 (control panel)
- Consider SSL/TLS for production use

## Troubleshooting

### Control Panel Not Responding

```bash
docker-compose logs control-panel
```

### Prometheus Permission Errors

```bash
sudo chown -R 65534:65534 prometheus/data
```

### Grafana Permission Errors

```bash
sudo chown -R 472:472 grafana/data
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

MIT License - See LICENSE file

## Support

For issues and feature requests, please use GitHub Issues.

---

**Built for Cingulum Health Network Infrastructure**
