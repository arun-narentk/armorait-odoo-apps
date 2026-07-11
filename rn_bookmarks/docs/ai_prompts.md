# AI Prompts

Use these prompts when extending the module.

## Add bookmark toggle to a custom model

```text
Inherit the form view for model my.model and add rn_bookmark_toggle widget
with hidden rn_is_bookmarked field. Follow rn_bookmarks/views/inherited_form_views.xml.
```

## Add a new bookmark type

```text
Extend rn.bookmark.bookmark_type selection in constants.py, handle open_bookmark
in bookmark_service.py, add wizard fields in bookmark_create_wizard.py, and add tests.
```

## Shared folder v2

```text
Add share_type on rn.bookmark.folder with private/team/company values,
record rules per scope, and service filter in get_sidebar_data. Keep backward
compatibility for existing private folders.
```

## Marketplace capture

```text
Update capture_rn_bookmarks.py to screenshot the Create Bookmark wizard
after seeding a menu and report bookmark demo.
```
