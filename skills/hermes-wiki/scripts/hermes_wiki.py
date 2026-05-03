#!/usr/bin/env python3
"""
Hermes Wiki - Local Intelligence CLI
Main entry point. READ-ONLY. LOCAL-ONLY. FAIL-CLOSED.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Add scripts dir to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from scanner import scan_all, scan_directory
from indexer import build_all_indexes
from query import ask
from cron_map import build_cron_map, format_cron_table
from skill_map import scan_skill_dir, format_skill_table
from trust_map import build_trust_map, format_trust_table
from server_map import collect_server_health, format_health_markdown
from load_rank import build_load_rank, format_load_table
from garbage_map import build_garbage_map, format_garbage_table
from cleanup_advisor import build_cleanup_advice, format_cleanup_report
from report import generate_report, save_report, save_snapshot


def cmd_scan(args):
    """Scan filesystem and build indexes."""
    paths = args.path if args.path else None
    print("Scanning...")
    build_all_indexes()
    print("Done. Indexes built.")


def cmd_cron_map(args):
    """Build and display cron map."""
    entries = build_cron_map()
    print(format_cron_table(entries))


def cmd_skill_map(args):
    """Build and display skill map."""
    skills = scan_skill_dir()
    print(format_skill_table(skills))


def cmd_trust_map(args):
    """Build and display trust map."""
    from scanner import scan_all
    scans = scan_all()
    entries = build_trust_map(scans)
    print(format_trust_table(entries))


def cmd_server_health(args):
    """Collect and display server health."""
    health = collect_server_health()
    print(format_health_markdown(health))


def cmd_load_rank(args):
    """Rank system load consumers."""
    entries = build_load_rank()
    print(format_load_table(entries))


def cmd_garbage_map(args):
    """Find garbage/cleanup candidates."""
    entries = build_garbage_map()
    print(format_garbage_table(entries))


def cmd_cleanup_advisor(args):
    """Show cleanup advice."""
    advice = build_cleanup_advice()
    print(format_cleanup_report(advice))


def cmd_ask(args):
    """Query local index."""
    if not args.question:
        print("Usage: hermes_wiki.py ask 'question'")
        sys.exit(1)
    result = ask(args.question)
    print(result)


def cmd_report(args):
    """Generate report."""
    if args.save:
        path = save_report(include_server=args.include_server)
        print(f"Report saved: {path}")
    else:
        print(generate_report(include_server=args.include_server))


def cmd_snapshot(args):
    """Save snapshot."""
    path = save_snapshot()
    print(f"Snapshot saved: {path}")


def main():
    parser = argparse.ArgumentParser(
        description="Hermes Wiki - Local Intelligence",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 hermes_wiki.py scan
  python3 hermes_wiki.py cron-map
  python3 hermes_wiki.py skill-map
  python3 hermes_wiki.py trust-map
  python3 hermes_wiki.py server-health
  python3 hermes_wiki.py load-rank
  python3 hermes_wiki.py garbage-map
  python3 hermes_wiki.py cleanup-advisor
  python3 hermes_wiki.py ask "Which scripts call external APIs?"
  python3 hermes_wiki.py report --save --include-server
  python3 hermes_wiki.py snapshot
        """
    )
    subparsers = parser.add_subparsers(dest="command")

    # scan
    p_scan = subparsers.add_parser("scan", help="Scan filesystem and build indexes")
    p_scan.add_argument("--path", nargs="+", help="Paths to scan")

    # cron-map
    subparsers.add_parser("cron-map", help="Map cron jobs")

    # skill-map
    subparsers.add_parser("skill-map", help="Map installed skills")

    # trust-map
    subparsers.add_parser("trust-map", help="Build trust map")

    # server-health
    subparsers.add_parser("server-health", help="Server health check")

    # load-rank
    subparsers.add_parser("load-rank", help="Rank load consumers")

    # garbage-map
    subparsers.add_parser("garbage-map", help="Find cleanup candidates")

    # cleanup-advisor
    subparsers.add_parser("cleanup-advisor", help="Cleanup advice")

    # ask
    p_ask = subparsers.add_parser("ask", help="Query local index")
    p_ask.add_argument("question", nargs="?", help="Question to ask")

    # report
    p_report = subparsers.add_parser("report", help="Generate report")
    p_report.add_argument("--include-server", action="store_true", help="Include server data")
    p_report.add_argument("--save", action="store_true", help="Save to file")

    # snapshot
    subparsers.add_parser("snapshot", help="Save snapshot")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    commands = {
        "scan": cmd_scan,
        "cron-map": cmd_cron_map,
        "skill-map": cmd_skill_map,
        "trust-map": cmd_trust_map,
        "server-health": cmd_server_health,
        "load-rank": cmd_load_rank,
        "garbage-map": cmd_garbage_map,
        "cleanup-advisor": cmd_cleanup_advisor,
        "ask": cmd_ask,
        "report": cmd_report,
        "snapshot": cmd_snapshot,
    }

    handler = commands.get(args.command)
    if handler:
        handler(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
