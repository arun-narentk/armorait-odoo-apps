# -*- coding: utf-8 -*-
"""Machine and work center downtime events."""

from odoo import api, fields, models

DOWNTIME_REASONS = [
    ('breakdown', 'Breakdown'),
    ('maintenance', 'Planned Maintenance'),
    ('setup', 'Setup / Changeover'),
    ('material', 'Material Shortage'),
    ('quality', 'Quality Hold'),
    ('other', 'Other'),
]


class RnMrpDowntimeLog(models.Model):
    """Downtime record for OEE and bottleneck analysis."""

    _name = 'rn.mrp.downtime.log'
    _description = 'Manufacturing Downtime Log'
    _inherit = ['mail.thread']
    _order = 'date_start desc'

    name = fields.Char(required=True)
    workcenter_id = fields.Many2one('mrp.workcenter', required=True, index=True)
    production_id = fields.Many2one('mrp.production', string='Manufacturing Order')
    shift_id = fields.Many2one('rn.mrp.shift', string='Shift')
    reason = fields.Selection(selection=DOWNTIME_REASONS, default='breakdown', required=True)
    date_start = fields.Datetime(required=True, index=True)
    date_end = fields.Datetime()
    duration_minutes = fields.Float(compute='_compute_duration', store=True)
    note = fields.Text()
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

    @api.depends('date_start', 'date_end')
    def _compute_duration(self):
        for rec in self:
            if rec.date_start and rec.date_end:
                delta = rec.date_end - rec.date_start
                rec.duration_minutes = delta.total_seconds() / 60.0
            else:
                rec.duration_minutes = 0.0
