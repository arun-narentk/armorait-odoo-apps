# -*- coding: utf-8 -*-
"""Approval workflow orchestration."""

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnAiDocumentApprovalService(models.AbstractModel):
    _name = 'rn.ai.document.approval.service'
    _description = 'AI Document Approval Service'

    def submit(self, documents):
        for document in documents:
            if not document.approval_ids:
                self.env['rn.ai.document.approval'].create({
                    'name': 'Manager Approval',
                    'document_id': document.id,
                    'role': 'manager',
                    'user_id': document.user_id.id,
                    'state': 'pending',
                })
            document.state = 'to_approve'
            document.activity_schedule(
                'mail.mail_activity_data_todo',
                summary='Approve document %s' % document.name,
                user_id=document.user_id.id,
            )
        return True

    def approve(self, documents):
        for document in documents:
            pending = document.approval_ids.filtered(lambda a: a.state == 'pending')
            pending.write({'state': 'approved', 'decision_date': fields.Datetime.now()})
            document.state = 'approved'
            self.env['rn.ai.document.version.service'].snapshot(document, reason='Approved')
        return True

    def reject(self, documents):
        for document in documents:
            pending = document.approval_ids.filtered(lambda a: a.state == 'pending')
            pending.write({'state': 'rejected', 'decision_date': fields.Datetime.now()})
            document.state = 'rejected'
        return True

    def approve_step(self, step):
        step.write({'state': 'approved', 'decision_date': fields.Datetime.now()})
        doc = step.document_id
        if not doc.approval_ids.filtered(lambda a: a.state == 'pending'):
            doc.state = 'approved'
        return True

    def reject_step(self, step):
        step.write({'state': 'rejected', 'decision_date': fields.Datetime.now()})
        step.document_id.state = 'rejected'
        return True
