# -*- coding: utf-8 -*-
"""KPI dashboard board model and lifecycle actions."""

import base64
import json

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

from .constants import (
    BACKGROUND_TYPE_SELECTION,
    DATE_FILTER_TYPE_SELECTION,
    DEFINITION_VERSION,
    LAYOUT_MODE_SELECTION,
    THEME_SELECTION,
)


class RnKpiDashboard(models.Model):
    """User-authored dashboard board used by Dashboard KPI Studio."""

    _name = 'rn.kpi.dashboard'
    _description = 'KPI Dashboard'
    _order = 'sequence, name, id'
    _inherit = ['mail.thread']

    name = fields.Char(required=True, index=True, tracking=True)
    active = fields.Boolean(default=True, tracking=True)
    sequence = fields.Integer(default=10, index=True)
    description = fields.Text()
    user_id = fields.Many2one(
        'res.users',
        string='Owner',
        default=lambda self: self.env.user,
        index=True,
        tracking=True,
    )
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
        index=True,
    )
    company_ids = fields.Many2many(
        'res.company',
        'rn_kpi_dashboard_company_rel',
        'dashboard_id',
        'company_id',
        string='Companies',
    )
    group_ids = fields.Many2many(
        'res.groups',
        'rn_kpi_dashboard_group_rel',
        'dashboard_id',
        'group_id',
        string='Allowed Groups',
    )
    is_public = fields.Boolean(
        string='Shared With All Users',
        help='When enabled, any internal user with module access can open this dashboard.',
        tracking=True,
    )
    is_favorite = fields.Boolean(
        string='Favorite',
        compute='_compute_is_favorite',
        inverse='_inverse_is_favorite',
        search='_search_is_favorite',
    )
    is_template = fields.Boolean(
        string='Template',
        help='Marks predefined/template dashboards that can be duplicated.',
        index=True,
    )
    theme = fields.Selection(
        selection=THEME_SELECTION,
        default='light',
        required=True,
    )
    layout_mode = fields.Selection(
        selection=LAYOUT_MODE_SELECTION,
        default='grid',
        required=True,
    )
    background_type = fields.Selection(
        selection=BACKGROUND_TYPE_SELECTION,
        default='none',
        required=True,
    )
    background_color = fields.Char(default='#f5f7fa')
    background_image = fields.Binary(attachment=True)
    auto_refresh = fields.Boolean(default=False)
    refresh_interval = fields.Integer(
        string='Refresh Interval (seconds)',
        default=0,
        help='0 means manual refresh only.',
    )
    date_filter_type = fields.Selection(
        selection=DATE_FILTER_TYPE_SELECTION,
        string='Default Date Filter',
    )
    date_from = fields.Date()
    date_to = fields.Date()
    filter_state = fields.Json(
        string='Filter State',
        help='Serialized runtime filter values for personalization.',
        copy=False,
    )
    action_id = fields.Many2one('ir.actions.client', string='Client Action', copy=False)
    menu_id = fields.Many2one('ir.ui.menu', string='Menu Entry', copy=False)
    item_ids = fields.One2many(
        'rn.kpi.dashboard.item',
        'dashboard_id',
        string='Items',
        copy=True,
    )
    filter_ids = fields.One2many(
        'rn.kpi.dashboard.filter',
        'dashboard_id',
        string='Filters',
        copy=True,
    )
    bookmark_ids = fields.One2many(
        'rn.kpi.dashboard.bookmark',
        'dashboard_id',
        string='Bookmarks',
        copy=False,
    )
    item_count = fields.Integer(compute='_compute_item_count')

    _refresh_interval_positive = models.Constraint(
        'CHECK(refresh_interval >= 0)',
        'Refresh interval cannot be negative.',
    )
    _dashboard_active_seq_idx = models.Index('(active, sequence, id)')

    @api.depends('item_ids')
    def _compute_item_count(self):
        for dashboard in self:
            dashboard.item_count = len(dashboard.item_ids)

    def _compute_is_favorite(self):
        Bookmark = self.env['rn.kpi.dashboard.bookmark']
        favorites = Bookmark.search([
            ('dashboard_id', 'in', self.ids),
            ('user_id', '=', self.env.uid),
            ('active', '=', True),
        ]).mapped('dashboard_id')
        favorite_ids = set(favorites.ids)
        for dashboard in self:
            dashboard.is_favorite = dashboard.id in favorite_ids

    def _inverse_is_favorite(self):
        Bookmark = self.env['rn.kpi.dashboard.bookmark']
        for dashboard in self:
            existing = Bookmark.search([
                ('dashboard_id', '=', dashboard.id),
                ('user_id', '=', self.env.uid),
            ], limit=1)
            if dashboard.is_favorite:
                if existing:
                    existing.active = True
                else:
                    Bookmark.create({
                        'dashboard_id': dashboard.id,
                        'user_id': self.env.uid,
                    })
            elif existing:
                existing.active = False

    def _search_is_favorite(self, operator, value):
        if operator not in ('=', '!='):
            raise UserError(_('Unsupported favorite search operator.'))
        bookmarks = self.env['rn.kpi.dashboard.bookmark'].search([
            ('user_id', '=', self.env.uid),
            ('active', '=', True),
        ])
        ids = bookmarks.mapped('dashboard_id').ids
        positive = bool(value) if operator == '=' else not bool(value)
        return [('id', 'in' if positive else 'not in', ids)]

    @api.constrains('date_from', 'date_to', 'date_filter_type')
    def _check_custom_date_range(self):
        for dashboard in self:
            if dashboard.date_filter_type == 'custom':
                if dashboard.date_from and dashboard.date_to and dashboard.date_from > dashboard.date_to:
                    raise ValidationError(_('Dashboard date "from" must be before "to".'))

    @api.constrains('company_id', 'company_ids')
    def _check_company_consistency(self):
        for dashboard in self:
            if dashboard.company_id and dashboard.company_ids and dashboard.company_id not in dashboard.company_ids:
                raise ValidationError(_(
                    'Primary company must be included in the allowed companies list.'
                ))

    @api.constrains('background_type', 'background_color', 'background_image')
    def _check_background(self):
        for dashboard in self:
            if dashboard.background_type == 'color' and not dashboard.background_color:
                raise ValidationError(_('Background color is required when background type is Color.'))
            if dashboard.background_type == 'image' and not dashboard.background_image:
                raise ValidationError(_('Background image is required when background type is Image.'))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            company_id = vals.get('company_id') or self.env.company.id
            company_ids = vals.get('company_ids')
            if company_id and not company_ids:
                vals['company_ids'] = [(6, 0, [company_id])]
        return super().create(vals_list)

    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {})
        default.setdefault('name', _('%s (copy)', self.name))
        default.setdefault('action_id', False)
        default.setdefault('menu_id', False)
        default.setdefault('is_template', False)
        default.setdefault('filter_state', False)
        default.setdefault('user_id', self.env.uid)
        return super().copy(default)

    def unlink(self):
        menus = self.mapped('menu_id')
        actions = self.mapped('action_id')
        self.write({'menu_id': False, 'action_id': False})
        menus.unlink()
        actions.unlink()
        return super().unlink()

    def action_open_dashboard(self):
        """Open the OWL client action for this dashboard."""
        self.ensure_one()
        return {
            'type': 'ir.actions.client',
            'tag': 'rn_dashboard_kpi.dashboard',
            'name': self.name,
            'params': {
                'dashboard_id': self.id,
            },
            'context': {
                'active_id': self.id,
                'active_model': self._name,
            },
        }

    def action_duplicate(self):
        """Duplicate dashboard with items and filters."""
        self.ensure_one()
        new_dashboard = self.copy()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Duplicated Dashboard'),
            'res_model': self._name,
            'res_id': new_dashboard.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_toggle_favorite(self):
        """Toggle bookmark/favorite for the current user."""
        for dashboard in self:
            dashboard.is_favorite = not dashboard.is_favorite
        return True

    def action_export(self):
        """Export a portable JSON definition as a downloadable attachment."""
        self.ensure_one()
        definition = self.get_dashboard_definition()
        content = json.dumps(definition, indent=2, sort_keys=True)
        filename = 'rn_kpi_dashboard_%s.json' % (self.id,)
        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': base64.b64encode(content.encode('utf-8')),
            'mimetype': 'application/json',
            'res_model': self._name,
            'res_id': self.id,
        })
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % attachment.id,
            'target': 'self',
        }

    def action_create_menu(self):
        """Create or refresh a client action and menu entry under Dashboard Studio."""
        self.ensure_one()
        parent_menu = self.env.ref(
            'rn_dashboard_kpi.menu_rn_dashboard_kpi_root',
            raise_if_not_found=False,
        )
        action_vals = {
            'name': self.name,
            'tag': 'rn_dashboard_kpi.dashboard',
            'params': {
                'dashboard_id': self.id,
            },
        }
        if self.action_id:
            self.action_id.write({
                'name': self.name,
                'params': action_vals['params'],
            })
            action = self.action_id
        else:
            action = self.env['ir.actions.client'].create(action_vals)
            self.action_id = action.id

        menu_vals = {
            'name': self.name,
            'action': 'ir.actions.client,%d' % action.id,
            'parent_id': parent_menu.id if parent_menu else False,
            'sequence': self.sequence,
        }
        if self.menu_id:
            self.menu_id.write(menu_vals)
        else:
            self.menu_id = self.env['ir.ui.menu'].create(menu_vals).id
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def get_dashboard_definition(self):
        """Return a portable dashboard definition without hard database IDs."""
        self.ensure_one()
        return {
            'version': DEFINITION_VERSION,
            'module': 'rn_dashboard_kpi',
            'dashboard': {
                'name': self.name,
                'description': self.description or '',
                'theme': self.theme,
                'layout_mode': self.layout_mode,
                'background_type': self.background_type,
                'background_color': self.background_color or '',
                'auto_refresh': self.auto_refresh,
                'refresh_interval': self.refresh_interval,
                'date_filter_type': self.date_filter_type or False,
                'date_from': fields.Date.to_string(self.date_from) if self.date_from else False,
                'date_to': fields.Date.to_string(self.date_to) if self.date_to else False,
                'is_public': self.is_public,
                'is_template': self.is_template,
                'sequence': self.sequence,
                'company': self.company_id.partner_id.name if self.company_id else False,
            },
            'filters': [flt.get_configuration() for flt in self.filter_ids.sorted('sequence')],
            'items': [item.get_configuration() for item in self.item_ids.sorted('sequence')],
        }
