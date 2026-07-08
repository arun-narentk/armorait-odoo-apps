# WhatsApp Connector for Odoo 19

Commercial-grade multi-provider WhatsApp integration for Odoo 19 Community.

## Phase 1 (current)

- Module skeleton and installable app shell
- Security groups: Administrator, Manager, User, Readonly
- Models: Account, Message, Template, Attachment, Webhook, History
- Service layer stubs: API, Provider, Message, PDF, Scheduler, Webhook
- Menus, settings, dashboard placeholder, send wizard
- Cron job placeholders
- Unit test skeleton

## Installation

1. Copy `rn_whatsapp_connector` into your `armora` addons path.
2. Update the apps list and install **WhatsApp Connector**.
3. Open **WhatsApp > Configuration > Settings** and enable the connector.

## Configuration

1. Create a **WhatsApp Account** under Configuration.
2. Choose a provider (Meta Cloud API, Twilio, 360Dialog, and more in later phases).
3. Set API credentials and webhook tokens.

## Architecture

```
Controllers -> Services -> Models -> Providers (Phase 3+)
```

Business logic lives in `services/`. Models store data only. Provider adapters will plug into `provider_service.py`.

## Roadmap

| Phase | Deliverable |
|-------|-------------|
| 1 | Skeleton (done) |
| 2 | Account model hardening and settings |
| 3 | Provider abstraction layer |
| 4 | Message sending service |
| 5 | Template engine |
| 6 | PDF attachments |
| 7 | CRM, Sales, Purchase, Accounting integrations |
| 8 | Webhook processing |
| 9 | OWL chat window |
| 10 | Automation rules and schedulers |
| 11 | Dashboard analytics |
| 12 | Tests, demo data, documentation |

## License

LGPL-3

## Support

info@armorait.com
