# -*- coding: utf-8 -*-
"""Dashboard KPI aggregation."""

from odoo import models


class RnGstDashboardService(models.AbstractModel):
    """Compute KPI cards and chart series for the OWL dashboard."""

    _name = 'rn.gst.dashboard.service'
    _description = 'GST Dashboard Service'

    def get_kpis(self, company_id=None):
        """Return Phase 1 KPI dict from return headers."""
        company_id = company_id or self.env.company.id
        Return = self.env['rn.gst.return']
        domain = [('company_id', '=', company_id)]
        returns = Return.search(domain)
        return {
            'return_count': len(returns),
            'pending_returns': Return.search_count(domain + [('state', 'in', ('draft', 'computed'))]),
            'validated_returns': Return.search_count(domain + [('state', '=', 'validated')]),
            'output_gst': sum(returns.mapped('total_tax')),
            'mismatch_count': self.env['rn.gst.validation'].search_count([
                ('company_id', '=', company_id),
                ('severity', 'in', ('error', 'critical')),
                ('state', '=', 'open'),
            ]),
        }
