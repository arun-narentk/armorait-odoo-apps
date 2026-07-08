# -*- coding: utf-8 -*-
"""Temple branches."""

from odoo import api, fields, models


class RnTempleBranch(models.Model):
    """Physical branch or shrine under a temple trust."""

    _name = 'rn.temple.branch'
    _description = 'Temple Branch'
    _inherit = ['mail.thread']
    _order = 'sequence, name'

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(copy=False, index=True, default='New')
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    temple_id = fields.Many2one(
        'rn.temple.temple',
        required=True,
        ondelete='cascade',
        index=True,
    )
    is_head_office = fields.Boolean(string='Head Office')
    partner_id = fields.Many2one('res.partner', string='Contact')
    phone = fields.Char()
    email = fields.Char()
    street = fields.Char()
    city = fields.Char()
    state_id = fields.Many2one('res.country.state')
    zip = fields.Char()
    country_id = fields.Many2one('res.country')
    manager_id = fields.Many2one('rn.temple.trustee', string='Branch Manager')
    timing_ids = fields.One2many('rn.temple.timing', 'branch_id', string='Timings')
    festival_ids = fields.One2many('rn.temple.festival', 'branch_id', string='Festivals')
    company_id = fields.Many2one(
        related='temple_id.company_id',
        store=True,
        index=True,
    )
    note = fields.Text()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('code', 'New') == 'New':
                vals['code'] = self.env['ir.sequence'].next_by_code('rn.temple.branch') or 'New'
        return super().create(vals_list)
