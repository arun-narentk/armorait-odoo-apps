# -*- coding: utf-8 -*-
"""Business brief for AI site generation."""

from odoo import api, fields, models

BUSINESS_TYPES = [
    ('bakery', 'Bakery'),
    ('salon', 'Salon / Spa'),
    ('restaurant', 'Restaurant'),
    ('tuition', 'Tuition Centre'),
    ('gym', 'Gym / Fitness'),
    ('boutique', 'Boutique'),
    ('car_wash', 'Car Wash'),
    ('hospital', 'Hospital'),
    ('clinic', 'Clinic'),
    ('travel', 'Travel Agency'),
    ('accountant', 'Chartered Accountant'),
    ('construction', 'Construction Company'),
    ('hotel', 'Hotel'),
    ('temple', 'Temple / Trust'),
    ('textile', 'Textile / Manufacturing'),
    ('real_estate', 'Real Estate'),
    ('other', 'Other Business'),
]

TONE_OPTIONS = [
    ('professional', 'Professional'),
    ('friendly', 'Friendly'),
    ('luxury', 'Luxury'),
    ('playful', 'Playful'),
    ('traditional', 'Traditional'),
]


class RnAiSiteBrief(models.Model):
    """Plain-language business description used to generate a website."""

    _name = 'rn.ai.site.brief'
    _description = 'AI Site Business Brief'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(required=True, tracking=True)
    reference = fields.Char(copy=False, index=True, default='New', tracking=True)
    business_type = fields.Selection(selection=BUSINESS_TYPES, default='other', required=True, tracking=True)
    business_name = fields.Char(required=True, tracking=True)
    location = fields.Char(tracking=True, help='City or area, e.g. Coimbatore')
    description = fields.Text(
        required=True,
        help='Describe your business in plain language. Example: We specialize in birthday and wedding cakes.',
    )
    services = fields.Text(help='Comma-separated services or products')
    target_audience = fields.Char()
    tone = fields.Selection(selection=TONE_OPTIONS, default='friendly', required=True)
    keywords = fields.Char(help='Comma-separated SEO keywords (auto-filled on generate)')
    phone = fields.Char()
    email = fields.Char()
    whatsapp = fields.Char()
    website_url = fields.Char(string='Existing Website')
    language = fields.Selection(
        selection=[
            ('en', 'English'),
            ('ta', 'Tamil'),
            ('hi', 'Hindi'),
            ('te', 'Telugu'),
            ('kn', 'Kannada'),
            ('ml', 'Malayalam'),
        ],
        default='en',
        required=True,
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('analyzed', 'Analyzed'),
            ('generated', 'Site Generated'),
            ('published', 'Published'),
        ],
        default='draft',
        tracking=True,
    )
    site_id = fields.Many2one('rn.ai.site.site', string='Generated Site', copy=False)
    partner_id = fields.Many2one('res.partner', string='Business Contact')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    note = fields.Html()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('reference', 'New') == 'New':
                vals['reference'] = self.env['ir.sequence'].next_by_code('rn.ai.site.brief') or 'New'
        return super().create(vals_list)

    def action_analyze(self):
        for brief in self:
            data = self.env['rn.ai.site.brief.service'].analyze_brief(brief)
            brief.write({
                'keywords': ', '.join(data.get('keywords', [])),
                'target_audience': brief.target_audience or data.get('target_audience', ''),
                'state': 'analyzed',
            })

    def action_generate_site(self):
        for brief in self:
            if brief.state == 'draft':
                brief.action_analyze()
            site = self.env['rn.ai.site.generation.service'].generate_from_brief(brief)
            brief.write({'site_id': site.id, 'state': 'generated'})
        return self._open_site_action()

    def action_open_site(self):
        self.ensure_one()
        if not self.site_id:
            return False
        return {
            'type': 'ir.actions.act_window',
            'name': 'Generated Site',
            'res_model': 'rn.ai.site.site',
            'view_mode': 'form',
            'res_id': self.site_id.id,
        }

    def _open_site_action(self):
        self.ensure_one()
        return self.action_open_site()
