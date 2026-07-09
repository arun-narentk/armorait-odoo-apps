# -*- coding: utf-8 -*-
"""Widget registry for low-code portal pages."""

from odoo import fields, models


class RnCustomerExperienceWidget(models.Model):
    _name = 'rn.customer.experience.widget'
    _description = 'Experience Portal Widget'
    _order = 'sequence, name'

    name = fields.Char(required=True)
    code = fields.Char(required=True, index=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    widget_type = fields.Selection(
        selection=[
            ('invoice_list', 'Invoice List'),
            ('order_list', 'Order List'),
            ('quotation_list', 'Quotation List'),
            ('delivery_list', 'Delivery List'),
            ('payment_button', 'Payment Button'),
            ('download_center', 'Download Center'),
            ('order_timeline', 'Order Timeline'),
            ('ticket_status', 'Ticket Status'),
            ('warranty_card', 'Warranty Card'),
            ('amc_summary', 'AMC Summary'),
            ('notification_feed', 'Notifications'),
            ('ai_chat', 'AI Assistant'),
            ('knowledge_base', 'Knowledge Base'),
        ],
        required=True,
    )
    description = fields.Text()
    template_key = fields.Char(
        required=True,
        help='QWeb template technical key used to render this widget.',
    )
    icon = fields.Char(default='fa-star')


class RnCustomerExperiencePage(models.Model):
    _name = 'rn.customer.experience.page'
    _description = 'Experience Portal Page'
    _order = 'sequence, name'

    name = fields.Char(required=True)
    code = fields.Char(required=True, index=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    config_id = fields.Many2one('rn.customer.experience.config', ondelete='cascade')
    company_id = fields.Many2one(related='config_id.company_id', store=True)
    is_home = fields.Boolean(string='Home Dashboard')
    widget_line_ids = fields.One2many(
        'rn.customer.experience.page.widget',
        'page_id',
        string='Widgets',
    )


class RnCustomerExperiencePageWidget(models.Model):
    _name = 'rn.customer.experience.page.widget'
    _description = 'Experience Page Widget Line'
    _order = 'sequence, id'

    page_id = fields.Many2one(
        'rn.customer.experience.page',
        required=True,
        ondelete='cascade',
    )
    widget_id = fields.Many2one(
        'rn.customer.experience.widget',
        required=True,
        ondelete='restrict',
    )
    sequence = fields.Integer(default=10)
    column = fields.Selection(
        selection=[('full', 'Full Width'), ('left', 'Left'), ('right', 'Right')],
        default='full',
    )
    company_id = fields.Many2one(related='page_id.company_id', store=True)
