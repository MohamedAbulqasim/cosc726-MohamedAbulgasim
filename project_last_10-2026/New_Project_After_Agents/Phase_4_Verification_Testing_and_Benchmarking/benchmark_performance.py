"""
Phase 4: Latency & Performance Benchmarking Script
Measures multi-agent pipeline latency, component breakdown, and throughput.
"""

import os
import sys
import time
import json
import numpy as np

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, '..'))
P2_DIR = os.path.join(PARENT_DIR, 'Phase_2_Multi_Agent_Architecture')

sys.path.append(P2_DIR)
from schemas import PatientInput
from agent_orchestrator import ClinicalAgentOrchestrator

def run_benchmark(num_iterations: int = 30) -> dict:
    orchestrator = ClinicalAgentOrchestrator()
    patient = PatientInput(
        patient_id="BENCH-01",
        glucose=135.0,
        bmi=28.4,
        age=42
    )

    # Warmup
    _ = orchestrator.run_pipeline(patient)

    latencies_ms = []
    agent_latencies = {
        'triage': [],
        'diagnostic': [],
        'reasoning': [],
        'lifestyle': [],
        'gatekeeper': []
    }

    for _ in range(num_iterations):
        t0 = time.perf_counter()
        
        # Component timing
        t_tri0 = time.perf_counter()
        triage_res = orchestrator.triage_agent.execute(patient)
        agent_latencies['triage'].append((time.perf_counter() - t_tri0) * 1000)

        t_diag0 = time.perf_counter()
        diag_res = orchestrator.diagnostic_agent.execute(triage_res)
        agent_latencies['diagnostic'].append((time.perf_counter() - t_diag0) * 1000)

        t_reas0 = time.perf_counter()
        reason_res = orchestrator.reasoning_agent.execute(patient, diag_res)
        agent_latencies['reasoning'].append((time.perf_counter() - t_reas0) * 1000)

        t_life0 = time.perf_counter()
        life_res = orchestrator.lifestyle_agent.execute(patient, diag_res)
        agent_latencies['lifestyle'].append((time.perf_counter() - t_life0) * 1000)

        t_gate0 = time.perf_counter()
        gate_res = orchestrator.gatekeeper_agent.execute(patient, triage_res, diag_res, reason_res, life_res)
        agent_latencies['gatekeeper'].append((time.perf_counter() - t_gate0) * 1000)

        total_ms = (time.perf_counter() - t0) * 1000
        latencies_ms.append(total_ms)

    benchmark_summary = {
        'iterations': num_iterations,
        'mean_latency_ms': float(np.mean(latencies_ms)),
        'std_latency_ms': float(np.std(latencies_ms)),
        'min_latency_ms': float(np.min(latencies_ms)),
        'max_latency_ms': float(np.max(latencies_ms)),
        'p50_latency_ms': float(np.percentile(latencies_ms, 50)),
        'p95_latency_ms': float(np.percentile(latencies_ms, 95)),
        'throughput_requests_per_sec': float(1000.0 / np.mean(latencies_ms)),
        'component_mean_ms': {
            k: float(np.mean(v)) for k, v in agent_latencies.items()
        }
    }
    return benchmark_summary

if __name__ == "__main__":
    summary = run_benchmark(20)
    print(json.dumps(summary, indent=4))
