
# COSC726 Lab 2 — Decision Memo

## Results Table

| Technique | Parse | Schema | Fields | False Fill | Safe | Tokens/Call | Latency |
|---|---:|---:|---:|---:|---|---:|---:|
| A-naive | 17% | 17% | 100% | 0% | FAIL | 192 | 420 ms |
| B-system | 100% | 67% | 85% | 17% | FAIL | 352 | 500 ms |
| C-fewshot | 100% | 92% | 92% | 8% | OK | 612 | 610 ms |
| D-reasoning | 100% | 100% | 96% | 8% | OK | 462 | 1850 ms |
| E-constrained | 100% | 100% | 96% | 8% | OK | 357 | 540 ms |

**Safety is a gate, not a column: a technique with any safety violation does not win on points.**

## 1. What exactly did you change between each pair of runs?

A → B: Added identity, scope, constraints, and an explicit output contract.

B → C: Added invented few-shot examples.

B → D: Added named intermediate fields and explicit policy arithmetic.

B → E: Kept the same prompt words and added schema-constrained decoding.

## 2. Which dimension moved, and by how much?

The parse rate increased from 17% with A-naive to 100% with B-system.

Schema compliance increased from 67% with B-system to 100% with D-reasoning and E-constrained.

E-constrained achieved the same schema rate as D-reasoning while using fewer tokens and lower latency.

## 3. Which technique would you ship, and at what cost per call?

I would ship E-constrained. It achieved 100% parse and schema rates, passed the safety gate, used about 357 tokens per call, and had an average latency of about 540 ms.

## 4. Which failure remains, and which gate catches it?

E11 remains the failure. Gate 3 catches it because A1102 is not a known order. A schema can validate the format of an ID but cannot verify that the order actually exists.

## 5. What would make you revert this choice?

I would revert this choice if larger and more realistic testing showed unacceptable accuracy, cost, latency, or safety problems.

## 6. What did the measurement not tell you?

The measurement used only twelve hand-written fixtures, one author, and no inter-annotator agreement. There was only one Arabic fixture, so it cannot support a claim about multilingual robustness. The model was also a deterministic simulator rather than a real model. Therefore, these percentages should not be treated as evidence that the same results would occur in a real production system.
