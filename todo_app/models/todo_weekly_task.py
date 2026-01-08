# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta, date


class TodoWeeklyTask(models.Model):
    """Weekly Task model for weekly planner feature."""
    
    _name = 'todo.weekly.task'
    _description = 'Weekly Todo Task'
    _inherit = ['mail.thread']
    _order = 'task_date, priority_level, sequence'

    # Basic Fields
    name = fields.Char(
        string='Task Title',
        required=True,
        tracking=True,
        default='Todo',
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    
    # Date Fields
    task_date = fields.Date(
        string='Task Date',
        required=True,
        default=fields.Date.today,
        tracking=True,
    )
    week_start = fields.Date(
        string='Week Start (Monday)',
        compute='_compute_week_info',
        store=True,
    )
    week_end = fields.Date(
        string='Week End (Sunday)',
        compute='_compute_week_info',
        store=True,
    )
    day_of_week = fields.Selection(
        selection=[
            ('0', 'Monday'),
            ('1', 'Tuesday'),
            ('2', 'Wednesday'),
            ('3', 'Thursday'),
            ('4', 'Friday'),
            ('5', 'Saturday'),
            ('6', 'Sunday'),
        ],
        string='Day of Week',
        compute='_compute_week_info',
        store=True,
    )
    day_name = fields.Char(
        string='Day Name',
        compute='_compute_week_info',
        store=True,
    )
    
    # Priority Level (A Must do, B Should do, C Could do)
    priority_level = fields.Selection(
        selection=[
            ('a_must', 'A - Must Do'),
            ('b_should', 'B - Should Do'),
            ('c_could', 'C - Could Do'),
        ],
        string='Priority Level',
        default='b_should',
        required=True,
        tracking=True,
    )
    
    # Status
    is_done = fields.Boolean(
        string='Completed',
        default=False,
        tracking=True,
    )
    
    # Relational Fields
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Assigned To',
        default=lambda self: self.env.user,
        required=True,
        tracking=True,
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
        compute='_compute_color',
    )
    
    # For grouping display
    priority_sequence = fields.Integer(
        string='Priority Sequence',
        compute='_compute_priority_sequence',
        store=True,
    )

    # -------------------------------------------------------------------------
    # Compute Methods
    # -------------------------------------------------------------------------
    
    @api.depends('task_date')
    def _compute_week_info(self):
        """Compute week start, end and day of week."""
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for task in self:
            if task.task_date:
                # Monday = 0, Sunday = 6
                weekday = task.task_date.weekday()
                task.week_start = task.task_date - timedelta(days=weekday)
                task.week_end = task.week_start + timedelta(days=6)
                task.day_of_week = str(weekday)
                task.day_name = day_names[weekday]
            else:
                task.week_start = False
                task.week_end = False
                task.day_of_week = False
                task.day_name = False

    @api.depends('priority_level')
    def _compute_priority_sequence(self):
        """Compute sequence for priority level ordering."""
        priority_map = {'a_must': 1, 'b_should': 2, 'c_could': 3}
        for task in self:
            task.priority_sequence = priority_map.get(task.priority_level, 2)

    @api.depends('priority_level', 'is_done')
    def _compute_color(self):
        """Compute color based on priority and completion status."""
        for task in self:
            if task.is_done:
                task.color = 10  # Green
            elif task.priority_level == 'a_must':
                task.color = 1   # Red
            elif task.priority_level == 'b_should':
                task.color = 3   # Yellow
            else:
                task.color = 4   # Blue

    # -------------------------------------------------------------------------
    # Action Methods
    # -------------------------------------------------------------------------
    
    def action_toggle_done(self):
        """Toggle task completion status."""
        for task in self:
            task.is_done = not task.is_done

    def action_mark_done(self):
        """Mark task as done."""
        self.write({'is_done': True})

    def action_mark_undone(self):
        """Mark task as not done."""
        self.write({'is_done': False})

    # -------------------------------------------------------------------------
    # Business Methods
    # -------------------------------------------------------------------------
    
    @api.model
    def get_week_tasks(self, week_start_date=None, user_id=None):
        """Get all tasks for a specific week."""
        if not week_start_date:
            today = fields.Date.today()
            weekday = today.weekday()
            week_start_date = today - timedelta(days=weekday)
        
        if not user_id:
            user_id = self.env.user.id
            
        week_end_date = week_start_date + timedelta(days=6)
        
        return self.search([
            ('task_date', '>=', week_start_date),
            ('task_date', '<=', week_end_date),
            ('user_id', '=', user_id),
        ], order='task_date, priority_sequence, sequence')

    @api.model
    def get_week_statistics(self, week_start_date=None, user_id=None):
        """Get statistics for a week."""
        tasks = self.get_week_tasks(week_start_date, user_id)
        
        total = len(tasks)
        completed = len(tasks.filtered('is_done'))
        
        # Per day statistics
        day_stats = {}
        for i in range(7):
            day_date = week_start_date + timedelta(days=i)
            day_tasks = tasks.filtered(lambda t: t.task_date == day_date)
            day_completed = day_tasks.filtered('is_done')
            day_stats[i] = {
                'date': day_date,
                'total': len(day_tasks),
                'completed': len(day_completed),
                'progress': (len(day_completed) / len(day_tasks) * 100) if day_tasks else 0,
            }
        
        return {
            'total': total,
            'completed': completed,
            'progress': (completed / total * 100) if total else 0,
            'days': day_stats,
        }

    @api.model
    def create_blank_week(self, week_start_date=None, user_id=None):
        """Create blank week template with sample tasks."""
        if not week_start_date:
            today = fields.Date.today()
            weekday = today.weekday()
            week_start_date = today - timedelta(days=weekday)
        
        if not user_id:
            user_id = self.env.user.id
            
        week_end_date = week_start_date + timedelta(days=6)
        
        # Check if tasks already exist
        existing = self.search_count([
            ('task_date', '>=', week_start_date),
            ('task_date', '<=', week_end_date),
            ('user_id', '=', user_id),
        ])
        
        if existing:
            raise ValidationError(
                _("Tasks already exist for this week (%s - %s). Cannot create blank template.") 
                % (week_start_date.strftime('%d/%m'), week_end_date.strftime('%d/%m'))
            )
        
        # Template tasks for each priority level
        templates = {
            'a_must': [_('Important task')],
            'b_should': [_('Normal task')],
            'c_could': [_('Optional task')],
        }
        
        created_tasks = self.env['todo.weekly.task']
        
        for i in range(7):
            task_date = week_start_date + timedelta(days=i)
            for priority, task_names in templates.items():
                for seq, task_name in enumerate(task_names, 1):
                    created_tasks |= self.create({
                        'name': task_name,
                        'task_date': task_date,
                        'priority_level': priority,
                        'user_id': user_id,
                        'sequence': seq * 10,
                    })
        
        return created_tasks


