# -*- coding: utf-8 -*-
"""Timeline event type metadata for rn_record_timeline."""

from __future__ import annotations

EVENT_TYPE_SELECTION = [
    ('created', 'Created'),
    ('sent', 'Sent'),
    ('confirmed', 'Confirmed'),
    ('approved', 'Approved'),
    ('invoice', 'Invoice'),
    ('payment', 'Payment'),
    ('delivery', 'Delivery'),
    ('received', 'Received'),
    ('won', 'Won'),
    ('lost', 'Lost'),
    ('posted', 'Posted'),
    ('reconciled', 'Reconciled'),
    ('cancelled', 'Cancelled'),
    ('pending', 'Pending'),
    ('activity', 'Activity'),
    ('completed', 'Completed'),
    ('other', 'Other'),
]

FILTER_CATEGORY_SELECTION = [
    ('general', 'General'),
    ('financial', 'Financial'),
    ('logistics', 'Logistics'),
    ('approval', 'Approval'),
]

DEFAULT_EVENT_META = {
    'created': {'icon': 'fa-plus-circle', 'color': '#2563eb'},
    'sent': {'icon': 'fa-paper-plane', 'color': '#2563eb'},
    'confirmed': {'icon': 'fa-check-circle', 'color': '#16a34a'},
    'approved': {'icon': 'fa-check', 'color': '#16a34a'},
    'invoice': {'icon': 'fa-file-invoice', 'color': '#7c3aed'},
    'payment': {'icon': 'fa-money-bill-wave', 'color': '#059669'},
    'delivery': {'icon': 'fa-truck', 'color': '#0891b2'},
    'received': {'icon': 'fa-box-open', 'color': '#0891b2'},
    'won': {'icon': 'fa-trophy', 'color': '#ca8a04'},
    'lost': {'icon': 'fa-times-circle', 'color': '#dc2626'},
    'posted': {'icon': 'fa-book', 'color': '#7c3aed'},
    'reconciled': {'icon': 'fa-link', 'color': '#059669'},
    'cancelled': {'icon': 'fa-ban', 'color': '#dc2626'},
    'pending': {'icon': 'fa-clock', 'color': '#ea580c'},
    'activity': {'icon': 'fa-calendar-check', 'color': '#2563eb'},
    'completed': {'icon': 'fa-flag-checkered', 'color': '#16a34a'},
    'other': {'icon': 'fa-circle', 'color': '#64748b'},
}

TIMELINE_PAGE_LIMIT = 50

SUPPORTED_MODELS = (
    'sale.order',
    'purchase.order',
    'account.move',
    'crm.lead',
)
