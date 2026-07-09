# -*- coding: utf-8 -*-
"""Lead merge audit log."""

from odoo import fields, models


class RnCrmMergeLog(models.Model):
    """Records merge operations for compliance and rollback support."""

    _name = 'rn.crm.merge.log'
    _description = 'CRM Lead Merge Log'
    _order = 'create_date desc'

    name = fields.Char(required=True)
    master_lead_id = fields.Many2one('crm.lead', string='Master Lead', required=True, ondelete='set null')
    merged_lead_ids = fields.Char(help='Comma-separated archived/merged lead IDs.')
    preserve_chatter = fields.Boolean(default=True)
    preserve_activities = fields.Boolean(default=True)
    preserve_attachments = fields.Boolean(default=True)
    notes = fields.Text()
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
