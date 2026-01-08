# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request


class TodoController(http.Controller):
    """Web controller for Todo App portal access."""

    @http.route('/todo/tasks', type='http', auth='user', website=True)
    def todo_tasks(self, **kwargs):
        """Display user's tasks in portal."""
        tasks = request.env['todo.task'].search([
            ('user_id', '=', request.env.user.id)
        ])
        return request.render('todo_app.portal_todo_tasks', {
            'tasks': tasks,
        })

    @http.route('/todo/api/tasks', type='json', auth='user')
    def api_get_tasks(self, **kwargs):
        """API endpoint to get user's tasks."""
        tasks = request.env['todo.task'].search_read(
            domain=[('user_id', '=', request.env.user.id)],
            fields=['name', 'state', 'priority', 'deadline', 'category_id'],
            limit=100,
        )
        return {'status': 'success', 'data': tasks}

    @http.route('/todo/api/task/<int:task_id>/done', type='json', auth='user')
    def api_mark_done(self, task_id, **kwargs):
        """API endpoint to mark a task as done."""
        task = request.env['todo.task'].browse(task_id)
        if task.exists() and task.user_id.id == request.env.user.id:
            task.action_done()
            return {'status': 'success', 'message': 'Task marked as done'}
        return {'status': 'error', 'message': 'Task not found or access denied'}
