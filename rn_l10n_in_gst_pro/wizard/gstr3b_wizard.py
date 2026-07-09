# -*- coding: utf-8 -*-
"""Wizard to create or refresh GSTR-3B."""

from odoo import fields, models


class RnGstGstr3bWizard(models.TransientModel):
    """Select period and create a GSTR-3B return shell."""

    _name = 'rn.gst.gstr3b.wizard'
    _description = 'Generate GSTR-3B'

    period_id = fields.Many2one('rn.gst.period', required=True)
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    auto_compute = fields.Boolean(default=True)

    def action_generate(self):
        self.ensure_one()
        gst_return = self.env['rn.gst.return'].create({
            'return_type': 'gstr3b',
            'period_id': self.period_id.id,
            'company_id': self.company_id.id,
        })
        if self.auto_compute:
            gst_return.action_compute()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'rn.gst.return',
            'res_id': gst_return.id,
            'view_mode': 'form',
        }
