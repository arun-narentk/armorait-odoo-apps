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
