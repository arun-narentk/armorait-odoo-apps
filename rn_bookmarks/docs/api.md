# API

## ORM service (`rn.bookmark.service`)

```python
env['rn.bookmark.service'].toggle_record_bookmark(record, note=None, folder_id=None)
env['rn.bookmark.service'].create_list_bookmark(name, res_model, domain=[], context={}, folder_id=None)
env['rn.bookmark.service'].create_menu_bookmark(menu, folder_id=None)
env['rn.bookmark.service'].create_report_bookmark(report_action, folder_id=None)
env['rn.bookmark.service'].open_bookmark(bookmark)
env['rn.bookmark.service'].get_sidebar_data(search=None, limit=200)
env['rn.bookmark.service'].get_dashboard_stats()
env['rn.bookmark.service'].move_bookmark(bookmark_id, folder_id=None, sequence=None)
env['rn.bookmark.service'].get_current_context_bookmark_state(res_model, res_id)
```

## HTTP JSON (auth=user)

### POST `/rn/bookmark/health`

Returns `{ status, module, stats }`.

### POST `/rn/bookmark/sidebar`

Params: `search`, `limit`. Returns pinned, folders, unfiled, stats.

### POST `/rn/bookmark/toggle`

Params: `res_model`, `res_id`, `note`, `folder_id`.

### POST `/rn/bookmark/open/<bookmark_id>`

Returns `{ action }` client action dict.

### POST `/rn/bookmark/move`

Params: `bookmark_id`, `folder_id`, `sequence`.

### POST `/rn/bookmark/state`

Params: `res_model`, `res_id`. Returns `{ bookmarked, bookmark_id }`.
