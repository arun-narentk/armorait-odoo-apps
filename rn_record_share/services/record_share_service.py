# -*- coding: utf-8 -*-
"""Record share business logic."""

from __future__ import annotations

import json
import logging
from datetime import timedelta
from urllib.parse import quote

from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError

from odoo.addons.rn_record_share import constants as const

_logger = logging.getLogger(__name__)


class RnRecordShareService(models.AbstractModel):
    _name = 'rn.record.share.service'
    _description = 'Record Share Service'

    @api.model
    def _param_str(self, key: str, default: str) -> str:
        value = self.env['ir.config_parameter'].sudo().get_param(key)
        return value if value not in (None, False, '') else default

    @api.model
    def _param_int(self, key: str, default: int) -> int:
        value = self.env['ir.config_parameter'].sudo().get_param(key)
        if value in (None, False, ''):
            return default
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    @api.model
    def _param_bool(self, key: str, default: bool = True) -> bool:
        value = self.env['ir.config_parameter'].sudo().get_param(key)
        if value in (None, False, ''):
            return default
        return str(value).lower() in ('1', 'true', 'yes')

    @api.model
    def get_settings(self) -> dict:
        return {
            'default_format': self._param_str(
                'rn_record_share.default_format',
                const.DEFAULT_LINK_FORMAT,
            ),
            'log_retention_days': self._param_int(
                'rn_record_share.log_retention_days',
                const.DEFAULT_LOG_RETENTION_DAYS,
            ),
            'enable_whatsapp': self._param_bool('rn_record_share.enable_whatsapp', True),
            'enable_email': self._param_bool('rn_record_share.enable_email', True),
        }

    @api.model
    def _get_record(self, res_model: str, res_id: int):
        if res_model not in self.env:
            raise UserError(_('Unsupported model: %s') % res_model)
        record = self.env[res_model].browse(res_id)
        if not record.exists():
            raise UserError(_('Record not found.'))
        return record

    @api.model
    def check_record_access(self, record) -> None:
        record.ensure_one()
        if not record.has_access('read'):
            raise AccessError(_('You do not have access to this record.'))

    @api.model
    def get_base_url(self) -> str:
        return (self.env['ir.config_parameter'].sudo().get_param('web.base.url') or '').rstrip('/')

    @api.model
    def get_internal_url(self, res_model: str, res_id: int) -> str:
        base = self.get_base_url()
        return f'{base}/odoo/{res_model}/{res_id}'

    @api.model
    def get_hash_url(self, res_model: str, res_id: int) -> str:
        base = self.get_base_url()
        return f'{base}/web#id={res_id}&model={res_model}&view_type=form'

    @api.model
    def get_record_label(self, record) -> str:
        record.ensure_one()
        return record.display_name or f'{record._name}/{record.id}'

    @api.model
    def format_share_text(self, record, fmt: str, url: str | None = None) -> str:
        record.ensure_one()
        label = self.get_record_label(record)
        share_url = url or self.get_internal_url(record._name, record.id)
        if fmt == const.FORMAT_MARKDOWN:
            return f'[{label}]({share_url})'
        if fmt == const.FORMAT_HTML:
            return f'<a href="{share_url}">{label}</a>'
        if fmt == const.FORMAT_NAME:
            return label
        if fmt == const.FORMAT_JSON:
            payload = {
                'model': record._name,
                'id': record.id,
                'name': label,
                'url': share_url,
            }
            return json.dumps(payload, indent=2)
        return share_url

    @api.model
    def log_share(
        self,
        record,
        action_type: str,
        fmt: str,
        shared_url: str,
    ) -> None:
        record.ensure_one()
        company_id = False
        if 'company_id' in record._fields and record.company_id:
            company_id = record.company_id.id
        self.env['rn.share.log'].sudo().create({
            'user_id': self.env.user.id,
            'company_id': company_id,
            'res_model': record._name,
            'res_id': record.id,
            'label': self.get_record_label(record),
            'action_type': action_type,
            'format_type': fmt,
            'shared_url': shared_url,
        })

    @api.model
    def clipboard_client_action(self, text: str, message: str | None = None):
        return {
            'type': 'ir.actions.client',
            'tag': 'rn_record_share.copy_clipboard',
            'params': {
                'text': text,
                'message': message or _('Copied to clipboard'),
            },
        }

    @api.model
    def copy_link_action(self, record, fmt: str | None = None):
        record.ensure_one()
        self.check_record_access(record)
        settings = self.get_settings()
        fmt = fmt or settings['default_format']
        text = self.format_share_text(record, fmt)
        self.log_share(record, const.ACTION_COPY, fmt, text)
        return self.clipboard_client_action(text, _('Link copied'))

    @api.model
    def get_share_payload(self, res_model: str, res_id: int) -> dict:
        record = self._get_record(res_model, res_id)
        self.check_record_access(record)
        internal_url = self.get_internal_url(res_model, res_id)
        hash_url = self.get_hash_url(res_model, res_id)
        label = self.get_record_label(record)
        settings = self.get_settings()
        qr_installed = bool(
            self.env['ir.module.module'].sudo().search_count([
                ('name', '=', 'rn_universal_qr'),
                ('state', '=', 'installed'),
            ])
        )
        return {
            'res_model': res_model,
            'res_id': res_id,
            'label': label,
            'internal_url': internal_url,
            'hash_url': hash_url,
            'formats': {
                fmt: self.format_share_text(record, fmt, internal_url)
                for fmt, _label in const.COPY_FORMATS
            },
            'settings': settings,
            'qr_installed': qr_installed,
            'email_subject': _('Record: %s') % label,
            'email_body': _('Open this record: %s') % internal_url,
            'whatsapp_text': _('Check this record: %s') % internal_url,
        }

    @api.model
    def action_copy_format(self, res_model: str, res_id: int, fmt: str):
        record = self._get_record(res_model, res_id)
        return self.copy_link_action(record, fmt)

    @api.model
    def action_email_share(self, res_model: str, res_id: int):
        record = self._get_record(res_model, res_id)
        self.check_record_access(record)
        if not self.get_settings()['enable_email']:
            raise UserError(_('Email share is disabled in settings.'))
        payload = self.get_share_payload(res_model, res_id)
        self.log_share(record, const.ACTION_EMAIL, const.FORMAT_URL, payload['internal_url'])
        subject = quote(payload['email_subject'])
        body = quote(payload['email_body'])
        return {
            'type': 'ir.actions.act_url',
            'url': f'mailto:?subject={subject}&body={body}',
            'target': 'new',
        }

    @api.model
    def action_whatsapp_share(self, res_model: str, res_id: int):
        record = self._get_record(res_model, res_id)
        self.check_record_access(record)
        if not self.get_settings()['enable_whatsapp']:
            raise UserError(_('WhatsApp share is disabled in settings.'))
        payload = self.get_share_payload(res_model, res_id)
        self.log_share(record, const.ACTION_WHATSAPP, const.FORMAT_URL, payload['internal_url'])
        text = quote(payload['whatsapp_text'])
        return {
            'type': 'ir.actions.act_url',
            'url': f'https://wa.me/?text={text}',
            'target': 'new',
        }

    @api.model
    def action_open_internal(self, res_model: str, res_id: int):
        record = self._get_record(res_model, res_id)
        self.check_record_access(record)
        self.log_share(record, const.ACTION_OPEN, const.FORMAT_URL, self.get_internal_url(res_model, res_id))
        return {
            'type': 'ir.actions.act_url',
            'url': self.get_internal_url(res_model, res_id),
            'target': 'new',
        }

    @api.model
    def open_qr_action(self, record):
        record.ensure_one()
        self.check_record_access(record)
        installed = self.env['ir.module.module'].sudo().search([
            ('name', '=', 'rn_universal_qr'),
            ('state', '=', 'installed'),
        ], limit=1)
        if not installed:
            raise UserError(_(
                'Install Universal QR Generator to generate QR codes from Record Share.'
            ))
        if not hasattr(record, 'action_generate_qr'):
            raise UserError(_('QR generation is not available on this model.'))
        record.action_generate_qr()
        self.log_share(
            record,
            const.ACTION_QR,
            const.FORMAT_URL,
            getattr(record, 'rn_qr_url', '') or self.get_internal_url(record._name, record.id),
        )
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('QR generated'),
                'message': _('QR code updated on this record.'),
                'type': 'success',
                'sticky': False,
            },
        }

    @api.model
    def get_dashboard_stats(self) -> dict:
        Log = self.env['rn.share.log']
        domain = [('user_id', '=', self.env.user.id)]
        today = fields.Datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        grouped = Log.read_group(
            domain,
            ['label:max'],
            ['res_model', 'res_id'],
            orderby='__count desc',
            limit=8,
            lazy=False,
        )
        return {
            'total_logs': Log.search_count(domain),
            'today_logs': Log.search_count(domain + [('create_date', '>=', today)]),
            'top_records': [
                {
                    'label': row.get('label_max') or row.get('label') or '',
                    'res_model': row['res_model'],
                    'res_id': row['res_id'],
                    'count': row['__count'],
                }
                for row in grouped
            ],
        }

    @api.model
    def cleanup_old_logs(self) -> None:
        days = self._param_int('rn_record_share.log_retention_days', const.DEFAULT_LOG_RETENTION_DAYS)
        if days <= 0:
            return
        cutoff = fields.Datetime.now() - timedelta(days=days)
        stale = self.env['rn.share.log'].sudo().search([('create_date', '<', cutoff)])
        if stale:
            _logger.info('Record Share cleanup removed %s log entries', len(stale))
            stale.unlink()
