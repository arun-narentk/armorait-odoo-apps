# Database

## Models

### `rn.bookmark`

| Field | Type | Notes |
|-------|------|-------|
| name | Char | Display label |
| user_id | Many2one res.users | Owner |
| company_id | Many2one res.company | Multi-company |
| bookmark_type | Selection | record, list, menu, report, dashboard |
| res_model | Char | Target model |
| res_id | Integer | Record id for type record |
| action_id | Many2one ir.actions.actions | Menu/dashboard |
| menu_id | Many2one ir.ui.menu | Menu target |
| report_action_id | Many2one ir.actions.report | Report target |
| domain | Text | JSON list domain |
| context | Text | JSON context |
| folder_id | Many2one rn.bookmark.folder | Optional folder |
| tag_ids | Many2many rn.bookmark.tag | Labels |
| color | Selection | UI color |
| note | Text | User note |
| sequence | Integer | Sort order |
| is_pinned | Boolean | Sidebar priority |
| is_favorite | Boolean | Favorite filter |
| last_opened_at | Datetime | Usage tracking |
| open_count | Integer | Usage counter |

### `rn.bookmark.folder`

User-owned folders with optional parent, color, icon, sequence.

### `rn.bookmark.tag`

User-owned tags with color.

### `base` inherit

| Field | Type |
|-------|------|
| rn_bookmark_count | Integer computed |
| rn_is_bookmarked | Boolean computed |

## Indexes

`user_id`, `res_model`, `res_id`, `bookmark_type`, `is_pinned`, `folder_id`, `last_opened_at` are indexed for sidebar queries.

## Config parameters

| Key | Default |
|-----|---------|
| rn_bookmarks.recent_limit | 50 |
| rn_bookmarks.enable_hotkey | True |
| rn_bookmarks.enable_systray | True |
