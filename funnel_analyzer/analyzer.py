"""
B2B SaaS GTM Full-Funnel Cohort & Conversion Analyzer.

Provides full-funnel stage metrics, step-by-step conversion analysis,
cumulative conversion rates, and leaky bucket diagnostics.
"""

from typing import Any, Dict, List, Optional, Tuple, Union


DEFAULT_STAGES: List[Tuple[str, int]] = [
    ("Leads", 10000),
    ("MQL", 2800),
    ("SAL", 1400),
    ("SQL", 560),
    ("POC", 280),
    ("Proposal", 140),
    ("Won", 48),
]


class FunnelAnalyzer:
    """
    Analyzes B2B Go-To-Market (GTM) conversion funnels and provides
    leaky bucket diagnostics and ASCII visualizations.
    """

    def __init__(
        self,
        stages: Optional[
            Union[
                List[Tuple[str, int]],
                List[Dict[str, Any]],
                Dict[str, int],
            ]
        ] = None,
    ) -> None:
        """
        Initialize the FunnelAnalyzer.

        :param stages: Custom funnel stages. Can be:
            - List of tuples: [("Leads", 10000), ("MQL", 2800), ...]
            - Dict: {"Leads": 10000, "MQL": 2800, ...}
            - List of dicts: [{"name": "Leads", "count": 10000}, ...]
            If None, the default 7-stage B2B funnel is used.
        """
        if stages is None:
            self.stages: List[Tuple[str, int]] = list(DEFAULT_STAGES)
        else:
            self.stages = self._normalize_stages(stages)

        if not self.stages:
            raise ValueError("Funnel must contain at least one stage.")

    def _normalize_stages(
        self,
        raw_stages: Union[
            List[Tuple[str, int]],
            List[Dict[str, Any]],
            Dict[str, int],
        ],
    ) -> List[Tuple[str, int]]:
        """Normalize raw stage inputs into a list of (name, count) tuples."""
        normalized: List[Tuple[str, int]] = []

        if isinstance(raw_stages, dict):
            for name, count in raw_stages.items():
                self._validate_stage(str(name), count)
                normalized.append((str(name), int(count)))
        elif isinstance(raw_stages, list):
            for item in raw_stages:
                if isinstance(item, (tuple, list)) and len(item) >= 2:
                    name, count = item[0], item[1]
                    self._validate_stage(str(name), count)
                    normalized.append((str(name), int(count)))
                elif isinstance(item, dict) and "name" in item and "count" in item:
                    name, count = item["name"], item["count"]
                    self._validate_stage(str(name), count)
                    normalized.append((str(name), int(count)))
                else:
                    raise ValueError(
                        f"Invalid stage format: {item}. Expected (name, count) tuple or dict."
                    )
        else:
            raise TypeError("Stages must be a list or dict.")

        return normalized

    @staticmethod
    def _validate_stage(name: str, count: Any) -> None:
        """Validate stage name and count."""
        if not name or not isinstance(name, str):
            raise ValueError("Stage name must be a non-empty string.")
        if not isinstance(count, (int, float)) or count < 0:
            raise ValueError(f"Stage count for '{name}' must be a non-negative number.")

    def analyze(self) -> Dict[str, Any]:
        """
        Perform funnel cohort and conversion analysis.

        :return: Dictionary containing:
            - top_of_funnel (int): volume at initial stage
            - bottom_of_funnel (int): volume at final stage
            - overall_conversion_pct (float): conversion from top to bottom
            - stage_metrics (list of dicts): per-stage conversion and leak metrics
            - leaks (list of dicts): drop-off details per stage transition
            - biggest_volume_leak (dict): transition with highest lost volume
            - tightest_bottleneck (dict): transition with lowest step conversion %
        """
        top_of_funnel = self.stages[0][1]
        bottom_of_funnel = self.stages[-1][1]

        overall_conversion_pct = (
            round((bottom_of_funnel / top_of_funnel) * 100, 2)
            if top_of_funnel > 0
            else 0.0
        )

        stage_metrics: List[Dict[str, Any]] = []
        leaks: List[Dict[str, Any]] = []

        prev_count: Optional[int] = None
        prev_name: Optional[str] = None

        for idx, (name, count) in enumerate(self.stages):
            if idx == 0:
                step_conversion_pct = 100.0
                cumulative_pct = 100.0
                drop_count = 0
                drop_pct = 0.0
            else:
                assert prev_count is not None
                assert prev_name is not None
                step_conversion_pct = (
                    round((count / prev_count) * 100, 2)
                    if prev_count > 0
                    else 0.0
                )
                cumulative_pct = (
                    round((count / top_of_funnel) * 100, 2)
                    if top_of_funnel > 0
                    else 0.0
                )
                drop_count = max(0, prev_count - count)
                drop_pct = (
                    round((drop_count / prev_count) * 100, 2)
                    if prev_count > 0
                    else 0.0
                )

                leaks.append({
                    "from_stage": prev_name,
                    "to_stage": name,
                    "lost_count": drop_count,
                    "drop_rate_pct": drop_pct,
                    "step_conversion_pct": step_conversion_pct,
                })

            metric = {
                "name": name,
                "count": count,
                "step_conversion_pct": step_conversion_pct,
                "cumulative_pct": cumulative_pct,
                "drop_count": drop_count,
                "drop_pct": drop_pct,
            }
            stage_metrics.append(metric)

            prev_count = count
            prev_name = name

        biggest_volume_leak = (
            max(leaks, key=lambda x: x["lost_count"]) if leaks else None
        )
        tightest_bottleneck = (
            min(leaks, key=lambda x: x["step_conversion_pct"]) if leaks else None
        )

        return {
            "top_of_funnel": top_of_funnel,
            "bottom_of_funnel": bottom_of_funnel,
            "overall_conversion_pct": overall_conversion_pct,
            "stage_metrics": stage_metrics,
            "leaks": leaks,
            "biggest_volume_leak": biggest_volume_leak,
            "tightest_bottleneck": tightest_bottleneck,
        }

    def print_funnel(self, bar_width: int = 32) -> str:
        """
        Generate and print the ASCII funnel with progress bars and leaky bucket metrics.

        :param bar_width: Width in characters for the progress bar.
        :return: Formatted ASCII string.
        """
        analysis = self.analyze()
        top_count = analysis["top_of_funnel"]
        stage_metrics = analysis["stage_metrics"]

        lines: List[str] = []
        divider = "=" * 80
        thin_divider = "-" * 80

        lines.append(divider)
        lines.append("                  B2B SaaS GTM Full-Funnel Cohort Analysis")
        lines.append(divider)
        lines.append(
            f"{'Stage':<14} {'Count':>8} {'Step Conv':>11} {'Cumulative':>12}  {'Progress Bar / Leaks'}"
        )
        lines.append(thin_divider)

        for idx, stage in enumerate(stage_metrics):
            name = stage["name"]
            count = stage["count"]
            step_conv = (
                f"{stage['step_conversion_pct']:.2f}%"
                if idx > 0
                else "---"
            )
            cumulative = f"{stage['cumulative_pct']:.2f}%"

            # Progress bar based on cumulative % of top of funnel
            ratio = count / top_count if top_count > 0 else 0.0
            filled_chars = int(round(ratio * bar_width))
            filled_chars = max(0, min(bar_width, filled_chars))
            bar = "█" * filled_chars + " " * (bar_width - filled_chars)

            if idx == 0:
                leak_note = ""
            else:
                leak_note = f" 🔻 -{stage['drop_pct']:.1f}% (-{stage['drop_count']:,})"

            lines.append(
                f"{name:<14} {count:>8,} {step_conv:>11} {cumulative:>12}  [{bar}]{leak_note}"
            )

        lines.append(thin_divider)

        # ASCII Funnel Silhouette
        lines.append("\n  Funnel Silhouette Visualization:")
        total_stages = len(stage_metrics)
        for idx, stage in enumerate(stage_metrics):
            indent = " " * (idx * 2)
            pad_spaces = (total_stages - idx - 1) * 4
            left_wall = "\\"
            right_wall = "/"
            stage_str = f"{stage['name']}: {stage['count']:,} ({stage['cumulative_pct']:.2f}%)"
            lines.append(f"   {indent}{left_wall}  {stage_str:<32}{' ' * pad_spaces}{right_wall}")
        bottom_pad = " " * (total_stages * 2)
        lines.append(f"   {bottom_pad}\\" + "_" * 36 + "/")

        # Diagnostics & Key Highlights
        lines.append("\n" + thin_divider)
        lines.append("  🔍 Leaky Bucket Diagnostics & Insights:")
        lines.append(
            f"   • Top of Funnel:       {top_count:,} leads"
        )
        lines.append(
            f"   • Bottom of Funnel:    {analysis['bottom_of_funnel']:,} won accounts"
        )
        lines.append(
            f"   • Overall Conversion:  {analysis['overall_conversion_pct']:.2f}%"
        )

        b_leak = analysis["biggest_volume_leak"]
        if b_leak:
            lines.append(
                f"   • Biggest Volume Leak: {b_leak['from_stage']} → {b_leak['to_stage']} "
                f"(-{b_leak['lost_count']:,} lost, {b_leak['drop_rate_pct']:.2f}% drop)"
            )

        t_bottle = analysis["tightest_bottleneck"]
        if t_bottle:
            lines.append(
                f"   • Tightest Bottleneck: {t_bottle['from_stage']} → {t_bottle['to_stage']} "
                f"({t_bottle['step_conversion_pct']:.2f}% step conversion)"
            )

        lines.append(divider)

        output = "\n".join(lines)
        print(output)
        return output
