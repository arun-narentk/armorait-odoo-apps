# -*- coding: utf-8 -*-
"""GST return headers (GSTR-1 / 3B / 9 and related)."""

from odoo import api, fields, models


class RnGstReturn(models.Model):
    """One GST return document for a company and period."""

    _name = 'rn.gst.return'
    _description = 'GST Return'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_end desc, id desc'

    name = fields.Char(required=True, copy=False, tracking=True)
    return_type = fields.Selection(
        selection=[
            ('gstr1', 'GSTR-1'),
            ('gstr3b', 'GSTR-3B'),
            ('gstr9', 'GSTR-9'),
            ('hsn', 'HSN Summary'),
            ('document', 'Document Summary'),
            ('tax', 'Tax Summary'),
        ],
        required=True,
        tracking=True,
        index=True,
    )
    period_id = fields.Many2one('rn.gst.period', string='Period', required=True, tracking=True)
    financial_year = fields.Char(related='period_id.financial_year', store=True)
    date_start = fields.Date(related='period_id.date_start', store=True)
    date_end = fields.Date(related='period_id.date_end', store=True)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        tracking=True,
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('computed', 'Computed'),
            ('validated', 'Validated'),
            ('exported', 'Exported'),
            ('locked', 'Locked'),
            ('filed', 'Filed'),
            ('cancelled', 'Cancelled'),
        ],
        default='draft',
        tracking=True,
        index=True,
    )
    invoice_line_ids = fields.One2many('rn.gst.invoice.line', 'return_id', string='Invoice Lines')
    summary_ids = fields.One2many('rn.gst.summary', 'return_id', string='Summaries')
    hsn_ids = fields.One2many('rn.gst.hsn.line', 'return_id', string='HSN Lines')
    document_ids = fields.One2many('rn.gst.document.summary', 'return_id', string='Documents')
    validation_ids = fields.One2many('rn.gst.validation', 'return_id', string='Validations')
    export_ids = fields.One2many('rn.gst.export', 'return_id', string='Exports')
    total_taxable = fields.Monetary(currency_field='currency_id', tracking=True)
    total_cgst = fields.Monetary(currency_field='currency_id')
    total_sgst = fields.Monetary(currency_field='currency_id')
    total_igst = fields.Monetary(currency_field='currency_id')
    total_cess = fields.Monetary(currency_field='currency_id')
    total_tax = fields.Monetary(currency_field='currency_id', tracking=True)
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id,
    )
    error_count = fields.Integer(compute='_compute_error_count')
    lock_date = fields.Datetime()
    notes = fields.Text()

    @api.depends('validation_ids', 'validation_ids.severity')
    def _compute_error_count(self):
        for rec in self:
            rec.error_count = len(rec.validation_ids.filtered(lambda v: v.severity in ('error', 'critical')))

    @api.model_create_multi
    def create(self, vals_list):
        """Assign sequence names for new returns."""
        seq = self.env['ir.sequence']
        for vals in vals_list:
            if not vals.get('name'):
                vals['name'] = seq.next_by_code('rn.gst.return') or 'New'
        return super().create(vals_list)

    def action_compute(self):
        """Compute return totals via calculation service (Phase 4+)."""
        self.env['rn.gst.calculation.service'].compute_returns(self)
        return True

    def action_validate(self):
        """Run GST validations for this return."""
        self.env['rn.gst.validation.service'].validate_returns(self)
        return True

    def action_lock(self):
        """Lock return against further edits."""
        self.write({'state': 'locked', 'lock_date': fields.Datetime.now()})
        return True
