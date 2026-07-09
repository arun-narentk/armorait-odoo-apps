# -*- coding: utf-8 -*-
"""Fleet operational expenses."""

from odoo import fields, models


class RnFleetExpenseLog(models.Model):
    """Toll, parking, repair, and other trip/vehicle costs."""

    _name = 'rn.fleet.expense.log'
    _description = 'Fleet Expense Log'
    _order = 'date desc, id desc'

    name = fields.Char(required=True)
    vehicle_id = fields.Many2one('fleet.vehicle', required=True, index=True)
    trip_id = fields.Many2one('rn.fleet.trip', index=True)
    driver_id = fields.Many2one('res.partner', string='Driver')
    date = fields.Date(required=True, default=fields.Date.context_today, index=True)
    expense_type = fields.Selection(
        selection=[
            ('toll', 'Toll'),
            ('parking', 'Parking'),
            ('fuel', 'Fuel'),
            ('repair', 'Repair'),
            ('insurance', 'Insurance'),
            ('tyres', 'Tyres'),
            ('fine', 'Fine'),
            ('other', 'Other'),
        ],
        default='other',
        required=True,
    )
    amount = fields.Monetary(required=True, currency_field='currency_id')
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id,
    )
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    note = fields.Text()
