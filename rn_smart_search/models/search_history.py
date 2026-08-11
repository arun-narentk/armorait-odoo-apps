# -*- coding: utf-8 -*-

from odoo import api, fields, models


class RnSearchHistory(models.Model):
    _name = 'rn.search.history'
    _description = 'Smart Search History'
    _order = 'last_opened desc, id desc'
    _rec_name = 'label'

    user_id = fields.Many2one(
        'res.users',
        string='User',
        required=True,
        index=True,
        default=lambda self: self.env.user,
        ondelete='cascade',
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        index=True,
    )
    history_type = fields.Selection(
        selection=[
            ('view', 'View'),
            ('search', 'Search'),
        ],
        string='Type',
        required=True,
        index=True,
    )
    model = fields.Char(string='Model', index=True)
    record_id = fields.Integer(string='Record ID', index=True)
    label = fields.Char(string='Label', required=True)
    search_query = fields.Char(string='Search Query')
    last_opened = fields.Datetime(
        string='Last Opened',
        default=fields.Datetime.now,
        required=True,
        index=True,
    )
    open_count = fields.Integer(string='Open Count', default=1)
    is_favorite = fields.Boolean(string='Favorite', default=False, index=True)
    entry_key = fields.Char(string='Entry Key', required=True, index=True)
    model_label = fields.Char(
        string='Model Label',
        compute='_compute_model_label',
        store=True,
    )

    _user_entry_key_uniq = models.Constraint(
        'unique(user_id, entry_key)',
        'Each history entry must be unique per user.',
    )

    @api.depends('model')
    def _compute_model_label(self):
        IrModel = self.env['ir.model']
        for record in self:
            if not record.model:
                record.model_label = False
                continue
            model_rec = IrModel.search([('model', '=', record.model)], limit=1)
            record.model_label = model_rec.name if model_rec else record.model

    def action_toggle_favorite(self):
        for record in self:
            record.is_favorite = not record.is_favorite
        return True

    def action_open_record(self):
        self.ensure_one()
        return self.env['rn.smart.search.service'].open_history_record(self.id)

    @api.model
    def _cron_cleanup_stale_history(self):
        """Cron entrypoint: remove old non-favorite history entries."""
        return self.env['rn.smart.search.service'].cleanup_stale_history()

