# -*- coding: utf-8 -*-
"""Product warranty tracking for portal customers."""

from odoo import fields, models


class RnCustomerExperienceWarranty(models.Model):
    _name = 'rn.customer.experience.warranty'
    _description = 'Experience Warranty'
    _order = 'end_date desc'

    name = fields.Char(required=True)
    partner_id = fields.Many2one('res.partner', required=True, index=True)
    product_id = fields.Many2one('product.product')
    serial_number = fields.Char(index=True)
    start_date = fields.Date()
    end_date = fields.Date()
    state = fields.Selection(
        selection=[
            ('active', 'Active'),
            ('expired', 'Expired'),
            ('claimed', 'Claimed'),
        ],
        default='active',
        index=True,
    )
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
    )
    notes = fields.Text()

    @property
    def remaining_days(self):
        if not self.end_date:
            return 0
        today = fields.Date.today()
        return max((self.end_date - today).days, 0)
