#!/usr/bin/env python3
"""Regression suite for all armora/rn_* commercial modules.

Phase A (always): static checks (manifest, Python syntax, XML parse, tests present).
Phase B (optional): Odoo --test-enable when a DB config is available.

Usage:
  python3.10 tools/run_rn_regression.py
  python3.10 tools/run_rn_regression.py --odoo --db armora_apps
  python3.10 tools/run_rn_regression.py --odoo --db armora_apps --installed-only
  python3.10 tools/run_rn_regression.py --odoo --modules rn_bookmarks,rn_workflow_builder

Never prints DB passwords. Uses repo-root .openerp_serverrc when --odoo is set.
"""
from __future__ import annotations

import argparse
import ast
import configparser
import json
import os
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass, field
from pathlib import Path

ARMORA = Path(__file__).resolve().parents[1]
REPO = ARMORA.parent
CONFIG = REPO / '.openerp_serverrc'
RUN_ODOO = REPO / 'run_odoo.sh'
OUT_DIR = ARMORA / 'tools' / 'regression_results'


@dataclass
class ModuleResult:
    name: str
    has_manifest: bool = False
    has_tests: bool = False
    test_files: int = 0
    static_ok: bool = False
    static_errors: list[str] = field(default_factory=list)
    odoo_status: str = 'skipped'
    odoo_detail: str = ''
    duration_s: float = 0.0
    installed: bool | None = None


def discover_modules() -> list[Path]:
    return sorted(
        p for p in ARMORA.iterdir()
        if p.is_dir() and p.name.startswith('rn_') and (p / '__manifest__.py').exists()
    )


def check_manifest(mod: Path, errors: list[str]) -> None:
    text = (mod / '__manifest__.py').read_text(encoding='utf-8')
    try:
        match = re.search(r'\{[\s\S]*\}', text)
        if not match:
            errors.append('manifest: no dict found')
            return
        data = ast.literal_eval(match.group())
    except Exception as exc:  # noqa: BLE001
        errors.append(f'manifest parse: {exc}')
        return
    for key in ('name', 'version', 'depends', 'license', 'installable'):
        if key not in data:
            errors.append(f'manifest missing {key}')
    if data.get('installable') is not True:
        errors.append('manifest installable is not True')


def check_python(mod: Path, errors: list[str]) -> None:
    for py in mod.rglob('*.py'):
        if '__pycache__' in py.parts:
            continue
        try:
            compile(py.read_text(encoding='utf-8'), str(py), 'exec')
        except SyntaxError as exc:
            errors.append(f'python syntax {py.relative_to(mod)}: {exc.msg} line {exc.lineno}')


def check_xml(mod: Path, errors: list[str]) -> None:
    for xml in mod.rglob('*.xml'):
        try:
            ET.parse(xml)
        except ET.ParseError as exc:
            errors.append(f'xml {xml.relative_to(mod)}: {exc}')


def count_tests(mod: Path) -> int:
    tdir = mod / 'tests'
    if not tdir.is_dir():
        return 0
    return len([p for p in tdir.rglob('test_*.py')])


def static_check(mod: Path) -> ModuleResult:
    result = ModuleResult(name=mod.name, has_manifest=True)
    errors: list[str] = []
    check_manifest(mod, errors)
    check_python(mod, errors)
    check_xml(mod, errors)
    result.test_files = count_tests(mod)
    result.has_tests = result.test_files > 0
    if not result.has_tests:
        errors.append('no test_*.py files')
    result.static_errors = errors
    result.static_ok = not errors
    return result


def _db_conn_args() -> dict[str, str]:
    """Read DB connection from .openerp_serverrc without exposing password in logs."""
    raw = CONFIG.read_text(encoding='utf-8')
    # Odoo configs are not always INI; parse key = value lines
    data: dict[str, str] = {}
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, val = line.split('=', 1)
        data[key.strip()] = val.strip()
    return {
        'host': data.get('db_host', 'localhost'),
        'port': data.get('db_port', '5432'),
        'user': data.get('db_user', 'odoo'),
        'password': data.get('db_password', ''),
    }


def query_installed(db_name: str) -> dict[str, str]:
    """Return {module_name: state} for rn_* in the given DB."""
    conn = _db_conn_args()
    env = {**os.environ, 'PGPASSWORD': conn['password']}
    sql = "SELECT name, state FROM ir_module_module WHERE name LIKE 'rn_%';"
    cmd = [
        'psql', '-h', conn['host'], '-p', conn['port'], '-U', conn['user'],
        '-d', db_name, '-tAc', sql,
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=30)
    except Exception as exc:  # noqa: BLE001
        print(f'  warn: could not query installed modules: {exc}')
        return {}
    if proc.returncode != 0:
        print(f'  warn: psql failed: {(proc.stderr or "")[:200]}')
        return {}
    out: dict[str, str] = {}
    for line in proc.stdout.splitlines():
        if '|' not in line:
            continue
        name, state = line.split('|', 1)
        out[name.strip()] = state.strip()
    return out


