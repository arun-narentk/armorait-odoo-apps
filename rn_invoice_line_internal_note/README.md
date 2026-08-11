# Invoice Line Internal Note

Add an internal note on each invoice or bill line that stays inside Odoo and is not printed on customer-facing documents.

## Purpose

Store line-specific operational comments (delivery instructions, vendor remarks, follow-ups) without changing invoice totals or the PDF.

## Features

- Internal Note field on every invoice/bill line
- Works for customer invoices, credit notes, vendor bills, and refunds
- Not included in standard invoice/bill PDF reports
- No impact on taxes, totals, or posting
- No configuration menus

## Installation

1. Add the module to your addons path
2. Update the Apps list
3. Install **Invoice Line Internal Note**

## Usage

1. Open a customer invoice or vendor bill
2. On an invoice line, enter text in **Internal Note**
3. Save the document

The note remains visible in the backend and is not printed on the standard PDF.

## Technical details

- Extends `account.move.line` with stored `internal_note` (`Text`)
- Inherits `account.view_move_form` (invoice line list + line form)
- Does not modify QWeb invoice reports
- Depends on `account` only

## Compatibility

- Odoo 19 Community

## License

OPL-1

## Support

ARMORA IT Technologies  
https://www.armorait.com  
info@armorait.com
