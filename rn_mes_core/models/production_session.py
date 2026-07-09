# -*- coding: utf-8 -*-
"""Active operator session on a terminal."""

from odoo import api, fields, models


class RnMesProductionSession(models.Model):
    """Links operator, terminal, and current work order execution."""

    _name = 'rn.mes.production.session'
    _description = 'MES Production Session'
    _inherit = ['mail.thread']
    _order = 'start_time desc'

    name = fields.Char(compute='_compute_name', store=True)
    terminal_id = fields.Many2one('rn.mes.terminal', required=True, index=True)
    operator_id = fields.Many2one('hr.employee', string='Operator', required=True, index=True)
    workorder_id = fields.Many2one('mrp.workorder', string='Work Order', index=True)
    workcenter_id = fields.Many2one(
        related='workorder_id.workcenter_id',
        store=True,
        readonly=True,
    )
    state = fields.Selection(
        [
            ('active', 'Active'),
            ('paused', 'Paused'),
            ('done', 'Done'),
        ],
        default='active',
        required=True,
        tracking=True,
    )
    start_time = fields.Datetime(default=fields.Datetime.now, required=True)
    end_time = fields.Datetime()
    good_qty = fields.Float(string='Good Quantity', digits='Product Unit')
    scrap_qty = fields.Float(string='Scrap Quantity', digits='Product Unit')
    reject_qty = fields.Float(string='Reject Quantity', digits='Product Unit')
    event_ids = fields.One2many('rn.mes.production.event', 'session_id')
    scrap_ids = fields.One2many('rn.mes.scrap.record', 'session_id')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

    @api.depends('terminal_id.name', 'operator_id.name', 'workorder_id.name')
    def _compute_name(self):
        for rec in self:
            parts = [
                rec.terminal_id.name or '',
                rec.operator_id.name or '',
                rec.workorder_id.name or '',
            ]
            rec.name = ' / '.join(p for p in parts if p) or 'MES Session'
