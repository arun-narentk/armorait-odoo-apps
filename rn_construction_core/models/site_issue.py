# -*- coding: utf-8 -*-

from odoo import fields, models


class RnConstructionSiteIssue(models.Model):
    _name = 'rn.construction.site.issue'
    _description = 'Site Issue'
    _order = 'create_date desc'

    name = fields.Char(required=True)
    site_id = fields.Many2one('rn.construction.site', required=True, index=True)
    issue_type = fields.Selection(
        [
            ('safety', 'Safety'),
            ('quality', 'Quality'),
            ('delay', 'Delay'),
            ('material', 'Material'),
            ('equipment', 'Equipment'),
            ('other', 'Other'),
        ],
        default='other',
    )
    state = fields.Selection(
        [('open', 'Open'), ('in_progress', 'In Progress'), ('resolved', 'Resolved')],
        default='open',
    )
    description = fields.Text()
    company_id = fields.Many2one(related='site_id.company_id', store=True, index=True)
