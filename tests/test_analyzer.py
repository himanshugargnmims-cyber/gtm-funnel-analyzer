"""
Unit tests for FunnelAnalyzer.
"""

import subprocess
import sys
import pytest

from funnel_analyzer import FunnelAnalyzer, DEFAULT_STAGES


def test_default_funnel_metrics():
    """Test default 7-stage B2B funnel analysis."""
    analyzer = FunnelAnalyzer()
    analysis = analyzer.analyze()

    # Core required assertions
    assert analysis["top_of_funnel"] == 10000
    assert analysis["bottom_of_funnel"] == 48
    assert len(analysis["stage_metrics"]) == 7
    assert analysis["overall_conversion_pct"] > 0
    assert analysis["overall_conversion_pct"] == pytest.approx(0.48, rel=1e-2)

    # Verify stage names and order
    expected_stage_names = ["Leads", "MQL", "SAL", "SQL", "POC", "Proposal", "Won"]
    actual_stage_names = [s["name"] for s in analysis["stage_metrics"]]
    assert actual_stage_names == expected_stage_names

    # Verify specific stage conversion metrics
    leads = analysis["stage_metrics"][0]
    assert leads["count"] == 10000
    assert leads["step_conversion_pct"] == 100.0
    assert leads["cumulative_pct"] == 100.0

    mql = analysis["stage_metrics"][1]
    assert mql["count"] == 2800
    assert mql["step_conversion_pct"] == pytest.approx(28.0, rel=1e-2)
    assert mql["cumulative_pct"] == pytest.approx(28.0, rel=1e-2)
    assert mql["drop_count"] == 7200
    assert mql["drop_pct"] == pytest.approx(72.0, rel=1e-2)

    won = analysis["stage_metrics"][6]
    assert won["count"] == 48
    assert won["step_conversion_pct"] == pytest.approx(34.29, rel=1e-2)
    assert won["cumulative_pct"] == pytest.approx(0.48, rel=1e-2)


def test_leaky_bucket_diagnostics():
    """Test leak and bottleneck identification."""
    analyzer = FunnelAnalyzer()
    analysis = analyzer.analyze()

    assert analysis["biggest_volume_leak"] is not None
    assert analysis["biggest_volume_leak"]["from_stage"] == "Leads"
    assert analysis["biggest_volume_leak"]["to_stage"] == "MQL"
    assert analysis["biggest_volume_leak"]["lost_count"] == 7200

    assert analysis["tightest_bottleneck"] is not None
    assert analysis["tightest_bottleneck"]["from_stage"] == "Leads"
    assert analysis["tightest_bottleneck"]["to_stage"] == "MQL"
    assert analysis["tightest_bottleneck"]["step_conversion_pct"] == pytest.approx(28.0, rel=1e-2)


def test_custom_funnel_tuples():
    """Test custom funnel defined as a list of tuples."""
    custom_stages = [
        ("Visitors", 1000),
        ("Signups", 200),
        ("Paid", 50),
    ]
    analyzer = FunnelAnalyzer(stages=custom_stages)
    analysis = analyzer.analyze()

    assert analysis["top_of_funnel"] == 1000
    assert analysis["bottom_of_funnel"] == 50
    assert len(analysis["stage_metrics"]) == 3
    assert analysis["overall_conversion_pct"] == 5.0

    # Step conversion check: Paid is 50 / 200 = 25%
    assert analysis["stage_metrics"][2]["step_conversion_pct"] == 25.0


def test_custom_funnel_dict():
    """Test custom funnel defined as a dictionary."""
    custom_dict = {
        "Impressions": 50000,
        "Clicks": 2500,
        "Trials": 250,
        "Customers": 25,
    }
    analyzer = FunnelAnalyzer(stages=custom_dict)
    analysis = analyzer.analyze()

    assert analysis["top_of_funnel"] == 50000
    assert analysis["bottom_of_funnel"] == 25
    assert len(analysis["stage_metrics"]) == 4
    assert analysis["overall_conversion_pct"] == pytest.approx(0.05, rel=1e-2)


def test_custom_funnel_list_of_dicts():
    """Test custom funnel defined as a list of dictionaries."""
    custom_list_dicts = [
        {"name": "Stage A", "count": 100},
        {"name": "Stage B", "count": 25},
    ]
    analyzer = FunnelAnalyzer(stages=custom_list_dicts)
    analysis = analyzer.analyze()

    assert analysis["top_of_funnel"] == 100
    assert analysis["bottom_of_funnel"] == 25
    assert len(analysis["stage_metrics"]) == 2
    assert analysis["overall_conversion_pct"] == 25.0


def test_print_funnel_output(capsys):
    """Test ASCII output generation from print_funnel."""
    analyzer = FunnelAnalyzer()
    output = analyzer.print_funnel(bar_width=20)

    # Check captured stdout
    captured = capsys.readouterr()
    assert "B2B SaaS GTM Full-Funnel Cohort Analysis" in captured.out
    assert "Leads" in captured.out
    assert "Won" in captured.out
    assert "🔻" in captured.out
    assert "Silhouette" in captured.out
    assert output == captured.out.strip()


def test_zero_top_of_funnel():
    """Test edge case where top of funnel count is 0."""
    stages = [("Leads", 0), ("Won", 0)]
    analyzer = FunnelAnalyzer(stages=stages)
    analysis = analyzer.analyze()

    assert analysis["top_of_funnel"] == 0
    assert analysis["bottom_of_funnel"] == 0
    assert analysis["overall_conversion_pct"] == 0.0


def test_single_stage():
    """Test single stage funnel."""
    stages = [("Standalone", 100)]
    analyzer = FunnelAnalyzer(stages=stages)
    analysis = analyzer.analyze()

    assert analysis["top_of_funnel"] == 100
    assert analysis["bottom_of_funnel"] == 100
    assert analysis["overall_conversion_pct"] == 100.0
    assert analysis["biggest_volume_leak"] is None
    assert analysis["tightest_bottleneck"] is None


def test_invalid_stages_error_handling():
    """Test validation errors for invalid funnel inputs."""
    with pytest.raises(ValueError, match="at least one stage"):
        FunnelAnalyzer(stages=[])

    with pytest.raises(ValueError, match="non-negative"):
        FunnelAnalyzer(stages=[("Leads", -50)])

    with pytest.raises(ValueError, match="non-empty string"):
        FunnelAnalyzer(stages=[("", 100)])

    with pytest.raises(TypeError):
        FunnelAnalyzer(stages=12345)  # type: ignore

    with pytest.raises(ValueError):
        FunnelAnalyzer(stages=["invalid_element"])  # type: ignore


def test_cli_execution():
    """Test executing the CLI directly via python."""
    result = subprocess.run(
        [sys.executable, "funnel_analyzer/cli.py"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "B2B SaaS GTM Full-Funnel Cohort Analysis" in result.stdout
    assert "Leads" in result.stdout
    assert "Won" in result.stdout

    # Test CLI with --json
    result_json = subprocess.run(
        [sys.executable, "funnel_analyzer/cli.py", "--json"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert '"top_of_funnel": 10000' in result_json.stdout
    assert '"bottom_of_funnel": 48' in result_json.stdout
