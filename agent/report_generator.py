"""Report Generator - runs pytest and produces HTML reports."""

import os
import subprocess
import json
from datetime import datetime
from typing import Dict, List


def run_tests_and_report(output_dir: str, headed: bool = False) -> Dict:
    """Execute generated tests via pytest and return a summary."""
    reports_dir = os.path.join(output_dir, "reports")
    os.makedirs(reports_dir, exist_ok=True)

    report_html = os.path.join(reports_dir, "report.html")
    cmd = [
        "python", "-m", "pytest",
        os.path.join(output_dir, "tests"),
        f"--html={report_html}",
        "--self-contained-html",
        "-v",
    ]
    if headed:
        cmd.append("--headed")

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=output_dir,
        timeout=300,
    )

    summary = {
        "timestamp": datetime.now().isoformat(),
        "return_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "report_path": report_html,
        "status": "passed" if result.returncode == 0 else "failed",
    }

    summary_path = os.path.join(reports_dir, "run_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    return summary


def generate_execution_report(
    execution_log: List[Dict], output_dir: str
) -> str:
    """Generate an HTML execution report from the browser agent log."""
    reports_dir = os.path.join(output_dir, "reports")
    os.makedirs(reports_dir, exist_ok=True)

    total = len(execution_log)
    passed = sum(1 for e in execution_log if e["status"] == "passed")
    failed = sum(1 for e in execution_log if e["status"] == "failed")
    skipped = sum(1 for e in execution_log if e["status"] == "skipped")

    rows = ""
    for entry in execution_log:
        status_class = {
            "passed": "status-pass",
            "failed": "status-fail",
            "skipped": "status-skip",
        }.get(entry["status"], "")
        error_cell = f'<span class="error-text">{entry["error"]}</span>' if entry["error"] else "-"
        rows += f"""
        <tr>
            <td>{entry["step_number"]}</td>
            <td>{entry["original_text"]}</td>
            <td>{entry["action"]}</td>
            <td>{entry["page_name"]}</td>
            <td class="{status_class}">{entry["status"].upper()}</td>
            <td>{error_cell}</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Execution Report</title>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; margin: 2rem; background: #f5f5f5; }}
        h1 {{ color: #1a1a2e; }}
        .summary {{ display: flex; gap: 1rem; margin-bottom: 1.5rem; }}
        .summary-card {{ padding: 1rem 1.5rem; border-radius: 8px; color: #fff; font-size: 1.1rem; }}
        .card-total {{ background: #2d3436; }}
        .card-pass {{ background: #00b894; }}
        .card-fail {{ background: #d63031; }}
        .card-skip {{ background: #fdcb6e; color: #2d3436; }}
        table {{ width: 100%; border-collapse: collapse; background: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        th {{ background: #1a1a2e; color: #fff; padding: 0.75rem; text-align: left; }}
        td {{ padding: 0.75rem; border-bottom: 1px solid #eee; }}
        tr:hover {{ background: #f8f9fa; }}
        .status-pass {{ color: #00b894; font-weight: 600; }}
        .status-fail {{ color: #d63031; font-weight: 600; }}
        .status-skip {{ color: #f39c12; font-weight: 600; }}
        .error-text {{ color: #d63031; font-size: 0.85rem; }}
    </style>
</head>
<body>
    <h1>🧪 Execution Report</h1>
    <p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    <div class="summary">
        <div class="summary-card card-total">Total: {total}</div>
        <div class="summary-card card-pass">Passed: {passed}</div>
        <div class="summary-card card-fail">Failed: {failed}</div>
        <div class="summary-card card-skip">Skipped: {skipped}</div>
    </div>
    <table>
        <thead>
            <tr>
                <th>#</th>
                <th>Step</th>
                <th>Action</th>
                <th>Page</th>
                <th>Status</th>
                <th>Error</th>
            </tr>
        </thead>
        <tbody>{rows}
        </tbody>
    </table>
</body>
</html>"""

    report_path = os.path.join(reports_dir, "execution_report.html")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html)

    return report_path
