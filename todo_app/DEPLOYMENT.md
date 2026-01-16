# Deployment Guide - Todo App for Odoo 17

This guide covers deployment of the Todo App module to various environments.

## 📋 Prerequisites

- Odoo 17.0 Community or Enterprise
- Python 3.10+
- PostgreSQL 12+
- Git (optional)

## 🖥️ Local Development

### 1. Clone/Copy Module

```bash
# Option A: Clone from repository
cd /path/to/odoo/addons
git clone <repo-url> todo_app

# Option B: Copy folder
cp -r todo_app /path/to/odoo/addons/
```

### 2. Add to Addons Path

Edit `odoo.conf`:
```ini
[options]
addons_path = /path/to/odoo/addons,/path/to/custom/addons
```

Or start Odoo with:
```bash
./odoo-bin --addons-path=/path/to/odoo/addons,/path/to/custom/addons
```

### 3. Update Apps List

```bash
# Via command line
./odoo-bin -d your_database -u base --stop-after-init

# Or via UI: Apps → Update Apps List
```

### 4. Install Module

```bash
# Via command line
./odoo-bin -d your_database -i todo_app --stop-after-init

# Or via UI: Apps → Search "Todo App" → Install
```

## 🐳 Docker Deployment

### docker-compose.yml

```yaml
version: '3.8'
services:
  odoo:
    image: odoo:17.0
    depends_on:
      - db
    ports:
      - "8069:8069"
    volumes:
      - odoo-web-data:/var/lib/odoo
      - ./addons:/mnt/extra-addons
      - ./config:/etc/odoo
    environment:
      - HOST=db
      - USER=odoo
      - PASSWORD=odoo

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=postgres
      - POSTGRES_PASSWORD=odoo
      - POSTGRES_USER=odoo
    volumes:
      - odoo-db-data:/var/lib/postgresql/data

volumes:
  odoo-web-data:
  odoo-db-data:
```

### Odoo Config (config/odoo.conf)

```ini
[options]
addons_path = /mnt/extra-addons
admin_passwd = admin
db_host = db
db_port = 5432
db_user = odoo
db_password = odoo
```

### Deploy Steps

```bash
# 1. Copy module to addons folder
cp -r todo_app ./addons/

# 2. Start containers
docker-compose up -d

# 3. Install module via UI or CLI
docker-compose exec odoo odoo -d mydb -i todo_app --stop-after-init
```

## 🏠 Mac Mini with Home Internet Deployment

This guide covers deploying Odoo with the Todo App on a Mac Mini at home, accessible via the internet.

### Prerequisites

- Mac Mini running macOS Monterey or later
- Minimum 8GB RAM (16GB recommended)
- 50GB free disk space
- Home internet connection with router access
- Domain name (optional but recommended)

### Phase 1: Install Dependencies

#### 1. Install Homebrew

```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### 2. Install Python 3.10+

```bash
# Install Python 3.10
brew install python@3.10

# Verify installation
python3.10 --version
```

#### 3. Install PostgreSQL

```bash
# Install PostgreSQL 15
brew install postgresql@15

# Start PostgreSQL service
brew services start postgresql@15

# Create Odoo database user
createuser -s odoo
psql postgres -c "ALTER USER odoo WITH PASSWORD 'odoo_password';"

# Create database
createdb -O odoo odoo_production
```

#### 4. Install Required System Libraries

```bash
# Install dependencies
brew install node npm git wget libxml2 libxslt libjpeg freetype libpng zlib openssl@1.1

# Install wkhtmltopdf for PDF reports
brew install --cask wkhtmltopdf
```

### Phase 2: Install Odoo 17

#### Option A: Using Source (Recommended)

```bash
# 1. Clone Odoo repository
cd ~/
git clone https://www.github.com/odoo/odoo --depth 1 --branch 17.0 --single-branch odoo17

# 2. Create Python virtual environment
cd ~/odoo17
python3.10 -m venv venv

