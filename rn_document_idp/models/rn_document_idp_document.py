# -*- coding: utf-8 -*-
"""Captured business document pending IDP pipeline."""

from odoo import api, fields, models
from odoo.exceptions import UserError

DOCUMENT_STATES = [
    ('draft', 'Captured'),
    ('extracting', 'Processing'),
    ('classified', 'Classified'),
    ('review', 'Needs Review'),
    ('approved', 'Approved'),
    ('posted', 'Posted to ERP'),
    ('rejected', 'Rejected'),
    ('duplicate', 'Duplicate'),
    ('fraud_flag', 'Fraud Alert'),
]

DOCUMENT_TYPES = [
    ('vendor_invoice', 'Vendor Invoice'),
    ('customer_invoice', 'Customer Invoice'),
    ('credit_note', 'Credit Note'),
    ('debit_note', 'Debit Note'),
    ('expense_receipt', 'Expense Receipt'),
    ('purchase_order', 'Purchase Order'),
    ('rfq', 'RFQ'),
    ('supplier_quotation', 'Supplier Quotation'),
    ('delivery_challan', 'Delivery Challan'),
    ('goods_receipt', 'Goods Receipt Note'),
    ('transport_bill', 'Transport Bill'),
    ('packing_list', 'Packing List'),
    ('contract', 'Contract'),
    ('other', 'Other'),
]

CAPTURE_CHANNELS = [
    ('upload', 'Upload'),
    ('email', 'Email'),
    ('whatsapp', 'WhatsApp'),
    ('scanner', 'Scanner'),
    ('mobile', 'Mobile Camera'),
    ('api', 'API'),
    ('folder', 'Shared Folder'),
]


class RnDocumentIdpDocument(models.Model):
    _name = 'rn.document.idp.document'
    _description = 'IDP Document'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(required=True, default='New', tracking=True)
    reference = fields.Char(copy=False, index=True, default='New', tracking=True)
    state = fields.Selection(selection=DOCUMENT_STATES, default='draft', tracking=True, index=True)
    document_type = fields.Selection(selection=DOCUMENT_TYPES, tracking=True, index=True)
    document_type_confidence = fields.Float(string='Classification Confidence %')
    capture_channel = fields.Selection(selection=CAPTURE_CHANNELS, default='upload', tracking=True)
    attachment_id = fields.Many2one('ir.attachment', string='Document File', required=True)
    attachment_name = fields.Char(related='attachment_id.name', store=True)
    mimetype = fields.Char(related='attachment_id.mimetype')
    raw_text = fields.Text(copy=False)
    partner_id = fields.Many2one('res.partner', string='Matched Partner', tracking=True, index=True)
    partner_name_extracted = fields.Char(string='Partner Name (Extracted)')
    partner_confidence = fields.Float()
    gstin = fields.Char(string='GSTIN / Tax ID')
    document_number = fields.Char(string='Document Number', index=True)
    document_date = fields.Date()
    due_date = fields.Date()
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    amount_untaxed = fields.Monetary(currency_field='currency_id')
    amount_tax = fields.Monetary(currency_field='currency_id')
    amount_total = fields.Monetary(currency_field='currency_id')
    amount_confidence = fields.Float()
    overall_confidence = fields.Float(compute='_compute_overall_confidence', store=True)
    validation_state = fields.Selection(
        selection=[
            ('pending', 'Pending'),
            ('passed', 'Passed'),
            ('failed', 'Failed'),
        ],
        default='pending',
        tracking=True,
    )
    validation_ids = fields.One2many('rn.document.idp.validation', 'document_id')
    line_ids = fields.One2many('rn.document.idp.line', 'document_id')
    line_confidence = fields.Float()
    is_duplicate = fields.Boolean(tracking=True)
    duplicate_move_id = fields.Many2one('account.move', string='Duplicate Bill')
    purchase_order_id = fields.Many2one('purchase.order', string='Linked PO')
    match_state = fields.Selection(
        selection=[
            ('na', 'Not Applicable'),
            ('pending', 'Pending'),
            ('matched', 'Matched'),
            ('mismatch', 'Mismatch'),
        ],
        default='na',
        tracking=True,
    )
    match_score = fields.Float(string='3-Way Match %')
    fraud_score = fields.Float()
    fraud_notes = fields.Text()
    move_id = fields.Many2one('account.move', string='Vendor Bill', copy=False, tracking=True)
    posted_model = fields.Char(string='Posted Model')
    posted_res_id = fields.Integer(string='Posted Record ID')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    note = fields.Html()
    processing_seconds = fields.Float(help='Time spent in extraction pipeline.')

    @api.depends(
        'document_type_confidence', 'partner_confidence', 'amount_confidence', 'line_confidence',
    )
    def _compute_overall_confidence(self):
        for document in self:
            scores = [
                document.document_type_confidence or 0,
                document.partner_confidence or 0,
                document.amount_confidence or 0,
                document.line_confidence or 0,
            ]
            document.overall_confidence = round(sum(scores) / len(scores), 1) if scores else 0.0

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('reference', 'New') == 'New':
                vals['reference'] = self.env['ir.sequence'].next_by_code('rn.document.idp.document') or 'New'
            if vals.get('name', 'New') == 'New':
                vals['name'] = vals.get('reference', 'New')
        records = super().create(vals_list)
        for record in records:
            if record.attachment_id and not record.attachment_id.res_id:
                record.attachment_id.write({
                    'res_model': record._name,
                    'res_id': record.id,
                })
        return records

    def action_process(self):
        for document in self:
            document.write({'state': 'extracting'})
            self.env['rn.document.idp.pipeline.service'].process_document(document)
        return True

    def action_approve(self):
        self.write({'state': 'approved'})

    def action_reject(self):
        self.write({'state': 'rejected'})

    def action_post_to_erp(self):
        self.ensure_one()
        if self.state not in ('review', 'approved', 'duplicate', 'classified'):
            raise UserError('Review or approve the document before posting to ERP.')
        result = self.env['rn.document.idp.posting.service'].post_document(self)
        if result.get('move_id'):
            self.write({
                'move_id': result['move_id'],
                'posted_model': 'account.move',
                'posted_res_id': result['move_id'],
                'state': 'posted',
            })
        return result.get('action')

    def action_open_posted_record(self):
        self.ensure_one()
        if self.move_id:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'account.move',
                'view_mode': 'form',
                'res_id': self.move_id.id,
            }
        if self.posted_model and self.posted_res_id:
            return {
                'type': 'ir.actions.act_window',
                'res_model': self.posted_model,
                'view_mode': 'form',
                'res_id': self.posted_res_id,
            }
        raise UserError('No ERP record linked yet.')

    def action_open_validations(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Validations',
            'res_model': 'rn.document.idp.validation',
            'view_mode': 'list,form',
            'domain': [('document_id', '=', self.id)],
        }
