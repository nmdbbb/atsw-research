# Independent review of relational Trial 02

Date: 2026-09-10. Scope: one proposed exact formula for bicausal transport
under a weighted common prefix-tree path cost, its conditional ordering bridge,
and a narrow prior-art check. The user has selected mathematical conditional
order preservation and delegated the next decisions. This document does not
amend the objective, register a hypothesis or report a benchmark.

**Verdict:** the proposed formula is correct for finite full-prefix trees with
nonnegative edge weights. Its key maximal-agreement construction is already
explicit in adapted-total-variation prior art; the weighted formula is an
elementary extension. The uniform ground-cost error bridge is also elementary.
Use both as supporting facts, not a paper-level contribution. The unresolved
research question is a useful, verifiable and cheap relation to the numeric
adapted-OT target on a substantive domain.

## Formula and proof

Assume a common finite alphabet at each time, common fixed horizon, natural
filtrations of the displayed paths, and a union tree whose nodes are complete
prefixes. A missing prefix has zero law mass. Let p(h) be the parent of h,
mu_h and nu_h the prefix probabilities, and w_h>=0 the length of the incoming
edge. With the empty prefix having probability one, define

    m_empty = 1
    m_h = m_p(h) min(mu_h / mu_p(h), nu_h / nu_p(h)).

Set m_h=0 whenever either parent probability is zero; no arbitrary conditional
law on an unvisited prefix affects the answer. Then the exact value is

    S_bc(mu,nu) = sum_{h nonempty} w_h (mu_h + nu_h - 2 m_h).

If a deterministic time zero has been omitted, its common edge has zero
contribution. A nonconstant initial observation must instead be included in the
filtration and prefix construction, with its cost convention specified.

For any bicausal coupling pi, write z_h=pi(X_1:|h|=Y_1:|h|=h). Conditional
on the two histories both being p(h), bicausality fixes the next-coordinate
marginals to the two laws' conditional marginals. Therefore

    z_h <= z_p(h) min(mu(h|p(h)), nu(h|p(h))) <= m_h.

This proves simultaneous upper bounds, but attainment also needs justification.
At every equal-history pair, couple the next marginals a,b by putting
min(a_i,b_i) on each diagonal entry. The residual row and column vectors
r=a-min(a,b) and s=b-min(a,b) have equal total R and disjoint coordinate
supports. If R>0, the residual matrix r_i s_j / R supplies all remaining
marginals without adding diagonal mass. If R=0, no residual is needed. At
unequal-history pairs use any coupling of the appropriate next marginals.
The resulting product of conditional couplings is bicausal and realizes
z_h=m_h for every h. Diverged full prefixes never become identical prefixes
again, even if their current numeric coordinates later coincide.

For each tree edge, its contribution to the path distance is w_h times the
indicator that exactly one of the two paths lies in its subtree. Thus

    E_pi[d_tree(X,Y)] = sum_h w_h (mu_h + nu_h - 2 z_h).

All w_h are nonnegative, so the simultaneously maximal z_h minimize every
term and their sum. This completes the proof for arbitrary node-dependent
nonnegative weights; they need not be depth-only or monotone in depth.
Zero weights may yield a pseudometric and nonunique optimizers. Negative
weights are outside the argument and outside ordinary tree metrics.

The proof depends on the subtree events being actual temporal prefixes.
It does not automatically apply to arbitrary geometric trees, learned partitions
of leaves, or a suffix-state graph that permits different histories to merge.
Changing the coupling set or filtration also requires a new argument.

As a direct check using Trial 01, for U versus V with unit edges the only
nonzero first-level agreement is m_(0)=1/2 and the only nonzero terminal
agreement is m_(0,0)=1/4. The two levels contribute 1 and 3/2, respectively,
so S_bc=5/2. For Q versus B the same agreement masses give 5/2, whereas
Q versus C gives 1. The numeric AW_1 values remain 3/16 and 1/4. Thus this
causal correction by itself still produces the earlier numeric-order inversion.

## Nearest prior art and significance

