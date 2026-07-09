# -*- coding: utf-8 -*-
"""Version snapshots and rollback."""

from odoo import models


class RnAiDocumentVersionService(models.AbstractModel):
    _name = 'rn.ai.document.version.service'
    _description = 'AI Document Version Service'

    def snapshot(self, documents, reason=''):
        Version = self.env['rn.ai.document.version']
        for document in documents:
            number = len(document.version_ids) + 1
            Version.create({
                'name': '%s v%s' % (document.name, number),
                'document_id': document.id,
                'version_number': number,
                'body_html': document.body_html,
                'reason': reason or 'Snapshot',
                'author_id': self.env.user.id,
            })
        return True

    def restore(self, version):
        version.ensure_one()
        document = version.document_id
        # Snapshot current before restore
        self.snapshot(document, reason='Before restore to v%s' % version.version_number)
        document.write({
            'body_html': version.body_html,
            'state': 'generated' if document.state in ('final', 'approved', 'signed') else document.state,
        })
        self.snapshot(document, reason='Restored v%s' % version.version_number)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'rn.ai.document',
            'res_id': document.id,
            'view_mode': 'form',
            'target': 'current',
        }
