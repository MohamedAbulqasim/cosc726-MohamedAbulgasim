"""
COSC726 - Lab 3
hello_agent.py

Contains the Lab 3 gates, dispatcher, and controller loop.
The code is designed to work with the objects created in the notebook:
Step, Trace, TraceStep, Stop, StopReason, TOOLS, Tier, OBSERVED, err,
propose_step, and KNOWN_ORDER_IDS.
"""

from typing import Any
from pydantic import BaseModel, ValidationError


class GateError(Exception):
    """Structured validation/permission failure exposed to the controller."""
    def __init__(self, code: str, detail: str = ""):
        super().__init__(detail or code)
        self.code = code
        self.detail = detail


def gate_2_conforms(args: dict, args_model: type[BaseModel]) -> None:
    """Validate tool arguments against the tool's Pydantic model."""
    try:
        args_model.model_validate(args)
    except ValidationError as exc:
        detail = exc.errors()[0]
        location = ".".join(str(x) for x in detail.get("loc", ())) or "args"
        raise GateError(
            "gate2",
            f"{location}: {detail.get('msg', 'invalid arguments')}"
        ) from exc


def gate_3_refers(args: dict) -> None:
    """When an order_id is supplied, it must refer to a known order."""
    order_id = args.get("order_id")
    if order_id is not None and order_id not in KNOWN_ORDER_IDS:
        raise GateError(
            "gate3",
            f"order_id {order_id!r} is not a known order"
        )


def gate_4_coheres(name: str, args: dict, trace) -> None:
    """
    request_approval is allowed only after:
      1. a successful track_order call,
      2. a successful policy lookup,
      3. observed days_late >= policy threshold.
    """
    if name != "request_approval":
        return

    successful_tools = [
        s.tool for s in trace.steps
        if s.tool and s.ok is True
    ]

    if "track_order" not in successful_tools:
        raise GateError(
            "missing_order_lookup",
            "request_approval requires a successful track_order lookup first"
        )

    if "get_late_delivery_policy" not in successful_tools:
        raise GateError(
            "missing_policy_lookup",
            "request_approval requires a successful policy lookup first"
        )

    days_late = OBSERVED.get("days_late")
    if days_late is None:
        raise GateError(
            "missing_days_late",
            "request_approval requires observed days_late"
        )

    threshold = POLICY_THRESHOLD_DAYS
    if days_late < threshold:
        raise GateError(
            "below_threshold",
            f"days_late={days_late} is below threshold={threshold}"
        )


def require_tier(tier: Tier, allow_consequential: bool) -> None:
    """Prevent consequential actions unless explicitly permitted."""
    if tier == Tier.CONSEQUENTIAL and not allow_consequential:
        raise GateError(
            "consequential_not_allowed",
            "consequential tools require explicit permission"
        )


def dispatch(
    step: Step,
    trace: Trace,
    allow_consequential: bool = True
):
    """
    Validate, permit, then execute a proposed tool call.

    Returns:
        (structured observation, TraceStep)
    """
    tstep = TraceStep(
        step=len(trace.steps) + 1,
        tool=step.action,
        args=step.args,
        thought=step.thought,
    )

    # Gate 1: tool exists.
    spec = TOOLS.get(step.action)
    if spec is None:
        tstep.ok = False
        tstep.error = "unknown_tool"
        tstep.state_changed = False
        return err(
            "unknown_tool",
            name=step.action,
            hint=f"Available: {', '.join(sorted(TOOLS))}."
        ), tstep

    tstep.tier = spec.tier.value

    try:
        # Gate 2: argument shape/types.
        gate_2_conforms(step.args, spec.args_model)

        # Gate 3: references known entities.
        gate_3_refers(step.args)

        # Gate 4: workflow/policy coherence.
        gate_4_coheres(step.action, step.args, trace)

        # Tier permission check.
        require_tier(spec.tier, allow_consequential)

    except GateError as exc:
        tstep.ok = False
        tstep.error = exc.code
        tstep.state_changed = False
        return err(exc.code, detail=exc.detail), tstep

    # Execute only after every check succeeds.
    try:
        result = spec.fn(**step.args)
    except Exception as exc:
        tstep.ok = False
        tstep.error = "tool_exception"
        tstep.state_changed = False
        return err("tool_exception", detail=str(exc)), tstep

    tstep.ok = bool(result.get("ok", False))
    tstep.error = None if tstep.ok else result.get("error", "tool_error")

    # Track state-changing tools.
    tstep.state_changed = (
        step.action in STATE_CHANGING and tstep.ok
    )

    # Stash observed facts needed by Gate 4.
    if step.action == "track_order" and tstep.ok:
        OBSERVED["days_late"] = result.get("days_late")

    return result, tstep


