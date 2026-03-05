import os
import subprocess
import tempfile
import time
from dataclasses import dataclass

from django.utils import timezone

from .models import Submission


@dataclass
class TestExecutionResult:
    passed: bool
    stdout: str
    stderr: str
    execution_time_ms: int
    timed_out: bool = False


def normalize_output(output: str) -> str:
    lines = [line.rstrip() for line in output.strip().splitlines()]
    return "\n".join(lines)


def run_python_code(source_code: str, stdin_data: str, timeout_seconds: float) -> TestExecutionResult:
    with tempfile.TemporaryDirectory() as tmp_dir:
        script_path = os.path.join(tmp_dir, "solution.py")
        with open(script_path, "w", encoding="utf-8") as script_file:
            script_file.write(source_code)

        started = time.perf_counter()
        try:
            completed = subprocess.run(
                ["python", script_path],
                input=stdin_data,
                text=True,
                capture_output=True,
                timeout=timeout_seconds,
                check=False,
            )
            elapsed_ms = int((time.perf_counter() - started) * 1000)
            passed = completed.returncode == 0
            return TestExecutionResult(
                passed=passed,
                stdout=completed.stdout,
                stderr=completed.stderr,
                execution_time_ms=elapsed_ms,
            )
        except subprocess.TimeoutExpired:
            elapsed_ms = int((time.perf_counter() - started) * 1000)
            return TestExecutionResult(
                passed=False,
                stdout="",
                stderr=f"Execution timed out after {timeout_seconds:.2f}s",
                execution_time_ms=elapsed_ms,
                timed_out=True,
            )


def grade_submission(submission: Submission) -> Submission:
    task = submission.task
    test_cases = task.test_cases.order_by("order_index", "id")

    submission.status = Submission.Status.RUNNING
    submission.total_tests = test_cases.count()
    submission.passed_tests = 0
    submission.score = 0
    submission.stdout = ""
    submission.stderr = ""
    submission.execution_time_ms = 0
    submission.save(update_fields=[
        "status",
        "total_tests",
        "passed_tests",
        "score",
        "stdout",
        "stderr",
        "execution_time_ms",
        "updated_at",
    ])

    if submission.total_tests == 0:
        submission.status = Submission.Status.ERROR
        submission.stderr = "No test cases configured for this task."
        submission.evaluated_at = timezone.now()
        submission.save(update_fields=["status", "stderr", "evaluated_at", "updated_at"])
        return submission

    total_weight = sum(test.weight for test in test_cases) or 1
    timeout_seconds = max(task.time_limit_ms, 100) / 1000
    collected_stdout = []
    collected_stderr = []
    total_time_ms = 0
    earned_weight = 0
    timed_out = False

    for index, test_case in enumerate(test_cases, start=1):
        result = run_python_code(submission.source_code, test_case.input_data, timeout_seconds)
        total_time_ms += result.execution_time_ms

        actual = normalize_output(result.stdout)
        expected = normalize_output(test_case.expected_output)
        case_passed = result.passed and not result.timed_out and actual == expected

        if case_passed:
            submission.passed_tests += 1
            earned_weight += test_case.weight
        elif result.timed_out:
            timed_out = True

        collected_stdout.append(f"[Test {index}]\n{result.stdout}".strip())
        if result.stderr:
            collected_stderr.append(f"[Test {index}] {result.stderr}".strip())

    submission.execution_time_ms = total_time_ms
    submission.score = int((earned_weight / total_weight) * task.max_score)
    submission.stdout = "\n\n".join(filter(None, collected_stdout))
    submission.stderr = "\n".join(filter(None, collected_stderr))
    submission.evaluated_at = timezone.now()

    if timed_out:
        submission.status = Submission.Status.TIMEOUT
    elif submission.passed_tests == submission.total_tests:
        submission.status = Submission.Status.PASSED
    else:
        submission.status = Submission.Status.FAILED

    submission.save(update_fields=[
        "passed_tests",
        "score",
        "stdout",
        "stderr",
        "execution_time_ms",
        "status",
        "evaluated_at",
        "updated_at",
    ])
    return submission
