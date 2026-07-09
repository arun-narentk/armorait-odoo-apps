# -*- coding: utf-8 -*-
"""Extend mrp.workcenter with intelligence fields."""

from odoo import api, fields, models


class MrpWorkcenter(models.Model):
    _inherit = 'mrp.workcenter'

    rn_status = fields.Selection(
        selection=[
            ('running', 'Running'),
            ('idle', 'Idle'),
            ('breakdown', 'Breakdown'),
            ('maintenance', 'Maintenance'),
            ('offline', 'Offline'),
        ],
        compute='_compute_rn_status',
        string='Live Status',
    )
    rn_status_id = fields.One2many(
        'rn.mrp.workcenter.status',
        'workcenter_id',
        string='Status Records',
    )
    rn_oee_target = fields.Float(string='OEE Target %', default=75.0)
    rn_last_maintenance_date = fields.Date(string='Last Maintenance')
    rn_next_maintenance_date = fields.Date(string='Next Maintenance')

    @api.depends('rn_status_id.status')
    def _compute_rn_status(self):
        Status = self.env['rn.mrp.workcenter.status']
        for wc in self:
            rec = Status.search([('workcenter_id', '=', wc.id)], limit=1)
            wc.rn_status = rec.status if rec else 'idle'
