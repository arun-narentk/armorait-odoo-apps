# -*- coding: utf-8 -*-
"""Background jobs for snapshots and cache refresh."""

import logging
from datetime import timedelta

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnBiSchedulerService(models.AbstractModel):
    """Create daily snapshots and warm dashboard cache."""

    _name = 'rn.bi.scheduler.service'
    _description = 'BI Scheduler Service'

    def cron_create_snapshot(self):
        """Persist a month-to-date snapshot per company."""
        Service = self.env['rn.bi.dashboard.service']
        Snapshot = self.env['rn.bi.sales.snapshot']
        today = fields.Date.context_today(self)
        for company in self.env['res.company'].search([]):
            data = Service.with_company(company).get_dashboard_data({
                'company_id': company.id,
                'date_preset': 'this_month',
            })
            cards = data.get('cards') or {}
            Snapshot.create({
                'name': 'MTD Snapshot %s' % today,
                'snapshot_date': today,
                'period_key': 'this_month',
                'revenue': cards.get('total_revenue', 0.0),
                'orders': cards.get('orders', 0),
                'quotations': cards.get('quotation_count', 0),
                'quotation_value': cards.get('quotation_value', 0.0),
                'customers': cards.get('customers', 0),
                'aov': cards.get('aov', 0.0),
                'won_opportunities': cards.get('won_opportunities', 0),
                'lost_opportunities': cards.get('lost_opportunities', 0),
                'company_id': company.id,
            })
        _logger.info('BI sales snapshots created')
        return True

    def cron_clear_cache(self):
        self.env['rn.bi.cache.service'].clear('bi_sales:')
        return True
