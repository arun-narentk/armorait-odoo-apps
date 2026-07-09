# -*- coding: utf-8 -*-
"""Managed Odoo instances."""

from odoo import api, fields, models


class RnCloudInstance(models.Model):
    _name = 'rn.cloud.instance'
    _description = 'Cloud Instance'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(required=True, copy=False, default='New', tracking=True)
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    provider_id = fields.Many2one('rn.cloud.provider', required=True, ondelete='restrict')
    customer_name = fields.Char(required=True)
    odoo_version = fields.Selection([('18', 'Odoo 18'), ('19', 'Odoo 19')], default='19', required=True)
    edition = fields.Selection([('community', 'Community'), ('enterprise', 'Enterprise')], default='community', required=True)
    domain_name = fields.Char(required=True)
    status = fields.Selection([('draft', 'Draft'), ('deploying', 'Deploying'), ('running', 'Running'), ('maintenance', 'Maintenance'), ('error', 'Error')], default='draft', required=True, tracking=True)
    python_version = fields.Char(default='3.12')
    environment_ids = fields.One2many('rn.cloud.environment', 'instance_id')
    backup_count = fields.Integer(compute='_compute_related_counts')
    recommendation_count = fields.Integer(compute='_compute_related_counts')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('rn.cloud.instance') or 'New'
        return super().create(vals_list)

    def _compute_related_counts(self):
        backup_group = self.env['rn.cloud.backup']._read_group([('instance_id', 'in', self.ids)], ['instance_id'], ['__count'])
        backup_counts = {instance.id: count for instance, count in backup_group}
        rec_group = self.env['rn.cloud.recommendation']._read_group([('instance_id', 'in', self.ids)], ['instance_id'], ['__count'])
        rec_counts = {instance.id: count for instance, count in rec_group}
        for record in self:
            record.backup_count = backup_counts.get(record.id, 0)
            record.recommendation_count = rec_counts.get(record.id, 0)
