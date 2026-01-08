# -*- coding: utf-8 -*-

from odoo import models, fields, api


class TodoCategory(models.Model):
    """Category model for organizing tasks."""
    
    _name = 'todo.category'
    _description = 'Task Category'
    _order = 'sequence, name'

    name = fields.Char(
        string='Category Name',
        required=True,
        translate=True,
    )
    description = fields.Text(
        string='Description',
        translate=True,
    )
    color = fields.Integer(
        string='Color Index',
        default=0,
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    task_ids = fields.One2many(
        comodel_name='todo.task',
        inverse_name='category_id',
        string='Tasks',
    )
    task_count = fields.Integer(
        string='Task Count',
        compute='_compute_task_count',
        store=True,
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        default=lambda self: self.env.company,
    )

    @api.depends('task_ids')
    def _compute_task_count(self):
        """Compute the number of tasks in each category."""
        for category in self:
            category.task_count = len(category.task_ids)

    def action_view_tasks(self):
        """Open tasks view filtered by this category."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Tasks - {self.name}',
            'res_model': 'todo.task',
            'view_mode': 'tree,kanban,form,calendar',
            'domain': [('category_id', '=', self.id)],
            'context': {'default_category_id': self.id},
        }
