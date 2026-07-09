# -*- coding: utf-8 -*-

from odoo import fields, models


class RnSchoolNotice(models.Model):
    _name = 'rn.school.notice'
    _description = 'School Notice'
    _inherit = ['mail.thread']
    _order = 'publish_date desc'

    name = fields.Char(required=True)
    body = fields.Html(required=True)
    target = fields.Selection(
        [('all', 'All Parents'), ('class', 'Specific Class'), ('staff', 'Staff Only')],
        default='all',
    )
    class_id = fields.Many2one('rn.school.class')
    publish_date = fields.Datetime(default=fields.Datetime.now)
    state = fields.Selection([('draft', 'Draft'), ('published', 'Published')], default='draft')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

    def action_publish(self):
        self.write({'state': 'published'})
