#!/usr/bin/env python3
"""
Project Sanity Check
- checks python + venv presence (best-effort)
- checks .env can be loaded (expects WARDROBE_API_KEY to exist OR warns)
- hits local endpoints: /healthz and /api/v2/health
- hits selection mode URL (ids)
- optional: checks admin route returns 200 only on localhost (informational)

Exit codes:
0 = all required checks ok
2 = one or more required checks failed
"""

from __future__ import annotations

import argparse
import os
import sys
import urllib.request
import urllib.error
from typing import Tuple


def http_get(url: str, timeout: int = 10) -> Tuple[int, str]:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return resp.status, body[:5000]
    except urllib.error.HTTPError as e:
        return int(e.code), e.read().decode("utf-8", errors="replace")[:5000]
    except Exception as e:
        return 0, str(e)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:5002", help="Base URL for local server")
    ap.add_argument("--user", default="karen", help="User to test")
    ap.add_argument("--ids", default="112,101,110", help="Selection IDs to test")
    args = ap.parse_args()

    base = args.base.rstrip("/")
    user = args.user

    fails = []

    # Basic python info
    print(f"[INFO] python={sys.version.split()[0]}")
    print(f"[INFO] executable={sys.executable}")

    # Environment
    key_present = bool(os.getenv("WARDROBE_API_KEY"))
    print(f"[INFO] env WARDROBE_API_KEY present={key_present}")
    # Not a hard fail because some runs may not require admin, but warn:
    if not key_present:
        print("[WARN] WARDROBE_API_KEY not set in current environment. Admin save/delete will fail unless .env is loaded by server process.")

    # Required endpoints
    for path in ["/healthz", "/api/v2/health"]:
        url = f"{base}{path}"
        code, body = http_get(url)
        ok = (code == 200)
        print(f"[CHECK] GET {url} -> {code} {'OK' if ok else 'FAIL'}")
        if not ok:
            fails.append(f"{path} returned {code}: {body[:200]}")

    # Selection URL
    sel_url = f"{base}/?user={user}&ids={args.ids}"
    code, _ = http_get(sel_url)
    ok = (code == 200)
    print(f"[CHECK] GET {sel_url} -> {code} {'OK' if ok else 'FAIL'}")
    if not ok:
        fails.append(f"selection returned {code}")

    # Admin (informational): should be 200 if local, else likely 403
    admin_url = f"{base}/?user={user}&mode=admin"
    code, _ = http_get(admin_url)
    print(f"[INFO] GET {admin_url} -> {code} (expected 200 locally; 403 remotely)")

    if fails:
        print("\n[FAILURES]")
        for f in fails:
            print(" - " + f)
        return 2

    print("\n[OK] All required sanity checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())