# -*- coding: utf-8 -*-
"""Dashboard definition and layout container."""

from odoo import api, fields, models


class RnDashboard(models.Model):
    """Reusable dashboard shell used by MRP and other intelligence modules."""

    _name = 'rn.dashboard'
    _description = 'Dashboard'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, name'

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(index=True, copy=False, default='New')
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    is_default = fields.Boolean(string='Default Dashboard')
    dashboard_type = fields.Selection(
        selection=[
            ('production', 'Production'),
            ('factory', 'Factory'),
            ('ceo', 'CEO'),
            ('maintenance', 'Maintenance'),
            ('quality', 'Quality'),
            ('planning', 'Planning'),
            ('tv', 'Live TV'),
            ('custom', 'Custom'),
        ],
        default='custom',
        required=True,
        tracking=True,
        index=True,
    )
    theme = fields.Selection(
        selection=[
            ('light', 'Light'),
            ('dark', 'Dark'),
            ('factory', 'Factory Floor'),
            ('corporate', 'Corporate'),
        ],
        default='light',
        required=True,
    )
    refresh_interval = fields.Integer(
        string='Refresh Interval (seconds)',
        default=30,
        help='0 disables auto refresh. TV boards typically use 5-15 seconds.',
    )
    is_tv_mode = fields.Boolean(
        string='TV Mode',
        help='Optimizes layout for wall-mounted kiosk displays.',
    )
    public_token = fields.Char(
        string='Public Access Token',
        copy=False,
        help='Optional token for future kiosk / TV routes without interactive login.',
    )
    show_logo = fields.Boolean(default=True)
    show_clock = fields.Boolean(default=True)
    show_alerts = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    filter_id = fields.Many2one('rn.dashboard.filter', string='Default Filter')
    widget_ids = fields.One2many('rn.dashboard.widget', 'dashboard_id', string='Widgets')
    alert_rule_ids = fields.One2many('rn.dashboard.alert.rule', 'dashboard_id', string='Alert Rules')
    note = fields.Html()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('code', 'New') == 'New':
                vals['code'] = self.env['ir.sequence'].next_by_code('rn.dashboard') or 'New'
            if vals.get('is_tv_mode') and not vals.get('refresh_interval'):
                vals['refresh_interval'] = 10
        return super().create(vals_list)

    def action_open_shell(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.client',
            'tag': 'rn_dashboard_core.shell',
            'name': self.name,
            'params': {'dashboard_id': self.id},
        }

    def action_set_default(self):
        for dashboard in self:
            others = self.search([
                ('company_id', '=', dashboard.company_id.id),
                ('is_default', '=', True),
                ('id', '!=', dashboard.id),
            ])
            others.write({'is_default': False})
            dashboard.is_default = True
        return True
