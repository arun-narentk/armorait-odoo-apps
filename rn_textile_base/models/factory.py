# -*- coding: utf-8 -*-
"""Factory / plant master."""

from odoo import api, fields, models

UNIT_TYPES = [
    ('spinning', 'Spinning Mill'),
    ('yarn_trading', 'Yarn Trading'),
    ('knitting', 'Knitting Unit'),
    ('dyeing', 'Dyeing Unit'),
    ('weaving', 'Weaving / Fabric Mill'),
    ('garment', 'Garment Factory'),
    ('export', 'Export House'),
    ('processing', 'Fabric Processing'),
    ('home_textile', 'Home Textile'),
    ('job_work', 'Job Work Unit'),
    ('trader', 'Textile Trader'),
    ('other', 'Other Unit'),
]


class RnTextileFactory(models.Model):
    """Textile manufacturing plant or trading unit."""

    _name = 'rn.textile.factory'
    _description = 'Textile Factory'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(copy=False, index=True, default='New', tracking=True)
    active = fields.Boolean(default=True)
    unit_type = fields.Selection(
        selection=UNIT_TYPES,
        default='knitting',
        required=True,
        tracking=True,
    )
    legal_name = fields.Char(string='Legal / Company Name', tracking=True)
    registration_no = fields.Char(string='Registration Number')
    gstin = fields.Char(string='GSTIN')
    iec_code = fields.Char(string='IEC Code', help='Import Export Code for export houses')
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
        default=lambda self: self.env.user.tz or 'Asia/Kolkata',
    )
    established_date = fields.Date()
    department_ids = fields.One2many('rn.textile.department', 'factory_id', string='Departments')
    department_count = fields.Integer(compute='_compute_counts')
    machine_ids = fields.One2many('rn.textile.machine', 'factory_id', string='Machines')
    machine_count = fields.Integer(compute='_compute_counts')
    yarn_spec_ids = fields.One2many('rn.textile.yarn.spec', 'factory_id', string='Yarn Specs')
    yarn_spec_count = fields.Integer(compute='_compute_counts')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    note = fields.Html()

    @api.depends('department_ids', 'machine_ids', 'yarn_spec_ids')
    def _compute_counts(self):
        for factory in self:
            factory.department_count = len(factory.department_ids)
            factory.machine_count = len(factory.machine_ids)
            factory.yarn_spec_count = len(factory.yarn_spec_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('code', 'New') == 'New':
                vals['code'] = self.env['ir.sequence'].next_by_code('rn.textile.factory') or 'New'
        return super().create(vals_list)

    def action_open_departments(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Departments',
            'res_model': 'rn.textile.department',
            'view_mode': 'list,form',
            'domain': [('factory_id', '=', self.id)],
            'context': {'default_factory_id': self.id},
        }

    def action_open_machines(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Machines',
            'res_model': 'rn.textile.machine',
            'view_mode': 'list,form',
            'domain': [('factory_id', '=', self.id)],
            'context': {'default_factory_id': self.id},
        }

    def action_open_yarn_specs(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Yarn Specifications',
            'res_model': 'rn.textile.yarn.spec',
            'view_mode': 'list,form',
            'domain': [('factory_id', '=', self.id)],
            'context': {'default_factory_id': self.id},
        }
