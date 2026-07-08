#!/usr/bin/env python3
"""Generate master capture checklist index for the ARMORA catalog."""
from __future__ import annotations

import json
from pathlib import Path

ARMORA = Path(__file__).resolve().parents[2]
CATALOG = ARMORA / 'tools' / 'apps_marketplace' / 'catalog.json'
OUT = Path(__file__).resolve().parent / 'CAPTURE_INDEX.md'


def main() -> None:
    catalog = json.loads(CATALOG.read_text(encoding='utf-8'))
    lines = [
        '# ARMORA Apps Store Capture Index',
        '',
        'Per-module checklists live in `marketplace/CAPTURE_CHECKLIST.md` after you run `python build_marketplace.py --init`.',
        '',
        '| Module | App name | Branch | Dashboard | Reports | Mobile | Checklist |',
        '|--------|----------|--------|-----------|---------|--------|-----------|',
    ]
    for technical, meta in sorted(catalog.items()):
        branch = meta.get('branch') or 'local'
        checklist = f'`{technical}/marketplace/CAPTURE_CHECKLIST.md`'
        lines.append(
            f'| `{technical}` | {meta["app_name"]} | {branch} | '
            f'{"yes" if meta.get("has_dashboard") else "no"} | '
            f'{"yes" if meta.get("has_reports") else "no"} | '
            f'{"yes" if meta.get("has_mobile") else "no"} | {checklist} |'
        )
    lines += [
        '',
        '## Workflow',
        '',
        '1. Install module on capture DB `armora_apps_capture`',
        '2. Run `python tools/apps_marketplace/capture_real_assets.py` or record manually',
        '3. Copy PNG/GIF files into `marketplace/screenshots/` and `marketplace/gifs/`',
        '4. Run `python build_marketplace.py <module> --zip`',
        '5. Upload ZIP from `apps_store_zips/`',
        '',
    ]
    OUT.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'Wrote {OUT}')


if __name__ == '__main__':
    main()
