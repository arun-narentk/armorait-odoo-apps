# -*- coding: utf-8 -*-
"""Document series summary (invoice / credit note counts)."""

from odoo import fields, models


class RnGstDocumentSummary(models.Model):
    """Document issued / cancelled counts by nature for GSTR-1."""

    _name = 'rn.gst.document.summary'
    _description = 'GST Document Summary'
    _order = 'nature, id'

    return_id = fields.Many2one('rn.gst.return', required=True, ondelete='cascade', index=True)
    nature = fields.Selection(
        selection=[
            ('invoice', 'Invoices'),
            ('credit', 'Credit Notes'),
            ('debit', 'Debit Notes'),
            ('delivery', 'Delivery Challans'),
            ('other', 'Other'),
        ],
        required=True,
    )
    series_from = fields.Char(string='From')
    series_to = fields.Char(string='To')
    total_number = fields.Integer()
    cancelled = fields.Integer()
    net_issued = fields.Integer()
    company_id = fields.Many2one(related='return_id.company_id', store=True)
