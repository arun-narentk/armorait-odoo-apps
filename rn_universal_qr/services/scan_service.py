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

# -*- coding: utf-8 -*-
"""Scan logging and redirect resolution."""

import logging

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError

_logger = logging.getLogger(__name__)


class RnQrScanService(models.AbstractModel):
    _name = 'rn.qr.scan.service'
    _description = 'Universal QR Scan Service'

    @api.model
    def _statistics_enabled(self):
        return self.env['ir.config_parameter'].sudo().get_param(
            'rn_universal_qr.enable_statistics', 'True'
        ) == 'True'

    @api.model
    def register_scan(self, qr_record, user_agent=None, ip_address=None, user=None):
        if self._statistics_enabled():
            now = fields.Datetime.now()
            self.env['rn.qr.scan.log'].sudo().create({
                'qr_record_id': qr_record.id,
                'user_id': user.id if user else False,
                'device': user_agent,
                'ip_address': ip_address,
            })
            qr_record.sudo().write({
                'scan_count': qr_record.scan_count + 1,
                'last_scan': now,
                'first_scan': qr_record.first_scan or now,
            })
        return True

    @api.model
    def process_token(self, token, user_agent=None, ip_address=None, user=None):
        qr = self.env['rn.qr.record'].sudo().search([('token', '=', token), ('active', '=', True)], limit=1)
        if not qr:
            raise UserError(_('QR code not found.'))
        if qr.is_expired():
            raise UserError(_('This QR code has expired.'))

        target = self.env[qr.res_model].browse(qr.res_id)
        if target.exists():
            try:
                target.with_user(user or self.env.user).check_access('read')
            except AccessError:
                if not user or user._is_public():
                    return {
                        'type': 'redirect',
                        'url': '/web/login?redirect=/rn/qr/%s' % token,
                    }
                raise

        self.register_scan(qr, user_agent=user_agent, ip_address=ip_address, user=user)
        action = self.env['rn.qr.service'].resolve_scan_action(qr)
        if action.get('type') == 'ir.actions.act_url':
            return {'type': 'redirect', 'url': action['url']}
        return action