The decisive source is [Beiglböck and Zona, *Pinsker's inequality for adapted
total variation*, arXiv:2506.22106v1, Lemma 2.1 and its proof](https://arxiv.org/pdf/2506.22106).
It explicitly represents adapted total variation through iterated minima of
conditional laws and proves optimality of successively maximal diagonal
couplings. Its total-variation convention is twice disagreement probability.
This directly overlaps the proposed m recursion and attainment mechanism.
The paper's footnote also records independent observation by Acciaio, Hou and
Pammer; this is further reason to avoid a priority claim.

For depth-only weights w_h=w_t, the present formula reduces to

    S_bc = 2 sum_t w_t (1 - sum_{|h|=t} m_h)
         = sum_t w_t ATV(mu_1:t, nu_1:t).

The same coupling attains every truncated-prefix term. Equivalently, if tau
is the first disagreement time, the path cost is
2 sum_t w_t 1{tau<=t}; maximizing survival of identical prefixes minimizes
this weighted stopping cost. Arbitrary prefix-dependent weights follow from
the componentwise diagonal argument above. That weighted extension is my
deduction here, not a claim that the source prints this exact formula.

This was a narrow check centered on the exact mechanism, with searches for
maximal bicausal agreement and first disagreement. It is not an exhaustive
novelty survey. The direct overlap is already enough to reject standalone
novelty for the recursion, greedy coupling, or depth-weighted formula.

## Conditional ordering bridge

For the same two path laws and the same bicausal coupling set, suppose a
verified bound holds on the support product:

    |c(x,y) - d_tree(x,y)| <= E_mu,nu.

Every feasible coupling's expected costs differ by at most E_mu,nu. Taking
infima in both directions gives

    |D_c(mu,nu) - S_bc(mu,nu)| <= E_mu,nu.

Consequently, for a common query q,

    S_bc(q,a) + E_q,a < S_bc(q,b) - E_q,b
    implies D_c(q,a) < D_c(q,b).

For a common E this requires a score gap exceeding 2E. Equality does not
certify a strict comparison. The result concerns AW_p^p when c is the sum
of pth-power stage costs; it must not silently apply an error bound in those
units to AW_p itself.

The implication is mathematically sound, but its usefulness is not established
by stating an E that always exists on finite supports. A worst-case diameter
bound may leave every relevant comparison unresolved. Calculating the exact
support-product supremum can itself require many path-pair evaluations.
Any method to verify E, choose weights or construct the common tree must be
charged, including query insertion and calibration. Computing a maximum on
sampled path pairs alone does not verify a support-wide bound for a reconstructed
law. The bridge also cannot cure a mismatch between raw empirical paths and
the finite k-window law being used as the reference.

## Representation and cost accounting

With an explicit full trie already built and its masses/kernels available, one
forward traversal computes m and the score in O(number of visited edges)
arithmetic operations. Terms sum_h w_h mu_h can be cached per law; the
cross-law m terms remain pair-dependent. A fixed common trie does not make all
database comparisons or theorem verification free. Exact rational operation
counts also omit numerator/denominator bit growth with horizon.

An empirical full-path law with n observed paths has at most nT noninitial
prefix nodes. A reconstructed finite k-window law may admit exponentially
many distinct full paths through recombining suffix states. Expanding that law
into its full trie can therefore be exponential in T even if its transition
tables are small. Using only the observed paths would change the target in
general. Arbitrary full-prefix weights cannot be assumed to have a compact
representation or fast evaluation under that law.

There is a useful qualification: exponential expansion is avoidable for certain
restricted weight representations. Suppose both laws are Markov on the same
aligned k-suffix state space (missing transitions have probability zero), and
w_h depends only on time t and the suffix state z(h). Define

    r_t(z) = sum_{h of length t with suffix z} m_h.

For a shared deterministic root initialize r_0 there to one. Then

    r_{t+1}(z') = sum_z r_t(z) min(K_mu,t(z,z'), K_nu,t(z,z')).

The state keeps the appended symbol, so an aligned transition represents the
same extension on both sides. This recursion aggregates only paths that have
agreed for their entire histories; it does not reinstate agreement after a
divergence. If p_mu,t and p_nu,t are the ordinary state marginals, then

    S_bc = sum_{t,z} w_t(z) [p_mu,t(z) + p_nu,t(z) - 2 r_t(z)].

Both r and the marginals can be propagated using sparse transition tables.
Weights depending on a shared state transition admit the analogous edge-sum
form. The work is linear in the aligned transition entries traversed per pair,
without a full trie. This is a derivation from the proven formula, not a tested
implementation or novelty claim. It does not cover arbitrary learned weights
on full histories, arbitrary geometric trees, or the cost of a numeric error
certificate. The relevant distinction is therefore the supplied representation
and its compatible weights, not an unconditional assertion that all k-window
uses are exponential.

## Bounded next decision

Accept the exact causal tree formula and the conditional ordering implication
as reviewed supporting facts. Do not invest in a benchmark, a broad learned
model, or a paper claim centered on this formula: the scientific contribution
is still missing.

The next decisive task should be a small theorem/obstruction packet for a
declared numeric process class and a compact, nontrivial weight construction.
It must supply a verifiable error or order condition with some nonzero useful
coverage and account for the cost of checking it. A support-diameter bound plus
an assumed separated score is insufficient as a substantive contribution.
If no plausible cheap certificate survives a small adversarial example, stop
that construction while leaving other representations and process subclasses
open. This review establishes no global impossibility and no completed research
contribution.
