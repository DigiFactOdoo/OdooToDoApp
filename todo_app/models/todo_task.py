# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta


class TodoTask(models.Model):
    """Main task model for todo application."""
    
    _name = 'todo.task'
    _description = 'Todo Task'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'priority desc, deadline asc, id desc'

    # Basic Fields
    name = fields.Char(
        string='Task Title',
        required=True,
        tracking=True,
        translate=True,
    )
    description = fields.Html(
        string='Description',
        sanitize=True,
        sanitize_attributes=True,
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
    )
    
    # Status Fields
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('in_progress', 'In Progress'),
            ('done', 'Done'),
            ('cancelled', 'Cancelled'),
        ],
        string='Status',
        default='draft',
        required=True,
        tracking=True,
        group_expand='_expand_states',
    )
    priority = fields.Selection(
        selection=[
            ('0', 'Low'),
            ('1', 'Normal'),
            ('2', 'High'),
            ('3', 'Urgent'),
        ],
        string='Priority',
        default='1',
        tracking=True,
    )
    progress = fields.Float(
        string='Progress (%)',
        default=0.0,
        tracking=True,
    )
    
    # Date Fields
    create_date = fields.Datetime(
        string='Created On',
        readonly=True,
    )
    deadline = fields.Date(
        string='Deadline',
        tracking=True,
    )
    completed_date = fields.Datetime(
        string='Completed Date',
        readonly=True,
    )
    
    # Computed Fields
    is_overdue = fields.Boolean(
        string='Is Overdue',
        compute='_compute_is_overdue',
        store=True,
    )
    days_remaining = fields.Integer(
        string='Days Remaining',
        compute='_compute_days_remaining',
    )
    
    # Relational Fields
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Assigned To',
        default=lambda self: self.env.user,
        tracking=True,
    )
    category_id = fields.Many2one(
        comodel_name='todo.category',
        string='Category',
        tracking=True,
    )
    tag_ids = fields.Many2many(
        comodel_name='todo.tag',
        relation='todo_task_tag_rel',
        column1='task_id',
        column2='tag_id',
        string='Tags',
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True,
    )
    
    # Color for kanban
    color = fields.Integer(
        string='Color Index',
    )

    # SQL Constraints
    _sql_constraints = [
        ('progress_range', 
         'CHECK(progress >= 0 AND progress <= 100)',
         'Progress must be between 0 and 100!'),
    ]

    # -------------------------------------------------------------------------
    # Compute Methods
    # -------------------------------------------------------------------------
    
    @api.depends('deadline', 'state')
    def _compute_is_overdue(self):
        """Check if task is overdue."""
        today = fields.Date.today()
        for task in self:
            task.is_overdue = (
                task.deadline 
                and task.deadline < today 
                and task.state not in ('done', 'cancelled')
            )

    @api.depends('deadline')
    def _compute_days_remaining(self):
        """Compute days remaining until deadline."""
        today = fields.Date.today()
        for task in self:
            if task.deadline:
                delta = task.deadline - today
                task.days_remaining = delta.days
            else:
                task.days_remaining = 0

    # -------------------------------------------------------------------------
    # Onchange Methods
    # -------------------------------------------------------------------------
    
    @api.onchange('state')
    def _onchange_state(self):
        """Update progress based on state."""
        if self.state == 'done':
            self.progress = 100.0
        elif self.state == 'draft':
            self.progress = 0.0

    # -------------------------------------------------------------------------
    # Constraint Methods
    # -------------------------------------------------------------------------
    
    @api.constrains('deadline')
    def _check_deadline(self):
        """Ensure deadline is not in the past for new tasks."""
        for task in self:
            if task.deadline and task.state == 'draft':
                if task.deadline < fields.Date.today():
                    raise ValidationError(
                        _("Deadline cannot be in the past for new tasks!")
                    )

    # -------------------------------------------------------------------------
    # CRUD Methods
    # -------------------------------------------------------------------------
    
    @api.model_create_multi
    def create(self, vals_list):
        """Override create to add custom logic."""
        for vals in vals_list:
            if vals.get('state') == 'done' and not vals.get('completed_date'):
                vals['completed_date'] = fields.Datetime.now()
        return super().create(vals_list)

    def write(self, vals):
        """Override write to track completion date."""
        if vals.get('state') == 'done':
            vals['completed_date'] = fields.Datetime.now()
            vals['progress'] = 100.0
        return super().write(vals)

    def unlink(self):
        """Prevent deletion of completed tasks."""
        for task in self:
            if task.state == 'done':
                raise ValidationError(
                    _("Cannot delete completed tasks! Archive them instead.")
                )
        return super().unlink()

    # -------------------------------------------------------------------------
    # Action Methods
    # -------------------------------------------------------------------------
    
    def action_start(self):
        """Start the task."""
        self.write({'state': 'in_progress'})

    def action_done(self):
        """Mark task as done."""
        self.write({'state': 'done'})

    def action_cancel(self):
        """Cancel the task."""
        self.write({'state': 'cancelled'})

    def action_reset_draft(self):
        """Reset task to draft."""
        self.write({
            'state': 'draft',
            'progress': 0.0,
            'completed_date': False,
        })

    def action_set_high_priority(self):
        """Set task to high priority."""
        self.write({'priority': '2'})

    # -------------------------------------------------------------------------
    # Group Expand
    # -------------------------------------------------------------------------
    
    @api.model
    def _expand_states(self, states, domain, order):
        """Return all states for kanban column grouping."""
        return [key for key, val in self._fields['state'].selection]
