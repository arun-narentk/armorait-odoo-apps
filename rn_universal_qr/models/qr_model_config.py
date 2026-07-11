# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError


class QrModelConfig(models.Model):
    _name = 'rn.qr.model.config'
    _description = 'Universal QR Model Configuration'
    _order = 'model_id'

    name = fields.Char(compute='_compute_name', store=True)
    active = fields.Boolean(default=True)
    model_id = fields.Many2one('ir.model', required=True, domain=[('transient', '=', False)])
    model_name = fields.Char(related='model_id.model', store=True)
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    template_id = fields.Many2one('rn.qr.template')
    auto_generate_on_create = fields.Boolean(default=False)
    show_on_form = fields.Boolean(default=True)
    include_in_reports = fields.Boolean(default=True)
    generated_view_id = fields.Many2one('ir.ui.view', readonly=True, copy=False)

    _sql_constraints = [
        ('rn_qr_model_config_unique', 'unique(model_id, company_id)', 'Configuration already exists for this model and company.'),
    ]

    @api.depends('model_id')
    def _compute_name(self):
        for record in self:
            record.name = record.model_id.name if record.model_id else False

    def _find_primary_form_view(self):
        self.ensure_one()
        view = self.env['ir.ui.view'].sudo().search(
            [('model', '=', self.model_name), ('type', '=', 'form'), ('mode', '=', 'primary')],
            limit=1,
        )
        if not view:
            raise UserError(f'No primary form view found for model {self.model_name}.')
        return view

    def action_generate_form_view(self):
        for record in self:
            if record.generated_view_id:
                record.generated_view_id.unlink()
            inherit_view = record._find_primary_form_view()
            generated_view = self.env['ir.ui.view'].sudo().create({
                'name': f'Auto QR Form Extension {record.model_name}',
                'type': 'form',
                'model': record.model_name,
                'mode': 'extension',
                'inherit_id': inherit_view.id,
                'arch_base': """
                    <data>
                        <xpath expr="//sheet" position="inside">
                            <group string="QR">
                                <field name="rn_qr_token" readonly="1"/>
                                <field name="rn_qr_scan_count" readonly="1"/>
                                <field name="rn_qr_url" readonly="1"/>
                                <field name="rn_qr_expires_at"/>
                                <field name="rn_qr_image" widget="image"/>
                                <button name="action_generate_qr" type="object" class="btn-primary" string="Generate QR"/>
                            </group>
                        </xpath>
                    </data>
                """,
            })
            record.generated_view_id = generated_view.id
        return True

# -*- coding: utf-8 -*-
"""Per-model QR configuration for universal coverage."""

