# ARMORA Restaurant Core

Foundation of ARMORA Restaurant Cloud POS for Odoo 19 Community.

## Overview

`rn_restaurant_core` defines restaurants, branches, dining areas, tables, menu categories/items, F&B taxes, and payment methods. POS, KDS, QR, inventory recipes, delivery, loyalty, and AI modules depend on this shared domain.

## Business Problem

Cafes, bakeries, cloud kitchens, and small hotels need a lightweight cloud stack. Most full ERP POS packs are heavy. This core keeps configuration reusable so outlets can start with setup and grow into billing, kitchen, QR, and delivery.

## Phase 1 Features

- Restaurant and multi-branch setup
- Floors and table states (available / occupied / reserved / dirty)
- Menu categories and items with kitchen stations
- Restaurant taxes and payment methods
- Setup wizard and menu CSV export
- OWL overview dashboard
- SaaS edition tracking (Starter / Professional / Enterprise)

## Suite Roadmap

```
rn_restaurant_core
├── rn_restaurant_pos
├── rn_restaurant_kds
├── rn_restaurant_inventory
├── rn_restaurant_qr
├── rn_restaurant_dashboard
├── rn_restaurant_delivery
├── rn_restaurant_loyalty
├── rn_restaurant_online
└── rn_ai_restaurant
```

## Pricing

Marketplace core list price: **49.99 USD**. SaaS plans sold separately (Starter / Professional / Enterprise).

## Installation

1. Install Contacts and Product.
2. Update Apps List and install **ARMORA Restaurant Core**.
3. Run **Setup Wizard** or open the demo cafe.

## Support

ARMORA IT Technologies  
Website: https://www.armorait.com  
Support: info@armorait.com

## License

OPL-1
