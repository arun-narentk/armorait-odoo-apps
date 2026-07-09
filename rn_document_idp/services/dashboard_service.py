# -*- coding: utf-8 -*-
"""IDP analytics dashboard data."""

from odoo import fields, models


class RnDocumentIdpDashboardService(models.AbstractModel):
    _name = 'rn.document.idp.dashboard.service'
    _description = 'IDP Dashboard Service'

    def get_dashboard_data(self):
        Document = self.env['rn.document.idp.document']
        company = self.env.company
        docs = Document.search([('company_id', '=', company.id)])
        review = docs.filtered(lambda doc: doc.state in ('review', 'fraud_flag'))
        posted = docs.filtered(lambda doc: doc.state == 'posted')
        duplicates = docs.filtered(lambda doc: doc.is_duplicate)
        avg_conf = round(sum(docs.mapped('overall_confidence')) / len(docs), 1) if docs else 0.0
        avg_time = round(sum(docs.mapped('processing_seconds')) / len(docs), 2) if docs else 0.0
        settings = self.env['rn.document.idp.settings'].search(
            [('company_id', '=', company.id)], limit=1,
        )
        return {
            'total_documents': len(docs),
            'review_queue': len(review),
            'posted_documents': len(posted),
            'duplicate_detections': len(duplicates),
            'avg_confidence': avg_conf,
            'avg_processing_seconds': avg_time,
            'credit_balance': settings.credit_balance if settings else 0,
            'manual_review_rate': round(len(review) / len(docs) * 100, 1) if docs else 0.0,
            'recent': [
                {
                    'id': doc.id,
                    'name': doc.name,
                    'document_type': doc.document_type,
                    'state': doc.state,
                    'confidence': doc.overall_confidence,
                }
                for doc in docs.sorted('create_date', reverse=True)[:8]
            ],
        }
