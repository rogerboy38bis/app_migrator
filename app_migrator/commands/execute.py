"""app-migrator-execute command (T1.8.2 — extracted from __init__.py)"""

import json

import click

try:
    import frappe
    from frappe.commands import pass_context
except ImportError:
    def pass_context(f):
        return f
from ._shared import ProgressTracker


def _extract_doctypes(plan):
    """Return a flat list of {'name', 'target_app'} dicts from either plan schema.

    W3 finding #3: `generate-plan` and `execute` used incompatible plan schemas,
    so the canonical generate->execute pipeline raised ``KeyError: 'doctypes'``.
    This shim consumes both:

    - Legacy flat schema:  ``plan['doctypes'] = [{'name', 'target_app'}, ...]``
    - Intelligent phased schema (generate-plan): ``plan['phases'][i]['doctypes'] =
      ['DocType Name', ...]`` with the target app at ``plan['target_app']``.

    DocType entries may be plain strings (phased) or dicts (flat); both normalize
    to ``{'name': <str>, 'target_app': <str|None>}``.
    """
    target = plan.get("target_app") or plan.get("target")

    def _norm(dt):
        if isinstance(dt, dict):
            return {"name": dt.get("name"), "target_app": dt.get("target_app", target)}
        return {"name": dt, "target_app": target}

    if "doctypes" in plan:
        return [_norm(dt) for dt in plan["doctypes"]]
    return [_norm(dt) for phase in plan.get("phases", []) for dt in phase.get("doctypes", [])]


@click.command('app-migrator-execute')
@click.option('--site', required=True, help='Site name')
@click.option('--plan', 'plan_file', required=True, help='Migration plan file')
@click.option('--dry-run/--apply', default=True, help='Dry run or apply')
@pass_context
def app_migrator_execute(context, site, plan_file, dry_run):
    """Execute a migration plan"""
    mode = "DRY-RUN" if dry_run else "APPLY"
    print(f"🚀 Executing migration [{mode}]")
    print("=" * 60)

    with open(plan_file) as f:
        plan = json.load(f)

    if not dry_run:
        if not click.confirm("⚠️ This will modify your database. Continue?"):
            print("❌ Cancelled")
            return

    frappe.init(site=site)
    frappe.connect()

    doctypes = _extract_doctypes(plan)
    tracker = ProgressTracker("Migration", len(doctypes))

    for dt in doctypes:
        tracker.update(f"Processing {dt['name']}")
        if not dry_run:
            frappe.db.sql("""
                UPDATE `tabDocType` SET module = %s WHERE name = %s
            """, (dt["target_app"], dt["name"]))

    if not dry_run:
        frappe.db.commit()

    frappe.db.close()
    tracker.complete()

    if dry_run:
        print("\n✅ Dry-run complete. Run with --apply to execute.")
    else:
        print(f"\n✅ Migration complete! Run 'bench --site {site} migrate'")
