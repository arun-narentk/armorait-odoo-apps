# -*- coding: utf-8 -*-
from odoo import fields, models


class QrScanLog(models.Model):
    _name = 'rn.qr.scan.log'
    _description = 'Universal QR Scan Log'
    _order = 'scan_datetime desc, id desc'

    qr_record_id = fields.Many2one('rn.qr.record', required=True, ondelete='cascade', index=True)
    token = fields.Char(required=True, index=True)
    res_model = fields.Char(required=True, index=True)
    res_id = fields.Integer(required=True, index=True)
    company_id = fields.Many2one('res.company', required=True, index=True)
    scan_datetime = fields.Datetime(required=True, default=fields.Datetime.now, index=True)
    source = fields.Selection(
        [('web', 'Web'), ('mobile', 'Mobile'), ('scanner', 'Scanner'), ('api', 'API')],
        default='web',
        required=True,
    )
    user_agent = fields.Char()
    ip_address = fields.Char()

# -*- coding: utf-8 -*-
"""Scan statistics for QR codes."""

from odoo import fields, models


class RnQrScanLog(models.Model):
    _name = 'rn.qr.scan.log'
    _description = 'QR Scan Log'
    _order = 'scan_date desc'

    qr_record_id = fields.Many2one('rn.qr.record', required=True, ondelete='cascade', index=True)
    res_model = fields.Char(related='qr_record_id.res_model', store=True, readonly=True)
    res_id = fields.Integer(related='qr_record_id.res_id', store=True, readonly=True)
    company_id = fields.Many2one(related='qr_record_id.company_id', store=True, readonly=True)
    scan_date = fields.Datetime(default=fields.Datetime.now, required=True, index=True)
    user_id = fields.Many2one('res.users', string='User', index=True)
    device = fields.Char(string='Device / User Agent')
    ip_address = fields.Char(string='IP Address')
