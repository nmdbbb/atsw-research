# Independent review: order architecture comparison 01

Date: 2026-09-10. Role: bounded mathematical/investment reviewer, not PO.
Verdict: **ACCEPT corrected packet as a baseline comparison and exact diagnostic;
support NO PROBE. No new scientific ordering gate has passed.**

## Version binding and reproduction

Only the packet, its checker and saved output, and the relevant primary-source
Section 3.1 were reviewed. This is one review including one correction by the
root agent during review; it is not a second independent replication.

| Artifact | SHA256 |
|---|---|
| Initially reviewed `order_architecture_compare_01.md` | `4d124f0108d8003645f9725aa03f0a4a85ce71d14955a5557492ed0489ac8d02` |
| Accepted corrected `order_architecture_compare_01.md` | `23a377d0e715b18de01b90405e3a9685c5433be53b8f859a4d89e7ab89f7d91e` |
| `research-workflow/tools/check_order_architecture_compare_01.py` | `767f56351702f93611eb878e64c7623bd73564eb0d5df91327e2560abb6d02b2` |
| `order_architecture_compare_01_checks.json` | `11467bbd902af5beb8c9f4dcf816bb414d8ed13943dbaed46f0a3fee54081d58` |
| Fresh checker stdout bytes | `11467bbd902af5beb8c9f4dcf816bb414d8ed13943dbaed46f0a3fee54081d58` |

Executed `python research-workflow/tools/check_order_architecture_compare_01.py`
through a capturing subprocess: exit 0; decoded JSON and stdout SHA256 both
match the saved output. The checker only printed output. Its embedded source
hash matches the actual checker. The final packet was reread and independently
hashed after the correction. No other artifact receives review coverage.

## Claim checks

