# -*- coding: utf-8 -*-
{
    'name': 'Todo App',
    'version': '17.0.1.0.0',
    'category': 'Productivity',
    'summary': 'Manage your tasks and to-do lists efficiently',
    'description': """
Todo App - Task Management Module
=================================

A comprehensive task management solution for Odoo that helps you organize
and track your daily tasks efficiently.

Key Features
------------
* Create and manage tasks with priorities
* Set due dates and reminders
* Organize tasks by categories/tags
* Track task progress and completion
* Dashboard with task statistics
* Kanban, List, and Calendar views

Benefits
--------
* Increase productivity
* Never miss important deadlines
* Easy to use interface
* Fully integrated with Odoo

Technical Details
-----------------
* Compatible with Odoo 17.0
* Multi-company support
* Access rights and security rules

For support, please contact: support@digifact.com
    """,
    'author': 'DigiFact',
    'website': 'https://www.digifact.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        # Security
        'security/todo_security.xml',
        'security/ir.model.access.csv',
        # Views
        'views/todo_task_views.xml',
        'views/todo_category_views.xml',
        'views/todo_tag_views.xml',
        'views/todo_weekly_views.xml',
        'views/todo_menus.xml',
        # Wizards
        'wizards/todo_task_wizard_views.xml',
        # Data
        'data/todo_data.xml',
    ],
    'demo': [
        'demo/todo_demo.xml',
        'demo/todo_weekly_demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'todo_app/static/src/css/todo_style.css',
        ],
    },
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'sequence': 1,
}
