# -*- coding: utf-8 -*-
"""Conversational document search (keyword router)."""

from datetime import timedelta

from odoo import fields, models


class RnDocumentIdpSearchService(models.AbstractModel):
    _name = 'rn.document.idp.search.service'
    _description = 'IDP Search Service'

    def search_documents(self, query: str, limit=20):
        query_lower = (query or '').lower()
        Document = self.env['rn.document.idp.document']
        domain = [('company_id', '=', self.env.company.id)]
        if 'pending' in query_lower or 'review' in query_lower or 'validation' in query_lower:
            domain.append(('state', 'in', ('review', 'fraud_flag')))
        if 'transport' in query_lower:
            domain.append(('document_type', '=', 'transport_bill'))
        if 'challan' in query_lower or 'delivery' in query_lower:
            domain.append(('document_type', '=', 'delivery_challan'))
        if 'invoice' in query_lower:
            domain.append(('document_type', 'in', ('vendor_invoice', 'customer_invoice')))
        if 'this week' in query_lower:
            week_ago = fields.Datetime.now() - timedelta(days=7)
            domain.append(('create_date', '>=', week_ago))
        amount = self._extract_amount(query_lower)
        if amount:
            domain.append(('amount_total', '>=', amount))
        partner_name = self._extract_partner_name(query_lower)
        if partner_name:
            domain.append(('partner_id.name', 'ilike', partner_name))
        documents = Document.search(domain, limit=limit, order='create_date desc')
        return [{
            'id': doc.id,
            'name': doc.name,
            'document_type': doc.document_type,
            'state': doc.state,
            'partner': doc.partner_id.name,
            'amount_total': doc.amount_total,
            'confidence': doc.overall_confidence,
        } for doc in documents]

    def _extract_amount(self, query_lower):
        import re
        match = re.search(r'(?:above|over|greater than)\s*[\u20b9rs\.]*\s*([\d,]+)', query_lower)
        if match:
            return float(match.group(1).replace(',', ''))
        match = re.search(r'([\d,]+)\s*(?:lakh|lac)', query_lower)
        if match:
            return float(match.group(1).replace(',', '')) * 100000
        return 0.0

    def _extract_partner_name(self, query_lower):
        import re
        match = re.search(r'from\s+([a-z0-9 &\.]+)', query_lower)
        return match.group(1).strip().title() if match else ''
