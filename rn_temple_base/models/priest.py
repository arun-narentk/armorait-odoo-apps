# -*- coding: utf-8 -*-
"""Priests and clergy."""

from odoo import fields, models


class RnTemplePriest(models.Model):
    """Priest, pujari, pastor, imam, granthi, or other religious officiant."""

    _name = 'rn.temple.priest'
    _description = 'Temple Priest / Clergy'
    _inherit = ['mail.thread']
    _order = 'name'

    name = fields.Char(required=True, tracking=True)
    active = fields.Boolean(default=True)
    temple_id = fields.Many2one(
        'rn.temple.temple',
        required=True,
        ondelete='cascade',
        index=True,
    )
    branch_id = fields.Many2one('rn.temple.branch', string='Primary Branch', index=True)
    employee_id = fields.Many2one('hr.employee', string='Linked Employee')
    partner_id = fields.Many2one('res.partner', string='Contact')
    priest_type = fields.Selection(
        selection=[
            ('head', 'Head Priest'),
            ('senior', 'Senior Priest'),
            ('priest', 'Priest'),
            ('assistant', 'Assistant'),
            ('volunteer', 'Volunteer Priest'),
        ],
        default='priest',
        required=True,
    )
    specialization = fields.Char(
        help='Example: Archana, Homam, Marriage, Special Darshan',
    )
    phone = fields.Char()
    email = fields.Char()
    languages = fields.Char(help='Comma-separated languages spoken')
    company_id = fields.Many2one(
        related='temple_id.company_id',
        store=True,
        index=True,
    )
    note = fields.Text()
