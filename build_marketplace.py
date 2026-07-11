#!/usr/bin/env python3
"""
ARMORA Product Builder

Generate Odoo Apps Store index.html from tools/apps_marketplace/catalog.json
and marketplace_framework templates. Do not edit static/description/index.html by hand.

Usage:
  python build_marketplace.py --sync-catalog      # add missing modules to catalog.json
  python build_marketplace.py --init              # bootstrap marketplace/module.json
  python build_marketplace.py --all --no-docs     # regenerate banners + index.html for all modules
  python build_marketplace.py rn_fleet_gps --zip    # build one module and zip
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'tools' / 'product_builder'))

from engine import main  # noqa: E402

if __name__ == '__main__':
    raise SystemExit(main())
