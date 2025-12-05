# Flask Integration Files for zCloud Production Server

These files integrate zCLI WebSocket demos with your production Flask server at www.zolo.media.

## Overview

Your Flask server provides the HTTP/HTTPS web interface, while zCLI provides WebSocket real-time communication. This integration allows users to test WebSocket connections directly from your website.

## Current Architecture

```
www.zolo.media
├── Caddy (Port 443)        → HTTPS reverse proxy
├── Gunicorn (Port 8000)    → Flask WSGI server
└── (to add) zCLI WSS (Port 8443) → WebSocket server
```

## Files to Deploy

1. **`demo_websocket_route.txt`** - Route to add to Flask server.py
2. **`zcloud-websocket.service`** - Systemd service for WebSocket server
3. **`demo_websocket.html`** - Template for WebSocket client page (will be created from demo 6)

## Installation Steps

### Step 1: Add WebSocket Demo Route to Flask

```bash
# On your LFS server
cd ~/Projects/zcloud-flask

# Edit server.py and add the route (see demo_websocket_route.txt)
nano server.py
```

Add this after the `/api/posts` route (around line 195):

```python
@app.route('/demo/websocket')
def demo_websocket():
    """WebSocket demo client page"""
    return render_template('demo_websocket.html', page='demo')
```

### Step 2: Copy WebSocket Client Template

```bash
# Create the template file
# (This will be created from Demos/Layer_0/zComm_Demo/lvl2_websocket/6_client_production.html)
nano ~/Projects/zcloud-flask/templates/demo_websocket.html
```

### Step 3: Create WebSocket Server Directory

```bash
sudo mkdir -p /opt/zcloud/websocket
sudo chown zcloud:zcloud /opt/zcloud/websocket

# Copy the production demo
# (This will be created from Demos/Layer_0/zComm_Demo/lvl2_websocket/6_websocket_production.py)
sudo cp 6_websocket_production.py /opt/zcloud/websocket/
```

### Step 4: Install zCLI in Production Environment

```bash
# Activate the zcloud virtual environment
sudo su - zcloud
source /opt/zcloud/venv/bin/activate

# Install zCLI
pip install git+https://github.com/ZoloAi/zolo-zcli.git

# Test installation
python3 -c "from zCLI import zCLI; print('zCLI installed successfully')"
```

### Step 5: Configure Systemd Service

```bash
# Copy systemd service file
sudo cp zcloud-websocket.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable and start the service
sudo systemctl enable zcloud-websocket
sudo systemctl start zcloud-websocket

# Check status
sudo systemctl status zcloud-websocket
```

### Step 6: Open Firewall Port

```bash
# Allow WebSocket port
sudo ufw allow 8443/tcp comment 'zCLI WebSocket Secure'
sudo ufw status
```

### Step 7: Restart Flask to Load New Route

```bash
sudo systemctl restart zcloud-gunicorn
sudo systemctl status zcloud-gunicorn
```

## Testing

### 1. Test Flask Route

```bash
curl https://www.zolo.media/demo/websocket
```

Should return the HTML page.

### 2. Test WebSocket Server

```bash
# Check if it's listening
sudo lsof -i :8443

# Check logs
sudo journalctl -u zcloud-websocket -f
```

### 3. Test from Browser

Visit: `https://www.zolo.media/demo/websocket`

You should see the WebSocket demo client. Click "Connect" to establish a WSS connection.

## Troubleshooting

### WebSocket Server Won't Start

```bash
# Check logs
sudo journalctl -u zcloud-websocket -xe

# Common issues:
# - Port 8443 already in use: sudo lsof -i :8443
# - SSL cert permissions: ls -la /etc/letsencrypt/live/zolo.media/
# - zCLI not installed: sudo -u zcloud /opt/zcloud/venv/bin/pip list | grep zCLI
```

### Can't Connect from Browser

```bash
# Check firewall
sudo ufw status | grep 8443

# Check if server is listening on all interfaces
sudo lsof -i :8443 | grep LISTEN

# Check browser console for errors (F12)
```

### SSL Certificate Errors

```bash
# Verify certificate exists and is readable
sudo ls -la /etc/letsencrypt/live/zolo.media/

# Give zcloud user access (if needed)
sudo usermod -a -G ssl-cert zcloud
```

## Maintenance

### View WebSocket Logs

```bash
# Real-time logs
sudo journalctl -u zcloud-websocket -f

# Last 100 lines
sudo journalctl -u zcloud-websocket -n 100

# Application logs (if configured)
sudo tail -f /var/log/zcloud/websocket.log
```

### Restart WebSocket Server

```bash
sudo systemctl restart zcloud-websocket
sudo systemctl status zcloud-websocket
```

### Update WebSocket Server Code

```bash
# Update the Python file
sudo nano /opt/zcloud/websocket/6_websocket_production.py

# Restart service to apply changes
sudo systemctl restart zcloud-websocket
```

## Uninstallation

```bash
# Stop and disable service
sudo systemctl stop zcloud-websocket
sudo systemctl disable zcloud-websocket

# Remove service file
sudo rm /etc/systemd/system/zcloud-websocket.service
sudo systemctl daemon-reload

# Remove WebSocket directory
sudo rm -rf /opt/zcloud/websocket

# Remove route from server.py
# Remove template from templates/demo_websocket.html

# Close firewall port
sudo ufw delete allow 8443/tcp
```

## Production Checklist

- [ ] Flask route added and server restarted
- [ ] WebSocket template deployed
- [ ] zCLI installed in production venv
- [ ] Systemd service configured and running
- [ ] Firewall port 8443 opened
- [ ] SSL certificates accessible to zcloud user
- [ ] Can access https://www.zolo.media/demo/websocket
- [ ] Can connect to wss://zolo.media:8443
- [ ] Logs are being written and rotated
- [ ] Service starts automatically on reboot

