# -*- coding: utf-8 -*-
"""Background jobs for forecast, analysis, and alerts."""

import logging
from datetime import timedelta

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnInvSchedulerService(models.AbstractModel):
    """Cron entry points for inventory forecasting."""

    _name = 'rn.inv.scheduler.service'
    _description = 'Inventory Forecast Scheduler Service'

    def cron_auto_forecast(self):
        """Create and generate a monthly rolling forecast per company."""
        today = fields.Date.context_today(self)
        for company in self.env['res.company'].search([]):
            settings = self.env['rn.inv.forecast.settings'].search(
                [('company_id', '=', company.id)], limit=1
            )
            if settings and not settings.enable_auto_forecast:
                continue
            history_days = settings.history_days if settings else 90
            horizon = settings.default_horizon_days if settings else 30
            run = self.env['rn.inv.forecast.run'].create({
                'name': 'Auto Forecast %s' % today,
                'period_type': 'monthly',
                'date_from': today - timedelta(days=history_days - 1),
                'date_to': today,
                'horizon_days': horizon,
                'company_id': company.id,
                'state': 'draft',
            })
            run.action_generate()
        _logger.info('Auto forecast cron finished')
        return True

    def cron_run_analysis(self):
        today = fields.Date.context_today(self)
        for company in self.env['res.company'].search([]):
            date_from, date_to = self.env['rn.inv.demand.service'].get_history_window(company.id)
            self.env['rn.inv.abc.service'].run_analysis(date_from, date_to, company_id=company.id)
            self.env['rn.inv.xyz.service'].run_analysis(date_from, date_to, company_id=company.id)
            self.env['rn.inv.fsn.service'].run_analysis(date_from, date_to, company_id=company.id)
            self.env['rn.inv.safety.stock.service'].compute_for_company(company.id)
            self.env['rn.inv.reorder.service'].generate_suggestions(company.id)
        _logger.info('Analysis cron finished for %s', today)
        return True

    def cron_scan_alerts(self):
        for company in self.env['res.company'].search([]):
            self.env['rn.inv.alert.service'].scan_alerts(company.id)
        return True
