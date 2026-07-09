# -*- coding: utf-8 -*-
"""Generate AI ops recommendations from monitoring and backup data."""

from odoo import models


class RnCloudOpsService(models.AbstractModel):
    _name = 'rn.cloud.ops.service'
    _description = 'Cloud Ops Service'

    def analyze_instance(self, instance):
        monitoring = self.env['rn.cloud.monitoring'].search([('instance_id', '=', instance.id)], order='snapshot_time desc', limit=1)
        backups = self.env['rn.cloud.backup'].search([('instance_id', '=', instance.id)], order='backup_date desc', limit=1)
        created = self.env['rn.cloud.recommendation']
        if monitoring and monitoring.cpu_percent >= 85:
            created |= self.env['rn.cloud.recommendation'].create({
                'instance_id': instance.id,
                'category': 'performance',
                'severity': 'high',
                'title': 'High CPU usage detected',
                'recommendation': 'Investigate long-running workers or custom reports before scaling compute.',
            })
        if monitoring and monitoring.storage_percent >= 80:
            created |= self.env['rn.cloud.recommendation'].create({
                'instance_id': instance.id,
                'category': 'storage',
                'severity': 'warning',
                'title': 'Storage usage is trending high',
                'recommendation': 'Review attachment growth, backups, and archival strategy before the next growth cycle.',
            })
        if backups and backups.restore_state != 'verified':
            created |= self.env['rn.cloud.recommendation'].create({
                'instance_id': instance.id,
                'category': 'backup',
                'severity': 'high',
                'title': 'Backup restore verification is incomplete',
                'recommendation': 'Run a restore drill for the latest backup to confirm database and filestore readiness.',
            })
        if not created:
            created |= self.env['rn.cloud.recommendation'].create({
                'instance_id': instance.id,
                'category': 'performance',
                'severity': 'info',
                'title': 'Environment is healthy',
                'recommendation': 'Keep daily backups, monitoring, and scheduled upgrade readiness reviews enabled.',
            })
        return created
