# -*- coding: utf-8 -*-
"""Invoice scan / OCR job."""

from odoo import api, fields, models
from odoo.exceptions import UserError

SCAN_STATES = [
    ('draft', 'Uploaded'),
    ('extracting', 'Extracting'),
    ('review', 'Ready for Review'),
    ('approved', 'Approved'),
    ('billed', 'Vendor Bill Created'),
    ('rejected', 'Rejected'),
    ('duplicate', 'Duplicate Detected'),
]


class RnAiInvoiceScan(models.Model):
    """Uploaded supplier invoice pending OCR and vendor bill creation."""

    _name = 'rn.ai.invoice.scan'
    _description = 'AI Invoice Scan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(required=True, default='New', tracking=True)
    reference = fields.Char(copy=False, index=True, default='New', tracking=True)
    state = fields.Selection(selection=SCAN_STATES, default='draft', tracking=True, index=True)
    attachment_id = fields.Many2one('ir.attachment', string='Invoice File', required=True)
    attachment_name = fields.Char(related='attachment_id.name', store=True)
    mimetype = fields.Char(related='attachment_id.mimetype')
    raw_text = fields.Text(string='Extracted Text', copy=False)
    partner_id = fields.Many2one('res.partner', string='Matched Vendor', tracking=True, index=True)
    partner_name_extracted = fields.Char(string='Vendor Name (OCR)')
    partner_confidence = fields.Float(string='Vendor Confidence %')
    gstin = fields.Char(string='GSTIN')
    gstin_confidence = fields.Float(string='GSTIN Confidence %')
    invoice_number = fields.Char(string='Invoice Number', index=True)
    invoice_number_confidence = fields.Float()
    invoice_date = fields.Date()
    invoice_date_confidence = fields.Float()
    due_date = fields.Date()
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    amount_untaxed = fields.Monetary(currency_field='currency_id')
    amount_tax = fields.Monetary(string='Tax Amount', currency_field='currency_id')
    amount_total = fields.Monetary(currency_field='currency_id')
    amount_confidence = fields.Float(string='Amount Confidence %')
    cgst_amount = fields.Monetary(string='CGST', currency_field='currency_id')
    sgst_amount = fields.Monetary(string='SGST', currency_field='currency_id')
    igst_amount = fields.Monetary(string='IGST', currency_field='currency_id')
    hsn_code = fields.Char(string='HSN/SAC')
    line_ids = fields.One2many('rn.ai.invoice.scan.line', 'scan_id', string='Line Items')
    line_confidence = fields.Float(string='Lines Confidence %')
    overall_confidence = fields.Float(compute='_compute_overall_confidence', store=True)
    is_duplicate = fields.Boolean(tracking=True)
    duplicate_move_id = fields.Many2one('account.move', string='Existing Bill')
    purchase_order_id = fields.Many2one('purchase.order', string='Linked PO')
    move_id = fields.Many2one('account.move', string='Vendor Bill', copy=False, tracking=True)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    note = fields.Html()

    @api.depends(
        'partner_confidence', 'gstin_confidence', 'invoice_number_confidence',
        'amount_confidence', 'line_confidence',
    )
    def _compute_overall_confidence(self):
        for scan in self:
            scores = [
                scan.partner_confidence or 0,
                scan.gstin_confidence or 0,
                scan.invoice_number_confidence or 0,
                scan.amount_confidence or 0,
                scan.line_confidence or 0,
            ]
            scan.overall_confidence = round(sum(scores) / len(scores), 1) if scores else 0.0

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('reference', 'New') == 'New':
                vals['reference'] = self.env['ir.sequence'].next_by_code('rn.ai.invoice.scan') or 'New'
            if vals.get('name', 'New') == 'New':
                vals['name'] = vals.get('reference', 'New')
        records = super().create(vals_list)
        for rec in records:
            if rec.attachment_id and not rec.attachment_id.res_id:
                rec.attachment_id.write({'res_model': rec._name, 'res_id': rec.id})
        return records

    def action_extract(self):
        for scan in self:
            scan.write({'state': 'extracting'})
            self.env['rn.ai.invoice.ocr.service'].process_scan(scan)
        return True

    def action_mark_review(self):
        self.write({'state': 'review'})

    def action_approve(self):
        self.write({'state': 'approved'})

    def action_reject(self):
        self.write({'state': 'rejected'})

    def action_create_vendor_bill(self):
        self.ensure_one()
        if self.state not in ('review', 'approved', 'duplicate'):
            raise UserError('Approve or review the scan before creating a vendor bill.')
        move = self.env['rn.ai.invoice.bill.service'].create_vendor_bill(self)
        self.write({'move_id': move.id, 'state': 'billed'})
        return {
            'type': 'ir.actions.act_window',
            'name': 'Vendor Bill',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': move.id,
        }

    def action_open_bill(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Vendor Bill',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': self.move_id.id,
        }
