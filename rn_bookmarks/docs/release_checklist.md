# Release Checklist (docs)

Mirror of module root checklist for packaging reviews.

1. Version bump in `__manifest__.py` and `CHANGELOG.md`
2. Tests green with `--test-tags=rn_bookmarks`
3. Wizard XML loads before `menu.xml`
4. Security CSV includes wizard model
5. Capture script run for updated UI
6. `build_marketplace.py rn_bookmarks --no-docs`
7. Push to `19.0` on GitHub
8. Trigger Odoo Apps rescan

Support: info@armorait.com
