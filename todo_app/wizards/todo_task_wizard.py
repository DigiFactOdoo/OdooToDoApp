# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class TodoTaskWizard(models.TransientModel):
    """Wizard to perform batch operations on tasks."""
    
    _name = 'todo.task.wizard'
    _description = 'Task Batch Operation Wizard'

    operation = fields.Selection(
        selection=[
            ('change_state', 'Change State'),
            ('change_category', 'Change Category'),
            ('change_assignee', 'Change Assignee'),
            ('add_tags', 'Add Tags'),
        ],
        string='Operation',
        required=True,
        default='change_state',
    )
    task_ids = fields.Many2many(
        comodel_name='todo.task',
        string='Tasks',
    )
    new_state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('in_progress', 'In Progress'),
            ('done', 'Done'),
            ('cancelled', 'Cancelled'),
        ],
        string='New State',
    )
    category_id = fields.Many2one(
        comodel_name='todo.category',
        string='Category',
    )
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Assignee',
    )
    tag_ids = fields.Many2many(
        comodel_name='todo.tag',
        string='Tags to Add',
    )

    @api.model
    def default_get(self, fields_list):
        """Set default tasks from context."""
        res = super().default_get(fields_list)
        active_ids = self.env.context.get('active_ids', [])
        if active_ids:
            res['task_ids'] = [(6, 0, active_ids)]
        return res

    def action_apply(self):
        """Apply the selected operation to all tasks."""
        self.ensure_one()
        
        if not self.task_ids:
            return {'type': 'ir.actions.act_window_close'}

        if self.operation == 'change_state' and self.new_state:
            self.task_ids.write({'state': self.new_state})
        elif self.operation == 'change_category' and self.category_id:
            self.task_ids.write({'category_id': self.category_id.id})
        elif self.operation == 'change_assignee' and self.user_id:
            self.task_ids.write({'user_id': self.user_id.id})
        elif self.operation == 'add_tags' and self.tag_ids:
            for task in self.task_ids:
                task.write({'tag_ids': [(4, tag.id) for tag in self.tag_ids]})

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('%d task(s) updated successfully.') % len(self.task_ids),
                'type': 'success',
                'sticky': False,
            }
        }
