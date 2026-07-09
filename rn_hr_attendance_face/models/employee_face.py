# -*- coding: utf-8 -*-
"""Employee face registration and encrypted embedding storage."""

from odoo import api, fields, models


class RnHrEmployeeFace(models.Model):
    """Stores face embeddings for one employee (never raw match photos)."""

    _name = 'rn.hr.employee.face'
    _description = 'Employee Face Profile'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'employee_id'

    name = fields.Char(compute='_compute_name', store=True)
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
        ondelete='cascade',
        tracking=True,
        index=True,
    )
    registration_date = fields.Datetime(
        string='Registration Date',
        default=fields.Datetime.now,
        tracking=True,
    )
    # Encrypted/base64 payload of embedding vector (Phase 3 writes real data).
    face_embedding = fields.Text(
        string='Face Embedding',
        groups='rn_hr_attendance_face.group_rn_face_admin',
        help='Encrypted embedding vector. Not human-readable plaintext.',
    )
    embedding_version = fields.Char(
        string='Embedding Version',
        default='v1',
        help='Algorithm and vector size fingerprint, e.g. insightface-512-v1.',
    )
    photo_count = fields.Integer(
        string='Photo Count',
        default=0,
        help='Number of capture frames used during enrollment.',
    )
    status = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('enrolling', 'Enrolling'),
            ('active', 'Active'),
            ('needs_reenroll', 'Needs Re-enrollment'),
            ('blocked', 'Blocked'),
        ],
        default='draft',
        tracking=True,
        index=True,
    )
    confidence = fields.Float(
        string='Enrollment Confidence',
        digits=(16, 4),
        help='Average quality score from enrollment samples.',
    )
    last_verified = fields.Datetime(string='Last Verified')
    company_id = fields.Many2one(
        'res.company',
        related='employee_id.company_id',
        store=True,
        index=True,
    )
    active = fields.Boolean(default=True)
    angle_coverage = fields.Char(
        string='Angle Coverage',
        help='CSV of captured poses: front,left,right,up,down,smile,...',
    )

    _employee_company_uniq = models.Constraint(
        'unique(employee_id, company_id)',
        'Each employee can have only one face profile per company.',
    )

    @api.depends('employee_id')
    def _compute_name(self):
        """Display employee name in list and chatters."""
        for record in self:
            record.name = record.employee_id.name or 'Face Profile'

    def action_start_enrollment(self):
        """Open the multi-angle face registration wizard (Phase 2)."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Register Face',
            'res_model': 'rn.hr.register.face.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_employee_id': self.employee_id.id,
                'default_face_id': self.id,
            },
        }
