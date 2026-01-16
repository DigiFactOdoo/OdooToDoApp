# Docker Setup Guide - Todo App for Odoo 17

Quick guide to run the Todo App using Docker for local testing.

## Prerequisites

- Docker Desktop installed and running
- At least 4GB RAM available for Docker
- Ports 8069 and 5432 not in use

## Quick Start

### 1. Start Docker Containers

Open PowerShell in the project directory and run:

```powershell
# Start containers in detached mode
docker-compose up -d

# View logs (optional)
docker-compose logs -f odoo
```

### 2. Wait for Odoo to Start

First startup takes 2-3 minutes. Check logs:

```powershell
docker-compose logs -f odoo
```

Wait for: `odoo.service.server: HTTP service (werkzeug) running on ...`

### 3. Access Odoo

Open browser and navigate to: **http://localhost:8069**

### 4. Create Database and Install Module

#### Option A: Via Web UI

1. On the database manager page, fill in:
   - **Master Password**: `admin123`
   - **Database Name**: `odoo_test`
   - **Email**: `admin@example.com`
   - **Password**: `admin`
   - **Language**: English
   - **Country**: Your country
   - Check **Load demonstration data** (optional)

2. Click **Create Database**

3. After database creation:
   - Go to **Apps** menu
   - Click **Update Apps List** (⟳ icon)
   - Search for **Todo App**
   - Click **Install**

#### Option B: Via Command Line (Faster)

```powershell
# Stop the running container
docker-compose stop odoo

# Install module and create database
docker-compose run --rm odoo odoo --init=todo_app --database=odoo_test --db_host=db --db_user=odoo --db_password=odoo --stop-after-init

# Start containers again
docker-compose up -d
```

Then access **http://localhost:8069** and login with:
- Email: `admin`
- Password: `admin`

### 5. Start Using the App

The Todo App will be available in the main menu. You can:
- Create tasks
- Set priorities and due dates
- Organize with categories and tags
- Use Kanban, List, and Calendar views

## Useful Commands

### Container Management

```powershell
# Start containers
docker-compose up -d

# Stop containers
docker-compose stop

# Restart containers
docker-compose restart

# Stop and remove containers (keeps data)
docker-compose down

# Stop and remove everything including volumes (DELETE ALL DATA)
docker-compose down -v

# View running containers
docker-compose ps

# View logs
docker-compose logs -f odoo        # Odoo logs
docker-compose logs -f db          # Database logs
```

### Module Management

```powershell
# Update module after code changes
docker-compose restart odoo

# Or force module upgrade
docker-compose exec odoo odoo --update=todo_app --database=odoo_test --stop-after-init
docker-compose restart odoo

# Install additional module
docker-compose exec odoo odoo --init=MODULE_NAME --database=odoo_test --stop-after-init
```

### Database Management

```powershell
# Access PostgreSQL
docker-compose exec db psql -U odoo -d odoo_test

# Backup database
docker-compose exec db pg_dump -U odoo odoo_test > backup.sql

# Restore database
docker-compose exec -T db psql -U odoo -d odoo_test < backup.sql

# List databases
docker-compose exec db psql -U odoo -l
```

### Development Workflow

```powershell
# Make code changes to todo_app files
# Container auto-reloads (dev mode enabled)

# If auto-reload doesn't work, restart:
docker-compose restart odoo

# View real-time logs while developing
docker-compose logs -f odoo
```

### Troubleshooting

```powershell
# Check if containers are running
docker-compose ps

# Restart everything
docker-compose restart

# View detailed logs
docker-compose logs --tail=100 odoo

# Remove everything and start fresh
docker-compose down -v
docker-compose up -d

# Check port conflicts
netstat -ano | findstr :8069
netstat -ano | findstr :5432

# Enter Odoo container shell
docker-compose exec odoo bash

# Enter PostgreSQL container shell
docker-compose exec db bash
```

## Project Structure

```
OdooToDoApp/
├── docker-compose.yml       # Docker services configuration
├── .dockerignore           # Files to exclude from Docker
├── config/
│   └── odoo.conf          # Odoo configuration
└── todo_app/              # Your module (mounted to container)
    ├── models/
    ├── views/
    ├── controllers/
    └── ...
```

## Configuration Files

### docker-compose.yml
Defines two services:
- **db**: PostgreSQL 15 database
- **odoo**: Odoo 17 application server

Your `todo_app` module is mounted at `/mnt/extra-addons/todo_app` inside the container.

### config/odoo.conf
Odoo configuration with:
- Database connection settings
- Admin master password: `admin123`
- Development mode enabled
- Auto-reload on code changes

## Ports

- **8069**: Odoo web interface
- **8072**: Odoo longpolling (for chat)
- **5432**: PostgreSQL (accessible from host)

## Volumes

Docker creates persistent volumes for:
- **odoo_web_data**: Odoo filestore and sessions
- **odoo_db_data**: PostgreSQL database files

Data persists even after `docker-compose down`. Only `docker-compose down -v` deletes volumes.

## Testing the Module

1. **Test Task Creation**
   - Go to Todo App menu
   - Click **Create**
   - Fill in task details
   - Save and verify

2. **Test Different Views**
   - Switch between List, Kanban, and Calendar views
   - Test filters and groupings

3. **Test Categories and Tags**
   - Create categories and tags
   - Assign to tasks
   - Filter by category/tag

4. **Test Weekly Tasks** (if included)
   - Navigate to Weekly Tasks
   - Create recurring tasks
   - Verify weekly logic

5. **Check Security**
   - Create additional users
   - Test access rights
   - Verify security rules

## Performance Tips

For better development performance:

```yaml
# In docker-compose.yml, add to odoo service:
environment:
  - ODOO_RC=/etc/odoo/odoo.conf
  - PYTHONUNBUFFERED=1
```

## Clean Up

When finished testing:

```powershell
# Keep data for next time
docker-compose down

# Remove everything including data
docker-compose down -v

# Also remove Docker images (frees space)
docker rmi odoo:17.0 postgres:15
```

## Next Steps

After local testing:
- Review [DEPLOYMENT.md](todo_app/DEPLOYMENT.md) for production deployment
- Deploy to Mac Mini (see Mac Mini section in DEPLOYMENT.md)
- Deploy to cloud platforms (Odoo.sh, AWS, etc.)

## Support

For issues:
1. Check logs: `docker-compose logs -f`
2. Restart: `docker-compose restart`
3. Clean start: `docker-compose down -v && docker-compose up -d`

---

**Happy Testing! 🚀**
