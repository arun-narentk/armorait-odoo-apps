# -*- coding: utf-8 -*-
"""Live work center operational status."""

from odoo import fields, models

STATUS_SELECTION = [
    ('running', 'Running'),
    ('idle', 'Idle'),
    ('breakdown', 'Breakdown'),
    ('maintenance', 'Maintenance'),
    ('offline', 'Offline'),
]


class RnMrpWorkcenterStatus(models.Model):
    """Current operational status snapshot for a work center."""

    _name = 'rn.mrp.workcenter.status'
    _description = 'Work Center Status'
    _order = 'write_date desc'

    workcenter_id = fields.Many2one('mrp.workcenter', required=True, index=True)
    status = fields.Selection(selection=STATUS_SELECTION, default='idle', required=True, index=True)
    current_production_id = fields.Many2one('mrp.production', string='Current MO')
    queue_count = fields.Integer(string='Queue Length')
    utilization_percent = fields.Float(string='Utilization %')
    running_hours_today = fields.Float()
    downtime_minutes_today = fields.Float()
    last_update = fields.Datetime(default=fields.Datetime.now)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

    _workcenter_company_uniq = models.Constraint(
        'unique(workcenter_id, company_id)',
        'Only one status row per work center per company.',
    )
