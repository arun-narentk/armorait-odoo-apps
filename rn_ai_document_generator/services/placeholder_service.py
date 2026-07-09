# -*- coding: utf-8 -*-
"""Resolve {{placeholders}} from Odoo records and document context."""

import json
import logging
import re

from odoo import models

_logger = logging.getLogger(__name__)

PLACEHOLDER_RE = re.compile(r'\{\{\s*([a-zA-Z0-9_\.]+)\s*\}\}')


class RnAiDocumentPlaceholderService(models.AbstractModel):
    _name = 'rn.ai.document.placeholder.service'
    _description = 'AI Document Placeholder Service'

    def build_context(self, document):
        """Assemble a flat dict of common business variables."""
        company = document.company_id
        partner = document.partner_id
        employee = document.employee_id
        ctx = {
            'company_name': company.name or '',
            'company_email': company.email or '',
            'company_phone': company.phone or '',
            'company_street': company.street or '',
            'company_city': company.city or '',
            'company_country': company.country_id.name if company.country_id else '',
            'customer_name': partner.name if partner else '',
            'vendor_name': partner.name if partner else '',
            'partner_email': partner.email if partner else '',
            'partner_phone': ((partner.phone or partner.mobile) if partner else ''),
            'partner_street': partner.street if partner else '',
            'partner_city': partner.city if partner else '',
            'employee_name': employee.name if employee else '',
            'department': employee.department_id.name if employee and employee.department_id else '',
            'designation': employee.job_title if employee else '',
            'joining_date': '',
            'salary': '',
            'invoice_total': '',
            'quotation_items': '',
            'valid_until': '',
            'currency': company.currency_id.name if company.currency_id else '',
            'salesperson': document.user_id.name if document.user_id else '',
            'manager': '',
            'payment_terms': '',
            'document_name': document.name or '',
            'subject': document.subject or '',
        }
        if employee and hasattr(employee, 'joining_date') and employee.joining_date:
            ctx['joining_date'] = str(employee.joining_date)
        if employee and employee.parent_id:
            ctx['manager'] = employee.parent_id.name
        if document.res_model and document.res_id and document.res_model in self.env:
            record = self.env[document.res_model].browse(document.res_id)
            if record.exists():
                ctx.update(self._from_record(record))
        return ctx

    def _from_record(self, record):
        data = {}
        for field_name, key in [
            ('name', 'record_name'),
            ('amount_total', 'invoice_total'),
            ('amount_untaxed', 'amount_untaxed'),
            ('date_order', 'order_date'),
            ('validity_date', 'valid_until'),
            ('payment_term_id', 'payment_terms'),
        ]:
            if field_name in record._fields:
                value = record[field_name]
                if hasattr(value, 'name'):
                    value = value.name
                data[key] = str(value or '')
                if field_name == 'amount_total':
                    data['invoice_total'] = str(value or '')
                if field_name == 'validity_date':
                    data['valid_until'] = str(value or '')
        if 'order_line' in record._fields:
            lines = []
            for line in record.order_line[:50]:
                lines.append('%s x %s' % (line.product_id.display_name, line.product_uom_qty))
            data['quotation_items'] = '<br/>'.join(lines)
        if 'wage' in record._fields:
            data['salary'] = str(record.wage or '')
        return data

    def render(self, html, values):
        values = values or {}

        def repl(match):
            key = match.group(1)
            if key in values:
                return str(values.get(key) or '')
            return ''

        return PLACEHOLDER_RE.sub(repl, html or '')

    def dump_values(self, values):
        return json.dumps(values or {}, default=str)
