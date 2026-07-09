# -*- coding: utf-8 -*-
"""Immutable signing audit log."""

from odoo import fields, models


class RnDocSignAudit(models.Model):
    """Audit entry for document signing events."""

    _name = 'rn.doc.sign.audit'
    _description = 'Document Sign Audit'
    _order = 'create_date desc'

    request_id = fields.Many2one(
        'rn.doc.sign.request',
        required=True,
        ondelete='cascade',
        index=True,
    )
    signer_id = fields.Many2one('rn.doc.sign.signer')
    user_id = fields.Many2one('res.users')
    action = fields.Selection(
        selection=[
            ('create', 'Created'),
            ('send', 'Sent'),
            ('view', 'Viewed'),
            ('sign', 'Signed'),
            ('decline', 'Declined'),
            ('remind', 'Reminder Sent'),
            ('complete', 'Completed'),
            ('hash', 'Hash Verified'),
        ],
        required=True,
    )
    ip_address = fields.Char()
    user_agent = fields.Char()
    document_hash = fields.Char()
    comment = fields.Text()
    company_id = fields.Many2one(related='request_id.company_id', store=True)
