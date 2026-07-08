# ARMORA Rental Core

Industry-agnostic rental engine for Odoo 19 Community.

## Overview

`rn_rental_core` is the shared foundation of ARMORA Rental. It provides rentable assets, categories, pricing strategies, availability conflict detection, lean bookings, OWL dashboard, and SaaS edition tracking. Industry packs (car, bike, camera, furniture, equipment) and companion modules (payment, deposit, return, damage, website) extend this core without duplicating business logic.

## Target Industries

Cars, bikes, cameras, furniture, construction machinery, party/event gear, medical equipment, IT gear, sports gear, and more.

## Phase 1 Features

- Rental assets and states
- Categories and pricing rules
- Availability and conflict checks
- Bookings with reserve/confirm/cancel
- Quick booking and availability wizards
- OWL rental dashboard
- Subscription / edition tracking
- Security, crons, docs, Apps assets

## Suite Architecture

```
rn_rental_core
├── rn_rental_booking / payment / deposit / return / damage
├── rn_rental_invoice / website / portal / dashboard / reports / api
└── Industry packs: rn_car_rental, rn_bike_rental, rn_camera_rental, ...
```

## Installation

1. Install Contacts and Product.
2. Update Apps List.
3. Install **ARMORA Rental Core**.
4. Create categories, assets, and pricing.

## Marketplace Pricing

Core module priced at **29.99 USD**. Companion modules and industry packs sold separately.

## Support

ARMORA IT Technologies  
Website: https://www.armorait.com  
Support: info@armorait.com

## License

OPL-1

## Credits

(c) ARMORA IT Technologies
