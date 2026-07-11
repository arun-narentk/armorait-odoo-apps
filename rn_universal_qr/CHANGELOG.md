# Changelog

## 19.0.1.0.0

- Rebuilt full `rn_universal_qr` module after corruption
- Added universal mixin, services, and public scan route
- Added templates, model config, settings, wizard, reports, and tests

# Changelog

## 19.0.1.0.0

- Rebuilt full `rn_universal_qr` commercial module after branch loss
- Added universal mixin inheritance on `base` for all models
- Added QR registry, scan logs, templates, model config, and services
- Added controller routes, settings, wizard, reports, security, and tests
# Changelog

## 19.0.1.0.0 - 2026-07-11

### Added

- Initial release of Universal QR Generator for Odoo 19 Community
- Generic `rn.qr.mixin` attached to all models through `base` inheritance
- `rn.qr.record` with UUID token URLs and image storage
- Model configuration for any `ir.model` with dynamic form UI setup
- QR templates, scan logs, bulk ZIP wizard, and label/A4 reports
- Secure scan controller at `/rn/qr/<token>`
- Settings app block for defaults and feature toggles
- Preconfigured models: sale order, purchase order, invoice, partner, product, CRM lead, stock picking
- Automated tests for generation, scans, expiration, bulk export, and HTTP routes
