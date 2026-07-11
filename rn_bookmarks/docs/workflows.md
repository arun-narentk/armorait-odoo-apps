# Workflows

## Record bookmark

1. User opens form view.
2. Clicks star or presses Ctrl+B.
3. Service creates `rn.bookmark` with type `record`.
4. Sidebar refreshes on next open.

## List bookmark (wizard)

1. User opens **Bookmarks > Create Bookmark**.
2. Selects **List View**, model, domain.
3. Wizard validates JSON and calls `create_list_bookmark`.
4. User opens bookmark from sidebar or list.

## Menu bookmark

1. Wizard type **Menu**, pick `ir.ui.menu`.
2. Service stores `menu_id` and linked `action_id`.
3. Open runs menu action via `_get_action_dict`.

## Report bookmark

1. Wizard type **Report**, pick `ir.actions.report`.
2. Open calls `report_action()` on the report.

## Pin workflow

1. User sets **Pinned** on bookmark form or wizard.
2. Sidebar shows item under Pinned section first.
3. List view supports handle drag for sequence.

## Folder workflow

1. Create folder under **Bookmarks > Folders**.
2. Assign bookmarks via form, wizard, or move API.
3. Sidebar groups bookmarks under folder name.
