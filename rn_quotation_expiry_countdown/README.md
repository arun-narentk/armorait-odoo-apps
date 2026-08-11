# Quotation Expiry Countdown

See exactly how much time is left before a quotation expires.

## Purpose

Make quotation urgency immediately visible to sales users next to the standard Expiration date.

## Features

- Countdown text on quotation form and list
- Colour by urgency (green / orange / red)
- Live client-side refresh on the form (every 60 seconds, no RPC)
- Search filters: Expiring Today, Expiring Within 24 Hours, Expired Quotations
- Hidden for confirmed and cancelled orders
- Optional warning threshold (default 24 hours)

## Installation

1. Add the module to your addons path
2. Update the Apps list
3. Install **Quotation Expiry Countdown**

## Usage

1. Open a quotation with an Expiration date
2. Read the Countdown next to Expiration
3. Use the quotation search filters to find expiring or expired quotes

## Configuration

Sales > Configuration > Settings:

- **Warning within (hours)**: orange countdown when less than this many hours remain (default 24)

## Technical notes

- Non-stored computed fields: `quotation_expiry_countdown`, `quotation_expiry_urgency`
- Uses `validity_date` (date-only); expiry instant is end of that day in the user timezone
- No cron jobs and no periodic database writes
- OWL field widget `rn_quotation_expiry_countdown` for live form updates

## Dependencies

- `sale`

## License

OPL-1

## Support

ARMORA IT Technologies  
https://www.armorait.com  
info@armorait.com
