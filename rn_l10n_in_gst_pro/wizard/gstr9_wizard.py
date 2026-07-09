# -*- coding: utf-8 -*-
"""Wizard to create GSTR-9 annual return shell."""

from odoo import fields, models


class RnGstGstr9Wizard(models.TransientModel):
    """Select annual period and create a GSTR-9 return shell."""

    _name = 'rn.gst.gstr9.wizard'
    _description = 'Generate GSTR-9'

    period_id = fields.Many2one('rn.gst.period', required=True, domain="[('period_type', '=', 'year')]")
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)

    def action_generate(self):
        self.ensure_one()
        gst_return = self.env['rn.gst.return'].create({
            'return_type': 'gstr9',
            'period_id': self.period_id.id,
            'company_id': self.company_id.id,
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'rn.gst.return',
            'res_id': gst_return.id,
            'view_mode': 'form',
        }
