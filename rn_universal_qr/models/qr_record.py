# -*- coding: utf-8 -*-
from odoo import api, fields, models


class QrRecord(models.Model):
    _name = 'rn.qr.record'
    _description = 'Universal QR Record'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'write_date desc, id desc'

    name = fields.Char(required=True, tracking=True)
    token = fields.Char(required=True, index=True, copy=False, tracking=True)
    res_model = fields.Char(required=True, index=True)
    res_id = fields.Integer(required=True, index=True)
    model_id = fields.Many2one('ir.model', compute='_compute_model_id', store=True)
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company, index=True)
    template_id = fields.Many2one('rn.qr.template')
    qr_image = fields.Binary(attachment=True, copy=False)
    qr_svg = fields.Text(copy=False)
    qr_url = fields.Char(copy=False)
    active = fields.Boolean(default=True)
    expiration_datetime = fields.Datetime()
    is_expired = fields.Boolean(compute='_compute_is_expired')
    last_generated_at = fields.Datetime(copy=False)
    scan_count = fields.Integer(compute='_compute_scan_stats')
    first_scanned_at = fields.Datetime(compute='_compute_scan_stats')
    last_scanned_at = fields.Datetime(compute='_compute_scan_stats')
    scan_log_ids = fields.One2many('rn.qr.scan.log', 'qr_record_id')

    _sql_constraints = [
        ('rn_qr_record_token_unique', 'unique(token)', 'QR token must be unique.'),
        ('rn_qr_record_model_res_unique', 'unique(res_model, res_id)', 'Only one QR record is allowed per business record.'),
    ]

    @api.depends('res_model')
    def _compute_model_id(self):
        model_names = [name for name in set(self.mapped('res_model')) if name]
        model_data = self.env['ir.model'].sudo().search_read([('model', 'in', model_names)], ['model'])
        model_map = {item['model']: item['id'] for item in model_data}
        for record in self:
            record.model_id = model_map.get(record.res_model)

    def _compute_is_expired(self):
        now = fields.Datetime.now()
        for record in self:
            record.is_expired = bool(record.expiration_datetime and record.expiration_datetime <= now)

    def _compute_scan_stats(self):
        grouped = self.env['rn.qr.scan.log'].read_group(
            [('qr_record_id', 'in', self.ids)],
            ['qr_record_id', 'scan_datetime:min', 'scan_datetime:max'],
            ['qr_record_id'],
            lazy=False,
        )
        counter = {row['qr_record_id'][0]: row for row in grouped if row.get('qr_record_id')}
        for record in self:
            value = counter.get(record.id, {})
            record.scan_count = value.get('qr_record_id_count', 0)
            record.first_scanned_at = value.get('scan_datetime_min')
            record.last_scanned_at = value.get('scan_datetime_max')

    def action_open_document(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': self.res_model,
            'res_id': self.res_id,
            'view_mode': 'form',
            'target': 'current',
        }

# -*- coding: utf-8 -*-
"""QR record storage with token-based secure URLs."""

