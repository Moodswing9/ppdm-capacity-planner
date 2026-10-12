#!/usr/bin/env python3
"""
ppdm-capacity-planner — Claude Opus 4.7-powered storage capacity forecasting for PPDM.
"""
__version__ = "1.0.1"

import argparse
import os
import sys
import json
import requests
import urllib3
import anthropic

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# ---------------------------------------------------------------------------
# PPDM REST API client
# ---------------------------------------------------------------------------

class PPDMClient:
    """Thin REST client for Dell EMC PowerProtect Data Manager."""

    def __init__(self, host: str, user: str, password: str, port: int = 8443):
        self.host = host
        self.user = user
        self.password = password
        self.port = port
        self.base_url = f"https://{host}:{port}/api/v2"
        self.token: str | None = None
        self.session = requests.Session()
        self.session.verify = False

    def login(self) -> None:
        """Authenticate and store Bearer token."""
        url = f"{self.base_url}/login"
        payload = {"username": self.user, "password": self.password}
        resp = self.session.post(url, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        self.token = data.get("access_token") or data.get("token")
        if not self.token:
            raise ValueError(f"Login response did not contain a token: {data}")
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})

    def get_storage_systems(self) -> list[dict]:
        """Return list of storage system objects from PPDM."""
        url = f"{self.base_url}/storage-systems"
        resp = self.session.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        # PPDM typically wraps results in {"content": [...]}
        if isinstance(data, dict) and "content" in data:
            return data["content"]
        if isinstance(data, list):
            return data
        return []

    def logout(self) -> None:
        """Invalidate the current session token."""
        if not self.token:
            return
        try:
            url = f"{self.base_url}/logout"
            self.session.post(url, timeout=10)
        except Exception:
            pass  # Best-effort
        finally:
            self.token = None


# ---------------------------------------------------------------------------
# Storage system helpers
# ---------------------------------------------------------------------------

def parse_storage_systems(raw: list[dict]) -> list[dict]:
    """
    Normalise raw PPDM storage-system records into a consistent schema.

    Each returned dict has:
        name            str
        total_gib       float
        used_gib        float
        used_pct        float
    """
    systems = []
    for item in raw:
        name = item.get("name") or item.get("id") or "unknown"
        total = float(item.get("totalCapacity", 0))
        used = float(item.get("usedCapacity", 0))
        pct = float(item.get("usedPercentage", (used / total * 100) if total > 0 else 0))
        systems.append(
            {
                "name": name,
                "total_gib": total,
                "used_gib": used,
                "used_pct": pct,
            }
        )
    return systems


def format_system(system: dict) -> str:
    """Return a human-readable single-line summary for one storage system."""
    return (
        f"{system['name']}: "
        f"{system['used_gib']:.1f} GiB used / {system['total_gib']:.1f} GiB total "
        f"({system['used_pct']:.1f}%)"
    )


# ---------------------------------------------------------------------------
# Prompt construction
# ---------------------------------------------------------------------------

def build_prompt(systems: list[dict]) -> str:
    """Build the Claude prompt that requests capacity forecasts."""
    lines = ["## PPDM Storage Systems — Current Snapshot\n"]
    for s in systems:
        lines.append(f"- {format_system(s)}")
    lines.append("")
    lines.append(
        "NOTE: This is a single-point-in-time snapshot. No historical growth data is "
        "available. Please provide conservative estimates and note the uncertainty."
    )
    lines.append("")
    lines.append(
        "Based on the storage utilisation figures above, please produce a structured "
        "capacity planning report with the following sections:\n"
        "\n"
        "1. **80% Capacity Breach Projections** — For each storage system, estimate "
        "the number of days until it reaches 80% utilisation (or note if it already "
        "has). Assume a conservative growth rate of 1–3% per month where unknown.\n"
        "\n"
        "2. **95% Capacity Breach Projections** — Same as above but for 95% "
        "utilisation (critical threshold).\n"
        "\n"
        "3. **Top Recommendations** — Actionable steps such as deduplication tuning, "
        "data cleanup, storage tiering, and capacity expansion. Prioritise by urgency.\n"
        "\n"
        "4. **Executive Summary** — A concise 3–5 sentence paragraph suitable for "
        "management.\n"
        "\n"
        "Be specific, concise, and practical. Format output in clean Markdown."
    )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Claude integration
