# -*- coding: utf-8 -*-
"""Compare two periods for executive review."""

from odoo import fields, models


class RnBiComparePeriodWizard(models.TransientModel):
    """Compute side-by-side KPI comparison."""

    _name = 'rn.bi.compare.period.wizard'
    _description = 'BI Compare Period Wizard'

    period_a_from = fields.Date(required=True)
    period_a_to = fields.Date(required=True)
    period_b_from = fields.Date(required=True)
    period_b_to = fields.Date(required=True)
    result_html = fields.Html(readonly=True)

    def action_compare(self):
        self.ensure_one()
        Service = self.env['rn.bi.dashboard.service']
        a = Service.get_dashboard_data({
            'date_preset': 'custom',
            'date_from': self.period_a_from,
            'date_to': self.period_a_to,
        })
        b = Service.get_dashboard_data({
            'date_preset': 'custom',
            'date_from': self.period_b_from,
            'date_to': self.period_b_to,
        })
        self.result_html = (
            '<p><b>Period A revenue:</b> %s<br/>'
            '<b>Period B revenue:</b> %s</p>'
            % (a['cards'].get('total_revenue'), b['cards'].get('total_revenue'))
        )
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'rn.bi.compare.period.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