1. **Monotone core and strictness: sound for the stated finite scalar Markov
   subclass.** Condition 2 includes the deterministic parent of the first draw,
   so induction with common independent uniforms preserves Q <= A <= B. The
   pairwise projections have the prescribed transition marginals and are
   bicausal KR couplings. Condition 1 supplies the required within-law
   monotonicity for their optimality. Reachable finite supports suffice: the
   argument only uses supplied rows; an increasing stepwise version outside a
   law's support can also be defined without changing that law. Positive
   probability of B_t > A_t for at least one time makes the summed cost strictly
   larger for QB, for both p=1 and p=2. This concerns a reachable witness under
   the actual coupling, not an arbitrary strict row inequality.

   The source check supports this use: Proposition 3.5 gives KR optimality
   under stochastic co-monotonicity and its cost assumptions; Remark 3.9
   includes the requested power costs. Remark 3.8 permits the current-state
   reduction for Markov laws and warns against the same reduction for general
   history dependence. Neither a general k=2 extension nor novelty follows.
   [Primary source, Section 3.1](https://arxiv.org/html/2209.03243v5#S3.SS1).

2. **p=1 exception: substantive objection resolved.** The original sentence
   denying that a feasible ordered triple alone proves the comparison was too
   broad. For any pairwise bicausal ordered triple, every coupling satisfies
   E|X_t-Y_t| >= |EX_t-EY_t|, while its ordered pair projections attain those
   bounds simultaneously. Thus D(Q,A)=sum(EA_t-EQ_t) and analogously for QB,
   regardless of condition 1. The final packet states this exception explicitly
   and confines the remaining pairwise-optimality caveat to p=2. The later
   generic-feasible-coupling caveat was corrected consistently. An asserted
   triple still needs a valid existence/feasibility argument. This stronger
   p=1 baseline must be retained when screening a future candidate.

3. **Uniform future bound: sound, with its stated uniform hypothesis.** Common
   independent uniforms give a feasible bicausal coupling even outside the
   monotone core. The recurrence bounds every realized discrepancy by induction,
   hence bounds its p-cost and the optimum. Each time-marginal transport cost is
   a lower bound on that time's cost under every path coupling; summing gives
   L <= D. Consequently U(Q,A) < L(Q,B) is sufficient. An average W1 contraction
   estimate would not imply the stated almost-sure quantile inequality.

4. **Exact discriminator: sound but not adapted-specific evidence.** The first
   coordinate identifies each path. Every first-bit coupling is therefore
   bicausal, and all path couplings arise this way. The two uniform 2x2 extrema
   exhaust the linear objective's possibilities. For QA, anti-diagonal cost is
   2^p and diagonal cost is sum over j=1,2,3 of (2 rho^j)^p. For QB, the
   translation coupling attains all marginal lower bounds, giving 4(9/8)^p.
   These yield exactly the table and both reversed KR rankings. A's first
   transition has slope -rho, later ones +rho; Q and B have slope +rho.

   The QA uniform condition also holds on all reachable cross-row pairs, not
   just the realized diagonal pairs: at the sign reversal, x,y are in {-1,1}
   and rho|x+y| <= rho|x-y|+2rho; afterward the two kernels have the same slope
   +rho. The resulting e and U equal the stated KR costs. The positive control
   has increasing affine kernels with ordered shifts and exact cost 4(1/4)^p.
   This is one rational example, with two cost choices and a consistency control.
   Its coincidence of ordinary and bicausal feasible sets prevents admission as
   evidence of a substantive adapted-versus-ordinary distinction.

5. **Signed regrets and interval collapse: correct.** Substituting
   D_X=S_X-r_X gives D_B-D_A=(S_B-S_A)+r_A-r_B. Using precisely the two separate
   bounds displayed in the packet gives
   (S_B-S_A)+(S_A-U_A)-(S_B-L_B)=L_B-U_A. Thus that construction contributes
   no relational information beyond independent interval separation. The
   statement correctly stops short of excluding other joint certificates.

6. **Work and scientific claims: appropriately limited.** Merging sorted
   breakpoints for each eligible row pair has the displayed conservative
   operation count. Sorting, within-law checks, reachability of strictness,
   marginal propagation and input construction remain charged. The final
   packet additionally distinguishes arithmetic operations from rational bit
   complexity. No speedup, subquadratic algorithm, empirical coverage, population
   guarantee, novelty, or successful investment gate is established. Checker
   success verifies this construction's arithmetic; it does not verify the
   general theorem or its computational usefulness.

## Objections and coverage limits

- **Resolved, substantive:** the original p=1 feasible-ordered-triple exclusion.
  Acceptance applies to the corrected packet hash, not that earlier sentence.
- **Resolved, clarification:** the cost count now explicitly excludes operand
  bit complexity and measured runtime.
- **Still open, expected research gap:** neither baseline gives a new structural
  comparison of optimization effects outside its existing justification, nor a
  demonstrated work advantage. This is not a defect in the diagnostic verdict.
- **Still open, investment interpretation:** one failed contraction-envelope
  separation does not show that every envelope refinement is unproductive.
  Preferring the direct-comparison question is a bounded PO priority, not a
  mathematical dominance theorem between entire research programs.
- No exhaustive literature review, general impossibility proof, arbitrary-window
  theorem, benchmark, or fresh conditional-randomness example was reviewed.
  Later artifacts and amendments do not inherit this sign-off.

## Investment verdict and next bounded question

Retain the corrected p=1 ordered-coupling baseline, the p=2 monotone/KR baseline,
and the uniform-coupling/marginal-bound baseline. Support the proposed no-probe,
no-grid/no-tuning decision: the current packet supplies a valid diagnostic and
a sharper statement of the missing theorem, not the theorem itself. The root
agent owns the final investment and checkpoint decisions.

One worthwhile next question is whether an explicitly declared finite scalar
Markov subclass, with fresh conditional randomness and cases outside the known
monotone core, admits a noncircular conditional-structure lemma certifying the
sign of D(Q,B)-D(Q,A) with less work than two complete dynamic transports. Before
any probe, require one precise lemma with charged input checks and one exact
example where it adds information beyond the corrected baselines and has a
substantive adapted-versus-ordinary distinction. Reject that construction if it
only renames independent value bounds, uses exact unknown regrets, or reduces
to known optimality. This is a bounded next theorem question, not approval of
an algorithm or closure of the broader ordering objective.
