# ARMORA AI Document Automation

AI-assisted document automation for Odoo 19 Community.

## Overview

`rn_ai_document_generator` is the foundation of the ARMORA Document Automation Platform. It combines templates, dynamic Odoo data, AI drafting, approvals, version history, and PDF output. It is not only a writer: it is document automation.

## Business Problem

Teams waste time copy-pasting quotations, offer letters, NDAs, reminders, and certificates. This module fills placeholders from Odoo records, drafts professional clauses, and tracks approval and versions.

## Phase 1 Features

- Document types (sales, HR, legal, finance, admin)
- HTML templates with `{{placeholders}}` and `{{ai_*}}` sections
- Built-in AI draft engine + optional OpenAI-compatible provider
- Generate wizard, preview, PDF report
- Approval workflow and built-in signed state
- Version snapshots with restore
- OWL dashboard and multi-company security

## Suite

```
rn_ai_document_generator
├── rn_document_templates (future)
├── rn_document_approval (future polish)
├── rn_document_esign
├── rn_document_versioning
├── rn_document_workflow
└── rn_ai_contract_review
```

## Pricing

| Edition | USD |
|---|---|
| Marketplace | 59.99 |
| Professional | 99.99 |
| SaaS | Monthly subscription |

## Installation

1. Install Contacts and HR.
2. Update Apps List and install **ARMORA AI Document Automation**.
3. Open AI Documents > Generate Document.

## Support

ARMORA IT Technologies  
Website: https://www.armorait.com  
Support: info@armorait.com

## License

OPL-1
