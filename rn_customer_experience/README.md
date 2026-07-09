# Customer Experience Portal

ARMORA IT Technologies commercial module for Odoo 19 Community.

## Overview

Customer Self-Service Experience Platform. Not a basic portal skin. A branded, mobile-first experience that reduces support calls, speeds payments, and improves retention.

## Business Problem

Odoo includes a customer portal, but many businesses need better design, branding, self-service, downloads, warranty visibility, AMC tracking, and AI assistance in one place.

## Phase 1 Features

- Mobile-first customer dashboard at `/my/experience`
- Orders, invoices, payments, and downloads
- Support tickets with AI triage foundation
- Warranty and AMC visibility
- Widget-based page builder foundation
- Admin analytics dashboard
- Company branding (colors, logo, feature toggles)

## Installation

1. Copy `rn_customer_experience` into your Odoo addons path under `armora/`.
2. Update the apps list and install **Customer Experience Portal**.
3. Open **Customer Experience > Configuration > Portal Settings** to brand the portal.

## Configuration

- Set portal title, welcome message, colors, and logo
- Enable or disable orders, invoices, payments, downloads, tickets, warranty, AMC, AI assistant
- Arrange widgets on portal pages for low-code layouts

## Usage

Portal users open **My Experience** from `/my` or `/my/experience`.

Backend users manage tickets, warranty, AMC, downloads, widgets, and analytics from the Customer Experience app menu.

## Permissions

- **Portal Manager**: operations and analytics
- **Portal Administrator**: full configuration
- Portal users see only their own tickets and shared downloads

## Requirements

- Odoo 19 Community
- `sale`, `account`, `portal`, `website`

## Support

- Website: https://www.armorait.com
- Email: info@armorait.com

## License

OPL-1. See LICENSE file.
