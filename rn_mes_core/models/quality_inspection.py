# -*- coding: utf-8 -*-
"""Quality inspections executed on the shop floor."""

from odoo import api, fields, models


class RnMesQualityInspection(models.Model):
    """Operator-driven inspection with pass/fail and NCR hooks."""

    _name = 'rn.mes.quality.inspection'
    _description = 'MES Quality Inspection'
    _inherit = ['mail.thread']
    _order = 'inspection_time desc'

    name = fields.Char(readonly=True, copy=False, default='New')
    session_id = fields.Many2one('rn.mes.production.session', index=True)
    workorder_id = fields.Many2one('mrp.workorder', index=True)
    checklist_id = fields.Many2one('rn.mes.quality.checklist', string='Checklist')
    operator_id = fields.Many2one('hr.employee', string='Inspector')
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('in_progress', 'In Progress'),
            ('pass', 'Pass'),
            ('fail', 'Fail'),
        ],
        default='draft',
        required=True,
        tracking=True,
    )
    inspection_time = fields.Datetime(default=fields.Datetime.now)
    line_ids = fields.One2many('rn.mes.quality.inspection.line', 'inspection_id')
    note = fields.Text()
    attachment_ids = fields.Many2many('ir.attachment', string='Photos')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        seq = self.env['ir.sequence']
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = seq.next_by_code('rn.mes.quality.inspection') or 'QI'
        return super().create(vals_list)


class RnMesQualityInspectionLine(models.Model):
    """Result line for a checklist checkpoint."""

    _name = 'rn.mes.quality.inspection.line'
    _description = 'MES Quality Inspection Line'
    _order = 'sequence, id'

    inspection_id = fields.Many2one('rn.mes.quality.inspection', required=True, ondelete='cascade')
    sequence = fields.Integer(default=10)
    name = fields.Char(required=True)
    check_type = fields.Selection(
        [
            ('pass_fail', 'Pass / Fail'),
            ('measurement', 'Measurement'),
            ('photo', 'Photo Required'),
            ('text', 'Text Note'),
        ],
        default='pass_fail',
    )
    result = fields.Selection([('pass', 'Pass'), ('fail', 'Fail')])
    measured_value = fields.Float(string='Value')
    note = fields.Text()
    attachment_ids = fields.Many2many('ir.attachment', string='Evidence')
