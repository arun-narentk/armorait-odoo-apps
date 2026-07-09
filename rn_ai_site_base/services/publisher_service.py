# -*- coding: utf-8 -*-
"""Publish hooks for Odoo Website and standalone SaaS."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnAiSitePublisherService(models.AbstractModel):
    """Publish generated sites. Full Odoo Website sync in companion module."""

    _name = 'rn.ai.site.publisher.service'
    _description = 'AI Site Publisher Service'

    def publish_to_odoo_hooks(self, sites):
        """Record publish intent and post chatter. rn_ai_site_publisher extends this."""
        settings = self.env['rn.ai.site.brief.service'].ensure_default_settings()
        for site in sites:
            site.message_post(
                body=(
                    f'Site marked published. Mode: {settings.publisher_mode}. '
                    f'Pages: {site.page_count}. Odoo Website sync ready for companion publisher.'
                ),
                message_type='notification',
            )
            if settings.enable_auto_crm:
                crm_installed = self.env['ir.module.module'].search_count([
                    ('name', '=', 'crm'),
                    ('state', '=', 'installed'),
                ])
                if crm_installed:
                    self._create_crm_lead_from_site(site)
        return True

    def _create_crm_lead_from_site(self, site):
        brief = site.brief_id
        if not brief:
            return
        existing = self.env['crm.lead'].search([
            ('name', '=', f'Website Launch: {site.business_name}'),
            ('company_id', '=', site.company_id.id),
        ], limit=1)
        if existing:
            return
        self.env['crm.lead'].create({
            'name': f'Website Launch: {site.business_name}',
            'type': 'opportunity',
            'description': brief.description,
            'partner_id': brief.partner_id.id if brief.partner_id else False,
            'company_id': site.company_id.id,
        })
