# H-B01 C1 verdict: temporal-envelope headroom

Registered record: `H_B01C1_envelope_headroom`, ledger hash
`6d9a13afca1e76f1657ec2317f72e1540fc67e4d4f3daca42789362dac6804a7`.
This was registered after lane C disclosed a post-hoc diagnostic, so it is a
registered replication of a threshold inherited from H-B, not a blind
preregistration.

## Result

The run completed all 24 declared cases: two frozen process contrasts, both
costs, three deltas and two development seeds, at k=1 and T=4.  The path count
was the frozen 4000/6000/8000 for delta 0.5/0.3/0.18.  Every pointwise envelope
check and every occupation mass/marginal check passed; the largest recorded
containment violation was zero in float64.

The registered occupation-headroom prediction failed in all 12 groups.  No
group had a layer through T-2 whose two-seed median could retain 10% of optimal
occupation within the 0.5% root budget.  The best group/layer median was 2.917%.
Excluding pairs incident to an out-degree-one state made no material difference.
The reachability envelope is therefore too loose on the value-carrying portion
of these frozen k=1 trees to justify implementing the full H-B hierarchy as
currently specified.

## What this does not prove

H-B's original performance threshold counts omitted distinct continuation
entries, not occupation mass.  The probe's deliberately optimistic necessary-
condition relaxation says 87.1% to 96.5% of entries could fit under the
occupation-weighted budget, mainly because many entries have zero exact-optimal
occupation.  This relaxation ignores alternative policies and mixed-depth
frontier constraints, so it neither supplies an algorithm nor proves those
entries are safely omittable.  It does prove that the C1 occupation result alone
cannot classify the original distinct-entry prediction as falsified.

Consequently:

* `H_B01C1_envelope_headroom`: `mechanism_headroom_falsified`.
* `H_B01_temporal_block_bounds`: remains `revise`; the original distinct-entry
  performance claim is `inconclusive_metric_mismatch`.
* Do not spend a full implementation/benchmark cycle on this particular
  reachability envelope.  A revision must either tighten the envelope on
  occupied mass or provide a sound oracle bound directly aligned with omitted
  entries and alternative-policy effects.

## Correction to the earlier review

The earlier post-hoc note's reported servable mass `0.000` is incompatible with
the fractional relaxation it described.  If total occupation-weighted slack is
196 times the budget, fractionally retaining the same proportion of every node
already admits at least 1/196, about 0.51%, of occupation.  The registered C1
uses the correct fractional-knapsack quantity.  The earlier note also inferred
the distinct-entry verdict from occupation mass; that inference is withdrawn.

Raw evidence: `runs/cycle_2/H_B01C1_envelope_headroom.json`.
Probe: `probes/envelope_headroom_c1.py`.

