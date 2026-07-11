# -*- coding: utf-8 -*-

from odoo import api, fields, models

from ..constants import COLOR_SELECTION, ICON_SELECTION


class RnVisualStatus(models.Model):
    _name = 'rn.visual.status'
    _description = 'Visual Status Map'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, id'

    name = fields.Char(compute='_compute_name', store=True, readonly=True)
    active = fields.Boolean(default=True, tracking=True)
    model_id = fields.Many2one(
        'ir.model',
        required=True,
        ondelete='cascade',
        index=True,
        domain=[('transient', '=', False)],
        tracking=True,
    )
    model_name = fields.Char(related='model_id.model', store=True, index=True)
    field_name = fields.Char(required=True, index=True, tracking=True)
    field_value = fields.Char(required=True, index=True, tracking=True)
    emoji = fields.Char(tracking=True)
    icon = fields.Selection(selection=ICON_SELECTION, default='none', tracking=True)
    color = fields.Selection(selection=COLOR_SELECTION, default='gray', index=True, tracking=True)
    label = fields.Char(tracking=True)
    sequence = fields.Integer(default=10, index=True)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
        tracking=True,
    )

    _sql_constraints = [
        (
            'rn_visual_status_unique',
            'unique(model_id, field_name, field_value, company_id)',
            'Each status value can only be mapped once per model and company.',
        ),
    ]

    @api.depends('model_id', 'field_name', 'field_value', 'emoji', 'label')
    def _compute_name(self):
        for record in self:
            parts = [
                record.model_id.name or record.model_name or '',
                record.field_name or '',
                record.field_value or '',
            ]
            record.name = ' / '.join(part for part in parts if part)

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        self.env['rn.color.rule.service'].clear_rule_cache()
        return records

    def write(self, vals):
        result = super().write(vals)
        self.env['rn.color.rule.service'].clear_rule_cache()
        return result

    def unlink(self):
        result = super().unlink()
        self.env['rn.color.rule.service'].clear_rule_cache()
        return result
