# -*- coding: utf-8 -*-
{
    'name': 'Cloud Platform',
    'version': '19.0.1.0.0',
    'category': 'Productivity',
    'summary': 'Managed Odoo cloud control plane for deployment, backups, monitoring, upgrades, and AI ops insight',
    'description': """
Cloud Platform for Odoo 19 Community
====================================

Not just Odoo hosting. A managed cloud control plane for Odoo deployments,
backups, monitoring, environments, upgrades, and AI-assisted operations insight.

Phase 1 delivers:

* Cloud provider profiles for AWS, Azure, GCP, DigitalOcean, Hetzner, and OVH
* Odoo instance registry with version, edition, domain, and deployment state
* Staging and production environment tracking
* Backup snapshots with restore-readiness metadata
* Monitoring snapshots for CPU, memory, storage, and response time
* AI ops recommendations that turn metrics into actionable infrastructure advice
    """,
    'author': 'ARMORA IT Technologies',
    'maintainer': 'ARMORA IT Technologies',
    'website': 'https://www.armorait.com',
    'support': 'info@armorait.com',
    'license': 'OPL-1',
    'currency': 'USD',
    'price': 99.0,
    'live_test_url': 'https://www.armorait.com',
    'sequence': 51,
    'depends': [
        'base',
        'mail',
        'web',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'data/provider_data.xml',
        'views/provider_views.xml',
        'views/instance_views.xml',
        'views/environment_views.xml',
        'views/backup_views.xml',
        'views/monitoring_views.xml',
        'views/recommendation_views.xml',
        'views/dashboard_views.xml',
        'views/menu.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'rn_cloud_platform/static/src/scss/cloud_platform.scss',
            'rn_cloud_platform/static/src/xml/cloud_platform_dashboard.xml',
            'rn_cloud_platform/static/src/js/cloud_platform_dashboard.js',
        ],
    },
    'images': [
        'static/description/banner.png',
        'static/description/icon.png',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
