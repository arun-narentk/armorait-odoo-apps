# -*- coding: utf-8 -*-
"""Trustees and board members."""

from odoo import fields, models


class RnTempleTrustee(models.Model):
    """Trustee, board member, or governing council representative."""

    _name = 'rn.temple.trustee'
    _description = 'Temple Trustee'
    _inherit = ['mail.thread']
    _order = 'sequence, name'

    name = fields.Char(required=True, tracking=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    temple_id = fields.Many2one(
        'rn.temple.temple',
        required=True,
        ondelete='cascade',
        index=True,
    )
    partner_id = fields.Many2one('res.partner', string='Contact')
    role = fields.Selection(
        selection=[
            ('chairperson', 'Chairperson'),
            ('trustee', 'Trustee'),
            ('secretary', 'Secretary'),
            ('treasurer', 'Treasurer'),
            ('member', 'Board Member'),
            ('advisor', 'Advisor'),
        ],
        default='trustee',
        required=True,
    )
    phone = fields.Char()
    email = fields.Char()
    term_start = fields.Date()
    term_end = fields.Date()
    is_signatory = fields.Boolean(string='Authorized Signatory')
    company_id = fields.Many2one(
        related='temple_id.company_id',
        store=True,
        index=True,
    )
    note = fields.Text()
