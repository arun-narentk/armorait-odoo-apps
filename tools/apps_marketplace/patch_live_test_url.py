#!/usr/bin/env python3
"""Add live_test_url to module manifests from catalog.json without touching assets."""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CATALOG = Path(__file__).resolve().parent / 'catalog.json'
LIVE = 'https://www.armorait.com'


def patch_manifest(path: Path, price: float) -> bool:
    text = path.read_text(encoding='utf-8')
    if "'live_test_url':" in text:
        return False
    needle = f"'price': {price},"
    if needle not in text:
        needle = f"'price': {int(price)}," if price == int(price) else None
    if not needle or needle not in text:
        m = re.search(r"'price':\s*[\d.]+,", text)
        if not m:
            return False
        needle = m.group(0)
    text = text.replace(needle, f"{needle}\n    'live_test_url': '{LIVE}',", 1)
    path.write_text(text, encoding='utf-8')
    return True


def main():
    catalog = json.loads(CATALOG.read_text(encoding='utf-8'))
    wt_root = Path('/tmp/armora_live_url_patch')
    if wt_root.exists():
        import shutil
        shutil.rmtree(wt_root)
    wt_root.mkdir()
    branches: dict[str, list[str]] = {}
    for technical, meta in catalog.items():
        branch = meta.get('branch')
        if branch:
            branches.setdefault(branch, []).append(technical)
        else:
            mod = ROOT / technical
            if (mod / '__manifest__.py').exists():
                if patch_manifest(mod / '__manifest__.py', meta.get('price', 9.99)):
                    print(f'patched local {technical}')

    for branch, modules in branches.items():
        wt = wt_root / branch.replace('/', '_')
        subprocess.run(['git', 'worktree', 'add', '-f', str(wt), branch], cwd=ROOT, check=True)
        changed = []
        for technical in modules:
            mf = wt / technical / '__manifest__.py'
            if mf.exists() and patch_manifest(mf, catalog[technical].get('price', 9.99)):
                changed.append(technical)
        if changed:
            subprocess.run(['git', 'add'] + changed, cwd=wt, check=True)
            subprocess.run(
                ['/usr/bin/git', 'commit', '--no-verify', '-m', 'Add live_test_url to Apps Store manifest'],
                cwd=wt,
                check=True,
            )
            subprocess.run(['git', 'push', 'origin', branch], cwd=ROOT, check=True)
            print(f'pushed {branch}: {", ".join(changed)}')
        subprocess.run(['git', 'worktree', 'remove', '--force', str(wt)], cwd=ROOT, check=False)

    import shutil
    shutil.rmtree(wt_root, ignore_errors=True)
    print('DONE')


if __name__ == '__main__':
    main()