# 3. Activate virtual environment
source venv/bin/activate

# 4. Install Python dependencies
pip install --upgrade pip
pip install wheel
pip install -r requirements.txt

# 5. Create custom addons directory
mkdir -p ~/odoo17/custom-addons
```

#### Option B: Using Docker (Alternative)

```bash
# Create project directory
mkdir -p ~/odoo-docker/{addons,config,data}

# Create docker-compose.yml (see Docker Deployment section)
# Then run:
cd ~/odoo-docker
docker-compose up -d
```

### Phase 3: Install Todo App Module

```bash
# Copy todo_app to custom addons
cp -r /path/to/todo_app ~/odoo17/custom-addons/

# Set proper permissions
chmod -R 755 ~/odoo17/custom-addons/todo_app
```

### Phase 4: Configure Odoo

#### 1. Create Configuration File

```bash
# Create config directory
mkdir -p ~/odoo17/config

# Create odoo.conf
cat > ~/odoo17/config/odoo.conf << 'EOF'
[options]
# Server settings
xmlrpc_port = 8069
http_interface = 0.0.0.0
workers = 2
max_cron_threads = 1

# Database settings
db_host = localhost
db_port = 5432
db_user = odoo
db_password = odoo_password
db_name = odoo_production
db_maxconn = 64

# Paths
addons_path = /Users/YOUR_USERNAME/odoo17/addons,/Users/YOUR_USERNAME/odoo17/custom-addons
data_dir = /Users/YOUR_USERNAME/odoo17/data

# Logging
logfile = /Users/YOUR_USERNAME/odoo17/logs/odoo.log
log_level = info

# Security
admin_passwd = CHANGE_THIS_MASTER_PASSWORD
list_db = False

# Performance
limit_memory_hard = 2684354560
limit_memory_soft = 2147483648
limit_request = 8192
limit_time_cpu = 600
limit_time_real = 1200
EOF

# Replace YOUR_USERNAME with your actual macOS username
sed -i '' "s/YOUR_USERNAME/$(whoami)/g" ~/odoo17/config/odoo.conf

# Create data and logs directories
mkdir -p ~/odoo17/{data,logs}
```

#### 2. Start Odoo Server

```bash
# Activate virtual environment
cd ~/odoo17
source venv/bin/activate

# Start Odoo
./odoo-bin -c config/odoo.conf

# Or start in background
nohup ./odoo-bin -c config/odoo.conf > logs/odoo-startup.log 2>&1 &
```

#### 3. Initialize Database and Install Module

```bash
# Access Odoo at http://localhost:8069
# Create database through UI or via command:
./odoo-bin -c config/odoo.conf -d odoo_production -i todo_app --stop-after-init
```

### Phase 5: Set Up Auto-Start with launchd

#### 1. Create Launch Agent

```bash
# Create launch agents directory if needed
mkdir -p ~/Library/LaunchAgents

# Create plist file
cat > ~/Library/LaunchAgents/com.digifact.odoo.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.digifact.odoo</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/YOUR_USERNAME/odoo17/venv/bin/python3</string>
        <string>/Users/YOUR_USERNAME/odoo17/odoo-bin</string>
        <string>-c</string>
        <string>/Users/YOUR_USERNAME/odoo17/config/odoo.conf</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/Users/YOUR_USERNAME/odoo17/logs/odoo-stdout.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/YOUR_USERNAME/odoo17/logs/odoo-stderr.log</string>
    <key>WorkingDirectory</key>
    <string>/Users/YOUR_USERNAME/odoo17</string>
</dict>
</plist>
EOF

# Replace YOUR_USERNAME
sed -i '' "s/YOUR_USERNAME/$(whoami)/g" ~/Library/LaunchAgents/com.digifact.odoo.plist
```

#### 2. Load and Start Service

```bash
# Load the service
launchctl load ~/Library/LaunchAgents/com.digifact.odoo.plist

