# -*- coding: utf-8 -*-
"""PDF generation for business documents."""

from odoo import models


class RnWhatsappPdfService(models.AbstractModel):
    """Generate PDF attachments for quotations, invoices, and deliveries."""

    _name = 'rn.whatsapp.pdf.service'
    _description = 'WhatsApp PDF Service'

    REPORT_MAP = {
        'sale.order': 'sale.action_report_saleorder',
        'account.move': 'account.account_invoices',
        'stock.picking': 'stock.action_report_delivery',
        'purchase.order': 'purchase.action_report_purchase_order',
    }

    def generate_pdf_attachment(self, record):
        """Return ir.attachment bytes for a supported business document."""
        report_xmlid = self.REPORT_MAP.get(record._name)
        if not report_xmlid:
            return False
        # Phase 6: render report and return attachment vals.
        return False
