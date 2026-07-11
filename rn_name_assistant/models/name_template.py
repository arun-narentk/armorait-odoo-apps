# -*- coding: utf-8 -*-
"""Configurable naming templates."""

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class RnNameTemplate(models.Model):
    _name = 'rn.name.template'
    _description = 'Name Template'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'priority desc, sequence, name'

    name = fields.Char(required=True, tracking=True)
    active = fields.Boolean(default=True, tracking=True)
    sequence = fields.Integer(default=10)
    priority = fields.Integer(
        default=10,
        help='Higher priority templates are evaluated first.',
        tracking=True,
    )
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
        tracking=True,
    )
    model_id = fields.Many2one(
        'ir.model',
        string='Model',
        ondelete='cascade',
        domain=[('model', 'in', [
            'product.template',
            'res.partner',
            'crm.lead',
            'project.project',
            'project.task',
        ])],
        tracking=True,
    )
    model_name = fields.Char(
        related='model_id.model',
        store=True,
        readonly=True,
    )
    template_body = fields.Char(
        required=True,
        help='Example: {Brand} {Series} {Model} {Category}',
        tracking=True,
    )
    condition_domain = fields.Char(
        string='Conditions',
        default='[]',
        help='Optional domain. Template applies only when the record matches.',
    )
    variant_template_ids = fields.One2many(
        'rn.name.template.variant',
        'template_id',
        string='Variant Templates',
    )
    preview_values = fields.Text(
        string='Preview JSON',
        help='Optional JSON for live preview in settings.',
    )

    @api.constrains('template_body')
    def _check_template_body(self):
        for template in self:
            if not template.template_body or '{' not in template.template_body:
                raise ValidationError('Template must include at least one placeholder like {Brand}.')


class RnNameTemplateVariant(models.Model):
    _name = 'rn.name.template.variant'
    _description = 'Name Template Variant'
    _order = 'sequence, id'

    template_id = fields.Many2one(
        'rn.name.template',
        required=True,
        ondelete='cascade',
    )
    sequence = fields.Integer(default=10)
    template_body = fields.Char(required=True)