import secrets

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class RnQrRecord(models.Model):
    _name = 'rn.qr.record'
    _description = 'QR Record'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(compute='_compute_name', store=True, readonly=True)
    active = fields.Boolean(default=True, tracking=True)
    token = fields.Char(required=True, index=True, copy=False, readonly=True, default=lambda self: self._default_token())
    res_model = fields.Char(required=True, index=True, tracking=True)
    res_id = fields.Integer(required=True, index=True, tracking=True)
    res_name = fields.Char(compute='_compute_res_name', store=True, readonly=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, index=True)

    payload_type = fields.Selection(
        selection='_selection_payload_type',
        required=True,
        default='record_url',
        tracking=True,
    )
    action_type = fields.Selection(
        selection='_selection_action_type',
        required=True,
        default='open_record',
        tracking=True,
    )
    custom_text = fields.Char(tracking=True)
    custom_url = fields.Char(tracking=True)
    server_action_id = fields.Many2one('ir.actions.server', ondelete='set null')

    qr_size = fields.Selection(selection='_selection_qr_size', required=True, default='200')
    qr_color = fields.Selection(selection='_selection_qr_color', required=True, default='black')
    custom_color = fields.Char(default='#000000')
    ecc_level = fields.Selection(selection='_selection_ecc_level', required=True, default='M')
    use_logo = fields.Boolean(default=False)
    template_id = fields.Many2one('rn.qr.template', ondelete='set null')

    qr_image = fields.Binary(attachment=True, copy=False)
    qr_url = fields.Char(compute='_compute_qr_url', store=True, readonly=True)
    payload_data = fields.Text(compute='_compute_payload_data', store=True, readonly=True)

    scan_count = fields.Integer(default=0, readonly=True, copy=False)
    first_scan = fields.Datetime(readonly=True, copy=False)
    last_scan = fields.Datetime(readonly=True, copy=False)
    expires_on = fields.Datetime(tracking=True)
    expiration_policy = fields.Selection(
        selection='_selection_expiration',
        default='never',
        required=True,
    )

    scan_log_ids = fields.One2many('rn.qr.scan.log', 'qr_record_id', string='Scan Logs')
    enable_report = fields.Boolean(
        string='Enable QR on Report',
        help='Include this QR on linked PDF reports when enabled globally.',
    )

    _sql_constraints = [
        ('token_unique', 'unique(token)', 'QR token must be unique.'),
    ]

    @api.model
    def _default_token(self):
        return secrets.token_urlsafe(24)

    @api.model
    def _selection_payload_type(self):
        return self.env['rn.qr.service']._get_payload_types()

    @api.model
    def _selection_action_type(self):
        return self.env['rn.qr.service']._get_action_types()

    @api.model
    def _selection_qr_size(self):
        return self.env['rn.qr.service']._get_qr_sizes()

    @api.model
    def _selection_qr_color(self):
        return self.env['rn.qr.service']._get_qr_colors()

    @api.model
    def _selection_ecc_level(self):
        return self.env['rn.qr.service']._get_ecc_levels()

    @api.model
    def _selection_expiration(self):
        return self.env['rn.qr.service']._get_expiration_policies()

    @api.depends('res_model', 'res_id', 'token')
    def _compute_name(self):
        for record in self:
            if record.res_model and record.res_id:
                record.name = 'QR %s [%s]' % (record.token[:8], record.res_model)
            else:
                record.name = 'QR %s' % (record.token[:8] if record.token else 'New')

    @api.depends('res_model', 'res_id')
    def _compute_res_name(self):
        for record in self:
            name = False
            if record.res_model and record.res_id:
                try:
                    target = self.env[record.res_model].browse(record.res_id)
                    if target.exists():
                        name = target.display_name
                except KeyError:
                    name = False
            record.res_name = name

    @api.depends('token')
    def _compute_qr_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url', '')
        for record in self:
            if record.token:
                record.qr_url = '%s/rn/qr/%s' % (base_url.rstrip('/'), record.token)
            else:
                record.qr_url = False

    @api.depends(
        'payload_type', 'action_type', 'token', 'custom_text', 'custom_url',
        'res_model', 'res_id', 'qr_url',
    )
    def _compute_payload_data(self):
        service = self.env['rn.qr.service']
        for record in self:
            record.payload_data = service.build_payload(record)

    @api.constrains('res_model', 'res_id')
    def _check_target_record(self):
        for record in self:
            if not record.res_model or not record.res_id:
                continue
            if record.res_model not in self.env:
                raise ValidationError(_('Model %s is not available.') % record.res_model)
            target = self.env[record.res_model].browse(record.res_id)
            if not target.exists():
                raise ValidationError(_('Linked record no longer exists.'))

    def action_generate_image(self):
        service = self.env['rn.qr.service']
        for record in self:
            record.qr_image = service.render_qr_image(record)
        return True

    def action_regenerate_token(self):
        service = self.env['rn.qr.service']
        for record in self:
            service.regenerate_qr_record(record)
        return True

    def action_open_target_record(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': self.res_model,
            'res_id': self.res_id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_view_scan_logs(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Scan Logs'),
            'res_model': 'rn.qr.scan.log',
            'view_mode': 'list,form',
            'domain': [('qr_record_id', '=', self.id)],
            'context': {'default_qr_record_id': self.id},
        }

    def is_expired(self):
        self.ensure_one()
        if not self.expires_on:
            return False
        return fields.Datetime.now() > self.expires_on

    def register_scan(self, user_agent=None, ip_address=None, user=None):
        self.ensure_one()
        return self.env['rn.qr.scan.service'].register_scan(
            self,
            user_agent=user_agent,
            ip_address=ip_address,
            user=user,
        )
