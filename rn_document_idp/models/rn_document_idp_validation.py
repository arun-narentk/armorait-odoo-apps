# -*- coding: utf-8 -*-
"""Business validation results for captured documents."""

from odoo import fields, models


class RnDocumentIdpValidation(models.Model):
    _name = 'rn.document.idp.validation'
    _description = 'IDP Validation Result'
    _order = 'id desc'

    document_id = fields.Many2one(
        'rn.document.idp.document',
        required=True,
        ondelete='cascade',
        index=True,
    )
    company_id = fields.Many2one(related='document_id.company_id', store=True)
    rule_code = fields.Char(required=True, index=True)
    name = fields.Char(required=True)
    state = fields.Selection(
        selection=[
            ('passed', 'Passed'),
            ('failed', 'Failed'),
            ('warning', 'Warning'),
        ],
        required=True,
    )
    message = fields.Text()
