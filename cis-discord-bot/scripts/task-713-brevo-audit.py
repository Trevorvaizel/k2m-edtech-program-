#!/usr/bin/env python3
"""
Task 7.13 Brevo audit and evidence helper.

Default mode is read-only. Use mutation flags only when you intend to change Brevo state:
  --ensure-domain : create domain in Brevo if missing
  --ensure-sender : create sender in Brevo if missing
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx


DEFAULT_BASE_URL = "https://api.brevo.com/v3"
DEFAULT_DOMAIN = "k2mlabs.com"
DEFAULT_SENDER_EMAIL = "trevor@k2mlabs.com"
DEFAULT_SENDER_NAME = "Trevor from K2M"
DEFAULT_TEST_TO = "k2m.labs@gmail.com"


def _utc_now_iso() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _load_env_file(path: Optional[str]) -> None:
    if not path:
        return
    env_path = Path(path)
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if key and key not in os.environ:
            os.environ[key] = value


class BrevoClient:
    def __init__(self, api_key: str, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")
        self._client = httpx.Client(
            headers={
                "api-key": api_key,
                "accept": "application/json",
                "content-type": "application/json",
            },
            timeout=30.0,
        )

    def close(self) -> None:
        self._client.close()

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> httpx.Response:
        return self._client.get(f"{self.base_url}{path}", params=params)

    def post(self, path: str, payload: Dict[str, Any]) -> httpx.Response:
        return self._client.post(f"{self.base_url}{path}", json=payload)


def _safe_json(response: httpx.Response) -> Dict[str, Any]:
    try:
        payload = response.json()
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {"_raw": payload}


def _find_sender(senders: List[Dict[str, Any]], sender_email: str) -> Optional[Dict[str, Any]]:
    sender_email_lc = sender_email.strip().lower()
    for sender in senders:
        if str(sender.get("email", "")).strip().lower() == sender_email_lc:
            return sender
    return None


def _collect_dns_gaps(dns_records: Dict[str, Any]) -> List[str]:
    gaps: List[str] = []
    for key, value in dns_records.items():
        if not isinstance(value, dict):
            continue
        status = bool(value.get("status"))
        if not status:
            host_name = value.get("host_name") or value.get("host") or "@"
            rec_type = value.get("type") or "TXT/CNAME"
            gaps.append(f"{key} not verified ({rec_type} {host_name})")
    return gaps


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Task 7.13 Brevo audit helper")
    parser.add_argument("--env-file", default="cis-discord-bot/.env")
    parser.add_argument("--base-url", default=os.getenv("BREVO_BASE_URL", DEFAULT_BASE_URL))
    parser.add_argument("--domain", default=DEFAULT_DOMAIN)
    parser.add_argument("--sender-email", default=DEFAULT_SENDER_EMAIL)
    parser.add_argument("--sender-name", default=DEFAULT_SENDER_NAME)
    parser.add_argument("--ensure-domain", action="store_true")
    parser.add_argument("--ensure-sender", action="store_true")
    parser.add_argument("--send-test", action="store_true")
    parser.add_argument("--test-to", default=DEFAULT_TEST_TO)
    parser.add_argument("--wait-seconds", type=int, default=5)
    parser.add_argument("--output", default="")
    return parser


def main() -> int:
    args = build_arg_parser().parse_args()
    _load_env_file(args.env_file)

    api_key = os.getenv("BREVO_API_KEY", "").strip()
    if not api_key:
        print("ERROR: BREVO_API_KEY is not set (env or env-file).")
        return 2

    report: Dict[str, Any] = {
        "task": "7.13",
        "timestamp_utc": _utc_now_iso(),
        "base_url": args.base_url.rstrip("/"),
        "domain": args.domain,
        "sender_email": args.sender_email,
        "sender_name": args.sender_name,
        "test_to": args.test_to if args.send_test else None,
        "actions": {
            "ensure_domain": bool(args.ensure_domain),
            "ensure_sender": bool(args.ensure_sender),
            "send_test": bool(args.send_test),
        },
        "checks": {},
        "blockers": [],
        "next_actions": [],
    }

    client = BrevoClient(api_key=api_key, base_url=args.base_url)
    try:
        # Account visibility
        account_resp = client.get("/account")
        account_payload = _safe_json(account_resp)
        report["checks"]["account"] = {
            "status_code": account_resp.status_code,
            "email": account_payload.get("email"),
            "companyName": account_payload.get("companyName"),
        }

        # Domain list
        domains_resp = client.get("/senders/domains")
        domains_payload = _safe_json(domains_resp)
        domains = domains_payload.get("domains") or []
        domain_names = [str(d.get("domain_name", "")).strip().lower() for d in domains]
        domain_exists = args.domain.strip().lower() in domain_names

        created_domain_payload: Optional[Dict[str, Any]] = None
        if (not domain_exists) and args.ensure_domain:
            create_domain_resp = client.post("/senders/domains", {"name": args.domain})
            created_domain_payload = _safe_json(create_domain_resp)
            domain_exists = create_domain_resp.status_code in (200, 201)
            report["checks"]["create_domain"] = {
                "status_code": create_domain_resp.status_code,
                "message": created_domain_payload.get("message"),
            }

        domain_detail: Dict[str, Any] = {}
        if domain_exists:
            domain_resp = client.get(f"/senders/domains/{args.domain}")
            domain_detail = _safe_json(domain_resp)
            report["checks"]["domain_detail"] = {
                "status_code": domain_resp.status_code,
                "verified": bool(domain_detail.get("verified")),
                "authenticated": bool(domain_detail.get("authenticated")),
                "dns_records": domain_detail.get("dns_records"),
            }
        else:
            report["checks"]["domain_detail"] = {
                "status_code": None,
                "verified": False,
                "authenticated": False,
                "dns_records": None,
            }
            if created_domain_payload:
                report["checks"]["domain_create_response"] = created_domain_payload

        # Senders
        senders_resp = client.get("/senders")
        senders_payload = _safe_json(senders_resp)
        senders = senders_payload.get("senders") or []
        sender = _find_sender(senders, args.sender_email)

        if (sender is None) and args.ensure_sender:
            create_sender_resp = client.post(
                "/senders",
                {"name": args.sender_name, "email": args.sender_email},
            )
            created_sender_payload = _safe_json(create_sender_resp)
            report["checks"]["create_sender"] = {
                "status_code": create_sender_resp.status_code,
                "spfError": created_sender_payload.get("spfError"),
                "dkimError": created_sender_payload.get("dkimError"),
                "id": created_sender_payload.get("id"),
            }
            # Re-read senders after create attempt
            senders_resp = client.get("/senders")
            senders_payload = _safe_json(senders_resp)
            senders = senders_payload.get("senders") or []
            sender = _find_sender(senders, args.sender_email)

        report["checks"]["sender"] = {
            "exists": sender is not None,
            "active": bool(sender.get("active")) if sender else False,
            "id": sender.get("id") if sender else None,
            "email": sender.get("email") if sender else None,
        }

        # Runtime sender config (local env only)
        email_from = os.getenv("EMAIL_FROM", "").strip()
        email_from_name = os.getenv("EMAIL_FROM_NAME", "").strip()
        report["checks"]["runtime_sender_env"] = {
            "EMAIL_FROM": email_from or None,
            "EMAIL_FROM_NAME": email_from_name or None,
            "matches_target_sender": email_from.lower() == args.sender_email.lower() if email_from else False,
        }

        # Optional transactional send probe
        if args.send_test:
            subject = f"K2M Task 7.13 test send {_utc_now_iso()}"
            send_payload = {
                "sender": {"email": args.sender_email, "name": args.sender_name},
                "to": [{"email": args.test_to}],
                "subject": subject,
                "htmlContent": "<p>Task 7.13 test send probe.</p>",
            }
            send_resp = client.post("/smtp/email", send_payload)
            send_resp_payload = _safe_json(send_resp)
            message_id = send_resp_payload.get("messageId")
            report["checks"]["test_send"] = {
                "status_code": send_resp.status_code,
                "messageId": message_id,
                "response": send_resp_payload,
                "subject": subject,
            }

            if message_id:
                events_payload: Dict[str, Any] = {}
                events_resp: Optional[httpx.Response] = None
                deadline = time.time() + max(2, args.wait_seconds)
                poll_interval = 2
                while time.time() <= deadline:
                    events_resp = client.get(
                        "/smtp/statistics/events",
                        params={"messageId": message_id},
                    )
                    events_payload = _safe_json(events_resp)
                    if events_payload.get("events"):
                        break
                    time.sleep(poll_interval)
                report["checks"]["test_send_events"] = {
                    "status_code": events_resp.status_code if events_resp else None,
                    "events": events_payload.get("events") or [],
                }

        # Evaluate blockers
        blockers: List[str] = []
        next_actions: List[str] = []

        domain_check = report["checks"]["domain_detail"]
        if not domain_exists:
            blockers.append(f"Brevo domain {args.domain} is missing.")
            next_actions.append(f"Create the domain in Brevo (UI or --ensure-domain).")
        else:
            if not domain_check.get("authenticated"):
                blockers.append(f"Brevo domain {args.domain} is not authenticated.")
            if not domain_check.get("verified"):
                blockers.append(f"Brevo domain {args.domain} is not verified.")
            dns_records = domain_check.get("dns_records") or {}
            dns_gaps = _collect_dns_gaps(dns_records)
            for gap in dns_gaps:
                blockers.append(gap)
            if dns_gaps:
                next_actions.append(
                    "Add/verify Brevo DNS records at your registrar, then re-run this script."
                )

        sender_check = report["checks"]["sender"]
        if not sender_check.get("exists"):
            blockers.append(f"Sender {args.sender_email} is missing in Brevo.")
            next_actions.append(f"Create sender {args.sender_email} (UI or --ensure-sender).")
        elif not sender_check.get("active"):
            blockers.append(f"Sender {args.sender_email} exists but is not active.")
            next_actions.append(
                "Activate/validate sender after domain authentication is complete."
            )

        sender_env_check = report["checks"]["runtime_sender_env"]
        if not sender_env_check.get("matches_target_sender"):
            blockers.append(
                f"EMAIL_FROM does not match target sender ({args.sender_email})."
            )
            next_actions.append(
                "After sender activation, set EMAIL_FROM to target sender in Railway and local env."
            )

        test_events = report["checks"].get("test_send_events", {}).get("events") or []
        if args.send_test:
            if not test_events:
                blockers.append("No Brevo event captured for test send.")
                next_actions.append("Re-run with --send-test and a longer --wait-seconds.")
            else:
                first_event = test_events[0]
                event_name = str(first_event.get("event", "")).lower()
                reason = str(first_event.get("reason", "")).strip()
                if event_name not in {"delivered", "opens", "clicks", "requests"}:
                    blockers.append(
                        f"Test send not delivered (event={first_event.get('event')}, reason={reason or 'n/a'})."
                    )
                    next_actions.append(
                        "Fix sender/domain/mailbox issues and repeat test send until delivered."
                    )

        report["blockers"] = blockers
        report["next_actions"] = next_actions
        report["overall_status"] = "pass" if not blockers else "blocked"

        # Print concise summary
        print(f"Task 7.13 audit status: {report['overall_status']}")
        print(f"Domain: {args.domain}")
        print(f"Sender: {args.sender_email}")
        if blockers:
            print("Blockers:")
            for blocker in blockers:
                print(f"- {blocker}")
        else:
            print("All checks passed.")

        if args.output:
            out_path = Path(args.output)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
            print(f"Report saved: {out_path}")

        return 0 if report["overall_status"] == "pass" else 1
    finally:
        client.close()


if __name__ == "__main__":
    sys.exit(main())
