# -*- coding: utf-8 -*-
"""Production and staging environments."""

from odoo import fields, models


class RnCloudEnvironment(models.Model):
    _name = 'rn.cloud.environment'
    _description = 'Cloud Environment'
    _order = 'sequence, id'

    sequence = fields.Integer(default=10)
    instance_id = fields.Many2one('rn.cloud.instance', required=True, ondelete='cascade')
    company_id = fields.Many2one(related='instance_id.company_id', store=True, readonly=True)
    environment_type = fields.Selection([('production', 'Production'), ('staging', 'Staging'), ('testing', 'Testing')], default='production', required=True)
    url = fields.Char(required=True)
    status = fields.Selection([('ready', 'Ready'), ('syncing', 'Syncing'), ('paused', 'Paused')], default='ready', required=True)
    database_name = fields.Char(required=True)
