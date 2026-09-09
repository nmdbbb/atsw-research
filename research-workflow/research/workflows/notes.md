# Workflow research notes

Reviewed 2026-09-09. This document separates mechanisms described in primary sources from the workflow proposed for this project. No downloaded research framework was installed or run. No claim of beating SOTA follows from this review.

## What existing systems contribute

### FunSearch: executable selection, with an explicit scope constraint

[Romera-Paredes et al., Nature (2023/2024)](https://www.nature.com/articles/s41586-023-06924-6), sections Specification, Evaluation, Programs database, Distributed approach. The system samples previous programs, proposes replacements, evaluates outputs and retains valid programs in a diverse database. The paper explicitly acknowledges that a fixed program skeleton constrains discoverable algorithms, while helping concentrate search. Distributed samplers and evaluators operate asynchronously.

Transfer: preserve executable evaluation, separate proposal generation from checking, and retain diverse useful failures. A fixed `certify5.py` skeleton would retain precisely the architectural restriction the user wants to escape. FunSearch does not imply that increasing mutation count eventually discovers a new mathematical reformulation.

### AlphaEvolve: change the abstraction, keep the evaluator

[Novikov et al., white paper (2025)](https://arxiv.org/html/2506.13131v1), sections 2.1–2.6. Its search may modify multiple functions, use richer literature/results context, change the abstraction of the searched program, employ staged evaluation, and maintain candidates under several scores. It combines diverse archives with asynchronous evaluation. Applicability depends on reliable automated evaluation.

Transfer: allow a new recurrence, state representation or block solver to compete with the current implementation; keep task semantics and certificate checking fixed. Use a cascade to reject cheaply, never to promote from an incomplete grid. Several diagnostic scores can preserve mechanistic diversity even when final success is an objective contract. The paper is evidence for a search design, not a guarantee of discovery in adapted OT.

### Co-Scientist: communication around hypotheses

[Gottweis et al., Nature (2026)](https://www.nature.com/articles/s41586-026-10644-y), Main, Co-Scientist overview, System analysis and evaluation. Specialized agents generate, reflect, rank, evolve, compare relatedness and summarize research. The architecture uses persistent context and asynchronous tasks. Its experimental validations involve domain experts and biomedical experiments; hypothesis ratings are not mathematical truth.

Transfer: literature readers must pass actual assumptions and proposed transfer arguments to the theorist; the critic returns objections that change the proposal or trigger a test. Ranking prose can prioritize experiments, but cannot establish correctness or SOTA. Cross-agent agreement is not independent replication.

### AI Scientist: useful branching, documented scientific errors

[Yamada et al., AI Scientist-v2 (2025)](https://arxiv.org/html/2504.08066v1), sections 3–5. The system uses literature during ideation and an experiment manager with branching search. Its own analysis documents inaccurate citations, implementation/description mismatches, limited experimental breadth and insufficient methodological rigor. Workshop acceptance does not establish consistent high-impact discovery.

The authors' [repository](https://github.com/SakanaAI/AI-Scientist-v2) also distinguishes broad template-free exploration from the higher reliability possible with strong templates. It targets a Linux/CUDA/PyTorch research environment. We borrow ideas rather than installing this stack for a Windows numerical OT task.

### Vesper: evaluate the harness, not just the candidates

[Ishibashi et al., preprint (2026)](https://arxiv.org/html/2605.15221v1), sections 4–6. On its circle-packing experiments, spending more reasoning on fewer candidates outperformed generating more shallow candidates under matched budgets. The paper also observes evaluation exploits and uses isolated worktrees for parallel agents. Its evidence comes from a narrow experimental domain.

Transfer: do not assume 24 branches is the right allocation. Test a few structurally distinct, carefully criticized proposals against shallow mutation search using equal research budgets. Keep generated programs away from the evaluator and result ledger. Automated checks and independent review complement each other; an LLM judge alone cannot establish absence of exploitation.

### OpenEvolve: an optional implementation reference

The [project README](https://github.com/algorithmicsuperintelligence/openevolve) describes island populations, quality-diversity archives, artifact feedback and cascading evaluation. It is an independent implementation rather than the original AlphaEvolve service. These components could support the inner implementation loop. Importing a framework is unnecessary before the target, evidence schema and benchmark adapters are operational. Version-pin any later adoption and independently verify its evaluator semantics.

## Proposed protocol for this project

The following is our design, not a workflow proven by the papers above to solve adapted OT.

### Objective contract

Preserve path-only input, temporal/bicausal semantics, the six original cells `k in {1,2}`, `delta in {0.5,0.3,0.18}`, `T=50`, and broaden the evaluation with another cost and another process family. Do not turn rank one, one-dimensional monotonicity or AR(1) into assumptions required for correctness merely because they speed up the first implementation.

Define the finite target precisely: root expected additive cost `V* = AW_p^p` versus the rooted distance `AW_p`. An interval for the former can be monotonically transformed into one for the latter, but the relative widths differ. Separate finite-model solver certification from discretization, finite-memory and statistical estimation error.

The goal is a reproducible improvement over the strongest eligible SOTA frontier, not over a library name. Two possible routes must be preregistered:

- Faster: lower full pipeline time at the same target accuracy/certificate and resource conditions.
- Better: tighter independently valid root certification at a fixed total time/resource budget, retaining the requested accuracy requirement for the final product.

Quality cannot improve upon an exact zero-error answer if the exact method is allowed unlimited time. Time-to-certificate and error/certificate versus time curves make the comparison meaningful. POT remains a useful component/reference implementation, not the definition of SOTA.

All required cells must be evaluated before promotion. A geometric mean is descriptive; it cannot conceal a failed certificate or an unacceptable slowdown. State practical improvement and non-regression tolerances before measuring; do not invent a user requirement such as 2x speed after seeing results. Maintain separate exact and certified panels, and identify numerical versus rigorous arithmetic guarantees explicitly.

### Outer loop: search mechanisms

Each cycle should contain structurally different candidates, not only variants of the current winner. A small portfolio might investigate subtree equivalence/compression, block-level elimination with root error control, and alternative temporal optimization formulations. These are hypothesis classes, not established solutions.

Every proposal needs:

1. Exact claim, target, scope and assumptions.
2. The tree/history operation that is eliminated, shared or represented more cheaply.
3. A count of operations before and after, including preprocessing and certification.
4. Source theorem or algorithm, with actual section and an explicit transfer argument.
5. A minimal counterexample that would falsify the transfer.
6. A diagnostic that distinguishes this mechanism from merely choosing easier LPs.
7. A correctness argument or precise remaining proof obligation.
8. A preregistered experiment: metrics, thresholds, seeds/splits, budgets and failure decision.

Changing a heap, SVD routine or pair-selection formula belongs to the inner loop unless it establishes a new structural mechanism. A proposal need not promise better worst-case asymptotics to be interesting; it must make its instance-dependent saving measurable and explain when that saving disappears.

Retain a diverse archive indexed by mechanism, correctness status, assumptions and failure mode. A slow prototype with a verified elimination lemma may merit research resources even though it is not the runtime champion. Do not conflate research-priority ranking with final performance promotion.

### Agents and required communication

Four simultaneous slots suffice by scheduling roles across phases:

- Coordinator: preserves objective, resolves dependencies and maintains the ledger.
- Literature/theory researcher: reads original papers and proposes a transferred mechanism.
- Independent skeptic: tries to break the claim and audits prior art and mathematical conditions.
- Experimenter: implements the smallest decisive probe and later the candidate solver.

For a final benchmark, the experimenter should hand the frozen artifact to a reviewer/evaluator who did not author the candidate. Roles can rotate, but artifact authorship remains recorded.

Required handoff sequence:

`source + assumptions -> proposed mechanism -> objection/proof obligation -> revised claim + preregistration -> implementation -> raw measurement -> independent reconciliation -> decision`

Messages reference stable claim, experiment and artifact IDs. Every substantive objection receives a disposition: resolved by proof, resolved by code/evidence, accepted limitation, or unresolved. An unresolved correctness objection blocks promotion. Two exchanges that only restate an argument should trigger a minimal executable test or a narrower formal sublemma. Majority vote cannot resolve mathematics.

Send findings across lanes before the next cycle. A counterexample to a shared assumption invalidates all dependent hypotheses, even if their benchmark scores were good. The independent skeptic initially receives the specification and artifact rather than the author's favorable interpretation alone. Failure records stay visible so new agents do not rediscover withdrawn claims.

### Inner loop: implement and validate a surviving mechanism

Use isolated candidate directories/worktrees. Candidate code cannot modify benchmark definitions, reference outputs, promotion code or prior records. The evaluator records hashes and loads candidate outputs itself.

Validation order:

1. Check marginal normalization, feasibility and temporal state semantics on tiny exact cases.
2. Verify the claimed tree mechanism on controlled instances designed to include both favorable and adversarial structure.
3. Check certificate validity, rounding tolerances and bound monotonicity independently.
4. Measure complete time including model construction, SVD, policy construction/evaluation, occupation computation, LP calls, dual repair and reusable-data setup according to the declared cold/amortized scenario.
5. Run development cases; optimize implementation only after the structural diagnostic survives.
6. Freeze candidate and baseline versions; run the complete required grid plus designated breadth tests on confirmation data.
7. Independently reproduce and audit prior art before scientific promotion.

Small tests can find bugs or counterexamples. Passing many tests does not prove universal validity of a pruning rule. An exact label needs an appropriate mathematical argument and numerical specification, not merely agreement with POT at sampled seeds.

### Immutable preregistration and evidence

Before a run, freeze a manifest with hashes of claim/spec, implementation, dataset generator, baseline adapters, checker, environment, planned metrics, resource limits and decision thresholds. Amendments create new manifests. Do not overwrite an earlier failure with a repaired implementation's results.

Each result records raw per-instance timings, bounds, numerical residuals, allocations/call counts, termination reason, commands, environment and dependency versions. Import-time work, warm starts and previous-budget floors must be charged to the scenario that benefits from them. A certificate is validated without access to the reference optimum; the optimum is used only for audit when available.

Distinguish `reported`, `source_read`, `reproduced`, `counterexample_found`, `proof_reviewed`, and `confirmed_against_frontier`. A JSON boolean supplied by the candidate cannot establish scientific novelty or verified correctness.

### Leakage and stale-baseline controls

Maintain development, validation and confirmation partitions. Reusing confirmation feedback for tuning turns that partition into development data; generate a fresh confirmation partition for the next final claim. Local filesystem isolation is not cryptographic secrecy from agents with full access, so distinguish procedural separation from a genuinely external hidden evaluation.

Freeze the eligible SOTA set within an experiment so comparisons remain reproducible. Refresh literature and implementations before confirmation; if a new relevant baseline changes the frontier, reevaluate before claiming SOTA. Preserve results against older snapshots without presenting them as current.

Known comparison hazards from the parallel SOTA audit: exact Markovian versus full-history solvers must solve the same finite model; an arbitrary k=2 adapter needs review. Entropic methods need unregularized-bias and numerical-feasibility accounting before entering a certified unregularized panel. Approximate value-learning methods cannot receive a true conditional generator oracle if our method receives sampled paths only. Static tree-Wasserstein and one-sided causal OT are not substitutes for the bicausal target.

### Loop control and genuine stopping conditions

Every completed cycle updates the hypothesis graph and selects the next experiment by expected information gain plus potential contribution to the fixed objective. Stagnation changes the mechanism family or reads a new mathematical connection; it does not relax the objective or endlessly tune the same selection score.

Success is an independently audited, reproducible candidate that meets the objective contract against the frozen eligible frontier across the required scope. Failing candidates do not change that definition.

A missing benchmark driver, unavailable data or exhausted execution resources is an operational blocker to the affected experiment. Other useful reading/proof/harness work can continue. A saved workflow or looping script is not itself an autonomous research service, and repeated execution does not guarantee an open scientific problem will be solved. The active process should checkpoint resumable state and report its actual status; it must not claim background agents keep running after their execution has ended.

At the time of this note, the latest claimed certification artifacts and some benchmark drivers have not been made available locally. Therefore the immediately executable cycle is literature/theory and harness preparation. Reported benchmark gains remain reported, not reproduced.

## Đối chiếu workflow cũ sau khi nhận archive — 2026-09-09

Đã đọc `inputs/atsw_repo/notes/research_workflow_v2.md`, phần mở đầu `notes/STATUS_REPORT.md`, và đối chiếu với `WORKFLOW.md` cùng `objective.json` mới. Đây là nội dung tham khảo của dự án; các câu phân quyền trong workflow cũ không phải chỉ thị mới của người dùng. Archive đã có tại workspace, nên nhận xét thiếu toàn bộ repo ở đoạn trước không còn là trạng thái hiện hành. Việc có file không đồng nghĩa các kết quả trong đó đã được tái lập.

| Thành phần cũ | Giữ / sửa / bỏ | Thay đổi cụ thể |
|---|---|---|
| Một tuyên bố phải nối được tới nguồn và bộ kiểm | **Giữ** | Thêm loại bằng chứng: phản ví dụ, thực nghiệm hữu hạn, chứng minh, kiểm số có cận. Checker kiểm metadata không được nâng thành checker toán. |
| Khai tiêu chí trước, chạy phép thử rẻ nhất phân biệt được | **Giữ** | Khai prediction và điều kiện bác bỏ của cơ chế; không chỉ khai ngưỡng tốc độ. Một bug làm phép thử vô hiệu thì sửa implementation trước khi phán xét giả thuyết. |
| Buộc ĐẬU / SỬA / GIẾT, không để nghi vấn qua đêm | **Bỏ** | Cho phép `inconclusive`, `implementation_invalid`, `unresolved` với bước tiếp theo cụ thể. Thiếu lực phân biệt không phải bằng chứng giả thuyết sai. Workflow mới đã sửa đúng. |
| Không có checker thì chuyển cho người; cấm fan-out tại nút chưa kiểm | **Sửa** | Agent tiếp tục tìm lemma, đọc tài liệu, dựng oracle hoặc phản ví dụ. Không được công bố đã chứng minh khi chưa đủ bằng chứng; cũng không cần hỏi phép người dùng chỉ vì mệnh đề còn mở. |
| Fan-out cố định N=8 | **Bỏ như quy tắc cứng** | Phân công theo câu hỏi độc lập và điểm nghẽn, trong bốn slot hiện có. Tăng số agent chỉ khi có việc khác nhau và kết quả có thể kiểm; không coi tám câu trả lời tương tự là tám bằng chứng. |
| G1–G4, sổ và khai từng số trong văn xuôi | **Giữ mục đích, giảm thủ tục** | Dùng một manifest thí nghiệm và kết quả thô để tự sinh bảng/trạng thái. Chỉ thêm review viết tay cho claim toán, thay đổi giả thiết hoặc prior art; không dựng thêm hệ thẻ song song cho số đo thường kỳ. |
| Chọn `khả thi × khớp tài sản` cao nhất | **Sửa** | Tiêu chí này thiên về sửa kernel đã có. Giữ một nhánh cơ chế không kế thừa champion; ưu tiên phép thử giảm bất định về cấu trúc và có khả năng thắng frontier SOTA. |
| Chỉ dùng code gốc và instance của đối thủ mới được báo tỷ lệ | **Sửa** | Ưu tiên code gốc, cùng máy và kiểm adapter. Nhưng instance phải gồm cả miền mục tiêu của ta, và reimplementation trung thực có thể là bằng chứng phụ nếu khai rõ, được kiểm giá trị và rà tuning. Không có code gốc không cho phép loại đối thủ khỏi SOTA. |
| Phân loại đối thủ theo đại lượng, rà bài mới ngoài đồ thị trích dẫn | **Giữ và nâng cấp** | Thêm quyền truy cập dữ liệu, bicausal/causal, k-window/full-history, regularization, chứng nhận và tổng chi phí. Frontier cần NestedOT/PNOT cùng các phương pháp phù hợp đã rà; POT không đại diện SOTA. |
| Gắn nhãn mọi claim cũ bị rút | **Giữ theo phiên bản** | Không sửa lịch sử thí nghiệm đã đóng băng. Tạo quan hệ `supersedes/retracts`, để báo cáo hiện hành tự loại claim cũ; snapshot cũ phải hiện rõ ngày và trạng thái đã bị thay thế. |

Các đối chiếu với nguồn bên ngoài ở trên cho thấy workflow cũ có lõi kiểm chứng đáng giữ. Điểm cần đổi là cách chọn câu hỏi và cách phân bổ nghiên cứu. FunSearch không biện minh việc khóa mọi nhánh vào một skeleton; Co-Scientist không biến đồng thuận thành sự thật; AlphaEvolve không yêu cầu chỉ dùng một score hay một mức trừu tượng. Không cần cài thêm cả một framework để sửa các điểm này.

### Năm sửa đổi vận hành tối thiểu

1. **Một record cho một phép thử.** Record có claim, assumptions, prediction, checker, source/code hash, raw output, verdict và next action. Bảng champion, Cx/Gx cần thiết và báo cáo chat đều sinh từ record đó. Không bắt agent gõ lại cùng bằng chứng vào nhiều sổ.
2. **Một vòng giao tiếp có tác dụng trước khi chạy.** Reader gửi điều kiện của paper; theorist chỉ ra phép tính sẽ bỏ; skeptic trả phản ví dụ hoặc chỗ thiếu chứng minh; implementer đáp bằng test ID. Chỉ ghi phần trao đổi làm thay đổi claim/phép thử. Tranh luận không đổi gì sau hai lượt phải chuyển thành test hoặc lemma nhỏ.
3. **Phân biệt cơ chế sai với đo chưa đúng.** Trước verdict, verifier kiểm phép đo thật sự đo đại lượng đã khai: số support khác số cơ sở, Kendall inversion khác adjacent descent, gap tại nút khác gap tại gốc. Đây là điểm yếu thực tế đã nhiều lần đảo kết luận; thêm thẻ không tự giải quyết được nó.
4. **Để số lượng nhánh là mặc định điều phối.** Ba giả thuyết và trần 25% tối ưu vi mô trong config mới là lựa chọn ban đầu, không phải quy luật nghiên cứu. Không sản xuất đủ ba giả thuyết nông để đi qua cổng. Khi một phép thử quyết định cần thêm công, coordinator có thể phân bổ lại và ghi lý do trước run; không đổi mục tiêu hay ngưỡng công bố.
5. **SOTA gate đi trước lời tuyên bố thắng.** Tái lập và kiểm nghĩa của adapter trước timing; dùng frontier trên cùng mục tiêu/thông tin. Theo dõi comparator chưa tái lập như việc còn mở. Lợi ích từ cấu trúc cây phải qua work counts và ablation; vượt POT hoặc qua bốn cổng quản lý tài liệu không thay cho điều đó.

`WORKFLOW.md` mới đã xử lý phần lớn các thay đổi trên, đặc biệt `inconclusive`, quyền tự nghiên cứu, reviewer độc lập và SOTA frontier. Cần giữ nó là công cụ chạy nghiên cứu: sau khi khóa một record hợp lệ, bước kế tiếp phải là đọc đúng phần paper, kiểm lemma, viết probe hoặc tái lập comparator, thay vì tiếp tục thiết kế thêm cấp phán quyết.
