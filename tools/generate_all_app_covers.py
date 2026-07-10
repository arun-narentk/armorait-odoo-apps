#!/usr/bin/env python3
"""Generate loempia_app_cover banners for all ARMORA Apps Store modules."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from apps_store_cover import DEFAULT_BRAND_LOGO, generate_covers_for_repo


def main() -> None:
    parser = argparse.ArgumentParser(description='Generate Apps Store cover banners for all modules.')
    parser.add_argument(
        'repo_root',
        nargs='?',
        default=str(Path(__file__).resolve().parents[1]),
        help='Path to armorait-odoo-apps repo (default: sibling clone)',
    )
    parser.add_argument(
        '--brand-logo',
        default=str(DEFAULT_BRAND_LOGO),
        help='Path to armorait_brand_logo.png',
    )
    args = parser.parse_args()
    repo_root = Path(args.repo_root).resolve()
    brand_logo = Path(args.brand_logo).resolve()
    if not repo_root.is_dir():
        raise SystemExit(f'Repo not found: {repo_root}')
    if not brand_logo.is_file():
        raise SystemExit(f'Brand logo not found: {brand_logo}')
    modules = generate_covers_for_repo(repo_root, brand_logo=brand_logo)
    print(f'Generated covers for {len(modules)} modules in {repo_root}')
    for name in modules:
        print(f'  {name}')


if __name__ == '__main__':
    main()
