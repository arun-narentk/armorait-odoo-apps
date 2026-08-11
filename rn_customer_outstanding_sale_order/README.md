# Customer Outstanding on Sale Order

Show the customer's current receivable outstanding amount on the Sale Order form.

## Purpose

Salespeople often confirm orders without seeing how much the customer already owes. This module puts that balance next to the Customer field so it is visible before confirmation.

## Features

- Customer Outstanding field on the Sale Order form
- Value comes from Odoo Total Receivable (`partner.credit`)
- Posted accounting entries only (draft and cancelled ignored)
- Handles invoices, credit notes, partial and full payments, reconciliations
- Commercial partner aware
- Multi-company aware (company currency)
- Warning style when outstanding is greater than zero
- Preserves credit (negative) balances

## Installation

1. Copy `rn_customer_outstanding_sale_order` into your addons path
2. Update the Apps list
3. Install **Customer Outstanding on Sale Order**

No extra configuration is required.

## Usage

1. Open or create a Sale Order
2. Select a Customer
3. Check **Customer Outstanding** next to the customer

Example:

- Customer: ABC Customer
- Customer Outstanding: 125,000.00 (company currency)

## Technical details

- Extends `sale.order`
- Computed fields: `customer_outstanding`, `has_customer_outstanding`
- Currency: company currency (`company_currency_id`)
- Source of truth: commercial partner `credit` (receivable residual of posted, unreconciled move lines)
- Does not replace the standard Sale Order form (XML inheritance only)

## Dependencies

- `sale`
- `account`

## Example use case

A salesperson opens a quotation for a customer who still has two unpaid invoices totaling 12,500. Before confirming, they see **Customer Outstanding: 12,500.00** highlighted on the form and can follow up on collections or adjust terms.

## Compatibility

- Odoo 19 Community

## License

OPL-1

## Support

ARMORA IT Technologies  
https://www.armorait.com  
info@armorait.com
