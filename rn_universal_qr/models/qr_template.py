# -*- coding: utf-8 -*-
from odoo import fields, models


class QrTemplate(models.Model):
    _name = 'rn.qr.template'
    _description = 'Universal QR Template'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, id'

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(required=True, index=True, copy=False)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    size = fields.Selection([('small', 'Small'), ('large', 'Large')], required=True, default='small', tracking=True)
    template_type = fields.Selection(
        [
            ('small', 'Small'),
            ('large', 'Large'),
            ('warehouse', 'Warehouse'),
            ('office', 'Office'),
            ('customer', 'Customer'),
            ('manufacturing', 'Manufacturing'),
        ],
        required=True,
        default='small',
        tracking=True,
    )
    include_company = fields.Boolean(default=True)
    include_model = fields.Boolean(default=True)
    include_record_name = fields.Boolean(default=True)
    include_reference = fields.Boolean(default=False)
    note = fields.Text()

    _sql_constraints = [
        ('rn_qr_template_code_unique', 'unique(code)', 'Template code must be unique.'),
    ]

# -*- coding: utf-8 -*-
"""Reusable QR layout templates."""

from odoo import fields, models


class RnQrTemplate(models.Model):
    _name = 'rn.qr.template'
    _description = 'QR Template'
    _order = 'sequence, name'

    name = fields.Char(required=True)
    code = fields.Char(required=True, index=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    description = fields.Text()

    qr_size = fields.Selection(
        selection=lambda self: self.env['rn.qr.record']._selection_qr_size(),
        required=True,
        default='200',
    )
    qr_color = fields.Selection(
        selection=lambda self: self.env['rn.qr.record']._selection_qr_color(),
        required=True,
        default='black',
    )
    custom_color = fields.Char(default='#000000')
    ecc_level = fields.Selection(
        selection=lambda self: self.env['rn.qr.record']._selection_ecc_level(),
        required=True,
        default='M',
    )
    use_logo = fields.Boolean(default=False)
    payload_type = fields.Selection(
        selection=lambda self: self.env['rn.qr.record']._selection_payload_type(),
        required=True,
        default='record_url',
    )
    action_type = fields.Selection(
        selection=lambda self: self.env['rn.qr.record']._selection_action_type(),
        required=True,
        default='open_record',
    )
    label_width_mm = fields.Float(default=50.0)
    label_height_mm = fields.Float(default=30.0)
    show_record_name = fields.Boolean(default=True)
    show_barcode = fields.Boolean(default=False)
    font_size = fields.Integer(default=10)

    _sql_constraints = [
        ('code_unique', 'unique(code)', 'Template code must be unique.'),
    ]