# ---------------------------------------------------------------------------

def generate_forecast(systems: list[dict]) -> str:
    """Call Claude Opus 4.7 and return the forecast narrative."""
    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env
    prompt = build_prompt(systems)
    message = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )
    return message.content[0].text


# ---------------------------------------------------------------------------
# Demo data
# ---------------------------------------------------------------------------

DEMO_SYSTEMS_RAW = [
    {
        "name": "DataDomain-Primary",
        "totalCapacity": 20480.0,   # 20 TiB in GiB
        "usedCapacity": 14745.6,    # 72%
        "usedPercentage": 72.0,
    },
    {
        "name": "DataDomain-DR",
        "totalCapacity": 10240.0,   # 10 TiB
        "usedCapacity": 9011.2,     # 88%
        "usedPercentage": 88.0,
    },
    {
        "name": "ObjectStore-Tier2",
        "totalCapacity": 51200.0,   # 50 TiB
        "usedCapacity": 28160.0,    # 55%
        "usedPercentage": 55.0,
    },
]


# ---------------------------------------------------------------------------
# Report printing
# ---------------------------------------------------------------------------

def print_report(systems: list[dict], narrative: str) -> None:
    """Print the full capacity planning report to stdout."""
    separator = "=" * 70
    print(separator)
    print("  PPDM CAPACITY PLANNING REPORT  —  powered by Claude Opus 4.7")
    print(separator)
    print()
    print("CURRENT STORAGE UTILISATION")
    print("-" * 40)
    for s in systems:
        bar_filled = int(s["used_pct"] / 5)
        bar = "[" + "#" * bar_filled + "." * (20 - bar_filled) + "]"
        flag = ""
        if s["used_pct"] >= 95:
            flag = "  *** CRITICAL ***"
        elif s["used_pct"] >= 80:
            flag = "  ** WARNING **"
        print(f"  {s['name']}")
        print(f"    {bar} {s['used_pct']:.1f}%{flag}")
        print(f"    Used: {s['used_gib']:.1f} GiB  /  Total: {s['total_gib']:.1f} GiB")
        print()
    print(separator)
    print("FORECAST & RECOMMENDATIONS  (Claude Opus 4.7 Analysis)")
    print(separator)
    print()
    print(narrative)
    print()
    print(separator)
    print(f"  ppdm-capacity-planner v{__version__}")
    print(separator)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog="planner",
        description="PPDM storage capacity forecasting via Claude Opus 4.7.",
    )
    parser.add_argument(
        "--host",
        default=os.environ.get("PPDM_HOST"),
        help="PPDM hostname or IP (env: PPDM_HOST)",
    )
    parser.add_argument(
        "--user",
        default=os.environ.get("PPDM_USER"),
        help="PPDM username (env: PPDM_USER)",
    )
    parser.add_argument(
        "--pass",
        dest="password",
        default=os.environ.get("PPDM_PASS"),
        help="PPDM password (env: PPDM_PASS)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("PPDM_PORT", "8443")),
        help="PPDM port (env: PPDM_PORT, default: 8443)",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Use built-in demo data instead of connecting to a live PPDM instance.",
    )
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)

    if args.demo:
        print("Running in DEMO mode — no PPDM connection required.")
        raw = DEMO_SYSTEMS_RAW
    else:
        if not args.host:
            print("ERROR: --host is required (or set PPDM_HOST).", file=sys.stderr)
            return 1
        if not args.user:
            print("ERROR: --user is required (or set PPDM_USER).", file=sys.stderr)
            return 1
        if not args.password:
            print("ERROR: --pass is required (or set PPDM_PASS).", file=sys.stderr)
            return 1

        client = PPDMClient(
            host=args.host, user=args.user, password=args.password, port=args.port
        )
        print(f"Connecting to PPDM at {args.host}:{args.port} ...", file=sys.stderr)
        try:
            client.login()
            raw = client.get_storage_systems()
        finally:
            client.logout()

    systems = parse_storage_systems(raw)
    if not systems:
        print("ERROR: No storage systems found.", file=sys.stderr)
        return 2

    print("Generating capacity forecast via Claude Opus 4.7 ...", file=sys.stderr)
    narrative = generate_forecast(systems)
    print_report(systems, narrative)
    return 0


if __name__ == "__main__":
    sys.exit(main())
