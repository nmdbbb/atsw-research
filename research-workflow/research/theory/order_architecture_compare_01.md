# Order architecture comparison 01

Status: comparison complete, awaiting independent review; no candidate promotion. 2026-09-10.
Task: `order_architecture_compare_01`. One comparative packet, no benchmark.

Question: on the SAME finite scalar Markov family, does directly certifying an
ordering remove work that approximate-future value bounds still require? What
nontrivial contribution remains after established monotone coupling results?

## Target, inputs and comparison domain

Target D(P,R)=AW_p(P,R)^p with cost E sum_t |X_t-Y_t|^p, p=1 or 2,
natural filtrations, common deterministic time zero and finite horizon. Inputs
are finite scalar Markov laws specified by their reachable states, initial laws
and transition rows. This is a declared k=1 subclass, not all reconstructed
k-window laws or a population certificate. Sorting and checking these inputs
are part of the cost. No exact reset or Gaussian assumption is made.

Both routes face the same family: an increasing-kernel core and a boundary with
one decreasing, still contractive, transition. Leaving the core tests the
limits of a proposed extension; it does not refute the core theorem. The exact
discriminator below has randomness only in its first draw. Consequently it
does NOT satisfy the investment gate requiring a substantive adapted versus
ordinary distinction. Its purpose is to expose an invalid ordering inference.

## Closest verified source

