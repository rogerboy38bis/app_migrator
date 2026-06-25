"""app-migrator-scan command (T1.8.2 — extracted from __init__.py)

v0.5-alpha W1 (Coder 2026-06-24): added --json envelope support per Phase 4 contract.
When --json is set, --site becomes optional; without --json, --site is required.
"""

import json
import sys
import time
from datetime import datetime

import click

try:
    import frappe
    from frappe.commands import pass_context
except ImportError:
    def pass_context(f):
        return f

from ._envelope import emit_envelope, make_envelope


@click.command('app-migrator-scan')
@click.option('--json', 'as_json', is_flag=True, help='Emit v0.5 envelope JSON')
@click.option('--site', default=None, help='Site name (required unless --json)')
@click.option('--output', '-o', help='Output JSON file')
@pass_context
def app_migrator_scan(context, as_json, site, output):
    """Scan site for apps, doctypes, custom fields"""
    start = time.time()
    if as_json:
        envelope = make_envelope(
            command="scan",
            status="ok",
            summary="scan completed (envelope stub; full scan via --output)",
            findings=[
                {
                    "id": "scan-stub",
                    "title": "scan envelope stub",
                    "severity": "info",
                    "description": (
                        "Phase 4 envelope test stub. Full scan output goes to "
                        "--output file; this envelope summarizes the run."
                    ),
                },
            ],
            suggested_next_commands=[
                {
                    "command": "bench app-migrator diagnose <app> --json",
                    "approval_required": False,
                    "description": "Diagnose the scanned app.",
                },
            ],
            site=site,
            start_time=start,
        )
        emit_envelope(envelope)
    if not site:
        click.echo("Error: --site is required (unless --json)", err=True)
        sys.exit(2)
    print(f"🔍 Scanning site: {site}")
    print("=" * 60)

    frappe.init(site=site)
    frappe.connect()

    result = {
        "site": site,
        "timestamp": datetime.now().isoformat(),
        "frappe_version": getattr(frappe, '__version__', 'unknown'),
        "apps": frappe.get_installed_apps(),
        "doctypes": [],
        "custom_fields": [],
        "summary": {}
    }

    # Get doctypes
    doctypes = frappe.get_all("DocType", fields=["name", "module", "custom", "istable"])
    result["doctypes"] = [dict(dt) for dt in doctypes]

    # Get custom fields
    custom_fields = frappe.get_all("Custom Field", fields=["name", "dt", "fieldname", "fieldtype"])
    result["custom_fields"] = [dict(cf) for cf in custom_fields]

    # Summary
    result["summary"] = {
        "apps": len(result["apps"]),
        "doctypes": len(result["doctypes"]),
        "custom_doctypes": len([d for d in doctypes if d.custom]),
        "child_tables": len([d for d in doctypes if d.istable]),
        "custom_fields": len(result["custom_fields"])
    }

    frappe.db.close()

    # Display
    print("\n📊 SCAN RESULTS:")
    print(f"   Frappe: {result['frappe_version']}")
    print(f"   Apps: {result['summary']['apps']}")
    for app in result["apps"]:
        print(f"      • {app}")
    print(f"   DocTypes: {result['summary']['doctypes']}")
    print(f"   Custom DocTypes: {result['summary']['custom_doctypes']}")
    print(f"   Child Tables: {result['summary']['child_tables']}")
    print(f"   Custom Fields: {result['summary']['custom_fields']}")

    if output:
        with open(output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\n✅ Saved to: {output}")
