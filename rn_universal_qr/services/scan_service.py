# -*- coding: utf-8 -*-
from odoo import fields, models


class ScanService(models.AbstractModel):
    _name = 'rn.qr.scan.service'
    _description = 'Universal QR Scan Service'

    def resolve_token(self, token):
        qr_record = self.env['rn.qr.record'].sudo().search([('token', '=', token), ('active', '=', True)], limit=1)
        if not qr_record:
            return False
        if qr_record.expiration_datetime and qr_record.expiration_datetime <= fields.Datetime.now():
            return False
        document = self.env[qr_record.res_model].sudo().browse(qr_record.res_id)
        if not document.exists():
            return False
        return qr_record, document

    def log_scan(self, qr_record, source='web', user_agent=None, ip_address=None):
        self.env['rn.qr.scan.log'].sudo().create({
            'qr_record_id': qr_record.id,
            'token': qr_record.token,
            'res_model': qr_record.res_model,
            'res_id': qr_record.res_id,
            'company_id': qr_record.company_id.id,
            'scan_datetime': fields.Datetime.now(),
            'source': source,
            'user_agent': user_agent,
            'ip_address': ip_address,
        })
        return True
