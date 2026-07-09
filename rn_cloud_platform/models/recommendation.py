# -*- coding: utf-8 -*-
"""AI ops recommendations for instances."""

from odoo import fields, models


class RnCloudRecommendation(models.Model):
    _name = 'rn.cloud.recommendation'
    _description = 'Cloud Recommendation'
    _order = 'severity desc, create_date desc'

    instance_id = fields.Many2one('rn.cloud.instance', required=True, ondelete='cascade')
    company_id = fields.Many2one(related='instance_id.company_id', store=True, readonly=True)
    category = fields.Selection([('performance', 'Performance'), ('backup', 'Backup'), ('security', 'Security'), ('upgrade', 'Upgrade'), ('storage', 'Storage')], required=True, default='performance')
    severity = fields.Selection([('info', 'Info'), ('warning', 'Warning'), ('high', 'High'), ('critical', 'Critical')], required=True, default='warning')
    title = fields.Char(required=True)
    recommendation = fields.Text(required=True)
    state = fields.Selection([('open', 'Open'), ('done', 'Done'), ('ignored', 'Ignored')], default='open', required=True)
