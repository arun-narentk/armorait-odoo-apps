# -*- coding: utf-8 -*-
"""MES core module tests."""

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestRnMesCore(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.terminal = cls.env['rn.mes.terminal'].create({
            'name': 'Line 1 Tablet',
            'code': 'TAB-01',
        })
        cls.operator = cls.env['hr.employee'].create({
            'name': 'Test Operator',
            'company_id': cls.env.company.id,
        })
        cls.checklist = cls.env['rn.mes.quality.checklist'].create({
            'name': 'Final Inspection',
            'line_ids': [(0, 0, {'name': 'Visual check', 'check_type': 'pass_fail'})],
        })
        cls.reason = cls.env.ref('rn_mes_core.downtime_reason_breakdown')

    def test_barcode_scan_unknown(self):
        result = self.env['rn.mes.barcode.service'].process_scan('UNKNOWN-CODE')
        self.assertEqual(result['scan_type'], 'unknown')

    def test_oee_snapshot_compute(self):
        wc = self.env['mrp.workcenter'].create({'name': 'WC Test MES'})
        snap = self.env['rn.mes.oee.service'].compute_snapshot(wc.id)
        self.assertTrue(snap)
        self.assertGreaterEqual(snap.availability, 0.0)

    def test_downtime_open_close(self):
        wc = self.env['mrp.workcenter'].create({'name': 'WC Downtime'})
        svc = self.env['rn.mes.downtime.service']
        evt_id = svc.start_downtime(wc.id, self.reason.id)
        self.assertTrue(evt_id)
        svc.end_downtime(evt_id)
        evt = self.env['rn.mes.downtime.event'].browse(evt_id)
        self.assertEqual(evt.state, 'closed')
        self.assertGreaterEqual(evt.duration_minutes, 0.0)

    def test_quality_inspection_from_checklist(self):
        insp_id = self.env['rn.mes.quality.service'].create_from_checklist(self.checklist.id)
        insp = self.env['rn.mes.quality.inspection'].browse(insp_id)
        self.assertEqual(insp.state, 'in_progress')
        self.assertEqual(len(insp.line_ids), 1)

    def test_iot_ingest(self):
        device = self.env['rn.mes.machine.device'].create({
            'name': 'CNC-01',
            'code': 'CNC01',
            'workcenter_id': self.env['mrp.workcenter'].create({'name': 'CNC WC'}).id,
            'protocol': 'mqtt',
        })
        reading_id = self.env['rn.mes.iot.service'].ingest_reading(
            'CNC01', 'status', value_text='running'
        )
        self.assertTrue(reading_id)
        self.assertEqual(device.status, 'running')

    def test_dashboard_payload(self):
        data = self.env['rn.mes.dashboard.service'].get_dashboard_data()
        self.assertIn('active_sessions', data)
        self.assertIn('oee_avg', data)

    def test_insight_service(self):
        data = self.env['rn.mes.insight.service'].analyze_line_performance()
        self.assertIn('summary', data)
