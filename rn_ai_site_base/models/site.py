# -*- coding: utf-8 -*-
"""Generated website project."""

from odoo import api, fields, models


class RnAiSiteSite(models.Model):
    """AI-generated website project with pages and theme."""

    _name = 'rn.ai.site.site'
    _description = 'AI Website Project'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(copy=False, index=True, default='New')
    active = fields.Boolean(default=True)
    brief_id = fields.Many2one('rn.ai.site.brief', string='Source Brief', index=True)
    business_name = fields.Char(required=True)
    business_type = fields.Selection(
        selection=lambda self: self.env['rn.ai.site.brief']._fields['business_type'].selection,
    )
    location = fields.Char()
    domain = fields.Char(help='Custom domain when published')
    theme_id = fields.Many2one('rn.ai.site.theme', string='Theme Preset')
    primary_color = fields.Char(default='#2563eb')
    secondary_color = fields.Char(default='#1e293b')
    font_heading = fields.Char(default='Inter')
    font_body = fields.Char(default='Inter')
    page_ids = fields.One2many('rn.ai.site.page', 'site_id', string='Pages')
    page_count = fields.Integer(compute='_compute_page_count')
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('ready', 'Ready to Publish'),
            ('published', 'Published'),
            ('archived', 'Archived'),
        ],
        default='draft',
        tracking=True,
    )
    odoo_website_id = fields.Integer(
        string='Odoo Website ID',
        help='Set when published to Odoo Website (companion publisher module).',
    )
    enable_crm_sync = fields.Boolean(default=True, string='Sync Leads to CRM')
    enable_whatsapp = fields.Boolean(default=True)
    enable_contact_form = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    note = fields.Html()

    @api.depends('page_ids')
    def _compute_page_count(self):
        for site in self:
            site.page_count = len(site.page_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('code', 'New') == 'New':
                vals['code'] = self.env['ir.sequence'].next_by_code('rn.ai.site.site') or 'New'
        return super().create(vals_list)

    def action_mark_ready(self):
        self.write({'state': 'ready'})

    def action_publish(self):
        self.env['rn.ai.site.publisher.service'].publish_to_odoo_hooks(self)
        self.write({'state': 'published'})
        if self.brief_id:
            self.brief_id.write({'state': 'published'})

    def action_open_pages(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Pages',
            'res_model': 'rn.ai.site.page',
            'view_mode': 'list,form',
            'domain': [('site_id', '=', self.id)],
            'context': {'default_site_id': self.id},
        }
