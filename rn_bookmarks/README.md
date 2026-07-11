# Bookmarks for Odoo 19

Bookmark any Odoo record, filtered list view, menu, report, or dashboard and reopen it from a sidebar in one click.

## Business Problem

Odoo has favorites in some apps, but no universal bookmark system across models. Users copy links, keep browser tabs, or search again for the same sale order, invoice, partner, or project every day.

## Features

- Universal record bookmarks on any model via `base` inheritance
- Actionable types: record, list view, menu, report, dashboard
- Folders, pins, favorites, colors, notes, and tags
- Systray sidebar with search and stats
- Form star button and **Ctrl+B** hotkey
- Smart button bookmark count on sales, partners, invoices, and leads
- Create Bookmark wizard for list, menu, report, and dashboard targets

## Benefits

- Reopen critical records without searching
- Organize bookmarks like a browser bookmark manager
- Pin urgent items and add notes for context
- Private per-user bookmarks with record rules

## Installation

See [INSTALL.md](INSTALL.md).

## Configuration

Go to **Settings > Bookmarks** to set recent limit, hotkey, and systray options.

Assign **ARMORA Bookmarks / User** to internal users.

## Usage

1. Open a record and click **Bookmark** or press **Ctrl+B**.
2. Use **Bookmarks > Create Bookmark** for list views, menus, or reports.
3. Organize under **Bookmarks > Folders**.
4. Open the star icon in the top bar for quick navigation.

## Permissions

| Group | Access |
|-------|--------|
| User | Own bookmarks, folders, tags |
| Manager | Same as user (admin pre-assigned) |

## Requirements

- Odoo 19 Community
- Python 3.12
- PostgreSQL

## Roadmap

See [ROADMAP.md](ROADMAP.md).

## FAQ

See [FAQ.md](FAQ.md).

## Support

- ARMORA IT Technologies
- https://www.armorait.com
- info@armorait.com

## License

OPL-1. See [LICENSE](LICENSE).

## Credits

Developed by ARMORA IT Technologies.
