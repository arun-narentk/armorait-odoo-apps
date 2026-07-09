# -*- coding: utf-8 -*-
"""Shop-floor terminal registration."""

from odoo import fields, models


class RnMesTerminal(models.Model):
    """Touch-screen kiosk or tablet bound to a work center."""

    _name = 'rn.mes.terminal'
    _description = 'MES Shop Floor Terminal'
    _inherit = ['mail.thread']
    _order = 'name'

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(required=True, index=True)
    workcenter_id = fields.Many2one('mrp.workcenter', string='Work Center', index=True)
    location_id = fields.Many2one('stock.location', string='Shop Floor Location')
    active = fields.Boolean(default=True)
    allow_barcode = fields.Boolean(default=True, string='Barcode Scanning')
    allow_photo = fields.Boolean(default=True, string='Photo Capture')
    allow_quality = fields.Boolean(default=True, string='Quality Checks')
    session_id = fields.Many2one('rn.mes.production.session', string='Active Session', copy=False)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    _sql_constraints = [
        ('code_company_uniq', 'unique(code, company_id)', 'Terminal code must be unique per company.'),
    ]
