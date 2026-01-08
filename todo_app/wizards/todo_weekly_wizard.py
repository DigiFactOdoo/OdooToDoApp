# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta


class TodoWeeklyWizard(models.TransientModel):
    """Wizard for weekly planner operations."""
    
    _name = 'todo.weekly.wizard'
    _description = 'Weekly Planner Wizard'

    wizard_type = fields.Selection(
        selection=[
            ('create_blank', 'Create Blank Week'),
            ('copy_week', 'Copy from Another Week'),
            ('clear_week', 'Clear Week Tasks'),
        ],
        string='Operation',
        required=True,
        default='create_blank',
    )
    
    # Target week
    target_date = fields.Date(
        string='Target Week Date',
        required=True,
        default=fields.Date.today,
        help='Select any date in the target week',
    )
    target_week_start = fields.Date(
        string='Week Start (Monday)',
        compute='_compute_target_week',
    )
    target_week_end = fields.Date(
        string='Week End (Sunday)',
        compute='_compute_target_week',
    )
    target_week_display = fields.Char(
        string='Target Week',
        compute='_compute_target_week',
    )
    
    # Source week (for copy)
    source_date = fields.Date(
        string='Source Week Date',
        help='Select any date in the source week to copy from',
    )
    source_week_start = fields.Date(
        string='Source Week Start',
        compute='_compute_source_week',
    )
    source_week_display = fields.Char(
        string='Source Week',
        compute='_compute_source_week',
    )
    
    # Options
    copy_completed_status = fields.Boolean(
        string='Copy Completion Status',
        default=False,
        help='If checked, tasks will keep their done/not done status',
    )
    include_a_must = fields.Boolean(string='Include A - Must Do', default=True)
    include_b_should = fields.Boolean(string='Include B - Should Do', default=True)
    include_c_could = fields.Boolean(string='Include C - Could Do', default=True)
    
    # Preview
    existing_task_count = fields.Integer(
        string='Existing Tasks in Target Week',
        compute='_compute_existing_tasks',
    )

    @api.depends('target_date')
    def _compute_target_week(self):
        """Compute target week start and end."""
        for wizard in self:
            if wizard.target_date:
                weekday = wizard.target_date.weekday()
                wizard.target_week_start = wizard.target_date - timedelta(days=weekday)
                wizard.target_week_end = wizard.target_week_start + timedelta(days=6)
                wizard.target_week_display = "%s - %s" % (
                    wizard.target_week_start.strftime('%d/%m/%Y'),
                    wizard.target_week_end.strftime('%d/%m/%Y')
                )
            else:
                wizard.target_week_start = False
                wizard.target_week_end = False
                wizard.target_week_display = False

    @api.depends('source_date')
    def _compute_source_week(self):
        """Compute source week start."""
        for wizard in self:
            if wizard.source_date:
                weekday = wizard.source_date.weekday()
                wizard.source_week_start = wizard.source_date - timedelta(days=weekday)
                source_week_end = wizard.source_week_start + timedelta(days=6)
                wizard.source_week_display = "%s - %s" % (
                    wizard.source_week_start.strftime('%d/%m/%Y'),
                    source_week_end.strftime('%d/%m/%Y')
                )
            else:
                wizard.source_week_start = False
                wizard.source_week_display = False

    @api.depends('target_week_start', 'target_week_end')
    def _compute_existing_tasks(self):
        """Count existing tasks in target week."""
        for wizard in self:
            if wizard.target_week_start and wizard.target_week_end:
                wizard.existing_task_count = self.env['todo.weekly.task'].search_count([
                    ('task_date', '>=', wizard.target_week_start),
                    ('task_date', '<=', wizard.target_week_end),
                    ('user_id', '=', self.env.user.id),
                ])
            else:
                wizard.existing_task_count = 0

    def action_execute(self):
        """Execute the selected operation."""
        self.ensure_one()
        
        if self.wizard_type == 'create_blank':
            return self._create_blank_week()
        elif self.wizard_type == 'copy_week':
            return self._copy_week()
        elif self.wizard_type == 'clear_week':
            return self._clear_week()

    def _create_blank_week(self):
        """Create a blank week with template tasks."""
        self.ensure_one()
        
        if self.existing_task_count > 0:
            raise ValidationError(
                _("Target week already has %d tasks. Please clear them first or choose a different week.") 
                % self.existing_task_count
            )
        
        # Build priority levels list
        priorities = []
        if self.include_a_must:
            priorities.append(('a_must', _('Important task')))
        if self.include_b_should:
            priorities.append(('b_should', _('Normal task')))
        if self.include_c_could:
            priorities.append(('c_could', _('Optional task')))
        
        if not priorities:
            raise ValidationError(_("Please select at least one priority level."))
        
        created_count = 0
        for i in range(7):
            task_date = self.target_week_start + timedelta(days=i)
            for priority, task_name in priorities:
                self.env['todo.weekly.task'].create({
                    'name': task_name,
                    'task_date': task_date,
                    'priority_level': priority,
                    'user_id': self.env.user.id,
                })
                created_count += 1
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Created %d blank tasks for week %s') % (created_count, self.target_week_display),
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }

    def _copy_week(self):
        """Copy tasks from source week to target week."""
        self.ensure_one()
        
        if not self.source_week_start:
            raise ValidationError(_("Please select a source week to copy from."))
        
        if self.source_week_start == self.target_week_start:
            raise ValidationError(_("Source and target weeks cannot be the same."))
        
        if self.existing_task_count > 0:
            raise ValidationError(
                _("Target week already has %d tasks. Please clear them first.") 
                % self.existing_task_count
            )
        
        # Build priority filter
        priority_filter = []
        if self.include_a_must:
            priority_filter.append('a_must')
        if self.include_b_should:
            priority_filter.append('b_should')
        if self.include_c_could:
            priority_filter.append('c_could')
        
        source_week_end = self.source_week_start + timedelta(days=6)
        
        source_tasks = self.env['todo.weekly.task'].search([
            ('task_date', '>=', self.source_week_start),
            ('task_date', '<=', source_week_end),
            ('user_id', '=', self.env.user.id),
            ('priority_level', 'in', priority_filter),
        ])
        
        if not source_tasks:
            raise ValidationError(_("No tasks found in source week to copy."))
        
        created_count = 0
        for task in source_tasks:
            # Calculate offset from source week start
            day_offset = (task.task_date - self.source_week_start).days
            new_date = self.target_week_start + timedelta(days=day_offset)
            
            self.env['todo.weekly.task'].create({
                'name': task.name,
                'task_date': new_date,
                'priority_level': task.priority_level,
                'user_id': self.env.user.id,
                'sequence': task.sequence,
                'is_done': task.is_done if self.copy_completed_status else False,
            })
            created_count += 1
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Copied %d tasks to week %s') % (created_count, self.target_week_display),
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }

    def _clear_week(self):
        """Clear all tasks in target week."""
        self.ensure_one()
        
        if self.existing_task_count == 0:
            raise ValidationError(_("No tasks to clear in target week."))
        
        # Build priority filter
        priority_filter = []
        if self.include_a_must:
            priority_filter.append('a_must')
        if self.include_b_should:
            priority_filter.append('b_should')
        if self.include_c_could:
            priority_filter.append('c_could')
        
        tasks_to_delete = self.env['todo.weekly.task'].search([
            ('task_date', '>=', self.target_week_start),
            ('task_date', '<=', self.target_week_end),
            ('user_id', '=', self.env.user.id),
            ('priority_level', 'in', priority_filter),
        ])
        
        deleted_count = len(tasks_to_delete)
        tasks_to_delete.unlink()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Deleted %d tasks from week %s') % (deleted_count, self.target_week_display),
                'type': 'warning',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }

    def action_prev_week(self):
        """Navigate to previous week."""
        self.target_date = self.target_week_start - timedelta(days=7)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'todo.weekly.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_next_week(self):
        """Navigate to next week."""
        self.target_date = self.target_week_start + timedelta(days=7)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'todo.weekly.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
