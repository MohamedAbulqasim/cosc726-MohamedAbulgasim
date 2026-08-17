
# Decision Memo — COSC726 Lab 3

## Model and Environment

- Model: Qwen/Qwen2.5-1.5B-Instruct
- Transformers: 5.13.1
- Pydantic: 2.13.4
- Repairs: `{'fence_or_prose': 4, 'retries': 3, 'gave_up': 0}`

---

## 1. What did you build, and which control caught which failure?

I built a ReAct support agent using Qwen/Qwen2.5-1.5B-Instruct, Pydantic validation, four pre-execution gates, a dispatcher, a controller loop, tracing, and a fifth gate for final-answer validation.

- Gate 1 checks whether the selected tool is known.
- Gate 2 validates the tool arguments against the Pydantic argument model.
- Gate 3 checks whether the order ID actually exists.
- Gate 4 protects consequential actions and checks that the required evidence and policy conditions exist.
- Gate 5 checks whether final-answer claims are supported by the trace.

The no-progress detector also stops the agent when it repeatedly makes the same tool call without making progress.

---

## 2. Which failure did no control catch, and why not?

Gates 1–4 cannot directly catch an unsupported claim in the final answer.

For example, the model could claim that an order was already refunded even though no tool result confirmed that. The tool calls themselves may be valid, so the failure occurs in the final answer rather than in a tool call.

This is why the fifth output-validation gate is needed. It checks the final answer against the recorded trace.

---

## 3. What would you add first, and why that first?

I would add the fifth output-validation gate first.

It provides a final safety check between the agent's reasoning and the customer-facing answer. It can prevent unsupported claims such as saying that a refund was completed when no tool confirmed it.

---

## 4. How often could the model not follow the contract?

The model used was Qwen/Qwen2.5-1.5B-Instruct.

The recorded repair statistics were:

- `fence_or_prose`: 4
- `retries`: 3
- `gave_up`: 0

Therefore, the model failed to follow the output contract four times and required three retries. It never completely gave up after the allowed retries.

This shows that a 1.5B model should not be trusted to follow a strict JSON and tool contract without validation, repair, and bounded retries in production. These failures can also increase latency and token usage.

---

## 5. Where does your agent still trust something it should not?

The agent still relies on the model to interpret customer intent and select the correct next action.

For example, in the out-of-scope billing case, the model repeatedly called the late-delivery policy tool instead of escalating to a human. The business rule that billing disputes are out of scope exists in the prompt, but it is not enforced by a dedicated gate.

Therefore, the system still trusts the model to correctly interpret some important business rules.

---

## 6. What did this lab not tell you?

This lab did not establish general model reliability.

First, it used Qwen/Qwen2.5-1.5B-Instruct, whose failure profile may be different from a frontier model.

Second, greedy decoding (`do_sample=False`) makes runs more comparable within a session, but it is not a complete reproducibility plan.

Third, each exercise was run only once. Therefore, there is no variance estimate and we cannot determine how stable the observed behavior is across repeated runs.

Fourth, the evaluation used only five hand-written emails written by one author. This is a smoke test rather than a representative evaluation dataset, and there was no inter-annotator agreement.

Finally, the results were obtained from a specific model and environment:

- Model: Qwen/Qwen2.5-1.5B-Instruct
- Transformers: 5.13.1
- Pydantic: 2.13.4

Therefore, these results should be treated as observations from this specific setup, not as general claims about the reliability of ReAct agents or language models.
