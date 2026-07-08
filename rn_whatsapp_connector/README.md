# ARMORA WhatsApp Automation Platform

Provider-agnostic WhatsApp communication automation for Odoo 19 Community.

## Overview

`rn_whatsapp_connector` is not just another API connector. It is a complete automation platform:

Odoo -> Automation Engine -> Message Templates -> Provider Layer -> WhatsApp (Meta, Twilio, 360Dialog, Gupshup, Interakt)

## Business Problem

SMBs want WhatsApp in Odoo, but most connectors are expensive, locked to one BSP, or lack automation. This module isolates providers behind a service interface and ships a registerable automation engine.

## Phase 1 Features

- Multi-provider accounts (Meta Cloud live-ready, others simulation adapters)
- Templates with variables
- Message queue, retries, scheduling
- Message log / history and webhook intake
- Automation rules (sale confirm, invoice post, delivery done, plus extensible triggers)
- OWL KPI dashboard
- Multi-company security
- SaaS edition tracking (Standard / Professional / Enterprise)

## Editions

| Edition | List Price (USD) |
|---|---|
| Standard | 29.99 |
| Professional (this Apps package) | 79.99 |
| Enterprise | 199.99 |

## Installation

1. Install Contacts, CRM, Sales, Accounting, Inventory.
2. Update Apps List and install **ARMORA WhatsApp Automation Platform**.
3. Open WhatsApp > Accounts, keep Simulation Mode for dry runs.
4. Configure automation rules and templates.

## Configuration

- Webhook URL: `/rn_whatsapp/webhook/meta_cloud`
- Use Simulation Mode until Cloud API credentials are validated.
- Set Default account per company.

## Support

ARMORA IT Technologies  
Website: https://www.armorait.com  
Support: info@armorait.com

## License

OPL-1

## Credits

(c) ARMORA IT Technologies
