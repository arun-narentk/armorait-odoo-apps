# User Guide

## Bookmark a record

1. Open any form (sale order, partner, invoice, lead, etc.).
2. Click **Bookmark** in the header or press **Ctrl+B**.
3. Click again to remove the bookmark.

## Sidebar

Click the **star** icon in the top bar to open the bookmarks panel.

- Search by name or note
- See pinned items first
- Browse folders and unfiled bookmarks
- Click a row to open the target

## Folders

Go to **Bookmarks > Folders** to create folders such as Sales, Invoices, or CRM.

Drag bookmarks in the list view to reorder. Assign a folder on the bookmark form or when creating from the wizard.

## Pins and favorites

- **Pinned**: always shown at the top of the sidebar
- **Favorite**: filter under **Bookmarks > Favorites**

Use buttons on the bookmark form or list decorations to manage status.

## Tags and notes

Add tags under **Bookmarks > Tags**. Assign tags on bookmark forms.

Use the **Note** field for context such as "Customer waiting" or "Review Friday".

## Create list, menu, or report bookmarks

1. Go to **Bookmarks > Create Bookmark**.
2. Choose type: **List View**, **Menu**, **Report**, or **Dashboard**.
3. Fill target fields (model + domain for lists, menu picker, report picker).
4. Set folder, color, pin, and tags.
5. Click **Save Bookmark**.

Example list bookmark:

- Name: `Overdue Invoices`
- Model: `account.move`
- Domain: `[('move_type', '=', 'out_invoice'), ('payment_state', '!=', 'paid')]`

## Smart button

On supported forms, the **Bookmarks** stat button shows how many bookmarks point to that record.

## Settings

**Settings > Bookmarks**

| Setting | Purpose |
|---------|---------|
| Recent limit | Max items in recent groups |
| Ctrl+B hotkey | Toggle bookmark on current record |
| Sidebar systray | Show star panel in top bar |

## Support

info@armorait.com
