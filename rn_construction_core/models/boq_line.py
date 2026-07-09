# -*- coding: utf-8 -*-

from odoo import api, fields, models


class RnConstructionBoqLine(models.Model):
    _name = 'rn.construction.boq.line'
    _description = 'BOQ Line'
    _order = 'sequence, id'

    boq_id = fields.Many2one('rn.construction.boq', required=True, ondelete='cascade', index=True)
    sequence = fields.Integer(default=10)
    item_type = fields.Selection(
        [
            ('material', 'Material'),
            ('labour', 'Labour'),
            ('equipment', 'Equipment'),
            ('subcontract', 'Subcontract'),
            ('overhead', 'Overhead'),
        ],
        default='material',
        required=True,
    )
    description = fields.Char(required=True)
    product_id = fields.Many2one('product.product')
    uom = fields.Char(string='UoM', default='Nos')
    quantity = fields.Float(default=1.0)
    unit_rate = fields.Float(string='Estimated Rate')
    estimated_amount = fields.Float(compute='_compute_amounts', store=True)
    actual_qty = fields.Float(string='Actual Qty')
    actual_rate = fields.Float(string='Actual Rate')
    actual_amount = fields.Float(compute='_compute_amounts', store=True)
    company_id = fields.Many2one(related='boq_id.company_id', store=True, index=True)

    @api.depends('quantity', 'unit_rate', 'actual_qty', 'actual_rate')
    def _compute_amounts(self):
        for line in self:
            line.estimated_amount = (line.quantity or 0.0) * (line.unit_rate or 0.0)
            aq = line.actual_qty if line.actual_qty else line.quantity
            ar = line.actual_rate if line.actual_rate else line.unit_rate
            line.actual_amount = (aq or 0.0) * (ar or 0.0)
