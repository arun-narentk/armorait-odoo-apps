# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AiBizPromotion(models.Model):
    """Configurable AI BIZ promotional landing content."""

    _name = 'ai.biz.promotion'
    _description = 'AI BIZ Promotion'
    _order = 'sequence, id'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(required=True, tracking=True)
    sequence = fields.Integer(default=10, index=True)
    active = fields.Boolean(default=True, tracking=True)
    banner_image = fields.Image(max_width=1920, max_height=1080)
    title = fields.Char(required=True, tracking=True)
    subtitle = fields.Char(tracking=True)
    description = fields.Html(sanitize_attributes=True)
    button_text = fields.Char(default='Explore AI BIZ', tracking=True)
    button_url = fields.Char(default='/contactus', tracking=True)
    footer_text = fields.Html(
        string='Bottom Section Text',
        sanitize_attributes=True,
        help='Centered copy shown above the CTA button.',
    )
    benefit_ids = fields.One2many(
        'ai.biz.benefit',
        'promotion_id',
        string='Benefits',
    )
    benefit_count = fields.Integer(compute='_compute_benefit_count')
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
        index=True,
    )

    @api.depends('benefit_ids')
    def _compute_benefit_count(self) -> None:
        for record in self:
            record.benefit_count = len(record.benefit_ids)

    def get_website_url(self) -> str:
        self.ensure_one()
        return '/ai-biz'

    def action_open_website(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': self.get_website_url(),
            'target': 'new',
        }
