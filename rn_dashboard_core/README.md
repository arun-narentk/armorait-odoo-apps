# ARMORA Dashboard Core

Shared real-time dashboard framework for Odoo 19 Community.

## Overview

`rn_dashboard_core` is the foundation of ARMORA Manufacturing Intelligence and other analytics suites. It provides dashboard definitions, widgets, filters, alert rules, KPI snapshots, OWL live board shell, chart helpers, cache, and SaaS edition tracking. Domain modules such as `rn_mrp_dashboard` and `rn_mrp_production_tv` depend on this core instead of duplicating board logic.

## Business Problem

Factories need live operational visibility, not static reports. Most Odoo dashboard apps only summarize existing data. This core is built to power production, OEE, downtime, quality, and TV boards with shared filters, alerts, and refresh behavior.

## Features (Phase 1)

- Dashboard definitions (production, factory, CEO, maintenance, quality, planning, TV)
- Widgets (KPI, gauge, charts, status grid, alerts, tables)
- Saved filters (plant, line, work center, machine, shift, operator, dates)
- Alert rules and open alert inbox
- KPI catalog and snapshots
- OWL live board with auto-refresh and TV mode styling
- Cache, export CSV, PDF summary, JSON APIs
- Subscription plans: Basic / Pro / Enterprise metadata

## Suite Roadmap

```
rn_dashboard_core
├── rn_mrp_dashboard
├── rn_mrp_production_tv
├── rn_mrp_oee
├── rn_mrp_downtime
├── rn_mrp_machine_monitor
├── rn_mrp_quality_dashboard
├── rn_mrp_shift_management
├── rn_mrp_cost_analysis
└── rn_mrp_ai
```

## Installation

1. Update Apps List.
2. Install **ARMORA Dashboard Core**.
3. Open Live Board or configure dashboard definitions.

## Configuration

- Set refresh and cache under Dashboard Settings.
- Create filters for plant / shift / work center.
- Map widgets to KPI keys used by future MRP modules.

## Permissions

Readonly, User, Manager under ARMORA Dashboard privilege.

## Marketplace Pricing

Module list price: **49.99 USD** (self-hosted Apps).

Optional SaaS tiers (monthly): Basic 29 | Pro 79 | Enterprise 199+.

## Support

ARMORA IT Technologies  
Website: https://www.armorait.com  
Support: info@armorait.com

## License

OPL-1

## Credits

(c) ARMORA IT Technologies
