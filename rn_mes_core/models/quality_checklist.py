# -*- coding: utf-8 -*-
"""Quality inspection checklist templates."""

from odoo import fields, models


class RnMesQualityChecklist(models.Model):
    """Reusable inspection template for products or operations."""

    _name = 'rn.mes.quality.checklist'
    _description = 'MES Quality Checklist'
    _order = 'name'

    name = fields.Char(required=True)
    product_id = fields.Many2one('product.product', string='Product')
    operation_id = fields.Many2one('mrp.routing.workcenter', string='Operation')
    active = fields.Boolean(default=True)
    line_ids = fields.One2many('rn.mes.quality.checklist.line', 'checklist_id')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )


class RnMesQualityChecklistLine(models.Model):
    """Single checkpoint on a checklist."""

    _name = 'rn.mes.quality.checklist.line'
    _description = 'MES Quality Checklist Line'
    _order = 'sequence, id'

    checklist_id = fields.Many2one('rn.mes.quality.checklist', required=True, ondelete='cascade')
    sequence = fields.Integer(default=10)
    name = fields.Char(required=True, string='Checkpoint')
    check_type = fields.Selection(
        [
            ('pass_fail', 'Pass / Fail'),
            ('measurement', 'Measurement'),
            ('photo', 'Photo Required'),
            ('text', 'Text Note'),
        ],
        default='pass_fail',
        required=True,
    )
    min_value = fields.Float(string='Min')
    max_value = fields.Float(string='Max')
    uom = fields.Char(string='Unit')
