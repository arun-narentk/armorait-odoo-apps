# -*- coding: utf-8 -*-
"""Confirmation wizard shown when a duplicate vendor invoice number is detected."""

from markupsafe import escape

from odoo import api, fields, models
from odoo.tools.misc import format_amount

from odoo.addons.rn_invoice_duplicate_warning.models.constants import CTX_SKIP_CHECK


class RnInvoiceDuplicateWarningWizard(models.TransientModel):
    _name = 'rn.invoice.duplicate.warning.wizard'
    _description = 'Duplicate Vendor Invoice Warning'

    move_id = fields.Many2one(
        'account.move',
        string='Vendor Bill',
        required=True,
        readonly=True,
        ondelete='cascade',
    )
    duplicate_move_id = fields.Many2one(
        'account.move',
        string='Existing Bill',
        required=True,
        readonly=True,
        ondelete='cascade',
    )
    block_mode = fields.Boolean(readonly=True)

    partner_id = fields.Many2one(
        related='move_id.partner_id',
        string='Vendor',
        readonly=True,
    )
    company_id = fields.Many2one(
        related='move_id.company_id',
        readonly=True,
    )
    invoice_reference = fields.Char(
        string='Invoice Number',
        related='move_id.ref',
        readonly=True,
    )
    duplicate_name = fields.Char(
        related='duplicate_move_id.name',
        string='Existing Bill Number',
        readonly=True,
    )
    duplicate_state = fields.Selection(
        related='duplicate_move_id.state',
        string='Status',
        readonly=True,
    )
    duplicate_date = fields.Date(
        related='duplicate_move_id.invoice_date',
        string='Date',
        readonly=True,
    )
    duplicate_amount = fields.Monetary(
        related='duplicate_move_id.amount_total',
        string='Amount',
        readonly=True,
        currency_field='currency_id',
    )
    currency_id = fields.Many2one(
        related='duplicate_move_id.currency_id',
        readonly=True,
    )
    warning_message = fields.Html(compute='_compute_warning_message')

    @api.depends(
        'partner_id', 'invoice_reference', 'duplicate_move_id',
        'duplicate_name', 'duplicate_state', 'duplicate_date',
        'duplicate_amount', 'company_id', 'block_mode', 'currency_id',
    )
    def _compute_warning_message(self):
        for wizard in self:
            amount_label = format_amount(
                wizard.env, wizard.duplicate_amount or 0.0, wizard.currency_id
            ) if wizard.currency_id else wizard.duplicate_amount
            state_label = dict(wizard.duplicate_move_id._fields['state'].selection).get(
                wizard.duplicate_state, wizard.duplicate_state or '-'
            )
            date_label = fields.Date.to_string(wizard.duplicate_date) if wizard.duplicate_date else '-'
            if wizard.block_mode:
                footer = (
                    '<p><strong>Posting is blocked</strong> until this invoice number '
                    'is unique for the vendor.</p>'
                )
            else:
                footer = (
                    '<p>You can cancel and fix the reference, or continue posting anyway.</p>'
                )
            wizard.warning_message = (
                '<div class="o_rn_dup_invoice_warning">'
                '<p>A vendor bill with the same invoice number already exists.</p>'
                '<ul>'
                f'<li><strong>Vendor:</strong> {escape(wizard.partner_id.display_name or "-")}</li>'
                f'<li><strong>Invoice Number:</strong> {escape(wizard.invoice_reference or "-")}</li>'
                f'<li><strong>Existing Bill:</strong> {escape(wizard.duplicate_name or "-")}</li>'
                f'<li><strong>Date:</strong> {escape(date_label)}</li>'
                f'<li><strong>Amount:</strong> {escape(str(amount_label))}</li>'
                f'<li><strong>Status:</strong> {escape(str(state_label))}</li>'
                f'<li><strong>Company:</strong> {escape(wizard.company_id.display_name or "-")}</li>'
                '</ul>'
                f'{footer}'
                '</div>'
            )

    def action_open_duplicate(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': self.duplicate_move_id.display_name,
            'res_model': 'account.move',
            'res_id': self.duplicate_move_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_continue_anyway(self):
        """Resume posting after an explicit user confirmation (warning mode only)."""
        self.ensure_one()
        if self.block_mode:
            return {'type': 'ir.actions.act_window_close'}
        return self.move_id.with_context(**{CTX_SKIP_CHECK: True}).action_post()

    def action_close(self):
        return {'type': 'ir.actions.act_window_close'}
