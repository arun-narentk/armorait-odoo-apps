# -*- coding: utf-8 -*-
"""Yarn specification master."""

from odoo import api, fields, models

BLEND_TYPES = [
    ('cotton', 'Cotton'),
    ('polyester', 'Polyester'),
    ('viscose', 'Viscose'),
    ('elastane', 'Elastane'),
    ('cotton_poly', 'Cotton / Polyester'),
    ('cotton_viscose', 'Cotton / Viscose'),
    ('other', 'Other Blend'),
]


class RnTextileYarnSpec(models.Model):
    """Yarn count, blend, and quality specification for traceability."""

    _name = 'rn.textile.yarn.spec'
    _description = 'Yarn Specification'
    _inherit = ['mail.thread']
    _order = 'name'

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(copy=False, index=True, default='New')
    active = fields.Boolean(default=True)
    factory_id = fields.Many2one(
        'rn.textile.factory',
        required=True,
        ondelete='cascade',
        index=True,
    )
    yarn_count = fields.Char(
        string='Yarn Count',
        help='e.g. 30s, 24s combed, 20/1',
        tracking=True,
    )
    blend_type = fields.Selection(selection=BLEND_TYPES, default='cotton', required=True)
    blend_ratio = fields.Char(string='Blend Ratio', help='e.g. 60/40 CVC')
    gsm = fields.Float(string='GSM')
    color_name = fields.Char(string='Color / Shade')
    lot_prefix = fields.Char(string='Lot Prefix', help='Prefix for batch lot numbers')
    supplier_id = fields.Many2one('res.partner', string='Preferred Supplier')
    uom_id = fields.Many2one(
        'uom.uom',
        string='UoM',
        default=lambda self: self.env.ref('uom.product_uom_kgm', raise_if_not_found=False),
    )
    description = fields.Text()
    company_id = fields.Many2one(
        related='factory_id.company_id',
        store=True,
        index=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('code', 'New') == 'New':
                vals['code'] = self.env['ir.sequence'].next_by_code('rn.textile.yarn.spec') or 'New'
            if vals.get('name', 'New') == 'New' and vals.get('yarn_count'):
                vals['name'] = vals['yarn_count']
        return super().create(vals_list)

    @api.onchange('yarn_count', 'blend_type', 'color_name')
    def _onchange_auto_name(self):
        parts = [p for p in (self.yarn_count, self.blend_type, self.color_name) if p]
        if parts and (not self.name or self.name == 'New'):
            self.name = ' / '.join(parts[:3])