# Start the service
launchctl start com.digifact.odoo

# Check if running
launchctl list | grep odoo

# View logs
tail -f ~/odoo17/logs/odoo.log
```

#### 3. Service Management Commands

```bash
# Stop service
launchctl stop com.digifact.odoo

# Restart service
launchctl stop com.digifact.odoo && launchctl start com.digifact.odoo

# Unload service (disable auto-start)
launchctl unload ~/Library/LaunchAgents/com.digifact.odoo.plist

# Reload service (after config changes)
launchctl unload ~/Library/LaunchAgents/com.digifact.odoo.plist
launchctl load ~/Library/LaunchAgents/com.digifact.odoo.plist
```

### Phase 6: Network Configuration for Internet Access

#### Option A: Port Forwarding (Basic Setup)

1. **Find Your Mac Mini's Local IP**
   ```bash
   # Get local IP address
   ipconfig getifaddr en0  # For Ethernet
   # or
   ipconfig getifaddr en1  # For Wi-Fi
   # Example output: 192.168.1.100
   ```

2. **Set Static IP on Mac Mini**
   - System Preferences → Network
   - Select your connection (Ethernet/Wi-Fi)
   - Click "Advanced" → TCP/IP
   - Configure IPv4: Manually
   - IP Address: 192.168.1.100 (example)
   - Subnet Mask: 255.255.255.0
   - Router: Your router's IP (e.g., 192.168.1.1)

3. **Configure Router Port Forwarding**
   - Log into your router (usually http://192.168.1.1)
   - Navigate to Port Forwarding settings
   - Add new rule:
     * External Port: 80 (or 443 for HTTPS)
     * Internal Port: 8069
     * Internal IP: 192.168.1.100 (your Mac Mini's IP)
     * Protocol: TCP
   - Save and enable the rule

4. **Find Your Public IP**
   ```bash
   curl ifconfig.me
   # Note this IP address
   ```

5. **Access Odoo from Internet**
   - Visit: http://YOUR_PUBLIC_IP
   - Note: Some ISPs block port 80/443; use alternate ports (e.g., 8080)

#### Option B: Dynamic DNS Setup (Recommended)

Home internet typically has dynamic IP addresses that change. Use DDNS for consistent access.

1. **Sign Up for DDNS Service** (Choose one)
   - [No-IP](https://www.noip.com) - Free tier available
   - [DuckDNS](https://www.duckdns.org) - Free
   - [Dynu](https://www.dynu.com) - Free tier available
   - [FreeDNS](https://freedns.afraid.org) - Free

2. **Example: Using DuckDNS**
   ```bash
   # Create account and subdomain at duckdns.org
   # Example: myodoo.duckdns.org
   
   # Install update script
   mkdir -p ~/duckdns
   cd ~/duckdns
   
   cat > duck.sh << 'EOF'
#!/bin/bash
echo url="https://www.duckdns.org/update?domains=YOUR_DOMAIN&token=YOUR_TOKEN&ip=" | curl -k -o ~/duckdns/duck.log -K -
EOF
   
   # Make executable
   chmod 700 duck.sh
   
   # Test it
   ./duck.sh
   cat duck.log  # Should show "OK"
   ```

3. **Set Up Auto-Update with Cron**
   ```bash
   # Edit crontab
   crontab -e
   
   # Add this line (updates every 5 minutes)
   */5 * * * * ~/duckdns/duck.sh >/dev/null 2>&1
   ```

4. **Access via Domain**
   - Visit: http://myodoo.duckdns.org

#### Option C: Using Cloudflare Tunnel (Most Secure - No Port Forwarding)

1. **Install Cloudflare Tunnel**
   ```bash
   # Install cloudflared
   brew install cloudflare/cloudflare/cloudflared
   
   # Login to Cloudflare
   cloudflared tunnel login
   ```

2. **Create Tunnel**
   ```bash
   # Create tunnel
   cloudflared tunnel create odoo-mac
   
   # Note the Tunnel ID from output
   # Create config file
   mkdir -p ~/.cloudflared
   
   cat > ~/.cloudflared/config.yml << 'EOF'
