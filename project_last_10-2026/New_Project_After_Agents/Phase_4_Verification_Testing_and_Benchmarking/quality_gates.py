"""
Phase 4 Quality Gates:
- Gate 4.1: Automated Test Suite 100% Pass Gate
- Gate 4.2: Real-Time Latency & Production Reliability Gate
"""

class Phase4QualityGates:
    @staticmethod
    def verify_gate_4_1_test_suite_pass(total_tests: int, failed_tests: int) -> dict:
        """Verifies that all automated unit and integration tests passed without exception."""
        issues = []
        if failed_tests > 0:
            issues.append(f"{failed_tests} tests failed out of {total_tests} executed.")
        if total_tests < 5:
            issues.append(f"Insufficient test volume ({total_tests} tests).")

        passed = len(issues) == 0
        return {
            'gate_name': 'Gate 4.1: Automated Test Suite 100% Pass Gate',
            'passed': passed,
            'total_tests': total_tests,
            'failed_tests': failed_tests,
            'issues': issues,
            'details': f"Zero test failures: all {total_tests} automated tests passed successfully." if passed else str(issues)
        }

    @staticmethod
    def verify_gate_4_2_latency_performance(benchmark_summary: dict) -> dict:
        """Verifies that average pipeline latency meets clinical real-time standards (< 350ms)."""
        issues = []
        mean_lat = benchmark_summary.get('mean_latency_ms', 1000.0)
        p95_lat = benchmark_summary.get('p95_latency_ms', 1000.0)

        if mean_lat > 350.0:
            issues.append(f"Mean latency {mean_lat:.2f}ms exceeds real-time limit 350ms.")
        if p95_lat > 600.0:
            issues.append(f"P95 latency {p95_lat:.2f}ms exceeds tolerance 600ms.")

        passed = len(issues) == 0
        return {
            'gate_name': 'Gate 4.2: Real-Time Latency & Production Reliability Gate',
            'passed': passed,
            'mean_latency_ms': mean_lat,
            'p95_latency_ms': p95_lat,
            'issues': issues,
            'details': f"Real-time benchmark certified: Mean latency = {mean_lat:.2f}ms, P95 = {p95_lat:.2f}ms." if passed else str(issues)
        }
