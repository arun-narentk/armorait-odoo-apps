# -*- coding: utf-8 -*-

from odoo import fields, models


class RnJewelleryKarigar(models.Model):
    _name = 'rn.jewellery.karigar'
    _description = 'Karigar / Artisan'
    _order = 'name'

    name = fields.Char(required=True)
    code = fields.Char(index=True)
    mobile = fields.Char()
    skill = fields.Selection(
        [
            ('casting', 'Casting'),
            ('polishing', 'Polishing'),
            ('setting', 'Stone Setting'),
            ('finishing', 'Finishing'),
            ('general', 'General'),
        ],
        default='general',
    )
    employee_id = fields.Many2one('hr.employee')
    wastage_avg_pct = fields.Float(string='Avg Wastage %')
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
