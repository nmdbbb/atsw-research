# Start here: relational scope v3

Active contract: **tree-adapted-ot-relational-v3**. User authorized this reframing
on 2026-09-10 after considering the theory update at `56fd25b`. Read
[SCOPE_REVISION_3.md](SCOPE_REVISION_3.md) for the Vietnamese analysis and handoff.

## Purpose and precedence

Find a scientifically substantive way to compare trajectory sets, preserving
adapted-OT ordering/top-K decisions with an explicit guarantee and lower total
cost. Scientific weight comes before implementation feasibility or cheap probes.
The reference remains the declared finite quantized k-window model, not population
AW or application labels. A shared tree is a candidate, not a validated solution.

`objective.json` and scope v3 supersede conflicting legacy instructions, including
v2's mandatory 0.5% value accuracy, full-grid launch and old next-action queues.
The unchanged [v2 contract](ledger/contracts/objective_v2.json) still governs any
separate legacy solver claim. Neither v3 nor v2 scientific objectives are achieved.

## Current state and next step

Read in order:

1. [Active objective](objective.json) and [scope analysis](SCOPE_REVISION_3.md).
2. [Revision record](ledger/contract_revision_3.json).
3. [Current checkpoint](status.orchestrator.json).
4. [Imported theory record](ledger/inbox/codex_orchestrator/theory_round_theorist_20260910.json)
   and its linked statement only as needed: independent skeptic review is pending.

Prepare ONE bounded packet: proposed successful claim, nearest prior art,
conditional-information mechanism, adversarial information-timing example, and
work accounting. No automatic P1/P2, W1 overhaul, hypothesis registration or grid.
After scientific-weight and guarantee review, freeze a small decisive protocol
with coverage/risk, ties, fallback, cost thresholds, splits and budget.

Use agents only for concrete decision-changing work: one independent reviewer
when the packet exists, then an implementer if warranted. Do not invent a quota
of hypotheses. For every step ask which objective it advances and what result
would change the next decision. Report evidence and decisions, not task counts.

## Integrity and tool boundaries

Preserve v1/v2 snapshots, historical runs, preregistrations, hashes and imported
reports. `status.json` is historical; the active checkpoint is
`status.orchestrator.json`. Never silently resume its old H_D02 queue.
`workflow.py check-report` is a v1/v2 numerical screen and returns NOT_READY for
v3. It does not validate ranking guarantees or scientific completion.

From the repository root:

```powershell
python research-workflow/tools/verify_hash_pins.py
python -m unittest discover -s research-workflow/tests -q
python research-workflow/workflow.py status
```

No research process is running in the background. The handoff prompt is in
[SCOPE_REVISION_3.md, section 7](SCOPE_REVISION_3.md).
