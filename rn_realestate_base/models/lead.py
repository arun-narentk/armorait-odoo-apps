# -*- coding: utf-8 -*-
"""Real estate lead management."""

from odoo import api, fields, models

LEAD_SOURCES = [
    ('website', 'Website'),
    ('facebook', 'Facebook Ads'),
    ('google', 'Google Ads'),
    ('whatsapp', 'WhatsApp'),
    ('phone', 'Phone Call'),
    ('walkin', 'Walk-in'),
    ('portal', 'Property Portal'),
    ('referral', 'Referral'),
    ('broker', 'Broker / Channel Partner'),
    ('other', 'Other'),
]

LEAD_STAGES = [
    ('new', 'New'),
    ('contacted', 'Contacted'),
    ('qualified', 'Qualified'),
    ('site_visit', 'Site Visit'),
    ('negotiation', 'Negotiation'),
    ('booked', 'Booked'),
    ('lost', 'Lost'),
]

PROPERTY_TYPES = [
    ('apartment', 'Apartment'),
    ('villa', 'Villa'),
    ('plot', 'Plot'),
    ('commercial', 'Commercial'),
]


class RnRealestateLead(models.Model):
    """Sales lead with budget, location preference, and stage."""

    _name = 'rn.realestate.lead'
    _description = 'Real Estate Lead'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(required=True, tracking=True)
    reference = fields.Char(copy=False, index=True, default='New', tracking=True)
    developer_id = fields.Many2one(
        'rn.realestate.developer',
        required=True,
        ondelete='restrict',
        index=True,
        tracking=True,
    )
    partner_id = fields.Many2one('res.partner', string='Contact', tracking=True)
    phone = fields.Char(tracking=True)
    email = fields.Char()
    lead_source = fields.Selection(
        selection=LEAD_SOURCES,
        default='website',
        required=True,
        tracking=True,
    )
    stage = fields.Selection(
        selection=LEAD_STAGES,
        default='new',
        required=True,
        tracking=True,
        index=True,
    )
    budget_min = fields.Monetary(string='Budget From', currency_field='currency_id')
    budget_max = fields.Monetary(string='Budget To', currency_field='currency_id')
    preferred_location = fields.Char()
    property_type = fields.Selection(selection=PROPERTY_TYPES, default='apartment')
    project_id = fields.Many2one('rn.realestate.project', string='Interested Project', index=True)
    unit_id = fields.Many2one(
        'rn.realestate.unit',
        string='Interested Unit',
        domain="[('project_id', '=', project_id)]",
    )
    user_id = fields.Many2one('res.users', string='Sales Executive', default=lambda self: self.env.user, tracking=True)
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id,
    )
    company_id = fields.Many2one(
        related='developer_id.company_id',
        store=True,
        index=True,
    )
    note = fields.Html()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('reference', 'New') == 'New':
                vals['reference'] = self.env['ir.sequence'].next_by_code('rn.realestate.lead') or 'New'
        return super().create(vals_list)

    @api.onchange('project_id')
    def _onchange_project_id(self):
        if self.unit_id and self.unit_id.project_id != self.project_id:
            self.unit_id = False

    def action_contact(self):
        self.write({'stage': 'contacted'})

    def action_qualify(self):
        self.write({'stage': 'qualified'})

    def action_site_visit(self):
        self.write({'stage': 'site_visit'})

    def action_negotiate(self):
        self.write({'stage': 'negotiation'})

    def action_book(self):
        self.write({'stage': 'booked'})

    def action_lost(self):
        self.write({'stage': 'lost'})

    @api.model
    def _cron_lead_followup_reminder(self):
        """Remind sales executives about open leads without recent activity."""
        leads = self.search([
            ('stage', 'not in', ('booked', 'lost')),
        ], limit=50)
        for lead in leads:
            lead.activity_schedule(
                'mail.mail_activity_data_call',
                summary='Follow up on real estate lead',
                user_id=lead.user_id.id or self.env.user.id,
            )
