# Security

- Token route validates active QR record and expiration.
- Scan route records traceable metadata in `rn.qr.scan.log`.
- Privilege groups:
  - Universal QR User
  - Universal QR Manager
- Multi-company rules are enabled for QR records, scan logs, and model config.

# Security

- Public scan endpoint resolves only tokenized records.
- Expired tokens are rejected.
- Internal models are protected with privilege groups:
  - Universal QR User
  - Universal QR Manager
- Multi-company record rules are enabled for QR records, scan logs, and model configuration.
# Security

## Access control

- `group_rn_universal_qr_user`: day-to-day QR generation and downloads
- `group_rn_universal_qr_manager`: templates, model configuration, and scan log administration

## Record rules

Multi-company rules apply to `rn.qr.record`, `rn.qr.scan.log`, and `rn.qr.model.config`.

## Token design

QR codes use random URL-safe tokens, not sequential database IDs. Tokens can be regenerated to invalidate old links.

## Scan route

`/rn/qr/<token>` is public for scanning. Linked records still enforce Odoo access rights. Unauthenticated users are redirected to login when required.

## Recommendations

- Use expiration policies for customer-facing QR labels.
- Regenerate tokens when access scope changes.
- Restrict manager group to administrators.

## Contact

info@armorait.com