url: http://localhost:8069
tunnel: TUNNEL_ID_HERE
credentials-file: /Users/YOUR_USERNAME/.cloudflared/TUNNEL_ID_HERE.json
EOF
   ```

3. **Configure DNS**
   ```bash
   # Route your domain to tunnel
   cloudflared tunnel route dns odoo-mac odoo.yourdomain.com
   ```

4. **Run Tunnel as Service**
   ```bash
   # Install as service
   sudo cloudflared service install
   
   # Start service
   sudo launchctl start com.cloudflare.cloudflared
   ```

5. **Access Securely**
   - Visit: https://odoo.yourdomain.com
   - No port forwarding needed!
   - Automatic HTTPS

### Phase 7: SSL/HTTPS Setup (Optional but Recommended)

#### Using Nginx as Reverse Proxy with Let's Encrypt

1. **Install Nginx**
   ```bash
   brew install nginx
   ```

2. **Configure Nginx**
   ```bash
   # Create Odoo config
   cat > /opt/homebrew/etc/nginx/servers/odoo.conf << 'EOF'
upstream odoo {
    server 127.0.0.1:8069;
}

upstream odoochat {
    server 127.0.0.1:8072;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL certificates (configured after certbot)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Proxy settings
    proxy_read_timeout 720s;
    proxy_connect_timeout 720s;
    proxy_send_timeout 720s;
    proxy_set_header X-Forwarded-Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Real-IP $remote_addr;

    # Log files
    access_log /opt/homebrew/var/log/nginx/odoo.access.log;
    error_log /opt/homebrew/var/log/nginx/odoo.error.log;

    # Handle file uploads
    client_max_body_size 100M;

    # Redirect longpoll requests to odoo longpolling port
    location /longpolling {
        proxy_pass http://odoochat;
    }

    # Redirect requests to odoo backend server
    location / {
        proxy_redirect off;
        proxy_pass http://odoo;
    }

    # Cache static files
    location ~* /web/static/ {
        proxy_cache_valid 200 90m;
        proxy_buffering on;
        expires 864000;
        proxy_pass http://odoo;
    }

    # Gzip compression
    gzip on;
    gzip_types text/css text/scss text/plain text/xml application/xml application/json application/javascript;
    gzip_min_length 1000;
}
EOF
   ```

3. **Install Certbot for SSL**
   ```bash
   brew install certbot
   
   # Get SSL certificate
   sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com
   
   # Set up auto-renewal
   (crontab -l 2>/dev/null; echo "0 0 * * 0 certbot renew --quiet") | crontab -
   ```

4. **Start Nginx**
   ```bash
   brew services start nginx
   ```

5. **Update Odoo Config**
   ```bash
   # Edit odoo.conf and add:
   proxy_mode = True
   ```

### Phase 8: Backup Configuration

#### 1. Database Backup Script

```bash
mkdir -p ~/odoo17/backups

cat > ~/odoo17/backups/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR=~/odoo17/backups
DB_NAME=odoo_production
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup
pg_dump $DB_NAME | gzip > $BACKUP_DIR/odoo_backup_$DATE.sql.gz

# Keep only last 7 days of backups
find $BACKUP_DIR -name "odoo_backup_*.sql.gz" -mtime +7 -delete

echo "Backup completed: odoo_backup_$DATE.sql.gz"
EOF

chmod +x ~/odoo17/backups/backup.sh
```

#### 2. Schedule Automated Backups

```bash
# Add to crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * ~/odoo17/backups/backup.sh >> ~/odoo17/logs/backup.log 2>&1
```

#### 3. Filestore Backup

```bash
# Backup filestore
tar -czf ~/odoo17/backups/filestore_$(date +%Y%m%d).tar.gz ~/odoo17/data/filestore/
```

### Phase 9: Monitoring and Maintenance

#### 1. Monitor Server Health

```bash
# Check Odoo process
ps aux | grep odoo

