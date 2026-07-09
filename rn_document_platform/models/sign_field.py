# -*- coding: utf-8 -*-
"""Signature field placement on PDF pages."""

from odoo import fields, models


class RnDocSignField(models.Model):
    """Drag-and-drop signature field coordinates."""

    _name = 'rn.doc.sign.field'
    _description = 'Document Sign Field'
    _order = 'page, sequence'

    request_id = fields.Many2one(
        'rn.doc.sign.request',
        required=True,
        ondelete='cascade',
        index=True,
    )
    signer_id = fields.Many2one('rn.doc.sign.signer', required=True)
    sequence = fields.Integer(default=10)
    field_type = fields.Selection(
        selection=[
            ('signature', 'Signature'),
            ('initial', 'Initial'),
            ('date', 'Date'),
            ('text', 'Text'),
            ('checkbox', 'Checkbox'),
        ],
        default='signature',
        required=True,
    )
    page = fields.Integer(default=1)
    pos_x = fields.Float(string='X %')
    pos_y = fields.Float(string='Y %')
    width = fields.Float(default=20.0)
    height = fields.Float(default=8.0)
    required = fields.Boolean(default=True)
    company_id = fields.Many2one(related='request_id.company_id', store=True)
