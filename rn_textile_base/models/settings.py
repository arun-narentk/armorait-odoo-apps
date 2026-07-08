# -*- coding: utf-8 -*-
"""Company textile settings."""

from odoo import fields, models


class RnTextileSettings(models.Model):
    """Defaults shared across textile companion modules."""

    _name = 'rn.textile.settings'
    _description = 'Textile Settings'
    _inherit = ['mail.thread']

    name = fields.Char(required=True, default='Textile Settings')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
    )
    default_factory_id = fields.Many2one('rn.textile.factory', string='Default Factory')
    unit_label = fields.Char(
        default='Factory',
        help='UI label override: Factory, Mill, Unit, Export House, etc.',
    )
    enable_lot_traceability = fields.Boolean(default=True)
    enable_job_work = fields.Boolean(default=True)
    enable_export_docs = fields.Boolean(default=False)
    enable_piece_rate = fields.Boolean(default=False)
    lot_prefix = fields.Char(default='LOT')
    batch_prefix = fields.Char(default='DYE')
    timezone = fields.Char(default='Asia/Kolkata')
    active = fields.Boolean(default=True)

    _company_uniq = models.Constraint(
        'unique(company_id)',
        'Only one textile settings record per company.',
    )
