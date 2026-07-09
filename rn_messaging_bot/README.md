# Messaging Bot Engine (`rn_messaging_bot`)

Omnichannel messaging connectors and bot flow engine for Odoo 19 Community.

## Overview

This module provides a unified customer messaging inbox, connector registry, webhook intake,
and menu-based bot flows. Phase 1 ships WhatsApp Cloud API support (with simulation mode),
CRM lead creation from chat, and human handoff.

## Business Problem

Teams using WhatsApp or other channels for sales and support need conversations inside Odoo
with automated first responses, lead capture, and agent takeover without a separate helpdesk tool.

## Features

- Connector registry (WhatsApp, Instagram, Facebook Messenger, live chat placeholder)
- Conversation inbox with inbound/outbound message history
- Bot flows: message, menu, CRM action, handoff nodes
- Webhook endpoint: `/rn_messaging/webhook/<connector_id>`
- Simulation mode for safe testing
- Multi-company record rules and security groups

## Installation

1. Copy `rn_messaging_bot` into your Odoo addons path under `armora/`.
2. Update the apps list and install **Messaging Bot Engine**.
3. Open **Messaging Bot > Connectors** and create or use the demo connector.

## Configuration

1. Assign **Messaging Bot User** or **Administrator** groups to your team.
2. Create a connector, link a bot, and set `webhook_verify_token`.
3. For live WhatsApp: add `phone_number_id`, `access_token`, disable simulation mode.
4. Register the webhook URL from the connector form in Meta Developer Console.

## Usage

- Inbound webhooks create or update conversations and run the linked bot.
- Users reply from the inbox or take over after handoff.
- Bot **Create CRM Lead** action links a lead to the conversation.

## Permissions

| Group | Access |
|-------|--------|
| User | Inbox, read connectors, read bot sessions |
| Administrator | Configure bots and connectors |
| Technical | API tokens and webhook secrets |

## Requirements

- Odoo 19 Community
- Python 3.12
- PostgreSQL
- Modules: `base`, `mail`, `contacts`, `crm`

## Support

- **Company:** ARMORA IT Technologies
- **Website:** https://www.armorait.com
- **Email:** info@armorait.com

## License

OPL-1. See `LICENSE`.
