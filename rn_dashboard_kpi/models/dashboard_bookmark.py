# -*- coding: utf-8 -*-
"""Per-user dashboard bookmarks."""

from odoo import fields, models


class RnKpiDashboardBookmark(models.Model):
    """Bookmark linking a user to a dashboard."""

    _name = 'rn.kpi.dashboard.bookmark'
    _description = 'KPI Dashboard Bookmark'
    _order = 'sequence, id'
    _rec_name = 'dashboard_id'

    dashboard_id = fields.Many2one(
        'rn.kpi.dashboard',
        required=True,
        ondelete='cascade',
        index=True,
    )
    user_id = fields.Many2one(
        'res.users',
        required=True,
        default=lambda self: self.env.user,
        index=True,
        ondelete='cascade',
    )
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    filter_state = fields.Json(
        string='Saved Filter State',
        help='Optional personal filter snapshot for this bookmark.',
        copy=False,
    )
    company_id = fields.Many2one(
        related='dashboard_id.company_id',
        store=True,
        index=True,
        readonly=True,
    )

    _dashboard_user_uniq = models.Constraint(
        'unique(dashboard_id, user_id)',
        'A user can bookmark a dashboard only once.',
    )
    _bookmark_user_seq_idx = models.Index('(user_id, sequence, id)')
