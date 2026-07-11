# -*- coding: utf-8 -*-

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestRnTimelineTemplate(TransactionCase):

    def test_find_template_sale_sent(self):
        order = self.env['sale.order'].create({
            'partner_id': self.env['res.partner'].create({'name': 'Template Partner'}).id,
        })
        template = self.env['rn.timeline.service'].find_template(order, 'draft', 'sent')
        self.assertTrue(template)
        self.assertEqual(template.event_label, 'Quotation Sent')

    def test_template_data_loaded(self):
        templates = self.env['rn.timeline.template'].search([
            ('model_name', '=', 'sale.order'),
        ])
        self.assertGreaterEqual(len(templates), 2)
        labels = templates.mapped('event_label')
        self.assertIn('Quotation Sent', labels)
        self.assertIn('Quotation Confirmed', labels)


@tagged('post_install', '-at_install')
class TestRnTimelineCrm(TransactionCase):

    def test_crm_lead_stage_change_logs_event(self):
        stage_new = self.env.ref('crm.stage_lead1')
        stage_won = self.env.ref('crm.stage_lead4')
        lead = self.env['crm.lead'].create({
            'name': 'Timeline CRM Lead',
            'stage_id': stage_new.id,
        })
        lead.write({'stage_id': stage_won.id})
        events = self.env['rn.timeline.event'].search([
            ('model', '=', 'crm.lead'),
            ('record_id', '=', lead.id),
        ])
        self.assertTrue(events.filtered(lambda event: stage_won.name in event.name))
