# -*- coding: utf-8 -*-
"""AI-style risk hints for approvers."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnApprovalRiskService(models.AbstractModel):
    """Build risk summary HTML for approval requests."""

    _name = 'rn.approval.risk.service'
    _description = 'Approval Risk Service'

    def build_risk_summary(self, request):
        hints = []
        hints.extend(self._amount_vs_history(request))
        hints.extend(self._duplicate_warnings(request))
        if not hints:
            return '<p>No risk flags detected. Ready for review.</p>'
        items = ''.join(f'<li>{hint}</li>' for hint in hints)
        return f'<p><strong>Review hints:</strong></p><ul>{items}</ul>'

    def _amount_vs_history(self, request):
        hints = []
        if request.res_model != 'purchase.order' or not request.amount:
            return hints
        po = self.env['purchase.order'].browse(request.res_id)
        if not po.exists() or not po.partner_id:
            return hints
        prior = self.env['purchase.order'].search([
            ('partner_id', '=', po.partner_id.id),
            ('company_id', '=', request.company_id.id),
            ('state', 'in', ('purchase', 'done')),
            ('id', '!=', po.id),
        ], order='date_order desc', limit=5)
        if not prior:
            hints.append('New vendor: no prior purchase orders on record.')
            return hints
        avg = sum(prior.mapped('amount_total')) / len(prior)
        if avg and request.amount > avg * 1.2:
            pct = round((request.amount - avg) / avg * 100, 1)
            hints.append(f'Amount is {pct}% above recent average for this vendor.')
        return hints

    def _duplicate_warnings(self, request):
        hints = []
        if request.res_model == 'purchase.order' and request.res_id:
            po = self.env['purchase.order'].browse(request.res_id)
            if po.exists():
                dup = self.env['purchase.order'].search_count([
                    ('partner_id', '=', po.partner_id.id),
                    ('amount_total', '=', po.amount_total),
                    ('company_id', '=', request.company_id.id),
                    ('id', '!=', po.id),
                    ('state', 'not in', ('cancel',)),
                ])
                if dup:
                    hints.append('Similar purchase order amount exists for this vendor.')
        if request.res_model == 'account.move' and request.res_id:
            move = self.env['account.move'].browse(request.res_id)
            if move.exists() and move.ref:
                dup = self.env['account.move'].search_count([
                    ('partner_id', '=', move.partner_id.id),
                    ('ref', '=ilike', move.ref),
                    ('company_id', '=', request.company_id.id),
                    ('id', '!=', move.id),
                    ('state', '!=', 'cancel'),
                ])
                if dup:
                    hints.append('Vendor bill with same reference may already exist.')
        return hints