def run(
    email: str,
    max_steps: int = 6,
    token_budget: int = 20_000,
    allow_consequential: bool = True,
    run_id: str = "run",
) -> Trace:
    """
    Controller loop.

    Controls:
      - turn/step cap
      - token budget
      - repeated identical-call / no-progress detection
      - escalation
      - malformed model output
      - explicit CAPPED fall-through
    """
    OBSERVED["days_late"] = None
    trace = Trace(run_id=run_id)
    observations: list[str] = []
    previous_calls: set[tuple[str, str]] = set()

    for _ in range(max_steps):
        # Token budget before requesting another model step.
        if trace.total_tokens >= token_budget:
            trace.stop = Stop(
                StopReason.CAPPED,
                detail="token budget exhausted"
            )
            return trace

        system = SYSTEM
        user = (
            f"CUSTOMER EMAIL:\n{email}\n\n"
            f"OBSERVATIONS:\n"
            f"{chr(10).join(observations[-6:]) if observations else '(none)'}\n\n"
            "Your next step:"
        )

        step, raw, tokens = propose_step(system, user)

        if step is None:
            trace.add(
                TraceStep(
                    step=len(trace.steps) + 1,
                    tool=None,
                    thought="Model could not produce a valid Step.",
                    tokens=tokens,
                )
            )
            trace.stop = Stop(
                StopReason.MALFORMED,
                detail="model could not produce a valid step after retries"
            )
            return trace

        # Account for the model proposal.
        if step.action == "final_answer":
            trace.add(
                TraceStep(
                    step=len(trace.steps) + 1,
                    tool=None,
                    thought=step.thought,
                    tokens=tokens,
                )
            )

            trace.stop = Stop(
                StopReason.COMPLETE,
                answer=step.args.get("text", "")
            )
            return trace

        call_key = (
            step.action,
            repr(sorted(step.args.items()))
        )

        if call_key in previous_calls:
            trace.add(
                TraceStep(
                    step=len(trace.steps) + 1,
                    tool=step.action,
                    args=step.args,
                    thought=step.thought,
                    tokens=tokens,
                )
            )
            trace.steps[-1].ok = False
            trace.steps[-1].error = "no_progress"
            trace.steps[-1].state_changed = False
            trace.steps[-1].tier = (
                TOOLS[step.action].tier.value
                if step.action in TOOLS else None
            )
            trace.stop = Stop(
                StopReason.BLOCKED,
                detail="no progress: repeated identical tool call"
            )
            return trace

        previous_calls.add(call_key)

        observation, tstep = dispatch(
            step,
            trace,
            allow_consequential=allow_consequential
        )
        tstep.tokens = tokens
        trace.add(tstep)

        observations.append(
            f"{step.action}: {observation}"
        )

        # Escalation is a successful terminal action.
        if step.action == "escalate_to_human" and observation.get("ok"):
            trace.stop = Stop(
                StopReason.ESCALATED,
                detail=observation.get("reason", "")
            )
            return trace

        # Approval requests are pending, not completed.
        if (
            step.action == "request_approval"
            and observation.get("ok")
            and observation.get("state") == "pending"
        ):
            trace.stop = Stop(
                StopReason.PENDING_APPROVAL,
                detail=observation.get("note", "Pending human approval")
            )
            return trace

        # Gate/tool failure becomes an observation for the model.
        if not observation.get("ok", False):
            observations.append(
                f"TOOL FAILURE: {observation.get('error', 'unknown_error')}"
            )

    # Explicit fall-through: never exit silently.
    trace.stop = Stop(
        StopReason.CAPPED,
        detail=f"turn cap reached ({max_steps} steps)"
    )
    return trace


if __name__ == "__main__":
    print("hello_agent.py loaded.")
    print("This file expects the Lab 3 notebook definitions to be available")
    print("when its functions are imported/executed.")
