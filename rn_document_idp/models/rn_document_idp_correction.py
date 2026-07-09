# -*- coding: utf-8 -*-
"""User corrections for continuous learning hooks."""

from odoo import fields, models


class RnDocumentIdpCorrection(models.Model):
    _name = 'rn.document.idp.correction'
    _description = 'IDP Field Correction'
    _order = 'create_date desc'

    document_id = fields.Many2one(
        'rn.document.idp.document',
        required=True,
        ondelete='cascade',
        index=True,
    )
    field_name = fields.Char(required=True)
    extracted_value = fields.Char()
    corrected_value = fields.Char(required=True)
    company_id = fields.Many2one(related='document_id.company_id', store=True)
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user)
