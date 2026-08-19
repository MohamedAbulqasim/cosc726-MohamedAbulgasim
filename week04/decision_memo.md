
# Decision Memo

## 1. What did you build?

We built a guarded support agent for Northwind Retail.
The system uses Pydantic models, a Step contract, four gates,
tool validation, bounded retries, progress detection, and trace auditing.

## 2. Which failure did no control catch?

The data-injection failure in Exercise 3 was not caught by Gates 1–4.
The model produced a final answer without making a tool call, so the
tool-level gates had no opportunity to intervene.

## 3. What would you add first?

I would add mandatory final-answer validation as Gate 5.
It should reject unsupported claims before the final answer is sent to the customer.

## 4. How often could the model not follow the contract?

Using Qwen/Qwen2.5-1.5B-Instruct:

- fence_or_prose: 24
- retries: 21
- gave_up: 0

This shows that the 1.5B model does not always follow the structured
output contract and therefore needs validation and bounded recovery.

## 5. Where does your agent still trust something it should not?

The agent can still trust untrusted customer text or its own unsupported
interpretation. Exercise 3 showed that an instruction embedded in the
customer email could influence the final answer.

## 6. What did this lab not tell you?

The results are specific to Qwen/Qwen2.5-1.5B-Instruct and should not be
generalized to frontier models.

Greedy decoding makes runs more comparable within the session, but it is
not a complete reproducibility plan.

Each exercise was run only once, so there is no variance estimate.

Five emails written by one person are a smoke test rather than a
representative evaluation set.
