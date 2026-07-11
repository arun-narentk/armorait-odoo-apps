# Release Checklist

## Code

- [x] Manifest version bumped
- [x] Security groups and access CSV
- [x] Record rules for user isolation
- [x] Wizard loads before menus in manifest
- [x] No debug prints or TODO stubs

## Tests

- [x] TransactionCase coverage
- [x] HttpCase health and sidebar routes
- [x] Wizard tests for list, menu, report

## Marketplace

- [x] `static/description/index.html`
- [x] Banner, icon, screenshots, GIF placeholders
- [x] `catalog.json` git_url on `19.0`
- [x] Price 9.99 USD

## Docs

- [x] README, CHANGELOG, INSTALL, USER_GUIDE
- [x] DEVELOPER_GUIDE, ROADMAP, SECURITY, FAQ, LICENSE
- [x] docs/ package

## Before publish

- [ ] Capture fresh screenshots after UI changes
- [ ] Run full test suite on staging
- [ ] Push to `19.0` and trigger Apps Store rescan
