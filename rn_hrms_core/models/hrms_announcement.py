# -*- coding: utf-8 -*-
"""Company announcements for ESS portals."""

from odoo import fields, models


class RnHrmsAnnouncement(models.Model):
    """HR / company announcement visible to employees."""

    _name = 'rn.hrms.announcement'
    _description = 'HRMS Announcement'
    _inherit = ['mail.thread']
    _order = 'date_start desc, id desc'

    name = fields.Char(required=True, tracking=True)
    body = fields.Html(required=True)
    date_start = fields.Date(required=True, default=fields.Date.context_today)
    date_end = fields.Date()
    audience = fields.Selection(
        selection=[
            ('all', 'All Employees'),
            ('department', 'Department'),
            ('branch', 'Branch'),
        ],
        default='all',
        required=True,
    )
    department_id = fields.Many2one('hr.department')
    branch_id = fields.Many2one('rn.hrms.branch')
    state = fields.Selection(
        selection=[('draft', 'Draft'), ('published', 'Published'), ('done', 'Done')],
        default='draft',
        tracking=True,
    )
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

    def action_publish(self):
        self.write({'state': 'published'})
        self.env['rn.hrms.notification.service'].notify_announcement(self)
        return True