Backhoff-Veraguas, Kallblad and Robinson, [Adapted Wasserstein distance between
the laws of SDEs, arXiv:2209.03243v5, Section 3.1](https://arxiv.org/html/2209.03243v5#S3.SS1).
Read the relevant definitions, proposition, remarks and proof context, not an
exhaustive full-paper or novelty review. Definition 3.1 constructs the KR coupling
by successive conditional quantiles with shared independent uniforms.
Proposition 3.5 gives its bicausal optimality under stochastic co-monotonicity
and the stated cost assumptions; Remark 3.9 covers |x-y|^p for p>=1. Remark 3.8
distinguishes the Markov case from general history dependence: checking only the
current coordinate is insufficient in the latter. Therefore no k=2 extension
is admitted by inspecting scalar current-state monotonicity alone.

## Route A: direct order on the monotone core

Write q_P,t(x,u) for the conditional quantile of the next state; the first
draw has a deterministic parent. Sufficient conditions, to be checked on the
supplied finite rows:

1. For each P in {Q,A,B}, q_P,t(x,u) is nondecreasing in x on its reachable
   state support, for every u except a null set.
2. For every ordered reachable cross-law pair x<=y, q_Q,t(x,u)<=q_A,t(y,u);
   and for y<=z, q_A,t(y,u)<=q_B,t(z,u). This includes the first draw.

Use independent uniforms U_t shared by the three laws. Induction gives
Q_t<=A_t<=B_t almost surely. Each pairwise coupling is KR and, by the cited
optimality result under condition 1, realizes its bicausal optimum. Thus

    D(Q,A) = E sum |Q_t-A_t|^p <= E sum |Q_t-B_t|^p = D(Q,B).

Strict order additionally requires positive probability of B_t>A_t at some
time; otherwise this proof gives only a weak order. Because p>0 and Q<=A<=B,
that witness makes the pointwise total cost inequality strict on a positive
probability event. Witness reachability has a cost; it is not inferred from
strictness in an unreachable row. For p=2, an ordered feasible triple alone
does not supply this argument's required pairwise optimality. Closeness of
adjacent kernels alone also does not establish the comparison.

Scientific weight: this is an elementary consequence of a known optimal
coupling, retained as a baseline. There is a stronger p=1 simplification:
ANY feasible bicausal ordered triple already attains both marginal mean lower
bounds, since E|X_t-Y_t|>=|E X_t-E Y_t|. It therefore proves
D(Q,A)=sum(E A_t-E Q_t), with the analogous formula for B, without condition 1.
The triple's existence must still be justified from the inputs. For p=2, computing
the exact KR cost can still require joint-state propagation; the structural
predicate may avoid that, but this corollary alone is not a new central claim.

Cost: after sorting, quantile inequalities can be checked by merging CDF
breakpoints for each relevant row pair. With m_P,t parent states and at most
d_P,t children per row, a conservative cross-law check costs
O(sum_t m_P,t m_R,t (d_P,t+d_R,t)), plus within-law monotonicity checks and
input construction. Ordered pairs may be fewer; no sparsity is assumed. The
check avoids transport LPs but is not automatically subquadratic. We do not
assume conditional rows at zero-probability states or free common-alphabet
extensions. A cheap special input representation would need a separate proof.
These are breakpoint/arithmetic operation counts, not bit-complexity or measured
runtime bounds; exact rational arithmetic has an additional operand-size cost.

## Route B: approximate future coupling bounds

Use the same shared-uniform quantile coupling, which remains bicausal even
without monotonicity. Suppose supplied nonnegative rho_t and epsilon_t satisfy
the following UNIFORM condition on relevant reachable state pairs and almost
every u:

    |q_P,t(x,u)-q_R,t(y,u)| <= rho_t |x-y| + epsilon_t.

Set e_0=0 and e_t=rho_t e_(t-1)+epsilon_t. Induction gives |X_t-Y_t|<=e_t
under this coupling, hence U(P,R)=sum_t e_t^p >= D(P,R). Combined with
L(Q,B)=sum_t W_p(Q_t,B_t)^p <= D(Q,B), U(Q,A)<L(Q,B) certifies order.
This is an elementary feasible-coupling bound, not a novelty claim. A W1 or
average contraction coefficient alone does not establish the uniform
condition or the squared-cost bound; those require their own moment argument.

Checking the uniform condition exactly on finite quantiles can require the
same dense row-pair breakpoint merges as Route A. Computing all marginal laws
and their one-dimensional transports also costs work. Arbitrary real-valued
floating input would require validated arithmetic for a numerical certificate;
the diagnostic here uses exact rational input. There is no measured speed or
coverage advantage. Looser analytically supplied constants can be cheaper to
check but may destroy separation.

## One exact discriminator, both routes

Let rho=9/10, T=4, and J uniform on {-1,+1}. Define the two-path laws

    Q = J(1, rho, rho^2, rho^3),
    A = J(1, -rho, -rho^2, -rho^3),
    B = Q + (9/8, 9/8, 9/8, 9/8).

Every transition after the first draw is deterministic with absolute
Lipschitz constant rho. A reverses sign only in its first transition; its
later transitions multiply by +rho. B has affine transitions with slope rho.
No deterministic common reset occurs. The first state identifies the entire
future, so any coupling of the first bits is bicausal. The two extrema of the
uniform 2x2 coupling polytope are diagonal (KR) and anti-diagonal; the optimum
is their smaller cost. This proves the oracle without a numerical LP.

| Cost | D(Q,A) | KR cost S_A | D(Q,B)=S_B=L(Q,B) | Result |
|---|---:|---:|---:|---|
| p=1 | 2 | 2439/500 = 4.878 | 9/2 = 4.5 | KR ordering is reversed |
| p=2 | 4 | 1997541/250000 = 7.990164 | 81/16 = 5.0625 | KR ordering is reversed |

For QA take epsilon_1=0, epsilon_2=2rho, epsilon_3=epsilon_4=0 and subsequent
rho_t=rho. (The first-stage coefficient is immaterial.) This uniform condition
holds on all reachable row pairs, and yields e=(0,2rho,2rho^2,2rho^3).
Consequently Route B gives U(Q,A)=S_A: correct but unable to separate the true
order in the table. The far lower bound is exact because each marginal is a
translation by 9/8. A is outside Route A's increasing-kernel hypothesis;
contractivity does not license silently dropping that hypothesis.

Positive control on the SAME family: replace A by Aplus=Q+(1/4,...,1/4).
Then the monotone-core conditions hold and D(Q,Aplus)=4(1/4)^p<D(Q,B).
This checks consistency, not usefulness on new stochastic data.

Reproduce: `python research-workflow/tools/check_order_architecture_compare_01.py`.
Exact assertions and source hash: [checker](../../tools/check_order_architecture_compare_01.py),
[saved output](order_architecture_compare_01_checks.json). No random sample,
preregistered prediction, benchmark, population inference, general impossibility
or adapted-specific advantage is claimed. The two p rows are one construction,
not independent research replications.

## What a direct comparison still has to solve

For a feasible reference score S_X and D_X=D(Q,X), define optimization regret
r_X=S_X-D_X>=0. Then exactly

    D_B-D_A = (S_B-S_A) + r_A-r_B.

This identity is not a result of scientific weight. In the discriminator,
r_B=0 and r_A>0: optimizing changes the order suggested by the reference score.
A putative direct method must control the SIGNED DIFFERENCE of optimization
effects, or give another valid comparison argument, using accessible structure.
Assuming cancellation or knowing only generic feasible couplings does not
establish the comparison. Additional structure can prove their optimality,
as in the p=1 ordered-triple exception above. Calculating the unknown regrets
by full OT does not meet the intended computational goal.

There is a concrete trap: if a method merely uses
r_A>=S_A-U_A and r_B<=S_B-L_B, then its lower bound on D_B-D_A is exactly
L_B-U_A. That is the old independent interval separation rewritten. It does not
demonstrate saved work or a new relational mechanism. This observation is about
these particular bounds, not a theorem excluding every joint certificate.

The next worthwhile question is whether shared conditional structure controls
relative optimization effects more cheaply than two full Bellman transports,
on a declared class that includes fresh conditional randomness and cases
outside the known monotone core. Neither route above supplies that lemma.
Targeted prior-art verification and this discriminator do not establish that
such a lemma is novel, true, or computationally useful.

## Provisional PO investment verdict

Do not promote either baseline to a probe and do not fund grid or code tuning.
Prefer a bounded search for a direct comparison of optimization effects over
another unconditional contraction-envelope refinement: the latter already
fails on this elementary boundary, while the former states the missing bridge.
This is a priority for the NEXT theorem question, not acceptance of an algorithm.

Next gate: one explicit, noncircular structural comparison lemma with charged
input checks; an exact finite example with fresh conditional randomness where
the claimed new comparison adds information beyond the retained baselines;
and a plausible work advantage over two dynamic transports. If it reduces to
known KR optimality, individual value bounds, or exact regrets, stop that
construction. A negative result here does not close the whole ordering scope.

Independent review must check the core conditions/strictness, uniform bound,
exact discriminator, regret algebra, cost qualifications and investment limits.
Final decision belongs in a separate version-bound verdict after review; do
not retrospectively attach that review to later edits of this packet.
