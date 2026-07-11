# -*- coding: utf-8 -*-
"""Share action audit log."""

from odoo import api, fields, models


class RnShareLog(models.Model):
    _name = 'rn.share.log'
    _description = 'Record Share Log'
    _order = 'create_date desc, id desc'
    _rec_name = 'label'

    user_id = fields.Many2one(
        'res.users',
        required=True,
        default=lambda self: self.env.user,
        index=True,
        ondelete='cascade',
    )
    company_id = fields.Many2one('res.company', index=True, ondelete='set null')
    res_model = fields.Char(required=True, index=True)
    res_id = fields.Integer(required=True, index=True)
    label = fields.Char(required=True, index=True)
    action_type = fields.Selection(
        selection=[
            ('copy', 'Copy'),
            ('share', 'Share'),
            ('email', 'Email'),
            ('whatsapp', 'WhatsApp'),
            ('qr', 'QR'),
            ('open', 'Open'),
        ],
        required=True,
        index=True,
    )
    format_type = fields.Selection(
        selection=[
            ('url', 'URL'),
            ('markdown', 'Markdown'),
            ('html', 'HTML'),
            ('name', 'Record Name'),
            ('json', 'JSON'),
        ],
        default='url',
    )
    shared_url = fields.Char()
    model_label = fields.Char(compute='_compute_model_label', store=True)

    @api.depends('res_model')
    def _compute_model_label(self):
        cache = {}
        for record in self:
            label = ''
            if record.res_model:
                if record.res_model not in cache:
                    ir_model = self.env['ir.model'].sudo().search(
                        [('model', '=', record.res_model)],
                        limit=1,
                    )
                    cache[record.res_model] = ir_model.name if ir_model else record.res_model
                label = cache[record.res_model]
            record.model_label = label

    @api.model
    def _cron_cleanup_share_logs(self):
        self.env['rn.record.share.service'].cleanup_old_logs()
