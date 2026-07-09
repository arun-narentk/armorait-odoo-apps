# -*- coding: utf-8 -*-
"""Wizard to create or refresh GSTR-1."""

from odoo import fields, models


class RnGstGstr1Wizard(models.TransientModel):
    """Select period and create a GSTR-1 return shell."""

    _name = 'rn.gst.gstr1.wizard'
    _description = 'Generate GSTR-1'

    period_id = fields.Many2one('rn.gst.period', required=True)
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    auto_compute = fields.Boolean(default=True)

    def action_generate(self):
        self.ensure_one()
        gst_return = self.env['rn.gst.return'].create({
            'return_type': 'gstr1',
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
