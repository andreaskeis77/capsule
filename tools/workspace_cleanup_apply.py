from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[1]
OPS_ROOT = REPO_ROOT / 'docs' / '_ops' / 'workspace_cleanup'
ARCHIVE_ROOT = REPO_ROOT / 'docs' / '_archive' / 'workspace_cleanup'
DEFAULT_INVENTORY_ROOT = REPO_ROOT / 'docs' / '_ops' / 'workspace_inventory'

ROOT_ARCHIVE_PATTERNS = {
    'APPLY_TRANCHE_',
    'APPLY_WORKSPACE_INVENTORY',
    'README_CapsuleKnowledgeRefresh',
    'Run-CapsuleKnowledgeRefresh',
    'Test-CapsuleKnowledgeRefresh',
    'capsule.ps1',
    'requirements-dev.txt',
}
ROOT_DELETE_NAMES = {'.env.bak'}
DELETE_DIRS = {'_release_staging'}
ARCHIVE_DIRS = {'docs/_metrics'}
DELETE_LOG_FILES = {'logs/wardrobe.log', 'logs/server_startup.log'}
ROOT_REVIEW_NOW_KEEP = {'pyproject.toml', 'MANIFEST.in', 'capsule.cmd'}
DELETE_IF_EXISTS = {'capsule_server_seed.zip'}
KEEP_PREFIXES = {
    '.git', '.github', '.venv', '.venv_broken_20260215', '.vscode', '01_raw_input', '02_wardrobe_images', '03_database', '04_user_data',
    'docs/_ops', 'docs/_snapshot', 'src', 'tests', 'tools', 'ontology', 'templates', 'logs/.gitkeep'
}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def ts(dt: datetime | None = None) -> str:
    return (dt or utc_now()).strftime('%Y%m%d-%H%M%S')


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


@dataclass
class Candidate:
    relative_path: str
    kind: str
    top_scope: str
    git_state: str
    size_bytes: int
    mtime_utc: str
    suggested_action: str
    reason: str
    suffix: str

    @property
    def path(self) -> Path:
        return REPO_ROOT / self.relative_path


@dataclass
class PlannedAction:
    relative_path: str
    path_type: str
    action: str
    reason: str
    target_relative_path: str = ''
    size_bytes: int = 0
    exists: bool = False


def latest_inventory_dir(inventory_root: Path) -> Path:
    runs = sorted([p for p in inventory_root.glob('run_*') if p.is_dir()])
    if not runs:
        raise FileNotFoundError(f'No inventory run found under {inventory_root}')
    return runs[-1]


