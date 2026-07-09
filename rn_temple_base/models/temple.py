# -*- coding: utf-8 -*-
"""Temple / institution master."""

from odoo import api, fields, models

INSTITUTION_TYPES = [
    ('hindu_temple', 'Hindu Temple'),
    ('jain_temple', 'Jain Temple'),
    ('gurudwara', 'Gurudwara'),
    ('church', 'Church'),
    ('mosque', 'Mosque / Waqf'),
    ('ashram', 'Ashram'),
    ('mutt', 'Mutt'),
    ('trust', 'Religious Trust'),
    ('other', 'Other Institution'),
]


class RnTempleTemple(models.Model):
    """Primary temple or religious institution record."""

    _name = 'rn.temple.temple'
    _description = 'Temple / Institution'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(copy=False, index=True, default='New', tracking=True)
    active = fields.Boolean(default=True)
    institution_type = fields.Selection(
        selection=INSTITUTION_TYPES,
        default='hindu_temple',
        required=True,
        tracking=True,
    )
    trust_name = fields.Char(string='Trust / Board Name', tracking=True)
    registration_no = fields.Char(string='Registration Number')
    pan_no = fields.Char(string='PAN')
    tan_no = fields.Char(string='TAN')
    eighty_g_registration = fields.Char(string='80G Registration')
    deity_name = fields.Char(
        string='Primary Deity / Focus',
        help='Configurable label: deity for temples, patron saint for churches, etc.',
    )
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
    timezone = fields.Selection(
        selection=lambda self: self.env['res.partner']._fields['tz'].selection,
        default=lambda self: self.env.user.tz or 'UTC',
    )
    established_date = fields.Date()
    branch_ids = fields.One2many('rn.temple.branch', 'temple_id', string='Branches')
    branch_count = fields.Integer(compute='_compute_counts')
    trustee_ids = fields.One2many('rn.temple.trustee', 'temple_id', string='Trustees')
    trustee_count = fields.Integer(compute='_compute_counts')
    priest_ids = fields.One2many('rn.temple.priest', 'temple_id', string='Priests / Clergy')
    priest_count = fields.Integer(compute='_compute_counts')
    department_ids = fields.One2many('rn.temple.department', 'temple_id', string='Departments')
    timing_ids = fields.One2many('rn.temple.timing', 'temple_id', string='Daily Timings')
    festival_ids = fields.One2many('rn.temple.festival', 'temple_id', string='Festivals')
    upcoming_festival_count = fields.Integer(compute='_compute_upcoming_festivals')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    note = fields.Html()

    @api.depends('branch_ids', 'trustee_ids', 'priest_ids')
    def _compute_counts(self):
        for temple in self:
            temple.branch_count = len(temple.branch_ids)
            temple.trustee_count = len(temple.trustee_ids)
            temple.priest_count = len(temple.priest_ids)

    @api.depends('festival_ids', 'festival_ids.date_start', 'festival_ids.state')
    def _compute_upcoming_festivals(self):
        today = fields.Date.context_today(self)
        Festival = self.env['rn.temple.festival']
        for temple in self:
            temple.upcoming_festival_count = Festival.search_count([
                ('temple_id', '=', temple.id),
                ('date_start', '>=', today),
                ('state', '!=', 'cancelled'),
            ])

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('code', 'New') == 'New':
                vals['code'] = self.env['ir.sequence'].next_by_code('rn.temple.temple') or 'New'
        return super().create(vals_list)

    def action_open_branches(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Branches',
            'res_model': 'rn.temple.branch',
            'view_mode': 'list,form',
            'domain': [('temple_id', '=', self.id)],
            'context': {'default_temple_id': self.id},
        }

    def action_open_festivals(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Festivals',
            'res_model': 'rn.temple.festival',
            'view_mode': 'calendar,list,form',
            'domain': [('temple_id', '=', self.id)],
            'context': {'default_temple_id': self.id},
        }
