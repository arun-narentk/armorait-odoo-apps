# -*- coding: utf-8 -*-

from odoo import fields, models


class AiBizBenefit(models.Model):
    """Benefit card shown on the AI BIZ landing page."""

    _name = 'ai.biz.benefit'
    _description = 'AI BIZ Benefit'
    _order = 'sequence, id'

    promotion_id = fields.Many2one(
        'ai.biz.promotion',
        required=True,
        ondelete='cascade',
        index=True,
    )
    sequence = fields.Integer(default=10, index=True)
    icon = fields.Image(max_width=256, max_height=256)
    title = fields.Char(required=True)
    description = fields.Text(required=True)
    company_id = fields.Many2one(
        related='promotion_id.company_id',
        store=True,
        index=True,
    )