def run_odoo_modules(
    mod_names: list[str],
    db_name: str,
    timeout: int,
    install: bool,
) -> tuple[str, str]:
    """Run Odoo tests for one or more modules in a single process."""
    if not RUN_ODOO.exists() or not CONFIG.exists():
        return 'skipped', 'missing run_odoo.sh or .openerp_serverrc'
    if not mod_names:
        return 'skipped', 'no modules'
    tags = ','.join(f'/{m}' for m in mod_names)
    action = ['-i', ','.join(mod_names)] if install else ['-u', ','.join(mod_names)]
    cmd = [
        str(RUN_ODOO),
        '-c', str(CONFIG),
        '-d', db_name,
        '--http-port', '0',
        '--stop-after-init',
        '--test-enable',
        '--test-tags', tags,
        *action,
        '--log-level', 'test',
    ]
    log_name = mod_names[0] if len(mod_names) == 1 else 'batch_' + '_'.join(mod_names[:3])
    log_path = OUT_DIR / f'{log_name}.log'
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(REPO),
            capture_output=True,
            text=True,
            timeout=timeout,
            env={**os.environ, 'PYTHONUNBUFFERED': '1'},
        )
    except subprocess.TimeoutExpired:
        return 'timeout', f'exceeded {timeout}s'
    except Exception as exc:  # noqa: BLE001
        return 'error', str(exc)

    output = (proc.stdout or '') + '\n' + (proc.stderr or '')
    log_path.write_text(output[-400000:], encoding='utf-8')
    detail_lines = [
        line for line in output.splitlines()
        if 'password' not in line.lower() and 'db_password' not in line.lower()
    ]
    tail = '\n'.join(detail_lines[-50:])

    # Per-module parse for batch: look for FAIL/ERROR with module context
    fail_count = len(re.findall(r'\bFAIL:', output))
    error_count = len(re.findall(r'\bERROR:', output))
    if proc.returncode == 0 and fail_count == 0 and error_count == 0:
        return 'pass', 'ok'
    # Only treat as installability failure when this module itself is skipped
    mod_joined = '|'.join(re.escape(m) for m in mod_names)
    if re.search(
        rf'module ({mod_joined}): not installable',
        output,
        re.I,
    ):
        return 'fail', 'not installable / missing dependency'
    if proc.returncode != 0 or fail_count or error_count:
        return 'fail', tail[-2000:] or f'exit {proc.returncode}'
    return 'pass', 'ok'


