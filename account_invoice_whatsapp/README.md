# WhatsApp Odoo Integration

Send messages via WhatsApp from Odoo. One-on-one communication with customers and vendors from **Sale Orders**, **Purchase Orders**, **Invoicing**, and **Delivery Orders**.

## Features

- **Sale Orders** – Send quotations and sales orders to customers. Message includes order reference, amount, and line items (product, quantity, amount). Optional link to view/download the order PDF from the portal.
- **Purchase Orders** – Send RFQs and POs to vendors. Message includes order reference, amount, and line items. Optional link to view/download the PO PDF from the vendor portal.
- **Invoicing** – Send customer invoices (and refunds/receipts). Message includes invoice number, total, due date, line items, and a **secure PDF download link**.
- **Delivery Orders** – Send delivery/transfer details to the contact. Message includes picking reference, contact name, and product lines with quantities.

All flows use the contact's **Phone** or **Mobile** and open **wa.me** with a pre-filled message. No WhatsApp API or Business account required.

## Requirements

- Odoo 19.0
- **account** (Invoicing)
- **sale_management** (Sales)
- **purchase** (Purchase)
- **stock** (Inventory)

## Installation

1. Copy the module folder into your addons path (e.g. `armora/`).
2. Update the Apps list: **Apps** → **Update Apps List**.
3. Search for **WhatsApp Odoo Integration** and click **Install**.

## Configuration

- Set **Phone** or **Mobile** on contacts (Customers, Vendors, and Delivery contacts) with country code (e.g. 919731100987).
- Ensure **web.base.url** (System Parameters) is correct so document links in messages work.

## Usage

- **Sale Order** – Open a quotation or sales order → click **Send via WhatsApp** in the header.
- **Purchase Order** – Open an RFQ or PO → click **Send via WhatsApp** in the header.
- **Invoice** – Open a posted customer invoice → click **Send via WhatsApp** (next to Print).
- **Delivery** – Open a transfer (e.g. delivery order) → click **Send via WhatsApp** in the header.

WhatsApp opens in a new tab with the contact’s number and a pre-filled message. Send the message (and optional document link) to your contact.

## License

LGPL-3.
