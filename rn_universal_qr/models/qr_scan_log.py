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
