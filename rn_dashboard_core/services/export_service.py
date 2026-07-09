# -*- coding: utf-8 -*-
"""CSV export helpers for dashboard KPI snapshots."""

import base64
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnDashboardExportService(models.AbstractModel):
    """Export snapshot rows as CSV attachment."""

    _name = 'rn.dashboard.export.service'
    _description = 'Dashboard Export Service'

    def export_snapshots_csv(self, company_id=None, limit=500):
        company_id = company_id or self.env.company.id
        rows = self.env['rn.dashboard.kpi.snapshot'].search([
            ('company_id', '=', company_id),
        ], limit=limit)
        lines = ['kpi_key,snapshot_at,value,target']
        for row in rows:
            lines.append('%s,%s,%s,%s' % (
                row.kpi_key or '',
                fields.Datetime.to_string(row.snapshot_at) if row.snapshot_at else '',
                row.value,
                row.target or 0.0,
            ))
        content = chr(10).join(lines)
        attachment = self.env['ir.attachment'].create({
            'name': 'dashboard_kpi_snapshots.csv',
            'type': 'binary',
            'datas': base64.b64encode(content.encode('utf-8')),
            'mimetype': 'text/csv',
        })
        _logger.info('Exported %s KPI snapshots', len(rows))
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % attachment.id,
            'target': 'self',
        }
