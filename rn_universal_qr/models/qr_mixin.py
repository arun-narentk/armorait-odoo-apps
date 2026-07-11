# -*- coding: utf-8 -*-
import secrets
from datetime import timedelta

from odoo import fields, models


class RnQrMixin(models.AbstractModel):
    _name = 'rn.qr.mixin'
    _description = 'Universal QR Mixin'

    rn_qr_token = fields.Char(string='QR Token', copy=False, index=True)
    rn_qr_image = fields.Binary(string='QR Image', attachment=True, copy=False)
    rn_qr_url = fields.Char(string='QR URL', copy=False)
    rn_qr_scan_count = fields.Integer(string='Scan Count', compute='_compute_rn_qr_scan_count')
    rn_qr_last_generated = fields.Datetime(string='Last Generated', copy=False)
    rn_qr_expires_at = fields.Datetime(string='Expires At', copy=False)

    def _compute_rn_qr_scan_count(self):
        scan_obj = self.env['rn.qr.scan.log'].sudo()
        grouped = scan_obj.read_group(
            [('res_model', '=', self._name), ('res_id', 'in', self.ids)],
            ['res_id'],
            ['res_id'],
            lazy=False,
        )
        counter = {item['res_id']: item['res_id_count'] for item in grouped}
        for record in self:
            record.rn_qr_scan_count = counter.get(record.id, 0)

    def _generate_qr_token(self):
        self.ensure_one()
        return secrets.token_urlsafe(18)

    def _default_expiration_datetime(self):
        self.ensure_one()
        expiration_days = int(
            self.env['ir.config_parameter'].sudo().get_param('rn_universal_qr.default_expiration_days', 0) or 0
        )
        if expiration_days <= 0:
            return False
        return fields.Datetime.now() + timedelta(days=expiration_days)

    def action_generate_qr(self):
        service = self.env['rn.qr.service']
        for record in self:
            if not record.rn_qr_token:
                record.rn_qr_token = record._generate_qr_token()
            image_data, qr_url = service.generate_png(record.rn_qr_token)
            qr_record = service.ensure_qr_record(record)
            expiration_dt = record._default_expiration_datetime()
            now = fields.Datetime.now()
            record.write({
                'rn_qr_image': image_data,
                'rn_qr_url': qr_url,
                'rn_qr_last_generated': now,
                'rn_qr_expires_at': expiration_dt,
            })
            qr_record.write({
                'token': record.rn_qr_token,
                'qr_image': image_data,
                'qr_url': qr_url,
                'last_generated_at': now,
                'expiration_datetime': expiration_dt,
            })
        return True
