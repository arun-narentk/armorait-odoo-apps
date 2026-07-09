# -*- coding: utf-8 -*-
"""Partner-facing downloadable documents."""

from odoo import fields, models


class RnCustomerExperienceDownload(models.Model):
    _name = 'rn.customer.experience.download'
    _description = 'Experience Download'
    _order = 'sequence, name'

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    partner_id = fields.Many2one('res.partner', index=True)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
    )
    document_type = fields.Selection(
        selection=[
            ('invoice', 'Invoice'),
            ('quotation', 'Quotation'),
            ('manual', 'User Manual'),
            ('certificate', 'Certificate'),
            ('warranty_card', 'Warranty Card'),
            ('contract', 'Contract'),
            ('other', 'Other'),
        ],
        default='other',
    )
    attachment_id = fields.Many2one('ir.attachment', required=True, ondelete='restrict')
    is_public = fields.Boolean(
        default=False,
        help='If enabled, all portal users of the company can download this file.',
    )
