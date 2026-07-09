# -*- coding: utf-8 -*-

from odoo import api, fields, models


class RnConstructionSiteDailyLog(models.Model):
    _name = 'rn.construction.site.daily.log'
    _description = 'Site Daily Log'
    _inherit = ['mail.thread']
    _order = 'log_date desc'

    name = fields.Char(required=True)
    site_id = fields.Many2one('rn.construction.site', required=True, index=True)
    log_date = fields.Date(required=True, default=fields.Date.context_today, index=True)
    weather = fields.Char()
    progress_note = fields.Html()
    labour_count = fields.Integer()
    material_received = fields.Text()
    incidents = fields.Text()
    attachment_ids = fields.Many2many('ir.attachment', string='Photos')
    ai_summary = fields.Text(string='AI Summary', readonly=True)
    company_id = fields.Many2one(related='site_id.company_id', store=True, index=True)

    def action_generate_ai_summary(self):
        for rec in self:
            rec.ai_summary = self.env['rn.construction.insight.service'].draft_daily_summary(rec.id)
