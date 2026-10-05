# 📊 GTM Funnel Analyzer

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)](https://python.org)
[![Tests Passing](https://img.shields.io/badge/Tests-Passing-success.svg)](tests/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/himanshugargnmims-cyber/gtm-funnel-analyzer)
[![Follow on GitHub](https://img.shields.io/github/followers/himanshugargnmims-cyber?label=Follow&style=social)](https://github.com/himanshugargnmims-cyber)

**Python SDK & CLI for B2B SaaS Full-Funnel Cohort & Conversion Analysis with Leaky Bucket Diagnostics & ASCII Visualization.**

</div>

---

## 🎯 Overview

In B2B SaaS revenue operations and growth engineering, understanding where prospect pipeline bleeds value is critical for capital efficiency. **GTM Funnel Analyzer** provides comprehensive stage-by-stage cohort conversion math, drop-off rate calculations, leaky bucket diagnosis, and terminal ASCII visual representations.

### The 7-Stage B2B SaaS Funnel Benchmark

```
        \  Leads: 10,000 (100.00%)                                 /
         \  MQL: 2,800 (28.00%)                                   /
          \  SAL: 1,400 (14.00%)                                 /
           \  SQL: 560 (5.60%)                                  /
             \  POC: 280 (2.80%)                               /
              \  Proposal: 140 (1.40%)                        /
                \  Won: 48 (0.48%)                          /
                  \________________________________________/
```

| Stage | Name | Benchmark Volume | Step Conversion | Drop-Off | Cumulative |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **0** | **Leads** (Inbound & Outbound Ingestion) | 10,000 | 100.00% | 0 | 100.00% |
| **1** | **MQL** (Marketing Qualified Leads) | 2,800 | 28.00% | -7,200 (72.0%) | 28.00% |
| **2** | **SAL** (Sales Accepted Leads) | 1,400 | 50.00% | -1,400 (50.0%) | 14.00% |
| **3** | **SQL** (Sales Qualified Opportunities) | 560 | 40.00% | -840 (60.0%) | 5.60% |
| **4** | **POC** (Proof of Concept / Technical Eval) | 280 | 50.00% | -280 (50.0%) | 2.80% |
| **5** | **Proposal** (Commercial Pricing & Security Review) | 140 | 50.00% | -140 (50.0%) | 1.40% |
| **6** | **Won** (Closed-Won Contract Execution) | 48 | 34.29% | -92 (65.7%) | 0.48% |

---

## 🚀 Key Features

- **⚡ Full-Funnel Cohort Diagnostics**: Step-by-step conversion percentages, volume drop-offs, and cumulative top-of-funnel conversion.
- **🔍 Automated Leaky Bucket Detection**: Automatically flags the **biggest volume leak** and the **tightest bottleneck stage**.
- **🎨 ASCII Visualization**: Terminal progress bars and silhouette funnel diagram for instant GTM review.
- **🛠️ Flexible Input Support**: Handles lists of tuples, dictionaries, and lists of dicts for custom funnel topologies.
- **💻 CLI & SDK**: Use either as a standalone command-line tool (with `--json` support) or import into automated RevOps pipelines.

---

## 📦 Installation

Clone the repository and install requirements:

```bash
git clone https://github.com/himanshugargnmims-cyber/gtm-funnel-analyzer.git
cd gtm-funnel-analyzer
pip install -r requirements.txt
```

---

## 💻 CLI Usage

### 1. Default Benchmark Analysis
Run the built-in 7-stage B2B funnel analysis:

```bash
python funnel_analyzer/cli.py
```

Output:
```text
================================================================================
                  B2B SaaS GTM Full-Funnel Cohort Analysis
================================================================================
Stage             Count   Step Conv   Cumulative  Progress Bar / Leaks
--------------------------------------------------------------------------------
Leads            10,000         ---      100.00%  [████████████████████████████████]
MQL               2,800      28.00%       28.00%  [█████████                       ] 🔻 -72.0% (-7,200)
SAL               1,400      50.00%       14.00%  [████                            ] 🔻 -50.0% (-1,400)
SQL                 560      40.00%        5.60%  [██                              ] 🔻 -60.0% (-840)
POC                 280      50.00%        2.80%  [█                               ] 🔻 -50.0% (-280)
Proposal            140      50.00%        1.40%  [                                ] 🔻 -50.0% (-140)
Won                  48      34.29%        0.48%  [                                ] 🔻 -65.7% (-92)
--------------------------------------------------------------------------------

  Funnel Silhouette Visualization:
   \  Leads: 10,000 (100.00%)                                 /
     \  MQL: 2,800 (28.00%)                                 /
       \  SAL: 1,400 (14.00%)                             /
         \  SQL: 560 (5.60%)                            /
           \  POC: 280 (2.80%)                        /
             \  Proposal: 140 (1.40%)               /
               \  Won: 48 (0.48%)                 /
                 \____________________________________/

--------------------------------------------------------------------------------
  🔍 Leaky Bucket Diagnostics & Insights:
   • Top of Funnel:       10,000 leads
   • Bottom of Funnel:    48 won accounts
   • Overall Conversion:  0.48%
   • Biggest Volume Leak: Leads → MQL (-7,200 lost, 72.00% drop)
   • Tightest Bottleneck: Leads → MQL (28.00% step conversion)
================================================================================
```

### 2. Custom Funnel via CLI
Pass customized stages directly:

```bash
python funnel_analyzer/cli.py --stages "Leads:5000,Demo:1200,Trial:400,Won:80"
```

### 3. Machine-Readable JSON Export
Emit structured JSON for RevOps workflows, dashboards, or Slack alerts:

```bash
python funnel_analyzer/cli.py --json
```

---

## 🐍 Python SDK Usage

Import `FunnelAnalyzer` directly into your data pipelines:

```python
from funnel_analyzer import FunnelAnalyzer

# 1. Default Benchmark Funnel
analyzer = FunnelAnalyzer()
analysis = analyzer.analyze()

print(f"Overall Conversion: {analysis['overall_conversion_pct']}%")
print(f"Biggest Leak: {analysis['biggest_volume_leak']['from_stage']} -> {analysis['biggest_volume_leak']['to_stage']}")

# 2. Custom Funnel Analysis
custom_stages = [
    ("Website Visitors", 50000),
    ("Signups", 3500),
    ("Activated Users", 1200),
    ("Paid Subscriptions", 240),
]

custom_analyzer = FunnelAnalyzer(stages=custom_stages)
custom_analyzer.print_funnel()
```

### Analysis Data Structure
The `.analyze()` method produces a dictionary:

```python
{
    "top_of_funnel": 10000,
    "bottom_of_funnel": 48,
    "overall_conversion_pct": 0.48,
    "stage_metrics": [
        {
            "name": "Leads",
            "count": 10000,
            "step_conversion_pct": 100.0,
            "cumulative_pct": 100.0,
            "drop_count": 0,
            "drop_pct": 0.0
        },
        ...
    ],
    "leaks": [...],
    "biggest_volume_leak": {
        "from_stage": "Leads",
        "to_stage": "MQL",
        "lost_count": 7200,
        "drop_rate_pct": 72.0,
        "step_conversion_pct": 28.0
    },
    "tightest_bottleneck": {
        "from_stage": "Leads",
        "to_stage": "MQL",
        "lost_count": 7200,
        "drop_rate_pct": 72.0,
        "step_conversion_pct": 28.0
    }
}
```

---

## 🧪 Testing

Run pytest test suite:

```bash
source .venv/bin/activate
PYTHONPATH=. pytest -v tests/
```

Test coverage includes:
- Default 7-stage B2B benchmark assertions (`top=10000`, `bottom=48`, 7 stages, overall > 0).
- Leaky bucket diagnostics and bottleneck calculations.
- Custom funnel ingestion (tuples, dicts, lists of dicts).
- Edge conditions (zero top of funnel, single stage, negative inputs).
- Terminal visual rendering and CLI execution validation.

---

## 📁 Repository Structure

```
gtm-funnel-analyzer/
├── funnel_analyzer/
│   ├── __init__.py         # Package exports & version
│   ├── analyzer.py         # FunnelAnalyzer core engine
│   └── cli.py              # CLI entrypoint with JSON & argument support
├── tests/
│   ├── __init__.py
│   └── test_analyzer.py    # Pytest test suite
├── .gitignore              # Ignored files & caches
├── LICENSE                 # MIT License
├── README.md               # Documentation & ASCII diagrams
└── requirements.txt        # Dependencies
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
