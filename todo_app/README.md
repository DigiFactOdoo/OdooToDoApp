# Todo App - Task Management for Odoo 17

[![License: LGPL-3](https://img.shields.io/badge/License-LGPL--3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)
[![Odoo Version](https://img.shields.io/badge/Odoo-17.0-purple.svg)](https://www.odoo.com)

A comprehensive task management module for Odoo 17.0 featuring a **Weekly Planner** with priority-based task organization.

## ✨ Features

### 📅 Weekly Planner (Main Feature)
- **7-Day Kanban Board** - Visual weekly overview with drag & drop
- **Priority Levels**:
  - 🔴 **A - Must Do** - Critical tasks
  - 🟡 **B - Should Do** - Important tasks  
  - 🔵 **C - Could Do** - Optional tasks
- **Progress Tracking** - Per-day completion indicators
- **Week Operations Wizard**:
  - Create blank week templates
  - Copy tasks from another week
  - Clear week tasks
- **Multiple Views** - Kanban, List, Calendar, Graph, Pivot

### ✅ Standard Tasks
- Create and manage tasks with rich descriptions
- Set priorities and deadlines
- Track progress with percentage completion
- Organize with categories and tags

### 👥 Collaboration
- Assign tasks to team members
- Activity scheduling and reminders
- Chatter for task discussions
- Email notifications

### 🔒 Security
- User and Manager access levels
- Users see only their own tasks
- Managers have full access
- Multi-company support

## 📁 Module Structure

```
todo_app/
├── __init__.py
├── __manifest__.py
├── README.md
├── DEPLOYMENT.md
├── controllers/
│   ├── __init__.py
│   └── main.py                    # API endpoints
├── data/
│   └── todo_data.xml              # Default categories & tags
├── demo/
│   ├── todo_demo.xml              # Demo tasks
│   └── todo_weekly_demo.xml       # Demo weekly tasks
├── models/
│   ├── __init__.py
│   ├── todo_category.py           # Category model
│   ├── todo_tag.py                # Tag model
│   ├── todo_task.py               # Standard task model
│   └── todo_weekly_task.py        # Weekly planner model
├── security/
│   ├── ir.model.access.csv        # Access rights
│   └── todo_security.xml          # Groups & rules
├── static/
│   ├── description/
│   │   ├── banner.png             # App Store banner
│   │   ├── icon.png               # Module icon
│   │   └── index.html             # App Store description
│   └── src/css/
│       └── todo_style.css         # Custom styles
├── views/
│   ├── todo_category_views.xml
│   ├── todo_menus.xml
│   ├── todo_tag_views.xml
│   ├── todo_task_views.xml
│   └── todo_weekly_views.xml      # Weekly planner views
└── wizards/
    ├── __init__.py
    ├── todo_task_wizard.py
    ├── todo_task_wizard_views.xml
    └── todo_weekly_wizard.py      # Week operations wizard
```

## 🚀 Quick Start

### Installation

1. Clone or download the module:
   ```bash
   git clone <repo-url> /path/to/odoo/addons/todo_app
   ```

2. Update Odoo apps list:
   - Go to **Apps** → **Update Apps List**

3. Install the module:
   - Search for "Todo App"
   - Click **Install**

### First Steps

1. Navigate to **Todo** menu
2. Go to **Weekly Planner** → **My Week**
3. Click **Week Operations** to create a blank week template
4. Start adding and organizing your tasks!

## 📖 Usage Guide

### Weekly Planner

1. **View Your Week**: Go to Todo → Weekly Planner → My Week
2. **Add Task**: Click on a day column and use quick create, or click "Create"
3. **Set Priority**: Choose A/B/C priority level for each task
4. **Mark Complete**: Toggle the checkbox to mark tasks done
5. **Drag & Drop**: Rearrange tasks between days
6. **Week Navigation**: Use filters to view different weeks

### Priority System

| Level | Color | Meaning |
|-------|-------|---------|
| A - Must Do | 🔴 Red | Critical, non-negotiable tasks |
| B - Should Do | 🟡 Yellow | Important but flexible timing |
| C - Could Do | 🔵 Blue | Nice-to-have, low priority |

### Week Operations

Access via **Todo → Weekly Planner → Week Operations**:

- **Create Blank Week**: Generate template tasks for a new week
- **Copy from Week**: Duplicate tasks from a previous week
- **Clear Week**: Remove all tasks from a week

## ⚙️ Configuration

### Access Rights

1. Go to **Settings** → **Users & Companies** → **Users**
2. Select a user
3. Under "Todo App" section:
   - **User**: Can manage own tasks only
   - **Manager**: Full access to all tasks and configuration

### Categories & Tags

Managers can configure at **Todo → Configuration**:
- **Categories**: Work, Personal, Shopping, Health & Fitness
- **Tags**: Urgent, Important, Needs Review, Waiting, Follow Up

## 🔧 Technical Details

- **Odoo Version**: 17.0
- **License**: LGPL-3
- **Dependencies**: `base`, `mail`
- **Python Version**: 3.10+

### Models

| Model | Description |
|-------|-------------|
| `todo.task` | Standard task with full features |
| `todo.weekly.task` | Weekly planner task |
| `todo.category` | Task categories |
| `todo.tag` | Task tags/labels |

## 🚀 Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions including:
- Local development setup
- Docker deployment
- Cloud deployment (Odoo.sh, AWS, GCP)
- Publishing to Odoo App Store

## 📞 Support

- **Author**: DigiFact
- **Website**: https://www.digifact.vn
- **Email**: support@digifact.com

## 📄 License

This module is licensed under [LGPL-3](https://www.gnu.org/licenses/lgpl-3.0.html).

## 📝 Changelog

### v17.0.1.0.0 (Initial Release)
- ✅ Weekly Planner with 7-day Kanban board
- ✅ A/B/C Priority levels (Must/Should/Could Do)
- ✅ Week operations wizard
- ✅ Standard task management
- ✅ Categories and Tags
- ✅ Multiple views (Kanban, List, Calendar, Graph, Pivot)
- ✅ User access control
- ✅ Multi-company support
- ✅ Chatter integration
