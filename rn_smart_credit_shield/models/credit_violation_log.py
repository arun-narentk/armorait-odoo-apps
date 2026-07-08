# -*- coding: utf-8 -*-
"""
Credit violation log for governance and compliance.
Records SO blocks and overrides: who, when, reason.
"""

from odoo import _, api, fields, models


class CreditViolationLog(models.Model):
    _name = 'credit.violation.log'
    _description = 'Credit Violation / Override Log'
    _order = 'create_date desc'

    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company, ondelete='cascade')
    order_id = fields.Many2one('sale.order', string='Sale Order', required=True, ondelete='cascade', index=True)
    partner_id = fields.Many2one('res.partner', string='Partner', related='order_id.partner_id', store=True, readonly=True)
    risk_level = fields.Selection(
        [('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')],
        string='Risk Level',
        required=True,
    )
    blocked_by_system = fields.Boolean(
        string='Blocked by System',
        default=True,
        help='True if confirmation was blocked; False if it was a warning (high risk) or override.',
    )
    override_by_id = fields.Many2one(
        'res.users',
        string='Override By',
        help='User who approved override (if overridden).',
    )
    override_reason = fields.Text(string='Override Reason')

    @api.model
    def log_block(self, order, risk_level='critical', override_by=None, override_reason=None):
        """
        Create a violation log entry.
        :param order: sale.order (singleton)
        :param risk_level: str
        :param override_by: res.users or None
        :param override_reason: str or None
        :return: credit.violation.log
        """
        return self.create({
            'company_id': order.company_id.id,
            'order_id': order.id,
            'risk_level': risk_level,
            'blocked_by_system': override_by is None,
            'override_by_id': override_by.id if override_by else False,
            'override_reason': override_reason or '',
        })
