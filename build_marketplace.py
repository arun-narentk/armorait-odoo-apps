#!/usr/bin/env python3
"""
ARMORA Product Builder

Generate Odoo Apps Store assets from marketplace/module.json and shared templates.

Usage:
  python build_marketplace.py --init              # bootstrap module configs from catalog
  python build_marketplace.py rn_fleet_gps        # build one module
  python build_marketplace.py --all --zip         # build all local rn_* modules and zip
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'tools' / 'product_builder'))

from engine import main  # noqa: E402

if __name__ == '__main__':
    raise SystemExit(main())
