# -*- coding: utf-8 -*-
"""Housing / layout projects."""

from odoo import api, fields, models

PROJECT_TYPES = [
    ('apartment', 'Apartment'),
    ('villa', 'Villa'),
    ('plot', 'Plot Layout'),
    ('commercial', 'Commercial'),
    ('mixed', 'Mixed Use'),
]


class RnRealestateProject(models.Model):
    """Real estate project or layout."""

    _name = 'rn.realestate.project'
    _description = 'Real Estate Project'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(copy=False, index=True, default='New', tracking=True)
    active = fields.Boolean(default=True)
    developer_id = fields.Many2one(
        'rn.realestate.developer',
        required=True,
        ondelete='cascade',
        index=True,
        tracking=True,
    )
    project_type = fields.Selection(
        selection=PROJECT_TYPES,
        default='apartment',
        required=True,
        tracking=True,
    )
    location = fields.Char(tracking=True)
    city = fields.Char()
    state_id = fields.Many2one('res.country.state')
    rera_id = fields.Char(string='Project RERA ID')
    launch_date = fields.Date()
    possession_date = fields.Date(string='Expected Possession')
    construction_progress = fields.Float(string='Construction %', default=0.0)
    amenities = fields.Text()
    block_ids = fields.One2many('rn.realestate.block', 'project_id', string='Blocks / Towers')
    block_count = fields.Integer(compute='_compute_block_count')
    unit_ids = fields.One2many('rn.realestate.unit', 'project_id', string='Units')
    unit_count = fields.Integer(compute='_compute_unit_stats')
    available_count = fields.Integer(compute='_compute_unit_stats')
    booked_count = fields.Integer(compute='_compute_unit_stats')
    sold_count = fields.Integer(compute='_compute_unit_stats')
    company_id = fields.Many2one(
        related='developer_id.company_id',
        store=True,
        index=True,
    )
    note = fields.Html()

    @api.depends('block_ids')
    def _compute_block_count(self):
        for project in self:
            project.block_count = len(project.block_ids)

    @api.depends('unit_ids', 'unit_ids.status')
    def _compute_unit_stats(self):
        for project in self:
            units = project.unit_ids
            project.unit_count = len(units)
            project.available_count = len(units.filtered(lambda u: u.status == 'available'))
            project.booked_count = len(units.filtered(lambda u: u.status == 'booked'))
            project.sold_count = len(units.filtered(lambda u: u.status == 'sold'))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('code', 'New') == 'New':
                vals['code'] = self.env['ir.sequence'].next_by_code('rn.realestate.project') or 'New'
        return super().create(vals_list)

    def action_open_units(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Units',
            'res_model': 'rn.realestate.unit',
            'view_mode': 'list,form',
            'domain': [('project_id', '=', self.id)],
            'context': {'default_project_id': self.id, 'default_developer_id': self.developer_id.id},
        }
