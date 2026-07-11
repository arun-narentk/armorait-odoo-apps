# Developer Guide

## Module layout

```text
rn_bookmarks/
  models/          # rn.bookmark, folders, tags, base inherit, settings
  services/        # rn.bookmark.service business logic
  controllers/     # JSON routes for sidebar and toggle
  wizard/          # Create Bookmark wizard
  static/src/      # OWL systray, toggle widget, hotkey service
  views/           # Backend menus and inherited forms
  security/        # Groups, access, record rules
  tests/
```

## Extension points

### Bookmark a custom model form

Inherit the form view and add:

```xml
<field name="rn_is_bookmarked" invisible="1"/>
<widget name="rn_bookmark_toggle"/>
```

Or call from Python:

```python
self.env['rn.bookmark.service'].toggle_record_bookmark(record)
```

### Service API

| Method | Purpose |
|--------|---------|
| `toggle_record_bookmark(record)` | Create or remove record bookmark |
| `create_list_bookmark(name, model, domain, context)` | Save filtered list |
| `create_menu_bookmark(menu)` | Save menu target |
| `create_report_bookmark(report)` | Save report action |
| `open_bookmark(bookmark)` | Return `ir.actions` dict |
| `get_sidebar_data(search, limit)` | Systray payload |
| `move_bookmark(id, folder_id, sequence)` | Reorder or refile |

### JSON routes

| Route | Auth | Purpose |
|-------|------|---------|
| `/rn/bookmark/health` | user | Module health + stats |
| `/rn/bookmark/sidebar` | user | Sidebar data |
| `/rn/bookmark/toggle` | user | Toggle current record |
| `/rn/bookmark/open/<id>` | user | Open bookmark action |
| `/rn/bookmark/move` | user | Move bookmark |
| `/rn/bookmark/state` | user | Current form bookmark state |

## Tests

```bash
./run_odoo.sh -d DB -c .openerp_serverrc --test-enable --stop-after-init --test-tags=rn_bookmarks
```

## Marketplace assets

```bash
python3 tools/apps_marketplace/capture_rn_bookmarks.py
python3 build_marketplace.py rn_bookmarks --no-docs
```

## Support

info@armorait.com
