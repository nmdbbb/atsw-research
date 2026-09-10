# Interval reuse decision, 2026-09-10

**Decision: defer a new hypothesis, implementation and empirical reuse probe.**
Nonzero-gap witness reuse is mathematically sound with the obligations below,
but is elementary LP sensitivity plus interval Bellman bookkeeping. The current
fixed upper policy already fails a cheaper necessary headroom test on existing
data. Improving lower-backup speed cannot remove that obstacle.

## Exact-arithmetic local rule

Fix the same transport marginals a,b with equal mass and polytope P. Let pi in P
and alpha_i+beta_j <= C_old(i,j) be certified feasible witnesses, with
d=a.alpha+b.beta, p=<pi,C_old>, and g=p-d>=0. Optimality of either witness is
unnecessary. For C_new=C_old+Delta with Delta>=0 entrywise,

    d <= OT(C_new) <= p + <pi,Delta>;
    new certified local width = g + <pi,Delta>.

Proof: the old dual remains feasible because costs increased; pi remains
feasible because marginals did not change. Weak duality proves both endpoints.
A positive support hit can therefore be tolerated within a gap budget without
finding another optimal-face coupling. Support misses preserve the old interval,
not an exact value when g>0. Tiny positive increments must contribute to the gap.
Sparse accumulation of <pi,Delta> is possible, but requires a complete, versioned
update record and includes all changed support incidences and their maintenance.

## Original-target root obligations

The upper endpoint above bounds OT(C_new). If C_new=c+ell_child uses lower
continuations, that endpoint does NOT bound the original continuation value V.
For valid child brackets ell<=V<=u, a safe local upper is <pi,c+u_child>.
Its width above the old dual is

    g + <pi,ell_new_child-ell_old_child> + <pi,u_child-ell_new_child>.

This formula assumes the cached matrix was c+ell_old_child. The last term cannot
be dropped; even an exactly solved surrogate can have large original-target error.

A sufficient coherent root construction is the following, in exact arithmetic.
At each pair node n, require ell_n <= T_n(ell_child), with terminal ell=0.
One way to certify it is a feasible local dual for c+ell_child whose value is at
least ell_n. Increasing child lower tables preserves previously certified duals.
Include the dummy root, its initial-law coupling, and zero root-stage cost.
Choose a feasible conditional coupling pi_n at every policy-reachable node and
evaluate this complete policy on original costs to obtain U_pi. Then

    ell_root <= V_root <= U_pi(root).
    r_n = <pi_n,c_n+ell_child> - ell_n >= 0.
    U_pi(root)-ell_root = sum_n mu_pi(n) r_n.

Here mu_pi is the occupancy of THAT complete feasible policy, including root
occupancy one. The identity follows by substituting the policy recursion and
telescoping over finite time. Recombining parents' probability masses add.
It uses no optimal occupancy oracle and establishes a sufficient global budget:
sum mu_pi*r <= 0.005*ell_root when ell_root>0. At zero, use an explicitly
declared absolute criterion; do not divide by an artificial denominator.

Do not sum historical event gaps as independent final residuals. Changing a
policy changes occupancies; changing ell changes residuals. Recompute or update
the coherent final certificate, charging that work. Stale occupancies may guide
search but cannot silently certify its result. Lower values obtained from other
valid bounds need not automatically have this subsolution residual identity.

Floating tolerances alone establish none of these exact inequalities. Preserve
the declared finite target: independently rounded normalized marginals can have
unequal exact totals. Any numerical implementation needs audited primal repair,
dual correction and outward arithmetic/error propagation through the root;
do not silently renormalize or require exact old primal-dual equality instead.
The existing policy-pool and global-subsolution modules explicitly remain
float64 development witnesses, not outward root certificates.

## What is already known and what is still missing

The local rule is weak duality/cost sensitivity, consistent with the optimality
and reoptimization framework in [Bertsekas and Tseng, RELAX (1988)](https://web.mit.edu/dimitrib/www/BT_Relax_1988.pdf).
Caching action values and applying individual successor increments overlaps with
[Van Seijen and Sutton, Small Backups (2013)](https://proceedings.mlr.press/v28/vanseijen13.html).
Monotone upper/lower bounds, gap-directed work and start-state guarantees are
central to [McMahan et al., BRTDP (2005)](https://www.cs.cmu.edu/~ggordon/mcmahan-likhachev-gordon.brtdp.pdf).
The derivations here specialize elementary principles; they do not claim a source
states an identical finite-horizon transport implementation or transfer its rates.

H_D01's prior-art review already identifies the same generic reverse-dependency
baseline. Different parent marginals sharing a continuation table describe a
workload, not yet a new operation. A new tree-mechanism claim needs a specified
shared computation that beats ordinary per-incidence updates and interval
AO-OT/BRTDP with the same witnesses, budget and local reoptimization kernel.
No such additional operation is supplied by allowing nonzero primal-dual gaps.

## Cheapest decisive diagnostic: fixed-upper headroom (already available)

For fixed U and any valid 0<L<=V, (U-L)/L >= (U-V)/V. Thus U>(1+epsilon)V
precludes an epsilon relative certificate regardless of how cheaply L is improved.
Read-only recomputation from `runs/cycle_2/policy_pool_common_smoke.json` gives
16/16 cases with (U-V_reference)/V_reference > 0.005; minimum 1.087451%, median
18.823667%, maximum 41.600493%. These are the existing incumbent SVD-policy
uppers and numerical references, not a new experiment or exact impossibility proof.
The inference is conditional on the numerical reference and this fixed policy;
it does not cover every feasible policy, update schedule or original-domain task.

**Stop condition met for this baseline:** do not build a lower-only interval-reuse
solver while retaining this U. Before reopening, identify an affordable feasible
upper-policy improvement and show certified-headroom potential on a declared tiny
development case. A passing upper test is only necessary, not sufficient; the
next gate must still show incremental work advantage over interval AO-OT/BRTDP,
including unsuccessful checks, witness maintenance and root certification.
No new hypothesis, code, solver run, registration, grid or scientific completion
claim follows from this review. It changes the next question to upper-policy
quality and avoids engineering a faster path to an inadequate certificate.
