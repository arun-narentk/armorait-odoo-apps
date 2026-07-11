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

# -*- coding: utf-8 -*-
import secrets
from datetime import timedelta

from odoo import api, fields, models


class RnQrMixin(models.AbstractModel):
    _name = 'rn.qr.mixin'
    _description = 'Universal QR Mixin'

    rn_qr_token = fields.Char(string='QR Token', copy=False, index=True)
    rn_qr_image = fields.Binary(string='QR Image', attachment=True, copy=False)
    rn_qr_url = fields.Char(string='QR URL', copy=False)
    rn_qr_last_generated = fields.Datetime(string='Last QR Generated', copy=False)
    rn_qr_expires_at = fields.Datetime(string='QR Expires At', copy=False)
    rn_qr_scan_count = fields.Integer(string='QR Scans', compute='_compute_rn_qr_scan_count')

    def _compute_rn_qr_scan_count(self):
        log_model = self.env['rn.qr.scan.log'].sudo()
        grouped = log_model.read_group(
            [('res_model', '=', self._name), ('res_id', 'in', self.ids)],
            ['res_id'],
            ['res_id'],
            lazy=False,
        )
        mapped = {item['res_id']: item['res_id_count'] for item in grouped}
        for record in self:
            record.rn_qr_scan_count = mapped.get(record.id, 0)

    def _rn_qr_generate_token(self) -> str:
        return secrets.token_urlsafe(18)

    def _rn_qr_get_payload(self) -> dict:
        self.ensure_one()
        return {
            'model': self._name,
            'id': self.id,
            'display_name': self.display_name,
        }

    def _rn_qr_get_expiration(self):
        self.ensure_one()
        default_days = int(
            self.env['ir.config_parameter'].sudo().get_param('rn_universal_qr.default_expiration_days', 0) or 0
        )
        if default_days <= 0:
            return False
        return fields.Datetime.now() + timedelta(days=default_days)

    def action_generate_qr(self):
        service = self.env['rn.qr.service']
        for record in self:
            if not record.rn_qr_token:
                record.rn_qr_token = record._rn_qr_generate_token()
            qr_record = service.ensure_qr_record(record)
            image_value, qr_url = service.generate_png(record.rn_qr_token)
            record.write({
                'rn_qr_image': image_value,
                'rn_qr_url': qr_url,
                'rn_qr_last_generated': fields.Datetime.now(),
                'rn_qr_expires_at': record._rn_qr_get_expiration(),
            })
            qr_record.write({
                'qr_image': image_value,
                'token': record.rn_qr_token,
                'expiration_datetime': record.rn_qr_expires_at,
                'last_generated_at': fields.Datetime.now(),
            })
        return True

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            if hasattr(record, 'rn_qr_token') and not record.rn_qr_token:
                record.rn_qr_token = record._rn_qr_generate_token()
        return records
# -*- coding: utf-8 -*-
"""Mixin to attach universal QR codes to any business document."""

import logging

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class RnQrMixin(models.AbstractModel):
    _name = 'rn.qr.mixin'
    _description = 'Universal QR Mixin'

    rn_qr_count = fields.Integer(compute='_compute_rn_qr_count', string='QR Codes')
    rn_qr_active_id = fields.Many2one(
        'rn.qr.record',
        compute='_compute_rn_qr_active',
        string='Active QR',
    )
    rn_qr_image = fields.Binary(related='rn_qr_active_id.qr_image', string='QR Preview')
    rn_qr_url = fields.Char(related='rn_qr_active_id.qr_url', string='QR URL')
    rn_qr_scan_count = fields.Integer(related='rn_qr_active_id.scan_count', string='Scans')
    rn_qr_last_scan = fields.Datetime(related='rn_qr_active_id.last_scan', string='Last Scan')

    @api.depends('rn_qr_active_id')
    def _compute_rn_qr_count(self):
        if not self.ids:
            for record in self:
                record.rn_qr_count = 0
            return
        grouped = self.env['rn.qr.record'].read_group(
            [
                ('res_model', '=', self._name),
                ('res_id', 'in', self.ids),
                ('active', '=', True),
            ],
            ['res_id'],
            ['res_id'],
            lazy=False,
        )
        counts = {row['res_id']: row['__count'] for row in grouped}
        for record in self:
            record.rn_qr_count = counts.get(record.id, 0)

    def _compute_rn_qr_active(self):
        qr_records = self.env['rn.qr.record'].search([
            ('res_model', '=', self._name),
            ('res_id', 'in', self.ids),
            ('active', '=', True),
        ], order='id desc')
        by_record = {}
        for qr in qr_records:
            by_record.setdefault(qr.res_id, qr)
        for record in self:
            record.rn_qr_active_id = by_record.get(record.id, False)

    def _get_qr_service(self):
        return self.env['rn.qr.service']

    def _generate_qr(self, values=None):
        self.ensure_one()
        return self._get_qr_service().get_or_create_qr(self._name, self.id, values)

    def _get_qr_url(self):
        self.ensure_one()
        qr = self._generate_qr()
        return qr.qr_url

    def _regenerate_qr(self):
        self.ensure_one()
        return self._get_qr_service().regenerate_qr(self._name, self.id)

    def _download_png(self):
        self.ensure_one()
        return self._get_qr_service().download_png(self._name, self.id)

    def _download_svg(self):
        self.ensure_one()
        return self._get_qr_service().download_svg(self._name, self.id)

    def action_generate_qr(self):
        self.ensure_one()
        self._generate_qr()
        return True

    def action_regenerate_qr(self):
        self.ensure_one()
        self._regenerate_qr()
        return True

    def action_download_qr_png(self):
        self.ensure_one()
        return self._download_png()

    def action_download_qr_svg(self):
        self.ensure_one()
        return self._download_svg()

    def action_print_qr_label(self):
        self.ensure_one()
        qr = self._generate_qr()
        return self.env.ref('rn_universal_qr.action_report_qr_label').report_action(qr)

    def action_print_qr_a4(self):
        self.ensure_one()
        qr = self._generate_qr()
        return self.env.ref('rn_universal_qr.action_report_qr_a4').report_action(qr)

    def action_view_qr_records(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('QR Codes'),
            'res_model': 'rn.qr.record',
            'view_mode': 'list,form',
            'domain': [
                ('res_model', '=', self._name),
                ('res_id', '=', self.id),
            ],
            'context': {
                'default_res_model': self._name,
                'default_res_id': self.id,
                'default_company_id': self._get_qr_company_id(),
            },
        }

    def _get_qr_company_id(self):
        self.ensure_one()
        if 'company_id' in self._fields and self.company_id:
            return self.company_id.id
        return self.env.company.id

    def _get_qr_display_name(self):
        self.ensure_one()
        if 'display_name' in self._fields:
            return self.display_name
        if 'name' in self._fields:
            return self.name
        return '%s,%s' % (self._name, self.id)
