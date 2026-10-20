"""
Phase 4 Verification Runner:
Executes the comprehensive automated test suite and latency benchmarks,
evaluating Gate 4.1 (Zero Failures) and Gate 4.2 (Latency & Reliability).
"""

import os
import sys
import json
import pytest

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
from benchmark_performance import run_benchmark
from quality_gates import Phase4QualityGates

def run_verification():
    print("=" * 70)
    print("  PHASE 4: VERIFICATION TESTING, BENCHMARKING & AUDIT")
    print("=" * 70)

    # Step 1: Run Pytest Suite
    print("\n[STEP 1] Running Automated Clinical Gates and Stress Testing Suites...")
    test_files = [
        os.path.join(CURRENT_DIR, "test_clinical_gates.py"),
        os.path.join(CURRENT_DIR, "test_edge_cases.py")
    ]
    
    # Run pytest capturing exit code
    ret_code = pytest.main(["-v", "-s"] + test_files)
    pytest_passed = (ret_code == 0)

    # Step 2: Run Latency Benchmarking
    print("\n[STEP 2] Running Latency & Throughput Benchmark across 25 Inferences...")
    bench_results = run_benchmark(num_iterations=25)
    print(f" -> Mean Pipeline Latency: {bench_results['mean_latency_ms']:.2f} ms")
    print(f" -> P95 Latency: {bench_results['p95_latency_ms']:.2f} ms")
    print(f" -> Throughput: {bench_results['throughput_requests_per_sec']:.1f} requests/sec")
    print(f" -> Component Breakdown (ms): {bench_results['component_mean_ms']}")

    # Step 3: Verify Phase 4 Quality Gates
    print("\n" + "-" * 70)
    print("VERIFYING PHASE 4 QUALITY GATES")
    print("-" * 70)

    gate_4_1 = Phase4QualityGates.verify_gate_4_1_test_suite_pass(
        total_tests=10,
        failed_tests=0 if pytest_passed else 1
    )
    print(f" -> {gate_4_1['gate_name']}: {'PASSED [OK]' if gate_4_1['passed'] else 'FAILED [X]'}")
    print(f"    Details: {gate_4_1['details']}")

    gate_4_2 = Phase4QualityGates.verify_gate_4_2_latency_performance(bench_results)
    print(f" -> {gate_4_2['gate_name']}: {'PASSED [OK]' if gate_4_2['passed'] else 'FAILED [X]'}")
    print(f"    Details: {gate_4_2['details']}")

    all_passed = gate_4_1['passed'] and gate_4_2['passed']

    # Step 4: Save Logs
    log_data = {
        'gate_4_1': gate_4_1,
        'gate_4_2': gate_4_2,
        'benchmarks': bench_results,
        'all_gates_passed': all_passed
    }
    with open(os.path.join(CURRENT_DIR, "phase4_gates_log.json"), 'w', encoding='utf-8') as f:
        json.dump(log_data, f, indent=4, ensure_ascii=False)

    print("\n" + "=" * 70)
    if all_passed:
        print(" [ALL GATES PASSED] Phase 4 Comprehensive Verification Certified!")
    else:
        print(" [GATE FAILURE] Phase 4 issues detected.")
    print("=" * 70)

    return all_passed

if __name__ == "__main__":
    success = run_verification()
    sys.exit(0 if success else 1)
