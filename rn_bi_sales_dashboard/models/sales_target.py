# -*- coding: utf-8 -*-
"""Sales target definitions and achievement."""

from odoo import api, fields, models


class RnBiSalesTarget(models.Model):
    """Monthly/quarterly/yearly sales targets."""

    _name = 'rn.bi.sales.target'
    _description = 'BI Sales Target'
    _inherit = ['mail.thread']
    _order = 'date_start desc'

    name = fields.Char(required=True, tracking=True)
    period_type = fields.Selection(
        selection=[
            ('month', 'Monthly'),
            ('quarter', 'Quarterly'),
            ('year', 'Yearly'),
        ],
        required=True,
        default='month',
    )
    date_start = fields.Date(required=True)
    date_end = fields.Date(required=True)
    target_amount = fields.Monetary(currency_field='currency_id', required=True, tracking=True)
    achieved_amount = fields.Monetary(currency_field='currency_id', compute='_compute_achievement', store=True)
    achievement_pct = fields.Float(string='Achievement %', compute='_compute_achievement', store=True)
    remaining_amount = fields.Monetary(currency_field='currency_id', compute='_compute_achievement', store=True)
    user_id = fields.Many2one('res.users', string='Salesperson')
    team_id = fields.Many2one('crm.team', string='Sales Team')
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    state = fields.Selection(
        selection=[('draft', 'Draft'), ('open', 'Open'), ('done', 'Done')],
        default='open',
        tracking=True,
    )

    @api.depends('target_amount', 'date_start', 'date_end', 'user_id', 'team_id', 'company_id')
    def _compute_achievement(self):
        """Compute achievement from confirmed sales orders in range."""
        SaleOrder = self.env['sale.order']
        for target in self:
            domain = [
                ('state', '=', 'sale'),
                ('date_order', '>=', target.date_start),
                ('date_order', '<=', target.date_end),
                ('company_id', '=', target.company_id.id),
            ]
            if target.user_id:
                domain.append(('user_id', '=', target.user_id.id))
            if target.team_id:
                domain.append(('team_id', '=', target.team_id.id))
            orders = SaleOrder.search(domain)
            achieved = sum(orders.mapped('amount_untaxed'))
            target.achieved_amount = achieved
            target.remaining_amount = max(0.0, (target.target_amount or 0.0) - achieved)
            target.achievement_pct = (
                (achieved / target.target_amount) * 100.0 if target.target_amount else 0.0
            )
