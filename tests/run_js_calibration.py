#!/usr/bin/env python3
"""Exécute runCalibrationVerificationSuite() via Chrome headless (logique JS réelle)."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")


def extract_block(source: str, start_marker: str, end_marker: str) -> str:
    start = source.index(start_marker)
    end = source.index(end_marker, start)
    return source[start:end]


def build_runner_html(index_source: str) -> str:
    constants = extract_block(
        index_source,
        "const BRANCH_COMMON_MAX = 30000;",
        "const BRANCH_BOISSY_MAX = 47200;",
    )
    constants += "\nconst BRANCH_BOISSY_MAX = 47200;\n"
    calib_const = extract_block(
        index_source,
        "const CALIBRATION_SINGLE_RADIUS = 1200;",
        "let calibrationSegments = { central: [], boissy: [], chessy: [] };",
    )
    calib_const += "\nlet calibrationSegments = { central: [], boissy: [], chessy: [] };\n"
    logic = extract_block(
        index_source,
        "function normalizeBranchKey(branchKey) {",
        "window.runCalibrationVerificationSuite = runCalibrationVerificationSuite;",
    )
    detect = extract_block(
        index_source,
        "function detectBranchForPk(pk, nameHint = null, addressHint = null) {",
        'return "central";\n  }',
    ) + "\n  }"

    return f"""<!DOCTYPE html>
<html lang="fr"><head><meta charset="utf-8"><title>calib js test</title></head>
<body><pre id="out">running</pre>
<script>
{constants}
{calib_const}
let pkOffset = 0;
function roughBranchFromLatLon() {{ return null; }}
{detect}
{logic}
try {{
  const report = runCalibrationVerificationSuite({{ verbose: false }});
  document.getElementById("out").textContent = JSON.stringify(report);
}} catch (err) {{
  document.getElementById("out").textContent = JSON.stringify({{ error: String(err), stack: err && err.stack }});
}}
</script></body></html>"""


def run_chrome(html_path: Path) -> dict:
    if not CHROME.is_file():
        return {"error": "Chrome introuvable", "summary": {"pass": False, "total": 0, "failed": []}, "results": []}
    url = html_path.as_uri()
    proc = subprocess.run(
        [
            str(CHROME),
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--no-first-run",
            "--allow-file-access-from-files",
            "--virtual-time-budget=10000",
            "--dump-dom",
            url,
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    match = re.search(r'<pre id="out">(.*?)</pre>', proc.stdout, re.DOTALL)
    if not match:
        return {
            "error": "Impossible de lire la sortie Chrome",
            "stdout_tail": proc.stdout[-2000:],
            "stderr_tail": proc.stderr[-2000:],
            "summary": {"pass": False, "total": 0, "failed": []},
            "results": [],
        }
    payload = match.group(1).strip()
    payload = payload.replace("&quot;", '"').replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    return json.loads(payload)


def main() -> int:
    index_source = INDEX.read_text(encoding="utf-8")
    html = build_runner_html(index_source)
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as tmp:
        tmp.write(html)
        html_path = Path(tmp.name)

    report = run_chrome(html_path)
    html_path.unlink(missing_ok=True)

    if "error" in report and "summary" not in report:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1

    if report.get("error"):
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1

    results = report.get("results", [])
    failed = [r for r in results if not r.get("pass")]
    summary = report.get("summary", {})
    total = summary.get("total", len(results))
    passed = total - len(failed)
    print(json.dumps(results, ensure_ascii=False, indent=2))
    print(f"\nRésumé JS: {passed}/{total} tests OK")
    if failed:
        print("Échecs JS:")
        for item in failed:
            print(f"- {item.get('name')}: {item.get('details')}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
