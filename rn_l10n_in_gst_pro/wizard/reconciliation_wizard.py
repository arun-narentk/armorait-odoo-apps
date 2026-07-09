# -*- coding: utf-8 -*-
"""Wizard to start a GST reconciliation batch."""

from odoo import fields, models


class RnGstReconciliationWizard(models.TransientModel):
    """Create a reconciliation header and run the service."""

    _name = 'rn.gst.reconciliation.wizard'
    _description = 'GST Reconciliation Wizard'

    period_id = fields.Many2one('rn.gst.period', required=True)
    reconciliation_type = fields.Selection(
        selection=[
            ('purchase_itc', 'Purchase vs Input Tax'),
            ('sales_output', 'Sales vs Output Tax'),
            ('duplicate', 'Duplicate Detection'),
            ('missing_gstin', 'Missing GSTIN'),
            ('missing_hsn', 'Missing HSN'),
            ('tax_diff', 'Tax Difference'),
        ],
        required=True,
        default='purchase_itc',
    )
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)

    def action_run(self):
        self.ensure_one()
        rec = self.env['rn.gst.reconciliation'].create({
            'name': 'Reconciliation %s' % self.period_id.display_name,
            'period_id': self.period_id.id,
            'reconciliation_type': self.reconciliation_type,
            'company_id': self.company_id.id,
        })
        self.env['rn.gst.reconciliation.service'].run_reconciliation(rec)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'rn.gst.reconciliation',
            'res_id': rec.id,
            'view_mode': 'form',
        }
