# -*- coding: utf-8 -*-
"""Export artifacts (JSON / Excel / PDF / CSV) for a return."""

from odoo import fields, models


class RnGstExport(models.Model):
    """Stores generated export file metadata and binary."""

    _name = 'rn.gst.export'
    _description = 'GST Export'
    _order = 'create_date desc'

    name = fields.Char(required=True)
    return_id = fields.Many2one('rn.gst.return', required=True, ondelete='cascade', index=True)
    export_type = fields.Selection(
        selection=[
            ('json', 'JSON'),
            ('excel', 'Excel'),
            ('pdf', 'PDF'),
            ('csv', 'CSV'),
        ],
        required=True,
    )
    datas = fields.Binary(attachment=True)
    filename = fields.Char()
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('done', 'Done'),
            ('failed', 'Failed'),
        ],
        default='draft',
    )
    error_message = fields.Text()
    company_id = fields.Many2one(related='return_id.company_id', store=True)