# Check logs
tail -f ~/odoo17/logs/odoo.log

# Check PostgreSQL
brew services list | grep postgresql
```

#### 2. Monitor Resource Usage

```bash
# Install htop
brew install htop

# Monitor resources
htop
```

#### 3. Update Module

```bash
# Stop Odoo
launchctl stop com.digifact.odoo

# Update module files
cp -r /path/to/updated/todo_app ~/odoo17/custom-addons/

# Upgrade module
cd ~/odoo17
source venv/bin/activate
./odoo-bin -c config/odoo.conf -d odoo_production -u todo_app --stop-after-init

# Start Odoo
launchctl start com.digifact.odoo
```

### Troubleshooting Mac Mini Deployment

#### Odoo Won't Start

```bash
# Check if port 8069 is in use
lsof -i :8069

# Check PostgreSQL is running
brew services list | grep postgresql

# Check logs
tail -50 ~/odoo17/logs/odoo.log
```

#### Can't Access from Internet

```bash
# Test local access first
curl http://localhost:8069

# Check firewall settings
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate

# Allow incoming connections
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add ~/odoo17/venv/bin/python3
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblock ~/odoo17/venv/bin/python3
```

#### Performance Issues

```bash
# Increase workers in odoo.conf
workers = 4  # Adjust based on CPU cores

# Monitor memory usage
vm_stat

# Optimize PostgreSQL
# Edit /opt/homebrew/var/postgresql@15/postgresql.conf
shared_buffers = 256MB
effective_cache_size = 1GB
```

### Security Best Practices

1. **Change Default Passwords**
   ```bash
   # Change master password in odoo.conf
   admin_passwd = YOUR_STRONG_PASSWORD
   
   # Change database password
   psql postgres -c "ALTER USER odoo WITH PASSWORD 'NEW_STRONG_PASSWORD';"
   ```

2. **Enable Firewall**
   ```bash
   sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate on
   ```

3. **Disable Database Manager**
   ```bash
   # In odoo.conf
   list_db = False
   ```

4. **Regular Updates**
   ```bash
   # Update Odoo
   cd ~/odoo17
   git pull origin 17.0
   source venv/bin/activate
   pip install --upgrade -r requirements.txt
   ```

5. **Use HTTPS Only**
   - Configure SSL (see Phase 7)
   - Redirect all HTTP to HTTPS

### Cost Considerations

- **Hardware**: One-time cost (Mac Mini ~$600-$1200)
- **Internet**: Existing home internet (requires upload speed 10+ Mbps)
- **Domain**: ~$10-15/year (optional)
- **DDNS**: Free or ~$5-25/year
- **Cloudflare**: Free tier available
- **Electricity**: ~$5-15/month

**Total Monthly Cost**: $5-30 (mostly electricity + domain)

---

## ☁️ Cloud Deployment

### Odoo.sh

1. **Push to Repository**
   ```bash
   git add todo_app/
   git commit -m "Add Todo App module"
   git push origin main
   ```

2. **Configure Branch**
   - Go to Odoo.sh project
   - Select your branch
   - Module auto-detected in `/addons` or root

3. **Install Module**
   - Navigate to Apps
   - Update Apps List
   - Install "Todo App"

### AWS / GCP / Azure

#### Using Docker

```bash
# Pull and run Odoo
docker run -d \
  --name odoo \
  -p 8069:8069 \
  -v /path/to/addons:/mnt/extra-addons \
  -v /path/to/config:/etc/odoo \
  --link postgres:db \
  odoo:17.0
```

#### Using Native Installation

```bash
# 1. Install Odoo 17
# Follow official Odoo installation guide

# 2. Copy module
sudo cp -r todo_app /opt/odoo/addons/

