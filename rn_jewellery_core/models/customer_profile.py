# -*- coding: utf-8 -*-

from odoo import fields, models


class RnJewelleryCustomerProfile(models.Model):
    _name = 'rn.jewellery.customer.profile'
    _description = 'Jewellery Customer Profile'
    _order = 'loyalty_points desc'

    partner_id = fields.Many2one('res.partner', required=True, ondelete='cascade', index=True)
    loyalty_points = fields.Integer(default=0)
    preferred_metal = fields.Selection(
        [('gold', 'Gold'), ('silver', 'Silver'), ('platinum', 'Platinum'), ('diamond', 'Diamond')],
    )
    birthday = fields.Date()
    anniversary = fields.Date()
    purchase_total = fields.Float(readonly=True)
    last_purchase_date = fields.Date()
    note = fields.Text()
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    _sql_constraints = [
        ('partner_company_uniq', 'unique(partner_id, company_id)', 'One jewellery profile per customer per company.'),
    ]
