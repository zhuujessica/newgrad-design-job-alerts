#!/usr/bin/env python3
"""
Polls the "Creatives and Design" job feed behind newgrad-jobs.com (?k=cd),
which is backed by a public Airtable shared view, and sends an ntfy.sh push
notification when a new listing matches a company AND a role keyword from
config.py.

State (which listings have already been seen, tracked by a stable job
fingerprint -- see job_fingerprint() -- rather than Airtable's row id,
which can be reassigned when the underlying table is rebuilt) is kept in
state.json next to this script. On the very first run, all currently-listed
rows are recorded as "seen" without notifying, so you don't get flooded
with hundreds of alerts for pre-existing postings.
"""

import hashlib
import json
import os
import re
import secrets
import sys
import urllib.parse
import urllib.request
from pathlib import Path

import config

EMBED_URL = "https://airtable.com/embed/app7O2uKT9GTvMx9J/shrWEq2l15qeODGG3?viewControls=on"
VIEW_ID = "viwmu6qmHc7zxmSlB"
STATE_FILE = Path(__file__).parent / "state.json"
JOB_ID_RE = re.compile(r"/jobs/info/([a-f0-9]+)")

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36"
)


def fetch_embed_html() -> str:
    req = urllib.request.Request(EMBED_URL, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")


def extract_access_policy(html: str) -> str:
    match = re.search(r'"accessPolicy":"(\{.*?\})"', html)
    if not match:
        raise RuntimeError(
            "Could not find accessPolicy in Airtable embed page -- "
            "the site's markup may have changed."
        )
    # The captured text is a JSON-escaped string; wrap in quotes and decode
    # to get the real JSON string back.
    return json.loads('"' + match.group(1) + '"')


def fetch_rows() -> list[dict]:
    html = fetch_embed_html()
    access_policy = extract_access_policy(html)

    params = {
        "stringifiedObjectParams": json.dumps({"shouldUseNestedResponseFormat": True}),
        "requestId": "req" + secrets.token_hex(8),
        "accessPolicy": access_policy,
    }
    url = f"https://airtable.com/v0.3/view/{VIEW_ID}/readSharedViewData?" + urllib.parse.urlencode(params)

    headers = {
        "User-Agent": USER_AGENT,
        "x-airtable-inter-service-client": "webClient",
        "x-airtable-application-id": "app7O2uKT9GTvMx9J",
        "x-time-zone": "America/Chicago",
        "x-airtable-accept-msgpack": "false",
        "x-user-locale": "en",
        "x-requested-with": "XMLHttpRequest",
        "Accept": "application/json",
    }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json.loads(resp.read().decode("utf-8"))

    table = payload["data"]["table"]
    columns = {c["id"]: c for c in table["columns"]}
    name_to_col_id = {c["name"]: c["id"] for c in table["columns"]}

    def resolve_choice(col_id: str, value):
        if value is None:
            return None
        col = columns[col_id]
        choices = (col.get("typeOptions") or {}).get("choices") or {}
        if col["type"] == "select":
            choice = choices.get(value)
            return choice["name"] if choice else value
        if col["type"] == "multiSelect" and isinstance(value, list):
            return [choices[v]["name"] if v in choices else v for v in value]
        return value

    rows = []
    for row in table["rows"]:
        cells = row["cellValuesByColumnId"]

        def get(field_name):
            col_id = name_to_col_id.get(field_name)
            if col_id is None:
                return None
            return resolve_choice(col_id, cells.get(col_id))

        apply_field = get("Apply") or {}
        row_data = {
            "id": row["id"],
            "title": get("Position Title") or "",
            "date": get("Date") or "",
            "company": get("Company") or "",
            "location": (get("Location") or "").split("\n")[0][:80],
            "work_model": get("Work Model") or "",
            "apply_url": apply_field.get("url") if isinstance(apply_field, dict) else None,
        }
        row_data["fingerprint"] = job_fingerprint(row_data)
        rows.append(row_data)
    return rows


def job_fingerprint(row: dict) -> str:
    """A stable identity for a listing, independent of Airtable's row id.

    Sites like this often periodically rebuild their underlying Airtable
    rows, which reassigns row ids to postings that haven't actually
    changed. The apply link embeds the job board's own internal id
    (e.g. jobright.ai/jobs/info/<id>), which stays stable across those
    rebuilds, so we prefer that over the Airtable row id for dedup.
    """
    match = JOB_ID_RE.search(row.get("apply_url") or "")
    if match:
        return "job:" + match.group(1)
    basis = f"{row['title'].strip().lower()}|{row['company'].strip().lower()}|{row['location'].strip().lower()}"
    return "hash:" + hashlib.sha256(basis.encode()).hexdigest()[:16]


def matches(row: dict) -> bool:
    title = row["title"].lower()
    company = row["company"].lower()
    company_hit = any(c.lower() in company for c in config.COMPANIES)
    role_hit = any(r.lower() in title for r in config.ROLE_KEYWORDS)
    return company_hit and role_hit


def load_seen_ids() -> set[str]:
    if STATE_FILE.exists():
        return set(json.loads(STATE_FILE.read_text()).get("seen_ids", []))
    return set()


def save_seen_ids(seen_ids: set[str]) -> None:
    STATE_FILE.write_text(json.dumps({"seen_ids": sorted(seen_ids)}, indent=2))


def send_notification(row: dict) -> None:
    ntfy_topic = os.environ.get("NTFY_TOPIC", config.NTFY_TOPIC)
    message = f"{row['company']} — {row['work_model']}, {row['location']} • {row['date']}"
    url = f"https://ntfy.sh/{ntfy_topic}"
    req = urllib.request.Request(
        url,
        data=message.encode("utf-8"),
        method="POST",
        headers={
            "Title": row["title"][:200],
            "Tags": "art",
            **({"Click": row["apply_url"]} if row["apply_url"] else {}),
        },
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        resp.read()


def main() -> None:
    rows = fetch_rows()
    seen_ids = load_seen_ids()
    first_run = len(seen_ids) == 0

    new_matches = []
    for row in rows:
        if row["fingerprint"] in seen_ids:
            continue
        seen_ids.add(row["fingerprint"])
        if not first_run and matches(row):
            new_matches.append(row)

    save_seen_ids(seen_ids)

    if first_run:
        print(f"First run: recorded {len(rows)} existing listings as baseline, no notifications sent.")
        return

    for row in new_matches:
        send_notification(row)
        print(f"Notified: {row['title']} @ {row['company']}")

    print(f"Checked {len(rows)} listings, {len(new_matches)} new match(es).")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
