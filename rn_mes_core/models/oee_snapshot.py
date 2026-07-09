# -*- coding: utf-8 -*-
"""OEE snapshots computed from shop-floor data."""

from odoo import api, fields, models


class RnMesOeeSnapshot(models.Model):
    """Overall Equipment Effectiveness per work center and period."""

    _name = 'rn.mes.oee.snapshot'
    _description = 'MES OEE Snapshot'
    _order = 'snapshot_date desc, id desc'

    name = fields.Char(required=True)
    workcenter_id = fields.Many2one('mrp.workcenter', required=True, index=True)
    snapshot_date = fields.Date(required=True, index=True)
    shift_label = fields.Char(string='Shift')
    availability = fields.Float(string='Availability %')
    performance = fields.Float(string='Performance %')
    quality = fields.Float(string='Quality %')
    oee = fields.Float(string='OEE %', compute='_compute_oee', store=True)
    planned_minutes = fields.Float()
    running_minutes = fields.Float()
    downtime_minutes = fields.Float()
    good_qty = fields.Float(string='Good Quantity')
    total_qty = fields.Float(string='Total Quantity')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

    @api.depends('availability', 'performance', 'quality')
    def _compute_oee(self):
        for rec in self:
            if rec.availability and rec.performance and rec.quality:
                rec.oee = round(
                    (rec.availability * rec.performance * rec.quality) / 10000.0,
                    2,
                )
            else:
                rec.oee = 0.0
