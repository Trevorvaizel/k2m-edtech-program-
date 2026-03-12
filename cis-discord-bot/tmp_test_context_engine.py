"""
Quick live smoke test for the Task 6.2 context engine webhooks.
Run from cis-discord-bot/ with CONTEXT_ENGINE_WEBHOOK_URL and CONTEXT_ENGINE_WEBHOOK_TOKEN set.

Usage:
    python tmp_test_context_engine.py
"""
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

# Load .env
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, val = line.partition("=")
            os.environ.setdefault(key.strip(), val.strip())

URL = os.getenv("CONTEXT_ENGINE_WEBHOOK_URL", "").strip()
TOKEN = os.getenv("CONTEXT_ENGINE_WEBHOOK_TOKEN", "").strip()

if not URL:
    print("ERROR: CONTEXT_ENGINE_WEBHOOK_URL not set in .env")
    sys.exit(1)
if not TOKEN:
    print("ERROR: CONTEXT_ENGINE_WEBHOOK_TOKEN not set in .env")
    print("  -> Copy the CONTEXT_WEBHOOK_TOKEN value from Apps Script Script Properties into .env")
    sys.exit(1)

def post(action, extra=None):
    body = {"action": action, "token": TOKEN}
    if extra:
        body.update(extra)
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(URL, data=data, method="POST",
                                  headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return {"success": False, "error": f"HTTP {e.code}: {e.read().decode()}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

print(f"Testing context engine at: {URL[:60]}...")
print()

# 1. Seed content (idempotent)
print("1) seedContextLibraryContent ...")
r = post("seedContextLibraryContent")
print(f"   {r}")
print()

# 2. Fetch examples for teacher, week 1
print("2) getExamplesByProfession(teacher, week=1) ...")
r = post("getExamplesByProfession", {"profession": "teacher", "week": 1})
if r.get("success"):
    print(f"   OK — {r.get('count',0)} examples returned")
    for ex in (r.get("examples") or [])[:2]:
        print(f"   - {ex.get('example_text','')[:80]}...")
else:
    print(f"   FAIL: {r}")
print()

# 3. Fetch examples for gap_year_student, week 3
print("3) getExamplesByProfession(gap_year_student, week=3) ...")
r = post("getExamplesByProfession", {"profession": "gap_year_student", "week": 3})
if r.get("success"):
    print(f"   OK — {r.get('count',0)} examples returned")
    for ex in (r.get("examples") or [])[:1]:
        print(f"   - {ex.get('example_text','')[:80]}...")
else:
    print(f"   FAIL: {r}")
print()

# 4. Fetch examples for 'other' (should fallback to working_professional)
print("4) getExamplesByProfession(other, week=2) — expects working_professional fallback ...")
r = post("getExamplesByProfession", {"profession": "other", "week": 2})
if r.get("success") and r.get("count", 0) > 0:
    print(f"   OK — {r.get('count',0)} examples returned (working_professional fallback confirmed)")
else:
    print(f"   FAIL or 0 results: {r}")
print()

# 5. Fetch intervention
print("5) getIntervention(identity, week=2) ...")
r = post("getIntervention", {"barrier_type": "identity", "week": 2})
if r.get("success") and r.get("intervention"):
    print(f"   OK — intervention text: {str(r['intervention'].get('intervention_text',''))[:80]}...")
else:
    print(f"   FAIL or null: {r}")
print()

print("Done.")
