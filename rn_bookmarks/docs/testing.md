# Testing

## Run tests

```bash
./run_odoo.sh -d armora_apps -c .openerp_serverrc \
  --test-enable --stop-after-init --test-tags=rn_bookmarks
```

## Coverage

| Area | Tests |
|------|-------|
| Toggle record bookmark | create and remove |
| Folder count | read_group aggregation |
| List bookmark open | action dict |
| Pin and favorite | bookmark actions |
| Move bookmark | folder reassignment |
| Sidebar data | service payload |
| Dashboard stats | counts |
| Smart button | count and action |
| Duplicate guard | ValidationError |
| Wizard list/menu/report | wizard actions |
| HTTP health | JSON route |
| HTTP sidebar | JSON route |

## Capture test

Run `capture_rn_bookmarks.py` on a running Odoo with module installed.

## CI suggestion

Run post_install tagged tests on merge to `19.0`.
