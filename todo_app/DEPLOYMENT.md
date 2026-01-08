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
- **Email**: support@digifact.com

---

© 2024 DigiFact - Licensed under LGPL-3
