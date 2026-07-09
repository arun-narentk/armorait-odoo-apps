# -*- coding: utf-8 -*-
"""Extend manufacturing work orders for MES execution."""

from odoo import fields, models


class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    mes_state = fields.Selection(
        [
            ('pending', 'Not Started'),
            ('running', 'Running'),
            ('paused', 'Paused'),
            ('done', 'Done on Floor'),
        ],
        string='Shop Floor Status',
        default='pending',
        copy=False,
        index=True,
    )
    mes_session_id = fields.Many2one('rn.mes.production.session', string='Active MES Session', copy=False)
    mes_good_qty = fields.Float(string='Floor Good Qty', digits='Product Unit', copy=False)
    mes_scrap_qty = fields.Float(string='Floor Scrap Qty', digits='Product Unit', copy=False)
    mes_reject_qty = fields.Float(string='Floor Reject Qty', digits='Product Unit', copy=False)
    mes_instruction_url = fields.Char(string='Digital Work Instruction URL')
    mes_inspection_ids = fields.One2many('rn.mes.quality.inspection', 'workorder_id')
    mes_event_count = fields.Integer(compute='_compute_mes_counts')
    mes_downtime_count = fields.Integer(compute='_compute_mes_counts')

    def _compute_mes_counts(self):
        Event = self.env['rn.mes.production.event']
        Downtime = self.env['rn.mes.downtime.event']
        for wo in self:
            wo.mes_event_count = Event.search_count([('workorder_id', '=', wo.id)])
            wo.mes_downtime_count = Downtime.search_count([('workorder_id', '=', wo.id)])

    def action_open_mes_tablet(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.client',
            'tag': 'rn_mes_core.tablet',
            'name': 'Shop Floor Tablet',
            'params': {'workorder_id': self.id},
        }
