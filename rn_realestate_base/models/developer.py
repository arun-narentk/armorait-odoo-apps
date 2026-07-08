# -*- coding: utf-8 -*-
"""Builder / developer master."""

from odoo import api, fields, models

DEVELOPER_TYPES = [
    ('builder', 'Real Estate Builder'),
    ('promoter', 'Property Developer'),
    ('villa_promoter', 'Villa Promoter'),
    ('layout', 'Layout Developer'),
    ('agency', 'Real Estate Agency'),
    ('channel_partner', 'Channel Partner Network'),
    ('other', 'Other'),
]


class RnRealestateDeveloper(models.Model):
    """Real estate builder, promoter, or agency."""

    _name = 'rn.realestate.developer'
    _description = 'Real Estate Developer'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(copy=False, index=True, default='New', tracking=True)
    active = fields.Boolean(default=True)
    developer_type = fields.Selection(
        selection=DEVELOPER_TYPES,
        default='builder',
        required=True,
        tracking=True,
    )
    legal_name = fields.Char(string='Legal Name', tracking=True)
    registration_no = fields.Char(string='Company Registration')
    rera_registration = fields.Char(string='RERA Registration')
    gstin = fields.Char(string='GSTIN')
    partner_id = fields.Many2one('res.partner', string='Official Contact')
    phone = fields.Char()
    email = fields.Char()
    website = fields.Char()
    street = fields.Char()
    street2 = fields.Char()
    city = fields.Char()
    state_id = fields.Many2one('res.country.state')
    zip = fields.Char()
    country_id = fields.Many2one('res.country')
    project_ids = fields.One2many('rn.realestate.project', 'developer_id', string='Projects')
    project_count = fields.Integer(compute='_compute_counts')
    lead_ids = fields.One2many('rn.realestate.lead', 'developer_id', string='Leads')
    lead_count = fields.Integer(compute='_compute_counts')
    unit_count = fields.Integer(compute='_compute_unit_count')
    available_unit_count = fields.Integer(compute='_compute_unit_count')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    note = fields.Html()

    @api.depends('project_ids', 'lead_ids')
    def _compute_counts(self):
        for dev in self:
            dev.project_count = len(dev.project_ids)
            dev.lead_count = len(dev.lead_ids)

    def _compute_unit_count(self):
        Unit = self.env['rn.realestate.unit']
        for dev in self:
            dev.unit_count = Unit.search_count([('developer_id', '=', dev.id)])
            dev.available_unit_count = Unit.search_count([
                ('developer_id', '=', dev.id),
                ('status', '=', 'available'),
            ])

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('code', 'New') == 'New':
                vals['code'] = self.env['ir.sequence'].next_by_code('rn.realestate.developer') or 'New'
        return super().create(vals_list)

    def action_open_projects(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Projects',
            'res_model': 'rn.realestate.project',
            'view_mode': 'list,form',
            'domain': [('developer_id', '=', self.id)],
            'context': {'default_developer_id': self.id},
        }

    def action_open_leads(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Leads',
            'res_model': 'rn.realestate.lead',
            'view_mode': 'list,form',
            'domain': [('developer_id', '=', self.id)],
            'context': {'default_developer_id': self.id},
        }
