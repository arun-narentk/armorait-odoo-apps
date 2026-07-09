# -*- coding: utf-8 -*-
"""Backups and restore readiness metadata."""

from odoo import fields, models


class RnCloudBackup(models.Model):
    _name = 'rn.cloud.backup'
    _description = 'Cloud Backup'
    _order = 'backup_date desc'

    instance_id = fields.Many2one('rn.cloud.instance', required=True, ondelete='cascade')
    company_id = fields.Many2one(related='instance_id.company_id', store=True, readonly=True)
    backup_date = fields.Datetime(required=True, default=fields.Datetime.now)
    backup_type = fields.Selection([('full', 'Full'), ('database', 'Database'), ('filestore', 'Filestore'), ('config', 'Configuration')], default='full', required=True)
    size_mb = fields.Float()
    storage_location = fields.Char()
    restore_state = fields.Selection([('unknown', 'Unknown'), ('verified', 'Verified'), ('failed', 'Failed')], default='unknown', required=True)
