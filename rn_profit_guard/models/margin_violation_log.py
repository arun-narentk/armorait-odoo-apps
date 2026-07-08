# -*- coding: utf-8 -*-

from odoo import fields, models


class MarginViolationLog(models.Model):
    _name = 'margin.violation.log'
    _description = 'Margin Violation Log'
    _order = 'create_date desc'

    order_id = fields.Many2one('sale.order', string='Sale Order', ondelete='cascade', index=True)
    order_line_id = fields.Many2one('sale.order.line', string='Order Line', ondelete='set null', index=True)
    margin_pct = fields.Float(string='Margin %', digits=(5, 2))
    status = fields.Selection([
        ('warning', 'Warning'),
        ('danger', 'Danger'),
        ('override', 'Override'),
    ], string='Status', required=True)
    reason = fields.Text(string='Reason')
    approved_by_id = fields.Many2one('res.users', string='Approved By', ondelete='set null')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
