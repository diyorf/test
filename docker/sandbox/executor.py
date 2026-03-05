import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def normalize_output(output: str) -> str:
    lines = [line.rstrip() for line in output.strip().splitlines()]
    return "\n".join(lines)


def main() -> None:
    payload = json.loads(sys.stdin.read() or "{}")
    source_code = payload.get("source_code", "")
    tests = payload.get("tests", [])
    time_limit_ms = int(payload.get("time_limit_ms", 2000))

    started = time.perf_counter()
    results = []
    passed = 0

    with tempfile.TemporaryDirectory() as tmp:
        script = Path(tmp) / "solution.py"
        script.write_text(source_code, encoding="utf-8")

        for idx, test in enumerate(tests, start=1):
            timeout = max(time_limit_ms, 100) / 1000
            case_start = time.perf_counter()
            try:
                completed = subprocess.run(
                    ["python", str(script)],
                    input=test.get("input", ""),
                    text=True,
                    capture_output=True,
                    timeout=timeout,
                    check=False,
                )
                elapsed = int((time.perf_counter() - case_start) * 1000)
                actual = normalize_output(completed.stdout)
                expected = normalize_output(test.get("expected", ""))
                ok = completed.returncode == 0 and actual == expected
                passed += int(ok)
                results.append(
                    {
                        "index": idx,
                        "passed": ok,
                        "execution_time_ms": elapsed,
                        "stdout": completed.stdout,
                        "stderr": completed.stderr,
                    }
                )
            except subprocess.TimeoutExpired:
                elapsed = int((time.perf_counter() - case_start) * 1000)
                results.append(
                    {
                        "index": idx,
                        "passed": False,
                        "execution_time_ms": elapsed,
                        "stdout": "",
                        "stderr": f"Timeout after {timeout:.2f}s",
                    }
                )

    total = len(results)
    total_time = int((time.perf_counter() - started) * 1000)
    print(
        json.dumps(
            {
                "passed_tests": passed,
                "failed_tests": max(total - passed, 0),
                "total_tests": total,
                "execution_time_ms": total_time,
                "results": results,
            }
        )
    )


if __name__ == "__main__":
    main()
