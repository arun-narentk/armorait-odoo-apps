# -*- coding: utf-8 -*-
"""Duplicate document detection."""

from odoo import models


class RnDocumentIdpDuplicateService(models.AbstractModel):
    _name = 'rn.document.idp.duplicate.service'
    _description = 'IDP Duplicate Service'

    def find_duplicate_bill(self, partner_id, document_number, company_id=None):
        if not document_number:
            return self.env['account.move']
        company_id = company_id or self.env.company.id
        domain = [
            ('move_type', 'in', ('in_invoice', 'in_refund')),
            ('company_id', '=', company_id),
            ('ref', '=ilike', document_number),
            ('state', '!=', 'cancel'),
        ]
        if partner_id:
            domain.append(('partner_id', '=', partner_id))
        return self.env['account.move'].search(domain, limit=1)

    def find_duplicate_document(self, partner_id, document_number, document_type, company_id=None):
        company_id = company_id or self.env.company.id
        domain = [
            ('company_id', '=', company_id),
            ('document_number', '=ilike', document_number),
            ('document_type', '=', document_type),
            ('state', 'not in', ('rejected',)),
        ]
        if partner_id:
            domain.append(('partner_id', '=', partner_id))
        return self.env['rn.document.idp.document'].search(domain, limit=1)
