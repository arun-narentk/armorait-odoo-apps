# -*- coding: utf-8 -*-
"""Barcode scan audit log from shop floor."""

from odoo import fields, models


class RnMesBarcodeScan(models.Model):
    """Logged barcode scan for materials, WOs, operators, machines."""

    _name = 'rn.mes.barcode.scan'
    _description = 'MES Barcode Scan'
    _order = 'scan_time desc'

    barcode = fields.Char(required=True, index=True)
    scan_type = fields.Selection(
        [
            ('workorder', 'Work Order'),
            ('product', 'Product'),
            ('lot', 'Lot / Batch'),
            ('operator', 'Operator'),
            ('machine', 'Machine'),
            ('location', 'Location'),
            ('tool', 'Tool'),
            ('unknown', 'Unknown'),
        ],
        default='unknown',
        required=True,
        index=True,
    )
    terminal_id = fields.Many2one('rn.mes.terminal')
    session_id = fields.Many2one('rn.mes.production.session')
    res_model = fields.Char(string='Matched Model')
    res_id = fields.Integer(string='Matched Record ID')
    scan_time = fields.Datetime(default=fields.Datetime.now, required=True, index=True)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
