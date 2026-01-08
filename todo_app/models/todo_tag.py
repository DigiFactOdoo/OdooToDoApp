# -*- coding: utf-8 -*-

from odoo import models, fields


class TodoTag(models.Model):
    """Tag model for labeling tasks."""
    
    _name = 'todo.tag'
    _description = 'Task Tag'
    _order = 'name'

    name = fields.Char(
        string='Tag Name',
        required=True,
        translate=True,
    )
    color = fields.Integer(
        string='Color Index',
        default=0,
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    task_ids = fields.Many2many(
        comodel_name='todo.task',
        relation='todo_task_tag_rel',
        column1='tag_id',
        column2='task_id',
        string='Tasks',
    )

    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'Tag name must be unique!'),
    ]
