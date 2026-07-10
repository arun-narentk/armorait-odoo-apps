#!/usr/bin/env python3
"""Build marketplace pages and Apps Store ZIPs for all catalog modules from git branches."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ARMORA_ROOT = Path(__file__).resolve().parents[2]
CATALOG = ARMORA_ROOT / 'tools' / 'apps_marketplace' / 'catalog.json'
ZIP_OUT = ARMORA_ROOT / 'apps_store_zips'
PY = Path(sys.executable)
BUILDER = ARMORA_ROOT / 'build_marketplace.py'


def load_catalog() -> dict:
    return json.loads(CATALOG.read_text(encoding='utf-8'))


def zip_module(mod_dir: Path) -> Path:
    ZIP_OUT.mkdir(parents=True, exist_ok=True)
    zip_path = ZIP_OUT / f'{mod_dir.name}.zip'
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for path in mod_dir.rglob('*'):
            if path.is_file() and '__pycache__' not in path.parts:
                zf.write(path, path.relative_to(mod_dir.parent))
    return zip_path


def main() -> int:
    catalog = load_catalog()
    wt_root = Path('/tmp/armora_product_builder_zips')
    if wt_root.exists():
        shutil.rmtree(wt_root)
    wt_root.mkdir()

    branches_done: dict[str, Path] = {}
    results = []

    for technical, meta in catalog.items():
        branch = meta.get('branch')
        if branch:
            if branch not in branches_done:
                wt = wt_root / branch.replace('/', '_')
                subprocess.run(
                    ['git', 'worktree', 'add', '-f', str(wt), branch],
                    cwd=ARMORA_ROOT,
                    check=True,
                )
                branches_done[branch] = wt
            mod_dir = branches_done[branch] / technical
            if not mod_dir.exists():
                results.append((technical, 'SKIP', 'missing on branch'))
                continue
        else:
            mod_dir = ARMORA_ROOT / technical
            if not mod_dir.exists():
                results.append((technical, 'SKIP', 'local missing'))
                continue

        subprocess.run([str(PY), str(BUILDER), technical], cwd=ARMORA_ROOT, check=False)
        if branch:
            subprocess.run([str(PY), str(BUILDER), technical], cwd=branches_done[branch], check=False)
            mod_dir = branches_done[branch] / technical
        else:
            mod_dir = ARMORA_ROOT / technical

        if not (mod_dir / 'static' / 'description' / 'index.html').exists():
            results.append((technical, 'FAIL', 'no index.html'))
            continue
        zp = zip_module(mod_dir)
        results.append((technical, 'OK', str(zp.name)))

    for wt in branches_done.values():
        subprocess.run(['git', 'worktree', 'remove', '--force', str(wt)], cwd=ARMORA_ROOT, check=False)
    shutil.rmtree(wt_root, ignore_errors=True)

    ok = sum(1 for _, status, _ in results if status == 'OK')
    print(f'DONE {ok}/{len(results)} zips in {ZIP_OUT}')
    for name, status, detail in results:
        print(f'{status:4} {name:30} {detail}')
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
