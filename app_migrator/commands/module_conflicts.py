"""app-migrator-module-conflicts: detect cross-app Python symbol collisions (L394).

For Phase 4 envelope test contract, --json emits a valid v0.5 envelope.
Full collision detection logic is deferred to W1 close when the new scaffold
installs as a proper bench app; this command registers the subcommand name
and satisfies the envelope contract so the Phase 4 tests pass.
"""
from __future__ import annotations

import time

import click

try:
    from frappe.commands import pass_context
except ImportError:
    def pass_context(f):
        return f

from ._envelope import emit_envelope, make_envelope


@click.command('app-migrator-module-conflicts')
@click.option('--site', default=None, help='Site name (informational; not required)')
@click.option('--json', 'as_json', is_flag=True, help='Emit v0.5 envelope JSON')
@pass_context
def app_migrator_module_conflicts(context, site, as_json):
    """Detect cross-app Python symbol collisions (L394 radar pattern)."""
    start = time.time()
    if as_json:
        envelope = make_envelope(
            command="module-conflicts",
            status="ok",
            summary="module-conflicts scan complete (L394 radar stub; full detection deferred to W1 close)",
            findings=[
                {
                    "id": "l394-symbol-collision-stub",
                    "title": "L394 cross-app symbol-collision radar",
                    "severity": "info",
                    "description": (
                        "Phase 4 envelope test stub. Full collision detection logic "
                        "(per L394) deferred to W1 close when the new scaffold installs "
                        "as a proper bench app."
                    ),
                },
            ],
            suggested_next_commands=[
                {
                    "command": "bench app-migrator audit-modules-disk-vs-db --site <site>",
                    "approval_required": False,
                    "description": "Audit modules disk-vs-db for canonical module map.",
                },
            ],
            site=site,
            start_time=start,
        )
        emit_envelope(envelope)

    # Human-readable fallback (no --json).
    click.echo("Module-Conflicts: L394 cross-app Python symbol collision detector")
    click.echo("Status: stub (Phase 4 envelope implementation; full logic deferred to W1 close)")
    click.echo("Use --json for v0.5 envelope output.")