class TodoWeeklyTaskDay(models.Model):
    """Virtual model for daily aggregation in weekly view."""
    
    _name = 'todo.weekly.task.day'
    _description = 'Weekly Task Day Summary'
    _auto = False
    _order = 'task_date'

    task_date = fields.Date(string='Date', readonly=True)
    day_name = fields.Char(string='Day', readonly=True)
    user_id = fields.Many2one('res.users', string='User', readonly=True)
    total_tasks = fields.Integer(string='Total Tasks', readonly=True)
    completed_tasks = fields.Integer(string='Completed', readonly=True)
    progress = fields.Float(string='Progress (%)', readonly=True)
    week_start = fields.Date(string='Week Start', readonly=True)

    def init(self):
        """Create SQL view for daily summary."""
        self.env.cr.execute("""
            DROP VIEW IF EXISTS todo_weekly_task_day;
            CREATE OR REPLACE VIEW todo_weekly_task_day AS (
                SELECT 
                    ROW_NUMBER() OVER (ORDER BY task_date, user_id) AS id,
                    task_date,
                    day_name,
                    user_id,
                    week_start,
                    COUNT(*) AS total_tasks,
                    SUM(CASE WHEN is_done THEN 1 ELSE 0 END) AS completed_tasks,
                    CASE 
                        WHEN COUNT(*) > 0 
                        THEN ROUND(SUM(CASE WHEN is_done THEN 1 ELSE 0 END)::numeric / COUNT(*)::numeric * 100, 1)
                        ELSE 0 
                    END AS progress
                FROM todo_weekly_task
                WHERE active = true
                GROUP BY task_date, day_name, user_id, week_start
            )
        """)
