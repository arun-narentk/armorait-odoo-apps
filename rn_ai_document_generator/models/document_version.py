# -*- coding: utf-8 -*-
"""Document version history and rollback."""

from odoo import fields, models


class RnAiDocumentVersion(models.Model):
    """Immutable snapshot of a document body."""

    _name = 'rn.ai.document.version'
    _description = 'AI Document Version'
    _order = 'create_date desc, id desc'

    name = fields.Char(required=True)
    document_id = fields.Many2one(
        'rn.ai.document',
        required=True,
        ondelete='cascade',
        index=True,
    )
    version_number = fields.Integer(required=True, default=1)
    author_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    body_html = fields.Html(sanitize=False)
    reason = fields.Char()
    comment = fields.Text()
    company_id = fields.Many2one(
        related='document_id.company_id',
        store=True,
        index=True,
    )

    def action_restore(self):
        self.ensure_one()
        return self.env['rn.ai.document.version.service'].restore(self)
