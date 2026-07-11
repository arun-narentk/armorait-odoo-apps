# Smart Search

Smart Search for Odoo 19 Community tracks recently viewed records and search queries so users can reopen work faster from the workspace, systray, or Ctrl+K command palette.

## Features

- Automatic view tracking on sale orders, contacts, CRM leads, invoices, and products
- Search query history with quick reopen
- Favorites and a dedicated workspace dashboard
- Systray shortcut and Ctrl+K provider
- Configurable retention, max history, and daily cleanup cron
- Per-user security with Odoo 19 privilege groups

## Installation

1. Copy `rn_smart_search` into your Odoo addons path under `armora/`.
2. Update the apps list and install **Smart Search**.
3. Assign the **Smart Search User** group to internal users.

## Configuration

Open **Settings > Smart Search** (manager group):

- Remember viewed records
- Remember search queries
- Maximum history entries
- Auto-clean after (days)

## Usage

- Open any supported form view to log a recent record automatically.
- Press **Ctrl+K** to reopen recent history items from the command palette.
- Use the systray history icon or **Smart Search > Workspace** for grouped history.
- Mark entries as favorites from the workspace.

## Support

ARMORA IT Technologies  
https://www.armorait.com  
info@armorait.com

## License

OPL-1. See `LICENSE`.
