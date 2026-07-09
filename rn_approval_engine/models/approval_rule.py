# -*- coding: utf-8 -*-
"""Routing rules to select workflows by amount, department, etc."""

from odoo import fields, models


class RnApprovalRule(models.Model):
    """Conditional rule that maps documents to workflows."""

    _name = 'rn.approval.rule'
    _description = 'Approval Rule'
    _order = 'sequence, id'

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    workflow_id = fields.Many2one(
        'rn.approval.workflow',
        required=True,
        ondelete='cascade',
        index=True,
    )
    model_id = fields.Many2one(related='workflow_id.model_id', store=True)
    rule_type = fields.Selection(
        selection=[
            ('amount', 'Amount Range'),
            ('department', 'Department'),
            ('category', 'Product Category'),
            ('partner', 'Vendor/Customer'),
            ('always', 'Always Apply'),
        ],
        default='amount',
        required=True,
    )
    amount_min = fields.Monetary(currency_field='currency_id')
    amount_max = fields.Monetary(currency_field='currency_id')
    department_id = fields.Many2one('hr.department', string='Department')
    category_id = fields.Many2one('product.category', string='Product Category')
    partner_id = fields.Many2one('res.partner', string='Partner')
    currency_id = fields.Many2one(
        'res.currency',
        related='workflow_id.company_id.currency_id',
    )
    company_id = fields.Many2one(related='workflow_id.company_id', store=True)