import logging

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class RnQrModelConfig(models.Model):
    _name = 'rn.qr.model.config'
    _description = 'QR Model Configuration'
    _order = 'model_id'

    name = fields.Char(compute='_compute_name', store=True, readonly=True)
    active = fields.Boolean(default=True)
    model_id = fields.Many2one('ir.model', required=True, ondelete='cascade', index=True)
    model_name = fields.Char(related='model_id.model', store=True, readonly=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    template_id = fields.Many2one('rn.qr.template', ondelete='set null')
    payload_type = fields.Selection(
        selection=lambda self: self.env['rn.qr.record']._selection_payload_type(),
        default='record_url',
    )
    action_type = fields.Selection(
        selection=lambda self: self.env['rn.qr.record']._selection_action_type(),
        default='open_record',
    )
    enable_smart_button = fields.Boolean(default=True)
    enable_notebook_page = fields.Boolean(default=True)
    enable_report = fields.Boolean(
        string='Enable QR on Report',
        help='Add QR block to supported report templates for this model.',
    )
    auto_generate = fields.Boolean(
        string='Auto-generate on Create',
        help='Create a QR code automatically when a new record is created.',
    )
    view_id = fields.Many2one('ir.ui.view', readonly=True, copy=False, ondelete='set null')

    _sql_constraints = [
        (
            'model_company_unique',
            'unique(model_id, company_id)',
            'Only one QR configuration per model and company is allowed.',
        ),
    ]

    @api.depends('model_id')
    def _compute_name(self):
        for record in self:
            record.name = record.model_id.name or record.model_id.model or 'QR Config'

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._setup_model_ui()
        return records

    def write(self, vals):
        res = super().write(vals)
        if any(key in vals for key in ('enable_smart_button', 'enable_notebook_page', 'active', 'model_id')):
            self._setup_model_ui()
        return res

    def unlink(self):
        views = self.mapped('view_id')
        res = super().unlink()
        views.filtered(lambda v: v.exists()).unlink()
        return res

    def _setup_model_ui(self):
        for config in self.filtered('active'):
            config._ensure_form_view_inheritance()
        inactive = self.filtered(lambda c: not c.active)
        inactive.mapped('view_id').unlink()
        inactive.write({'view_id': False})

    def _ensure_form_view_inheritance(self):
        self.ensure_one()
        if not self.model_id or not self.model_id.model:
            return
        model_name = self.model_id.model
        if model_name not in self.env:
            return
        base_view = self.env['ir.ui.view'].search([
            ('model', '=', model_name),
            ('type', '=', 'form'),
            ('mode', '=', 'primary'),
        ], limit=1)
        if not base_view:
            base_view = self.env['ir.ui.view'].search([
                ('model', '=', model_name),
                ('type', '=', 'form'),
            ], limit=1, order='priority asc, id asc')
        if not base_view:
            _logger.info('No form view found for model %s; skipping QR UI setup.', model_name)
            return

        arch_parts = ['<data>']
        if self.enable_smart_button:
            arch_parts.append("""
                <xpath expr="//div[@name='button_box']" position="inside">
                    <button name="action_view_qr_records" type="object"
                            class="oe_stat_button" icon="fa-qrcode"
                            groups="rn_universal_qr.group_rn_universal_qr_user">
                        <field name="rn_qr_count" widget="statinfo" string="QR"/>
                    </button>
                </xpath>
            """)
        if self.enable_notebook_page:
            arch_parts.append("""
                <xpath expr="//sheet" position="inside">
                    <group string="QR Code" name="rn_qr_group"
                           groups="rn_universal_qr.group_rn_universal_qr_user">
                        <group>
                            <field name="rn_qr_image" widget="image" class="oe_avatar"
                                   invisible="not rn_qr_active_id"/>
                            <field name="rn_qr_url" widget="url" invisible="not rn_qr_active_id"/>
                            <field name="rn_qr_scan_count" invisible="not rn_qr_active_id"/>
                            <field name="rn_qr_last_scan" invisible="not rn_qr_active_id"/>
                        </group>
                        <group>
                            <button name="action_generate_qr" type="object"
                                    string="Generate" class="btn-primary"
                                    invisible="rn_qr_active_id"/>
                            <button name="action_regenerate_qr" type="object"
                                    string="Regenerate"
                                    invisible="not rn_qr_active_id"/>
                            <button name="action_download_qr_png" type="object"
                                    string="Download PNG"
                                    invisible="not rn_qr_active_id"/>
                            <button name="action_download_qr_svg" type="object"
                                    string="Download SVG"
                                    invisible="not rn_qr_active_id"/>
                            <button name="action_print_qr_label" type="object"
                                    string="Print Label"
                                    invisible="not rn_qr_active_id"/>
                            <button name="action_print_qr_a4" type="object"
                                    string="Print A4"
                                    invisible="not rn_qr_active_id"/>
                        </group>
                    </group>
                </xpath>
            """)
        arch_parts.append('</data>')
        arch = '\n'.join(arch_parts)

        view_vals = {
            'name': 'rn.universal.qr.%s.form' % model_name.replace('.', '_'),
            'type': 'form',
            'model': model_name,
            'inherit_id': base_view.id,
            'mode': 'extension',
            'arch': arch,
            'active': True,
        }
        if self.view_id:
            self.view_id.write(view_vals)
        else:
            view = self.env['ir.ui.view'].create(view_vals)
            self.write({'view_id': view.id})

    def get_values_for_record(self):
        self.ensure_one()
        values = {
            'payload_type': self.payload_type or 'record_url',
            'action_type': self.action_type or 'open_record',
            'template_id': self.template_id.id if self.template_id else False,
            'company_id': self.company_id.id,
        }
        if self.template_id:
            values.update({
                'qr_size': self.template_id.qr_size,
                'qr_color': self.template_id.qr_color,
                'custom_color': self.template_id.custom_color,
                'ecc_level': self.template_id.ecc_level,
                'use_logo': self.template_id.use_logo,
                'payload_type': self.template_id.payload_type,
                'action_type': self.template_id.action_type,
            })
        return values
