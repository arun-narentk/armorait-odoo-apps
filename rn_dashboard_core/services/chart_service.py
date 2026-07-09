# -*- coding: utf-8 -*-
"""Normalize chart payloads for OWL / Chart.js consumers."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnDashboardChartService(models.AbstractModel):
    """Build chart series dictionaries with a stable schema."""

    _name = 'rn.dashboard.chart.service'
    _description = 'Dashboard Chart Service'

    def build_line(self, labels, datasets, title=''):
        return {
            'type': 'line',
            'title': title,
            'labels': list(labels or []),
            'datasets': list(datasets or []),
        }

    def build_bar(self, labels, datasets, title=''):
        return {
            'type': 'bar',
            'title': title,
            'labels': list(labels or []),
            'datasets': list(datasets or []),
        }

    def build_pie(self, labels, values, title=''):
        return {
            'type': 'pie',
            'title': title,
            'labels': list(labels or []),
            'datasets': [{'data': list(values or [])}],
        }

    def build_gauge(self, value, min_value=0.0, max_value=100.0, title=''):
        return {
            'type': 'gauge',
            'title': title,
            'value': float(value or 0.0),
            'min': float(min_value),
            'max': float(max_value),
        }

    def build_pareto(self, labels, values, title=''):
        labels = list(labels or [])
        values = [float(v or 0.0) for v in (values or [])]
        pairs = sorted(zip(labels, values), key=lambda item: item[1], reverse=True)
        labels = [p[0] for p in pairs]
        values = [p[1] for p in pairs]
        total = sum(values) or 1.0
        cumulative = []
        running = 0.0
        for val in values:
            running += val
            cumulative.append(round(100.0 * running / total, 2))
        return {
            'type': 'pareto',
            'title': title,
            'labels': labels,
            'datasets': [
                {'type': 'bar', 'label': 'Count', 'data': values},
                {'type': 'line', 'label': 'Cumulative %', 'data': cumulative},
            ],
        }
