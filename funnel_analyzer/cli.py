"""
Command-Line Interface (CLI) for GTM Funnel Analyzer.

Usage:
    python funnel_analyzer/cli.py
    python -m funnel_analyzer.cli
    python funnel_analyzer/cli.py --json
    python funnel_analyzer/cli.py --stages "Leads:5000,MQL:1500,SQL:300,Won:30"
"""

import argparse
import json
import os
import sys

# Ensure repository root is in sys.path when run directly as a script
if __name__ == "__main__" and __package__ is None:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

from funnel_analyzer.analyzer import FunnelAnalyzer


def parse_stages_arg(stages_str: str):
    """
    Parse a comma-separated key:value string into a list of (name, count) tuples.
    Example: "Leads:10000,MQL:2800,Won:48"
    """
    stages = []
    pairs = stages_str.split(",")
    for pair in pairs:
        pair = pair.strip()
        if not pair:
            continue
        if ":" not in pair:
            raise ValueError(f"Invalid stage pair '{pair}'. Format must be 'StageName:Count'.")
        name, count_str = pair.split(":", 1)
        name = name.strip()
        try:
            count = int(count_str.strip())
        except ValueError:
            raise ValueError(f"Invalid count for stage '{name}': '{count_str}' must be an integer.")
        stages.append((name, count))
    return stages


def main():
    """Main CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="B2B SaaS GTM Full-Funnel Cohort & Conversion Analyzer with Leaky Bucket Diagnostics."
    )
    parser.add_argument(
        "--stages",
        type=str,
        default=None,
        help="Custom funnel stages in 'Name:Count,Name:Count' format. Defaults to 7-stage B2B benchmark funnel.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output analysis results as structured JSON.",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=32,
        help="Width of ASCII progress bars (default: 32).",
    )

    args = parser.parse_args()

    stages = None
    if args.stages:
        stages = parse_stages_arg(args.stages)

    analyzer = FunnelAnalyzer(stages=stages)

    if args.json:
        analysis = analyzer.analyze()
        print(json.dumps(analysis, indent=2))
    else:
        analyzer.print_funnel(bar_width=args.width)


if __name__ == "__main__":
    main()
