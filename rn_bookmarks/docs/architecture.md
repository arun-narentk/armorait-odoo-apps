# Architecture

## Layers

| Layer | Responsibility |
|-------|----------------|
| Models | `rn.bookmark`, folders, tags, `base` inherit fields |
| Services | `rn.bookmark.service` toggle, open, sidebar, stats |
| Controllers | Thin JSON endpoints for OWL client |
| Wizard | Create list/menu/report/dashboard bookmarks |
| OWL | Systray sidebar, form toggle, Ctrl+B hotkey |

## Data flow

1. User toggles bookmark on form -> `action_toggle_rn_bookmark` -> service creates/unlinks `rn.bookmark`.
2. Systray loads -> ORM `get_sidebar_data` -> renders folders and pinned rows.
3. User clicks bookmark -> `open_bookmark` returns `ir.actions.act_window` or report action.
4. Wizard creates non-record bookmarks with typed target fields.

## Dependencies

Sales, CRM, Account, and related apps are manifest dependencies for inherited form views only. Core bookmark logic depends on `base`, `mail`, and `web`.

## Future

v2 shared folders will add team rules without changing the service contract.
