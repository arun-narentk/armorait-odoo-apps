# Performance

## ORM

- `read_group` for bookmark counts on `base` records instead of per-record search.
- Sidebar query limited to 200 rows by default.
- Indexed fields on `user_id`, `res_model`, `res_id`, `is_pinned`.

## UI

- Systray loads data on open, not on every page change.
- Search input debounced 300ms in OWL sidebar.
- Hotkey service registers once at web client start.

## Recommendations

- Keep recent limit at 50-100 for large databases.
- Archive stale bookmarks instead of deleting history metrics.
- Use folders to avoid flat lists above 500 items.

## Load testing

For 10k bookmarks per user, consider pagination in sidebar (planned v2).
