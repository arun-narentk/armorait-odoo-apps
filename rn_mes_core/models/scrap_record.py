# -*- coding: utf-8 -*-
"""Scrap and reject quantities captured on the floor."""

from odoo import fields, models


class RnMesScrapRecord(models.Model):
    """Shop-floor scrap/reject entry linked to a session."""

    _name = 'rn.mes.scrap.record'
    _description = 'MES Scrap Record'
    _order = 'create_date desc'

    session_id = fields.Many2one('rn.mes.production.session', required=True, ondelete='cascade', index=True)
    workorder_id = fields.Many2one(related='session_id.workorder_id', store=True, readonly=True)
    product_id = fields.Many2one('product.product', string='Product')
    scrap_type = fields.Selection(
        [
            ('scrap', 'Scrap'),
            ('reject', 'Reject'),
        ],
        default='scrap',
        required=True,
    )
    quantity = fields.Float(required=True, digits='Product Unit')
    reason = fields.Char()
    note = fields.Text()
    attachment_ids = fields.Many2many('ir.attachment', string='Evidence')
    company_id = fields.Many2one(
        related='session_id.company_id',
        store=True,
        readonly=True,
        index=True,
    )
