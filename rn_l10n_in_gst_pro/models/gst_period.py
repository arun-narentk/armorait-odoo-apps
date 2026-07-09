# -*- coding: utf-8 -*-
"""GST return period and financial year masters."""

from odoo import api, fields, models


class RnGstPeriod(models.Model):
    """Defines a filing period (month/quarter) for GST returns."""

    _name = 'rn.gst.period'
    _description = 'GST Return Period'
    _order = 'date_start desc'

    name = fields.Char(required=True)
    code = fields.Char(required=True, index=True)
    financial_year = fields.Char(string='Financial Year', required=True, index=True)
    period_type = fields.Selection(
        selection=[
            ('month', 'Monthly'),
            ('quarter', 'Quarterly'),
            ('year', 'Annual'),
        ],
        default='month',
        required=True,
    )
    date_start = fields.Date(required=True)
    date_end = fields.Date(required=True)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
    )
    state = fields.Selection(
        selection=[
            ('open', 'Open'),
            ('locked', 'Locked'),
            ('filed', 'Filed'),
        ],
        default='open',
    )
    return_ids = fields.One2many('rn.gst.return', 'period_id', string='Returns')
    active = fields.Boolean(default=True)
    display_name = fields.Char(compute='_compute_display_name', store=True)

    _code_company_uniq = models.Constraint(
        'unique(code, company_id)',
        'Period code must be unique per company.',
    )

    @api.depends('name', 'code', 'financial_year')
    def _compute_display_name(self):
        for rec in self:
            label = rec.name or rec.code or 'Period'
            rec.display_name = '%s (%s)' % (label, rec.financial_year or '')
