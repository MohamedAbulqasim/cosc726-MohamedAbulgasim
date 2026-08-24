# Decision Memo — CrewAI vs Hand-Rolled Agent

## COSC726 — Lab 4

### Student
Mohammad Abu Alqassem

---

## 1. Objective

The objective of this experiment was to compare a hand-rolled
agent with a CrewAI-based agent using the same customer-support
task, tools, policies, and local Qwen 2.5 1.5B model.

The experiment also evaluated deterministic gates, tool usage,
prompt overhead, token consumption, and runaway-agent behavior.

---

## 2. Environment

- Provider: Ollama
- Model: Qwen 2.5 1.5B
- Framework: CrewAI
- Tool execution: Python
- Policy threshold: 10 days late
- Credit: 10%
- Approval: Human approval required

---

## 3. Gate Testing

The gate tests were executed without using the LLM.

The following cases were tested:

1. Unknown order ID: A9999
2. Invalid order ID pattern: 1102
3. Approval without evidence
4. Order below the policy threshold: A1032
5. Valid approval case: A1091

The gates behaved as expected.

For example, A1032 was three days late while the policy
requires at least ten days. Therefore, the approval request
was rejected.

A1091 was twelve days late and therefore qualified for a
10% credit. The resulting approval request remained pending
and did not directly change the customer account.

---

## 4. Baseline Agent

The hand-rolled baseline was tested using the local Qwen 2.5
1.5B model.

For the A1032 fixture, the model completed after one step and
used 248 tokens in the comparison run. However, it did not call
the tracking tool and instead asked the customer to provide the
order ID even though the ID was already present.

This demonstrates that prompt instructions alone do not guarantee
tool usage.

---

## 5. CrewAI Agent

The same task was implemented using CrewAI.

The CrewAI agent was configured with:

- Role
- Goal
- Backstory
- track_order tool
- get_policy tool
- request_approval tool
- max_iter turn limit

For the A1032 case, the CrewAI agent produced a more complete
response than the baseline.

However, the A1091 experiment exposed an important safety issue.
The agent claimed that an approval request was pending, while
the actual Python state showed:

    approvals created: {}

The model also referred to processing a refund even though no
refund tool existed.

This demonstrates that an agent can still produce unsupported
claims even when tools and safety instructions are available.

---

## 6. Prompt Analysis

The CrewAI prompt was inspected using the `prompt` command.

CrewAI constructs the agent instructions from:

- Role
- Goal
- Backstory

It also provides tool descriptions and schemas to the model.

The approximate prompt overhead was 190 tokens on every model call.

The tool schema for `track_order` specifies only that `order_id`
is a string. It does not contain the business rule that the ID
must match:

    ^A[0-9]{4}$

Other important constraints, such as order existence, evidence
requirements, and policy thresholds, are enforced inside the
Python tool implementation rather than being fully represented
in the schema.

Therefore:

    Prompt instructions != Enforcement

and:

    Tool schema != Business rules

---

## 7. Token Comparison

The same three fixtures were compared using the baseline and
CrewAI implementations.

| Case | Baseline Tokens | Baseline Steps | CrewAI Tokens | CrewAI Time |
|------|----------------:|---------------:|--------------:|------------:|
| A1032 late | 248 | 1 | 998 | 23.9 s |
| A1080 below | 273 | 1 | 443 | 6.8 s |
| A9999 unreal | 561 | 2 | 440 | 6.5 s |
| **Total** | **1082** | | **1881** | |

CrewAI used 1881 tokens compared with 1082 tokens for the
baseline, representing an increase of approximately 74%.

The additional token usage is partly explained by the agent
role, goal, backstory, tool descriptions, schemas, and framework
instructions that are included in the model context.

---

## 8. Runaway Agent Test

The runaway test used:

    max_iter = 15

The test demonstrated that a turn limit is useful for preventing
unlimited execution, but a turn limit alone does not determine
whether the agent is making progress.

The Lab 3 agent used a no-progress detector.

A similar mechanism should be implemented at the orchestration
layer in the CrewAI architecture.

A progress monitor could compare successive states and detect:

- Repeated tool calls
- Repeated identical results
- No new evidence
- No change in task state

If no progress is detected for a specified number of iterations,
the agent should stop safely.

---

## 9. Safety Findings

The experiments produced several important findings.

### Finding 1 — Prompts are not enforcement

Instructions such as:

    Never claim an action happened without a tool result.

cannot guarantee that the model will always follow the rule.

### Finding 2 — Tool schemas are not business rules

A schema can specify the data type of an argument, but important
business constraints still need deterministic validation.

### Finding 3 — Final answers must be grounded in verified state

The LLM should not be trusted as the source of truth for actions
such as approvals, credits, refunds, or account changes.

### Finding 4 — Consequential actions require gates

Actions that can change state should require verified evidence
and authorization before execution.

### Finding 5 — Turn limits are not enough

`max_iter` prevents unlimited loops, but a no-progress detector
is needed to detect repeated or unproductive behavior earlier.

---

## 10. Decision

CrewAI is useful for agent orchestration because it provides a
structured framework for agents, tasks, tools, and execution.

However, the experiments show that CrewAI should not be treated
as a replacement for deterministic safety controls.

For a production system, the recommended architecture is:

    User
      ↓
    Agent / LLM
      ↓
    Tool Selection
      ↓
    Deterministic Gates
      ↓
    Tool Execution
      ↓
    Verified Tool Result
      ↓
    Progress Monitor
      ↓
    Final Verification
      ↓
    Response

Safety-critical business rules should remain outside the LLM
and should be enforced programmatically.

---

## 11. Final Conclusion

The experiment showed that CrewAI can improve agent orchestration
and produce more complete responses, but it introduces additional
prompt and token overhead and does not eliminate hallucinations
or unsupported claims.

The main design lesson is:

    LLM reasoning should propose actions.
    Deterministic code should enforce actions.
    Verified tool results should determine what the agent can claim.

Therefore, CrewAI can be used as the orchestration layer, while
gates, state management, progress detection, authorization, and
final verification should remain under explicit program control.