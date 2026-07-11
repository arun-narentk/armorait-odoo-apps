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
