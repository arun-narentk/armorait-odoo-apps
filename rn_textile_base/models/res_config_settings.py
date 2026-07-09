# -*- coding: utf-8 -*-
"""Settings bridge."""

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    textile_default_factory_id = fields.Many2one(
        related='company_id.textile_default_factory_id',
        readonly=False,
    )
    textile_unit_label = fields.Char(
        related='company_id.textile_unit_label',
        readonly=False,
    )
    textile_enable_lot_traceability = fields.Boolean(
        related='company_id.textile_enable_lot_traceability',
        readonly=False,
    )
    textile_enable_job_work = fields.Boolean(
        related='company_id.textile_enable_job_work',
        readonly=False,
    )
    textile_enable_export_docs = fields.Boolean(
        related='company_id.textile_enable_export_docs',
        readonly=False,
    )


class ResCompany(models.Model):
    _inherit = 'res.company'

    textile_default_factory_id = fields.Many2one('rn.textile.factory', string='Default Factory')
    textile_unit_label = fields.Char(default='Factory')
    textile_enable_lot_traceability = fields.Boolean(default=True)
    textile_enable_job_work = fields.Boolean(default=True)
    textile_enable_export_docs = fields.Boolean(default=False)
