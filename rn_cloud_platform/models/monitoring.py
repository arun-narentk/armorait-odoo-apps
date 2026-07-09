# -*- coding: utf-8 -*-
"""Operational monitoring snapshots."""

from odoo import fields, models


class RnCloudMonitoring(models.Model):
    _name = 'rn.cloud.monitoring'
    _description = 'Cloud Monitoring Snapshot'
    _order = 'snapshot_time desc'

    instance_id = fields.Many2one('rn.cloud.instance', required=True, ondelete='cascade')
    company_id = fields.Many2one(related='instance_id.company_id', store=True, readonly=True)
    snapshot_time = fields.Datetime(required=True, default=fields.Datetime.now)
    cpu_percent = fields.Float()
    ram_percent = fields.Float()
    storage_percent = fields.Float()
    response_ms = fields.Float()
    active_users = fields.Integer()
    worker_utilization = fields.Float()