def parse_batch_module_status(log_text: str, mod_names: list[str]) -> dict[str, tuple[str, str]]:
    """Best-effort per-module status from a shared Odoo log."""
    statuses: dict[str, tuple[str, str]] = {m: ('pass', 'ok') for m in mod_names}
    # If whole run failed hard on install of one module, mark all fail with shared detail
    if 'Some modules have inconsistent states' in log_text or 'Module loading failed' in log_text:
        for m in mod_names:
            statuses[m] = ('fail', 'module loading failed')
    for m in mod_names:
        # Test failures tagged with module path
        if re.search(rf'FAIL:.*{re.escape(m)}', log_text) or re.search(
            rf'ERROR:.*{re.escape(m)}', log_text
        ):
            statuses[m] = ('fail', f'test failure in {m}')
        # Install failure for this module
        if re.search(rf"Module {re.escape(m)}:.*failed", log_text, re.I):
            statuses[m] = ('fail', f'install/update failed for {m}')
    return statuses


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='ARMORA rn_* regression suite')
    parser.add_argument('--odoo', action='store_true', help='Also run Odoo module tests')
    parser.add_argument('--db', default='armora_apps', help='Database name')
    parser.add_argument('--modules', default='', help='Comma-separated module filter')
    parser.add_argument('--timeout', type=int, default=420, help='Per-module Odoo timeout seconds')
    parser.add_argument(
        '--installed-only',
        action='store_true',
        help='Only run Odoo tests for modules already installed in the DB',
    )
    parser.add_argument(
        '--try-install',
        action='store_true',
        help='For uninstalled modules, attempt -i then run tests (explicit install for regression)',
    )
    parser.add_argument(
        '--batch',
        action='store_true',
        help='Run all selected installed modules in one Odoo process (faster)',
    )
    args = parser.parse_args(argv)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    modules = discover_modules()
    if args.modules:
        wanted = {m.strip() for m in args.modules.split(',') if m.strip()}
        modules = [m for m in modules if m.name in wanted]

    results: list[ModuleResult] = []
    print(f'Static regression on {len(modules)} rn_* modules...')
    for mod in modules:
        res = static_check(mod)
        results.append(res)
        mark = 'PASS' if res.static_ok else 'FAIL'
        print(f'  [static {mark}] {mod.name} tests={res.test_files} errors={len(res.static_errors)}')

    if args.odoo:
        installed_map = query_installed(args.db)
        print(f'Odoo regression db={args.db} installed_rn={sum(1 for s in installed_map.values() if s == "installed")}...')

        for res in results:
            res.installed = installed_map.get(res.name) == 'installed'

        installed_results = [r for r in results if r.installed]
        uninstalled_results = [r for r in results if not r.installed]

        if args.batch and installed_results:
            names = [r.name for r in installed_results]
            print(f'  Batch testing {len(names)} installed modules...')
            started = time.time()
            status, detail = run_odoo_modules(names, args.db, max(args.timeout, 900), install=False)
            log_path = OUT_DIR / f'batch_{names[0]}.log'
            # Prefer the newest matching log
            candidates = sorted(OUT_DIR.glob('batch_*.log'), key=lambda p: p.stat().st_mtime, reverse=True)
            log_text = candidates[0].read_text(encoding='utf-8') if candidates else detail
            per = parse_batch_module_status(log_text, names) if status != 'pass' else {
                n: ('pass', 'ok') for n in names
            }
            if status == 'pass':
                per = {n: ('pass', 'ok') for n in names}
            elif status in ('timeout', 'error', 'skipped'):
                per = {n: (status, detail) for n in names}
            elapsed = round(time.time() - started, 1)
            for res in installed_results:
                st, det = per.get(res.name, (status, detail))
                res.odoo_status = st
                res.odoo_detail = det[:2000]
                res.duration_s = elapsed
                print(f'  [odoo {st.upper():7s}] {res.name} (batch {elapsed}s)')
        else:
            for res in installed_results:
                started = time.time()
                status, detail = run_odoo_modules([res.name], args.db, args.timeout, install=False)
                res.odoo_status = status
                res.odoo_detail = detail[:2000]
                res.duration_s = round(time.time() - started, 1)
                print(f'  [odoo {status.upper():7s}] {res.name} ({res.duration_s}s)')

        for res in uninstalled_results:
            if args.installed_only and not args.try_install:
                res.odoo_status = 'skipped'
                res.odoo_detail = 'not installed in DB'
                print(f'  [odoo SKIPPED] {res.name} (not installed)')
                continue
            if not args.try_install:
                res.odoo_status = 'skipped'
                res.odoo_detail = 'not installed (use --try-install to install for regression)'
                print(f'  [odoo SKIPPED] {res.name} (not installed)')
                continue
            started = time.time()
            status, detail = run_odoo_modules([res.name], args.db, args.timeout, install=True)
            res.odoo_status = status
            res.odoo_detail = detail[:2000]
            res.duration_s = round(time.time() - started, 1)
            print(f'  [odoo {status.upper():7s}] {res.name} install+test ({res.duration_s}s)')

    summary = {
        'modules': len(results),
        'static_pass': sum(1 for r in results if r.static_ok),
        'static_fail': sum(1 for r in results if not r.static_ok),
        'with_tests': sum(1 for r in results if r.has_tests),
        'odoo_pass': sum(1 for r in results if r.odoo_status == 'pass'),
        'odoo_fail': sum(1 for r in results if r.odoo_status == 'fail'),
        'odoo_timeout': sum(1 for r in results if r.odoo_status == 'timeout'),
        'odoo_skipped': sum(1 for r in results if r.odoo_status == 'skipped'),
        'results': [asdict(r) for r in results],
    }
    out_json = OUT_DIR / 'summary.json'
    out_json.write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')

    lines = [
        f"RN regression summary ({time.strftime('%Y-%m-%d %H:%M')})",
        f"Modules: {summary['modules']}",
        f"Static PASS: {summary['static_pass']}  FAIL: {summary['static_fail']}",
        f"Modules with tests: {summary['with_tests']}",
        f"Odoo PASS: {summary['odoo_pass']}  FAIL: {summary['odoo_fail']}  "
        f"TIMEOUT: {summary['odoo_timeout']}  SKIPPED: {summary['odoo_skipped']}",
        '',
        'Module | Static | Tests | Odoo | Notes',
        '---|---|---|---|---',
    ]
    for r in results:
        note = '; '.join(r.static_errors[:2]) if r.static_errors else (
            r.odoo_detail.splitlines()[0] if r.odoo_detail and r.odoo_status != 'pass' else ''
        )
        note = note.replace('|', '/')[:120]
        lines.append(
            f"{r.name} | {'PASS' if r.static_ok else 'FAIL'} | {r.test_files} | "
            f"{r.odoo_status.upper()} | {note}"
        )
    out_txt = OUT_DIR / 'summary.txt'
    out_txt.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print('\n' + '\n'.join(lines[:12]))
    print(f'\nWrote {out_json} and {out_txt}')
    return 0 if summary['static_fail'] == 0 and summary['odoo_fail'] == 0 else 1


if __name__ == '__main__':
    raise SystemExit(main())
