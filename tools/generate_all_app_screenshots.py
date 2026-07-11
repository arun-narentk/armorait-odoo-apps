#!/usr/bin/env python3
"""Generate Apps Store screenshot placeholders for all ARMORA modules."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from apps_store_screenshots import (
    generate_screenshots_for_repo,
    update_all_manifest_images,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Generate Apps Store screenshot placeholders for all modules.',
    )
    parser.add_argument(
        'repo_root',
        nargs='?',
        default=str(Path(__file__).resolve().parents[1]),
        help='Path to armora modules root (default: armora/)',
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Overwrite existing screenshot PNG files',
    )
    parser.add_argument(
        '--skip-manifests',
        action='store_true',
        help='Do not update __manifest__.py images lists',
    )
    args = parser.parse_args()
    repo_root = Path(args.repo_root).resolve()
    if not repo_root.is_dir():
        raise SystemExit(f'Repo not found: {repo_root}')

    if not args.skip_manifests:
        manifest_updates = update_all_manifest_images(repo_root)
        print(f'Updated images in {len(manifest_updates)} manifests')

    generated = generate_screenshots_for_repo(repo_root, force=args.force)
    print(f'Generated screenshots for {len(generated)} modules in {repo_root}')
    for name, files in generated.items():
        print(f'  {name}: {", ".join(files)}')


if __name__ == '__main__':
    main()