def load_candidates(csv_path: Path) -> list[Candidate]:
    rows: list[Candidate] = []
    with csv_path.open('r', encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(Candidate(
                relative_path=row['relative_path'].replace('\\', '/'),
                kind=row['kind'],
                top_scope=row['top_scope'],
                git_state=row['git_state'],
                size_bytes=int(row.get('size_bytes') or 0),
                mtime_utc=row.get('mtime_utc', ''),
                suggested_action=row.get('suggested_action', ''),
                reason=row.get('reason', ''),
                suffix=row.get('suffix', ''),
            ))
    return rows


def is_keep_prefix(rel: str) -> bool:
    return any(rel == p or rel.startswith(p + '/') for p in KEEP_PREFIXES)


def classify(candidate: Candidate, archive_stamp: str) -> PlannedAction | None:
    rel = candidate.relative_path
    name = Path(rel).name
    if is_keep_prefix(rel):
        return None
    if rel in ROOT_REVIEW_NOW_KEEP:
        return None
    if rel in ROOT_DELETE_NAMES:
        return PlannedAction(rel, candidate.kind, 'delete', 'backup env file', size_bytes=candidate.size_bytes, exists=candidate.path.exists())
    if rel in DELETE_IF_EXISTS:
        return PlannedAction(rel, candidate.kind, 'delete', 'large root export zip', size_bytes=candidate.size_bytes, exists=candidate.path.exists())
    if rel in DELETE_LOG_FILES:
        return PlannedAction(rel, candidate.kind, 'delete', 'replaceable runtime log', size_bytes=candidate.size_bytes, exists=candidate.path.exists())
    if any(rel == d or rel.startswith(d + '/') for d in DELETE_DIRS):
        # only delete at top directory action level
        if rel in DELETE_DIRS:
            return PlannedAction(rel, candidate.kind, 'delete', 'staging/export workspace', size_bytes=candidate.size_bytes, exists=candidate.path.exists())
        return None
    if any(rel == d or rel.startswith(d + '/') for d in ARCHIVE_DIRS):
        if rel in ARCHIVE_DIRS:
            target = f"docs/_archive/workspace_cleanup/{archive_stamp}/docs_metrics"
            return PlannedAction(rel, candidate.kind, 'archive_move', 'generated metrics output', target_relative_path=target, size_bytes=candidate.size_bytes, exists=candidate.path.exists())
        return None
    if candidate.kind == 'file' and candidate.git_state == 'untracked':
        stem = Path(rel).stem
        if any(stem.startswith(p) or name.startswith(p) for p in ROOT_ARCHIVE_PATTERNS):
            target = f"docs/_archive/workspace_cleanup/{archive_stamp}/root_notes/{name}"
            return PlannedAction(rel, candidate.kind, 'archive_move', 'root work note/script', target_relative_path=target, size_bytes=candidate.size_bytes, exists=candidate.path.exists())
    return None


def unique_actions(actions: Iterable[PlannedAction]) -> list[PlannedAction]:
    seen = set()
    out = []
    for a in actions:
        key = (a.relative_path, a.action, a.target_relative_path)
        if key not in seen:
            seen.add(key)
            out.append(a)
    return out


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def write_csv(path: Path, actions: list[PlannedAction]) -> None:
    ensure_parent(path)
    with path.open('w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['relative_path', 'path_type', 'action', 'reason', 'target_relative_path', 'size_bytes', 'exists'])
        for a in actions:
            writer.writerow([a.relative_path, a.path_type, a.action, a.reason, a.target_relative_path, a.size_bytes, 'yes' if a.exists else 'no'])


def apply_actions(actions: list[PlannedAction], dry_run: bool) -> dict:
    results = []
    for a in actions:
        src = REPO_ROOT / a.relative_path
        record = {
            'relative_path': a.relative_path,
            'action': a.action,
            'reason': a.reason,
            'target_relative_path': a.target_relative_path,
            'exists_before': src.exists(),
            'status': 'planned' if dry_run else 'skipped',
            'bytes_before': a.size_bytes,
        }
        try:
            if not src.exists():
                record['status'] = 'missing'
            elif dry_run:
                record['status'] = 'planned'
            elif a.action == 'delete':
                if src.is_dir():
                    shutil.rmtree(src)
                else:
                    src.unlink()
                record['status'] = 'deleted'
            elif a.action == 'archive_move':
                dst = REPO_ROOT / a.target_relative_path
                ensure_parent(dst)
                if dst.exists():
                    raise FileExistsError(f'target exists: {dst}')
                shutil.move(str(src), str(dst))
                record['status'] = 'moved'
            else:
                record['status'] = 'unsupported'
        except Exception as exc:
            record['status'] = 'error'
            record['error'] = f'{type(exc).__name__}: {exc}'
        results.append(record)
    return {'results': results}


def summarize(actions: list[PlannedAction], execution: dict, inventory_dir: Path, mode: str) -> str:
    ctr = Counter(a.action for a in actions)
    by_scope = Counter(a.relative_path.split('/')[0] for a in actions)
    total_bytes = sum(a.size_bytes for a in actions)
    exec_ctr = Counter(r['status'] for r in execution['results'])
    lines = [
        '# Workspace Cleanup Plan',
        '',
        f'- generated_utc: {utc_now().isoformat()}',
        f'- repo_root: `{REPO_ROOT}`',
        f'- source_inventory: `{inventory_dir}`',
        f'- mode: `{mode}`',
        '',
        '## Plan Summary',
        '',
        f'- planned_items: {len(actions)}',
        f'- planned_bytes: {total_bytes} ({total_bytes / 1024 / 1024:.2f} MB)',
        f'- planned_archive_moves: {ctr.get("archive_move", 0)}',
        f'- planned_deletes: {ctr.get("delete", 0)}',
        '',
        '## Scope Breakdown',
        '',
        '| scope | count |',
        '| --- | ---: |',
    ]
    for scope, count in by_scope.most_common():
        lines.append(f'| {scope} | {count} |')
    lines += [
        '',
        '## Execution Status',
        '',
        '| status | count |',
        '| --- | ---: |',
    ]
    for status, count in exec_ctr.items():
        lines.append(f'| {status} | {count} |')
    lines += [
        '',
        '## Selected Actions',
        '',
        '| relative_path | action | target | reason |',
        '| --- | --- | --- | --- |',
    ]
    for a in actions[:200]:
        lines.append(f'| `{a.relative_path}` | {a.action} | `{a.target_relative_path}` | {a.reason} |')
    return '\n'.join(lines) + '\n'


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description='Conservative workspace cleanup based on inventory output.')
    p.add_argument('--inventory-run', default='', help='Specific inventory run directory name under docs/_ops/workspace_inventory.')
    p.add_argument('--apply', action='store_true', help='Apply moves/deletes. Default is dry-run only.')
    return p.parse_args()


def main() -> int:
    args = parse_args()
    inventory_dir = DEFAULT_INVENTORY_ROOT / args.inventory_run if args.inventory_run else latest_inventory_dir(DEFAULT_INVENTORY_ROOT)
    candidates_csv = inventory_dir / 'cleanup_candidates.csv'
    if not candidates_csv.exists():
        raise FileNotFoundError(f'Missing cleanup_candidates.csv in {inventory_dir}')

    archive_stamp = ts()
    run_dir = OPS_ROOT / f'run_{archive_stamp}'
    run_dir.mkdir(parents=True, exist_ok=True)

    candidates = load_candidates(candidates_csv)
    actions = unique_actions(a for c in candidates if (a := classify(c, archive_stamp)))

    # Protect tracked files from move/delete except explicit ignored/log/temp cases above.
    protected = []
    filtered = []
    for a in actions:
        if a.relative_path.endswith('.md') and a.relative_path.startswith('docs/'):
            protected.append(a)
            continue
        filtered.append(a)
    actions = filtered

    write_csv(run_dir / 'cleanup_plan.csv', actions)
    execution = apply_actions(actions, dry_run=not args.apply)
    with (run_dir / 'cleanup_execution.json').open('w', encoding='utf-8') as f:
        json.dump(execution, f, indent=2, ensure_ascii=False)
    with (run_dir / 'cleanup_summary.md').open('w', encoding='utf-8') as f:
        f.write(summarize(actions, execution, inventory_dir, mode='apply' if args.apply else 'dry-run'))
    with (run_dir / 'protected_items.json').open('w', encoding='utf-8') as f:
        json.dump([a.__dict__ for a in protected], f, indent=2, ensure_ascii=False)

    print(f"[OK] workspace cleanup {'applied' if args.apply else 'planned'}: {run_dir}")
    print('[ARTIFACTS]')
    print('- cleanup_summary.md')
    print('- cleanup_plan.csv')
    print('- cleanup_execution.json')
    print('- protected_items.json')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
