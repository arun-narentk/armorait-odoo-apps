# -*- coding: utf-8 -*-
"""OEE snapshots per work center."""

from odoo import api, fields, models


class RnMrpOeeRecord(models.Model):
    """Overall Equipment Effectiveness record."""

    _name = 'rn.mrp.oee.record'
    _description = 'OEE Record'
    _order = 'date desc, id desc'

    name = fields.Char(required=True)
    workcenter_id = fields.Many2one('mrp.workcenter', required=True, index=True)
    date = fields.Date(required=True, index=True)
    shift_id = fields.Many2one('rn.mrp.shift')
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
