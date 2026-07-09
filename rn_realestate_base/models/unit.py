# -*- coding: utf-8 -*-
"""Property unit / plot inventory."""

from odoo import api, fields, models

UNIT_STATUS = [
    ('available', 'Available'),
    ('blocked', 'Blocked'),
    ('booked', 'Booked'),
    ('sold', 'Sold'),
]

FACING_OPTIONS = [
    ('north', 'North'),
    ('south', 'South'),
    ('east', 'East'),
    ('west', 'West'),
    ('north_east', 'North East'),
    ('north_west', 'North West'),
    ('south_east', 'South East'),
    ('south_west', 'South West'),
]


class RnRealestateUnit(models.Model):
    """Apartment unit, villa, or plot in inventory."""

    _name = 'rn.realestate.unit'
    _description = 'Property Unit'
    _inherit = ['mail.thread']
    _order = 'project_id, block_id, floor_no, name'

    name = fields.Char(required=True, tracking=True, string='Unit Number')
    code = fields.Char(copy=False, index=True, default='New')
    active = fields.Boolean(default=True)
    developer_id = fields.Many2one(
        'rn.realestate.developer',
        required=True,
        ondelete='restrict',
        index=True,
    )
    project_id = fields.Many2one(
        'rn.realestate.project',
        required=True,
        ondelete='cascade',
        index=True,
        tracking=True,
    )
    block_id = fields.Many2one(
        'rn.realestate.block',
        string='Block / Tower',
        index=True,
        domain="[('project_id', '=', project_id)]",
    )
    floor_no = fields.Integer(string='Floor')
    unit_type = fields.Selection(
        selection=[
            ('apartment', 'Apartment'),
            ('villa', 'Villa'),
            ('plot', 'Plot'),
            ('shop', 'Shop'),
            ('office', 'Office'),
        ],
        default='apartment',
        required=True,
    )
    status = fields.Selection(
        selection=UNIT_STATUS,
        default='available',
        required=True,
        tracking=True,
        index=True,
    )
    facing = fields.Selection(selection=FACING_OPTIONS)
    carpet_area = fields.Float(string='Carpet Area (sq ft)')
    builtup_area = fields.Float(string='Built-up Area (sq ft)')
    plot_area = fields.Float(string='Plot Area (sq ft)')
    base_price = fields.Monetary(string='Base Price', currency_field='currency_id', tracking=True)
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id,
    )
    lead_id = fields.Many2one('rn.realestate.lead', string='Linked Lead', copy=False)
    partner_id = fields.Many2one('res.partner', string='Customer', copy=False)
    company_id = fields.Many2one(
        related='project_id.company_id',
        store=True,
        index=True,
    )
    note = fields.Text()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('code', 'New') == 'New':
                vals['code'] = self.env['ir.sequence'].next_by_code('rn.realestate.unit') or 'New'
        return super().create(vals_list)

    @api.onchange('project_id')
    def _onchange_project_id(self):
        if self.project_id:
            self.developer_id = self.project_id.developer_id
        if self.block_id and self.block_id.project_id != self.project_id:
            self.block_id = False

    def action_block(self):
        self.write({'status': 'blocked'})

    def action_release(self):
        self.write({'status': 'available'})

    def action_mark_booked(self):
        self.write({'status': 'booked'})

    def action_mark_sold(self):
        self.write({'status': 'sold'})
