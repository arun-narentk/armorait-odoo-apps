# -*- coding: utf-8 -*-
"""Settings bridge."""

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    rn_ai_doc_provider = fields.Selection(
        selection=[
            ('builtin', 'Built-in Draft Engine'),
            ('openai', 'OpenAI Compatible'),
            ('disabled', 'Disabled'),
        ],
        default='builtin',
    )


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    rn_ai_doc_provider = fields.Selection(
        related='company_id.rn_ai_doc_provider',
        readonly=False,
    )