# 3. Set permissions
sudo chown -R odoo:odoo /opt/odoo/addons/todo_app

# 4. Restart Odoo
sudo systemctl restart odoo

# 5. Update and install via UI
```

## 🔄 Upgrading Module

### Development

```bash
./odoo-bin -d your_database -u todo_app --stop-after-init
```

### Production

```bash
# 1. Backup database first!
pg_dump your_database > backup_$(date +%Y%m%d).sql

# 2. Update module files
git pull origin main
# or copy new files

# 3. Upgrade module
./odoo-bin -d your_database -u todo_app --stop-after-init

# 4. Restart Odoo service
sudo systemctl restart odoo
```

### Docker

```bash
# 1. Update files in addons volume
# 2. Upgrade
docker-compose exec odoo odoo -d mydb -u todo_app --stop-after-init
# 3. Restart
docker-compose restart odoo
```

## 🏪 Publishing to Odoo App Store

### 1. Prepare Module

- [ ] Version format: `17.0.X.Y.Z`
- [ ] License: LGPL-3 (required for App Store)
- [ ] Complete `__manifest__.py`
- [ ] Add screenshots in `static/description/`
- [ ] Create `static/description/index.html`
- [ ] Test on clean Odoo 17.0 installation

### 2. Screenshots Required

Place in `static/description/`:
- `screenshot_1.png` - Main feature view
- `screenshot_2.png` - Secondary view
- `banner.png` - 900x300px banner
- `icon.png` - 100x100px icon

### 3. Create App Store Account

1. Go to [apps.odoo.com](https://apps.odoo.com)
2. Sign in with Odoo account
3. Click "Publish Your App"

### 4. Submit Module

1. Create ZIP file:
   ```bash
   cd /path/to/addons
   zip -r todo_app.zip todo_app/ -x "*.pyc" -x "*__pycache__*" -x "*.git*"
   ```

2. Upload to App Store
3. Fill in details:
   - App name
   - Category
   - Price (or free)
   - Description
   - Support email

4. Submit for review

### 5. App Store Checklist

- [ ] No syntax errors
- [ ] No hardcoded credentials
- [ ] Proper translations support
- [ ] Demo data included
- [ ] Security rules defined
- [ ] Access rights configured
- [ ] Clean code (PEP8)
- [ ] Documentation complete

## 🔧 Troubleshooting

### Module Not Found

```bash
# Check addons path
./odoo-bin --addons-path=/path/to/addons -d mydb

# Verify module structure
ls -la /path/to/addons/todo_app/
# Should contain __manifest__.py and __init__.py
```

### Import Errors

```bash
# Check Python syntax
python3 -m py_compile todo_app/models/todo_task.py

# Check all files
find todo_app -name "*.py" -exec python3 -m py_compile {} \;
```

### Database Errors

```bash
# Reset module state (development only!)
psql your_database -c "DELETE FROM ir_module_module WHERE name='todo_app';"

# Then reinstall
./odoo-bin -d your_database -i todo_app --stop-after-init
```

### Permission Errors

```bash
# Fix file permissions
sudo chown -R odoo:odoo /path/to/addons/todo_app
sudo chmod -R 755 /path/to/addons/todo_app
```

## 📊 Performance Tips

### For Large Installations

1. **Enable Stored Computed Fields**
   - Already configured in `todo_weekly_task.py`

2. **Add Database Indexes**
   ```python
   _sql_constraints = [
       # Add indexes for frequently searched fields
   ]
   ```

3. **Use Record Rules Efficiently**
   - Avoid complex domain expressions

4. **Configure Workers**
   ```ini
   [options]
   workers = 4
   max_cron_threads = 2
   ```

## 📞 Support

- **Documentation**: See README.md
- **Issues**: Open GitHub issue
- **Email**: justindohust@gmaol.com

---

© 2026 DigiFact - Licensed under LGPL-3
