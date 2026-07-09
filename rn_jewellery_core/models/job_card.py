# -*- coding: utf-8 -*-

from odoo import api, fields, models


class RnJewelleryJobCard(models.Model):
    _name = 'rn.jewellery.job.card'
    _description = 'Manufacturing Job Card'
    _inherit = ['mail.thread']
    _order = 'create_date desc'

    name = fields.Char(readonly=True, copy=False, default='New')
    design_code = fields.Char()
    description = fields.Text()
    karigar_id = fields.Many2one('rn.jewellery.karigar', index=True)
    metal_type = fields.Selection(
        [('gold', 'Gold'), ('silver', 'Silver'), ('platinum', 'Platinum')],
        default='gold',
    )
    purity_id = fields.Many2one('rn.jewellery.metal.purity')
    issue_weight = fields.Float(string='Issue Weight (g)', digits=(16, 3))
    receive_weight = fields.Float(string='Receive Weight (g)', digits=(16, 3))
    wastage_weight = fields.Float(compute='_compute_wastage', store=True, digits=(16, 3))
    stage = fields.Selection(
        [
            ('design', 'Design'),
            ('casting', 'Casting'),
            ('polishing', 'Polishing'),
            ('setting', 'Stone Setting'),
            ('finishing', 'Finishing'),
            ('qc', 'Quality Check'),
            ('done', 'Done'),
        ],
        default='design',
        tracking=True,
    )
    state = fields.Selection(
        [('draft', 'Draft'), ('in_progress', 'In Progress'), ('done', 'Done'), ('cancelled', 'Cancelled')],
        default='draft',
        tracking=True,
    )
    customer_order_id = fields.Many2one('rn.jewellery.customer.order')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

    @api.depends('issue_weight', 'receive_weight')
    def _compute_wastage(self):
        for card in self:
            card.wastage_weight = max((card.issue_weight or 0.0) - (card.receive_weight or 0.0), 0.0)

    @api.model_create_multi
    def create(self, vals_list):
        seq = self.env['ir.sequence']
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = seq.next_by_code('rn.jewellery.job.card') or 'JC'
        return super().create(vals_list)
