# -*- coding: utf-8 -*-
"""PDF and image text extraction."""

import base64
import logging
import re

from odoo import models

_logger = logging.getLogger(__name__)


class RnAiInvoiceOcrService(models.AbstractModel):
    """Orchestrate OCR extraction and populate scan record."""

    _name = 'rn.ai.invoice.ocr.service'
    _description = 'AI Invoice OCR Service'

    def process_scan(self, scan):
        """Full pipeline: extract text, parse fields, match, duplicate check."""
        settings = self._get_settings(scan.company_id.id)
        if settings.credit_balance <= 0:
            scan.message_post(body='OCR credit balance is zero. Add credits to continue.')
            scan.write({'state': 'draft'})
            return

        raw_text = self._extract_text(scan.attachment_id)
        fields_data = self.env['rn.ai.invoice.extraction.service'].parse_invoice_text(raw_text)
        gst_data = {}
        if settings.enable_gst_india:
            gst_data = self.env['rn.ai.invoice.gst.service'].parse_gst(raw_text, fields_data)

        partner, partner_conf = self.env['rn.ai.invoice.vendor.match.service'].match_vendor(
            fields_data.get('partner_name'),
            fields_data.get('gstin'),
            company_id=scan.company_id.id,
        )
        dup = self.env['rn.ai.invoice.duplicate.service'].find_duplicate(
            partner.id if partner else False,
            fields_data.get('invoice_number'),
            company_id=scan.company_id.id,
        )

        scan.line_ids.unlink()
        lines = fields_data.get('lines', [])
        line_confs = []
        Line = self.env['rn.ai.invoice.scan.line']
        for idx, line in enumerate(lines):
            product, prod_conf = self.env['rn.ai.invoice.product.match.service'].match_product(
                line.get('description'),
                company_id=scan.company_id.id,
            )
            line_confs.append(prod_conf)
            Line.create({
                'scan_id': scan.id,
                'sequence': (idx + 1) * 10,
                'description': line.get('description'),
                'product_id': product.id if product else False,
                'quantity': line.get('quantity', 1.0),
                'price_unit': line.get('price_unit', 0.0),
                'tax_percent': line.get('tax_percent', 0.0),
                'price_subtotal': line.get('price_subtotal', 0.0),
                'hsn_code': line.get('hsn_code'),
                'confidence': prod_conf,
            })

        line_confidence = round(sum(line_confs) / len(line_confs), 1) if line_confs else 0.0
        state = 'duplicate' if dup else 'review'

        scan.write({
            'raw_text': raw_text,
            'partner_name_extracted': fields_data.get('partner_name'),
            'partner_id': partner.id if partner else False,
            'partner_confidence': partner_conf,
            'gstin': fields_data.get('gstin') or gst_data.get('gstin'),
            'gstin_confidence': 100.0 if fields_data.get('gstin') else 0.0,
            'invoice_number': fields_data.get('invoice_number'),
            'invoice_number_confidence': 95.0 if fields_data.get('invoice_number') else 0.0,
            'invoice_date': fields_data.get('invoice_date'),
            'invoice_date_confidence': 90.0 if fields_data.get('invoice_date') else 0.0,
            'due_date': fields_data.get('due_date'),
            'amount_untaxed': fields_data.get('amount_untaxed'),
            'amount_tax': fields_data.get('amount_tax'),
            'amount_total': fields_data.get('amount_total'),
            'amount_confidence': 95.0 if fields_data.get('amount_total') else 0.0,
            'cgst_amount': gst_data.get('cgst_amount', 0.0),
            'sgst_amount': gst_data.get('sgst_amount', 0.0),
            'igst_amount': gst_data.get('igst_amount', 0.0),
            'hsn_code': gst_data.get('hsn_code'),
            'line_confidence': line_confidence,
            'is_duplicate': bool(dup),
            'duplicate_move_id': dup.id if dup else False,
            'state': state,
        })
        settings.credit_balance -= 1
        scan.message_post(body='OCR extraction completed. Review highlighted fields.')

    def _extract_text(self, attachment):
        data = base64.b64decode(attachment.datas or b'')
        mimetype = (attachment.mimetype or '').lower()
        if 'pdf' in mimetype:
            return self._extract_pdf_text(data)
        if mimetype.startswith('image/'):
            return self._extract_image_placeholder(attachment.name)
        return data.decode('utf-8', errors='ignore')[:50000]

    def _extract_pdf_text(self, data):
        try:
            from pypdf import PdfReader
            import io
            reader = PdfReader(io.BytesIO(data))
            parts = []
            for page in reader.pages:
                parts.append(page.extract_text() or '')
            return '\n'.join(parts)
        except ImportError:
            try:
                from PyPDF2 import PdfReader
                import io
                reader = PdfReader(io.BytesIO(data))
                return '\n'.join(page.extract_text() or '' for page in reader.pages)
            except Exception as exc:
                _logger.warning('PDF extract failed: %s', exc)
                return ''
        except Exception as exc:
            _logger.warning('PDF extract failed: %s', exc)
            return ''

    def _extract_image_placeholder(self, filename):
        return (
            f'Image file {filename or "upload"}. '
            'Install Tesseract or enable LLM OCR companion for image text extraction.'
        )

    def _get_settings(self, company_id):
        Settings = self.env['rn.ai.invoice.ocr.settings']
        settings = Settings.search([('company_id', '=', company_id)], limit=1)
        if not settings:
            settings = Settings.create({
                'name': 'Invoice OCR Settings',
                'company_id': company_id,
            })
        return settings
