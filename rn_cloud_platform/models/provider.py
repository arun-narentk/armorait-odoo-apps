# -*- coding: utf-8 -*-
"""Cloud provider profiles."""

from odoo import fields, models


class RnCloudProvider(models.Model):
    _name = 'rn.cloud.provider'
    _description = 'Cloud Provider'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(required=True, tracking=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    provider_type = fields.Selection(
        [('aws', 'AWS'), ('azure', 'Azure'), ('gcp', 'Google Cloud'), ('digitalocean', 'DigitalOcean'), ('hetzner', 'Hetzner'), ('ovh', 'OVH')],
        required=True, default='aws', tracking=True,
    )
    region = fields.Char(required=True, default='ap-south-1')
    status = fields.Selection([('draft', 'Draft'), ('connected', 'Connected'), ('error', 'Error')], default='draft')
    instance_count = fields.Integer(compute='_compute_instance_count')

    def _compute_instance_count(self):
        grouped = self.env['rn.cloud.instance']._read_group([('provider_id', 'in', self.ids)], ['provider_id'], ['__count'])
        counts = {provider.id: count for provider, count in grouped}
        for record in self:
            record.instance_count = counts.get(record.id, 0)
