# -*- coding: utf-8 -*-
"""Vendor bill duplicate invoice-number checks on account.move."""

from odoo import _, api, fields, models

from .constants import (
    CTX_SKIP_CHECK,
    PARAM_BLOCK,
    PARAM_CASE_INSENSITIVE,
    PARAM_ENABLE,
)


class AccountMove(models.Model):
    _inherit = 'account.move'

    rn_has_duplicate_vendor_ref = fields.Boolean(
        string='Duplicate Vendor Invoice Number',
        compute='_compute_rn_has_duplicate_vendor_ref',
        help='True when another vendor bill uses the same normalized invoice reference '
             'for this vendor and company.',
    )

    @api.depends('ref', 'partner_id', 'commercial_partner_id', 'company_id', 'move_type', 'state')
    def _compute_rn_has_duplicate_vendor_ref(self):
        for move in self:
            if move.move_type != 'in_invoice' or not move._rn_normalize_invoice_reference(move.ref):
                move.rn_has_duplicate_vendor_ref = False
                continue
            move.rn_has_duplicate_vendor_ref = bool(move._rn_find_duplicate_vendor_bills(limit=1))

    @api.model
    def _rn_is_duplicate_warning_enabled(self):
        return self.env['ir.config_parameter'].sudo().get_param(PARAM_ENABLE, 'True') == 'True'

    @api.model
    def _rn_is_block_duplicate_enabled(self):
        return self.env['ir.config_parameter'].sudo().get_param(PARAM_BLOCK, 'False') == 'True'

    @api.model
    def _rn_is_case_insensitive(self):
        return self.env['ir.config_parameter'].sudo().get_param(PARAM_CASE_INSENSITIVE, 'True') == 'True'

    @api.model
    def _rn_normalize_invoice_reference(self, reference, case_insensitive=None):
        """Trim whitespace; optionally lowercase for comparison.

        Does not strip hyphens or other meaningful characters.
        """
        if not reference:
            return ''
        normalized = reference.strip()
        if not normalized:
            return ''
        if case_insensitive is None:
            case_insensitive = self._rn_is_case_insensitive()
        if case_insensitive:
            normalized = normalized.casefold()
        return normalized

    def _rn_find_duplicate_vendor_bills(self, limit=False):
        """Return other vendor bills with the same normalized ref for vendor + company.

        Scope:
        - move_type = in_invoice only (vendor credit notes are excluded)
        - same company_id
        - same commercial_partner_id
        - states draft and posted
        - excludes empty refs and the current record
        """
        self.ensure_one()
        if self.move_type != 'in_invoice':
            return self.env['account.move']

        case_insensitive = self._rn_is_case_insensitive()
        normalized = self._rn_normalize_invoice_reference(
            self.ref, case_insensitive=case_insensitive
        )
        if not normalized or not self.commercial_partner_id or not self.company_id:
            return self.env['account.move']

        domain = [
            ('company_id', '=', self.company_id.id),
            ('commercial_partner_id', '=', self.commercial_partner_id.id),
            ('move_type', '=', 'in_invoice'),
            ('state', 'in', ('draft', 'posted')),
            ('ref', '!=', False),
            ('ref', '!=', ''),
        ]
        if isinstance(self.id, int):
            domain.append(('id', '!=', self.id))

        # Scoped to one vendor + company so the candidate set stays small.
        candidates = self.search(domain, order='state desc, invoice_date desc, id desc')
        duplicates = candidates.filtered(
            lambda move: self._rn_normalize_invoice_reference(
                move.ref, case_insensitive=case_insensitive
            ) == normalized
        )
        if limit:
            return duplicates[:limit]
        return duplicates

    def _rn_pick_duplicate_for_wizard(self, duplicates):
        """Prefer a posted duplicate for the warning dialog."""
        posted = duplicates.filtered(lambda move: move.state == 'posted')[:1]
        return posted or duplicates[:1]

    def _rn_open_duplicate_warning_wizard(self, duplicate, block_mode):
        self.ensure_one()
        wizard = self.env['rn.invoice.duplicate.warning.wizard'].create({
            'move_id': self.id,
            'duplicate_move_id': duplicate.id,
            'block_mode': block_mode,
        })
        return {
            'name': _('Duplicate Vendor Invoice Detected'),
            'type': 'ir.actions.act_window',
            'res_model': 'rn.invoice.duplicate.warning.wizard',
            'res_id': wizard.id,
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'dialog_size': 'medium',
            },
        }

    def _rn_check_duplicate_vendor_invoice(self):
        """Return a wizard action if posting must pause; otherwise False."""
        if self.env.context.get(CTX_SKIP_CHECK):
            return False
        if not self._rn_is_duplicate_warning_enabled():
            return False

        block_mode = self._rn_is_block_duplicate_enabled()
        for move in self.filtered(lambda m: m.move_type == 'in_invoice' and m.state == 'draft'):
            duplicates = move._rn_find_duplicate_vendor_bills()
            if not duplicates:
                continue
            duplicate = move._rn_pick_duplicate_for_wizard(duplicates)
            return move._rn_open_duplicate_warning_wizard(duplicate, block_mode)
        return False

    def action_post(self):
        wizard_action = self._rn_check_duplicate_vendor_invoice()
        if wizard_action:
            return wizard_action
        return super().action_post()
