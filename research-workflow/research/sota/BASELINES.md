# Bảng baseline — tổng hợp và làm mới trích dẫn

Sinh ngày 2026-09-10. Nguồn định danh: OpenAlex API + arXiv API, truy vấn trong phiên này.

Đây là phần `research/sota/notes.md` tự khai còn thiếu: *"Refresh forward/backward citations and
2025–2026 search before the final confirmation cycle; this pass did not establish literature
completeness."* Bảng dưới **bổ sung** notes.md, không thay thế nó.

## Cách quét

Trích dẫn tiến của 6 công trình nền (lọc `from_publication_date:2025-01-01`) cộng 5 truy vấn chủ đề
(`adapted Wasserstein distance`, `bicausal optimal transport`, `nested distance stochastic`,
`causal optimal transport`, `adapted empirical measure`).

| bước | số kết quả |
|---|---|
| thô từ OpenAlex | 388 |
| sau lọc theo thuật ngữ phân biệt của lĩnh vực | 39 |
| sau bỏ nhiễu và gộp bản trùng preprint/tạp chí | 26 |
| đưa vào bảng baseline | 16 |

Lọc chặt là cần thiết: xếp hạng mờ của OpenAlex trả về cả giám sát thuỷ điện, suy giảm linh kiện
vệ tinh và dự đoán CTR — trùng chữ *causal optimal transport*, không trùng bài toán.

## Định danh 6 công trình nền: xác minh 6/6

| nhãn trong notes.md | định danh đã xác minh | năm | trích dẫn (OpenAlex) |
|---|---|---|---|
| Bontorno–Hou (PNOT) | `arXiv:2509.06702v1` | 2025 | 0 |
| Eckstein–Pammer | `arXiv:2203.05005v2` | 2022 | 2 |
| Qu–Tran (END) | `arXiv:2107.09864v1` | 2021 | 0 |
| Bayraktar–Han (FVI) | `arXiv:2306.12658v3` | 2023 | 1 |
| Calo và cộng sự (SVI/SPI) | `arXiv:2406.04056v2` | 2024 | 0 |
| Pichler–Weinhardt | `doi:10.1007/s10287-021-00415-7` | 2021 | **16** |

Không sai lệch nào so với notes.md. Số trích dẫn của bản preprint thấp vì OpenAlex tách bản
preprint khỏi bản tạp chí; đừng đọc chúng như mức độ ảnh hưởng.

## Tầng 1 — đối thủ exact (track solver)

### PNOT / NestedOT

`arXiv:2509.06702v1` · Bontorno, Hou · 2025 · preprint

- **Vai dưới objective:** Priority exact comparator; ledger role = exact k=1 predefined-root ONLY (certificate_eligible=false, k2_eligible=false, full_domain_qualified=false)
- **Mức bằng chứng:** đã đọc đầy đủ (lane trước)
- **Ghi chú:** API `markovian` is a boolean, not arbitrary memory k; C++ returns the additive cost V[0][0][0], not its pth root; wrapper falls back to Python on any C++ exception.
- **Mã nguồn:** `github.com/justinhou95/NestedOT @ 9f85f18fb32b67f9ba1112cf38a97f4f98c57d8a (vendored, sha256 verified)`

### AOTNumerics

`arXiv:2203.05005v2` · Eckstein, Pammer · 2022 · preprint

- **Vai dưới objective:** Reference algorithms + verification implementation; select bicausal, not causal
- **Mức bằng chứng:** đã đọc đầy đủ (lane trước)
- **Ghi chú:** Adapted Sinkhorn (path-level causal projection) differs from nested Sinkhorn (Sinkhorn inside backward induction); do not conflate. Gurobi dependency is an availability limitation, not a competitor failure.
- **Mã nguồn:** `github.com/stephaneckstein/aotnumerics @ 6f2d706009c4cb55c6f488686b194f6024819a4e`

### POT backward recursion

`library` · Flamary et al. · — · software

- **Vai dưới objective:** Implementation baseline and small-instance oracle; objective.pot_role forbids treating it as SOTA
- **Mức bằng chứng:** đang dùng trong dự án
- **Ghi chú:** Agreement with common_model._transport_value measured at 5.33e-15 on this grid.
- **Mã nguồn:** `PyPI: pot`

## Tầng 2 — xấp xỉ CÓ chứng nhận (track quality)

### Nested Sinkhorn

`doi:10.1007/s10287-021-00415-7` · Pichler, Weinhardt · 2021 · Computational Management Science

- **Vai dưới objective:** Priority certified-approximation comparator
- **Mức bằng chứng:** đã đọc đầy đủ (lane trước)
- **Ghi chú:** Provides nested duality + entropy-based approximation inequalities. CONSEQUENCE: possessing a root certificate is NOT itself novelty; contribution must be tightness, cost, or certifying while omitting computation. 16 citations (OpenAlex).

### END (entropic nested distance)

`arXiv:2107.09864v1` · Qu, Tran · 2021 · preprint

- **Vai dưới objective:** Second entropic starting point
- **Mức bằng chứng:** đã đọc đầy đủ (lane trước)
- **Ghi chú:** Authors note numerical instability at small regularization; compare a stabilized implementation rather than exploiting an avoidable underflow defect. Revision pinning still pending.
- **Mã nguồn:** `github.com/BenoitTran/END (Julia)`

### nested_sinkhorn_certified (lane D)

`runs/cycle_1/D/sinkhorn_tiny.json` · this project · 2026 · internal

- **Vai dưới objective:** certified-quality track ONLY; excluded from the exact track
- **Mức bằng chứng:** đo tại chỗ
- **Ghi chú:** Valid two-sided root bound on 20/20 tiny instances, max dual-feasibility violation 3.25e-16. Fails 1e-9 match on non-degenerate fixtures for a measured cost-law reason (width Theta(eps), iterations Theta(1/eps)); the iterations x eps product was measured on ONE 2x2 subproblem, so it is NOT a general lower bound.
- **Mã nguồn:** `adapters/nested_sinkhorn_comparator.D.py`

## Tầng 3 — xấp xỉ quy mô lớn, CẦN bộ chuyển đổi chứng nhận

### Fitted value iteration (FVI)

`doi:10.1007/s00245-025-10283-1` · Bayraktar, Han · 2025 · Applied Mathematics & Optimization

- **Vai dưới objective:** Scalable approximation and idea comparator; needs a certificate adapter
- **Mức bằng chứng:** đã đọc bản preprint; bản tạp chí MỚI tìm thấy
- **Ghi chú:** UPDATE FOUND THIS PASS: notes.md cites only arXiv:2306.12658; the journal version exists and should be the citation of record.
- **Mã nguồn:** `github.com/hanbingyan/FVIOT @ 6826b5603cab69ce61617abb7a27d0b1ebae9d9b`

### Scalable bi-causal OT (KL relaxation + policy gradients)

`arXiv:2605.17271v1` · Cao, Hoekstra, R. Xu, Y. Xu, Zhang · 2026 · preprint

- **Vai dưới objective:** NEW - absent from the existing panel. Candidate scalable comparator; NOT certificate-eligible without a conversion
- **Mức bằng chứng:** MỚI — chỉ mới đọc abstract
- **Ghi chú:** KL-penalised relaxation replaces HARD MARGINAL CONSTRAINTS with divergence penalties, converging to bicausal OT only as the penalty grows. A relaxed coupling therefore need not be feasible for the original problem, so it does NOT automatically yield an upper bound. Nonasymptotic regret guarantees are not a per-instance root certificate.

### SVI / SPI (occupancy reformulation)

`arXiv:2406.04056v2` · Calo, Jonsson, Neu · 2024 · NeurIPS 2024

- **Vai dưới objective:** Reformulation comparator; finite-horizon equivalence must be established before direct scoring
- **Mức bằng chứng:** đã đọc đầy đủ (lane trước)
- **Ghi chú:** Target is infinite-horizon DISCOUNTED stationary finite Markov, not undiscounted T=50. Setting gamma=1 in a theorem with inverse powers of (1-gamma) is invalid. Appendix F.2 attributes much of the speed to warm-starting transition couplings - a direct novelty overlap with our reuse.
- **Mã nguồn:** `github.com/SergioCalo/SVI (not installed or inspected)`

## Tầng 4 — biểu diễn / lượng tử hoá

### Tree approximation of scenario processes

`doi:10.1007/s10287-025-00542-5` · Kirui, Pflug, Pichler · 2025 · Computational Management Science

- **Vai dưới objective:** NEW - representation/quantisation comparator in the Pflug-Pichler nested-distance lineage
- **Mức bằng chứng:** MỚI — mới định danh, chưa đọc
- **Ghi chú:** Bears on the tree-construction half of the timing contract, which objective.comparison.time_includes requires us to count.

## Tầng 5 — tham chiếu giải tích (oracle, không phải đối thủ tốc độ)

### Adapted OT between Gaussian processes (discrete time)

`openalex:Gunasingam-Wong-2025` · Gunasingam, Wong · 2025 · Electronic Communications in Probability

- **Vai dưới objective:** Names the previously unnamed 'Gaussian adapted-OT formulas' oracle row
- **Mức bằng chứng:** MỚI — chỉ mới đọc abstract
- **Ghi chú:** Analytic special-case reference. True parameters cannot be granted in a paths-only timing comparison.

### Entropic adapted Wasserstein distance on Gaussians

`openalex:Acciaio-Hou-Pammer-2025` · Acciaio, Hou, Pammer · 2025 · Electronic Communications in Probability

- **Vai dưới objective:** NEW - closed-form reference for the ENTROPIC track
- **Mức bằng chứng:** MỚI — chỉ mới đọc abstract
- **Ghi chú:** Directly useful: lets nested Sinkhorn be validated against a closed form instead of only against a tiny exact oracle.

## Tầng 6 — lý thuyết đối ngẫu, nền của chứng nhận

### General duality and dual attainment for adapted transport

`openalex:Krsek-Pammer-2025` · Krsek, Pammer · 2025 · Applied Mathematics & Optimization

- **Vai dưới objective:** NEW - underpins the free lower bound mechanism (dual feasibility => valid bound)
- **Mức bằng chứng:** MỚI — chỉ mới đọc abstract
- **Ghi chú:** Prior art for the certificate side; must be cited before claiming any duality-based bound is new.

### A transfer principle for computing the adapted Wasserstein distance

`arXiv:2505.21337v2` · Jiang, Lim · 2025 · preprint

- **Vai dưới objective:** NEW - explicitly about COMPUTING the adapted distance
- **Mức bằng chứng:** MỚI — chỉ mới đọc abstract
- **Ghi chú:** Needs a full read before the panel is called complete.

## Tầng 7 — track estimator: tốc độ hội tụ và sàn nhiễu

### Convergence of the adapted empirical measure for mixing observations

`openalex:Mirmominov-Wiesel-2025` · Mirmominov, Wiesel · 2025 · preprint

- **Vai dưới objective:** NEW - bears directly on the sampling-noise-floor problem
- **Mức bằng chứng:** MỚI — chỉ mới đọc abstract
- **Ghi chú:** The measured contrast/noise ratio at T=8 was 1.51x (ar1) and 1.31x (second-order), i.e. most of the quantity may be sampling noise. This literature is where the rate for that gap lives.

### Fast rate of convergence of the smooth adapted Wasserstein distance

`openalex:Larsson-Park-Wiesel-2025` · Larsson, Park, Wiesel · 2025 · preprint

- **Vai dưới objective:** NEW - convergence rate, same noise-floor question
- **Mức bằng chứng:** MỚI — chỉ mới đọc abstract
- **Ghi chú:** Smoothed variant; check whether the rate transfers to the unsmoothed quantized target.

## Bảy mục MỚI so với panel hiện có

| mục | vì sao quan trọng |
|---|---|
| **Cao, Hoekstra, R. Xu, Y. Xu, Zhang 2026** `arXiv:2605.17271` | Thuật toán bicausal OT quy mô lớn, panel hiện tại **không có**. Nhưng nới lỏng KL thay ràng buộc biên **cứng** bằng phạt phân kỳ, chỉ hội tụ khi hệ số phạt tăng — nên coupling nới lỏng **không** đương nhiên khả thi cho bài gốc, và **không** đương nhiên cho cận trên. Bảo đảm regret phi tiệm cận **không phải** chứng nhận theo từng instance. |
| Acciaio, Hou, Pammer 2025 — entropic AW trên Gaussian | Dạng đóng cho track **entropic**: cho phép kiểm nested Sinkhorn bằng công thức thay vì chỉ bằng oracle tiny. |
| Kršek, Pammer 2025 — đối ngẫu tổng quát cho adapted transport | Nền của cận dưới miễn phí (khả thi đối ngẫu ⇒ cận hợp lệ). Phải trích trước khi nói cơ chế chứng nhận nào là mới. |
| Jiang, Lim 2025 `arXiv:2505.21337` | Nói thẳng về **tính toán** khoảng cách adapted. Chưa đọc. |
| Mirmominov, Wiesel 2025 · Larsson, Park, Wiesel 2025 | Tốc độ hội tụ của độ đo thực nghiệm adapted — đúng chỗ trả lời vấn đề **sàn nhiễu lấy mẫu** (tỉ lệ tương phản/nhiễu đo được ở T=8 chỉ 1,51× và 1,31×). |
| Kirui, Pflug, Pichler 2025 — xấp xỉ cây | Nửa dựng-cây của hợp đồng thời gian, thứ `comparison.time_includes` bắt phải tính. |
| Bayraktar–Han bản **tạp chí** `doi:10.1007/s00245-025-10283-1` | notes.md chỉ trích bản arXiv. |

## Điều bảng này KHÔNG thiết lập

- **Bảy dòng mới chỉ mới đọc abstract**, một dòng mới chỉ mới định danh. Chúng **chưa** được đọc đầy đủ
  như năm công trình nền trong notes.md. Không dòng nào trong số đó đủ tư cách làm đối thủ đã định tính
  cho tới khi có bản đọc đầy đủ và, nếu có mã, một bản pin revision.
- **Không có tuyên bố tốc độ hay SOTA nào.** Không đối thủ nào được chạy trong lần quét này.
- Tính đầy đủ của literature **vẫn chưa** thiết lập được: quét này chỉ phủ 2025+ và chỉ qua OpenAlex;
  chưa quét backward citation, chưa quét kỷ yếu hội nghị không có DOI.

## Việc tiếp theo, theo thứ tự

1. Đọc đầy đủ `arXiv:2605.17271` và quyết định nó vào track nào; nếu nó cho được cận trên hợp lệ thì
   nó là đối thủ mạnh nhất của track quality, còn nếu không thì nó là đối thủ track tốc độ và phải nói rõ.
2. Đọc Kršek–Pammer trước khi phát biểu bất cứ điều gì mới về cơ chế chứng nhận.
3. Dùng Acciaio–Hou–Pammer làm oracle giải tích cho nested Sinkhorn.
4. Đọc hai bài tốc độ hội tụ để biết sàn nhiễu ở T=50 có tự đóng lại theo cỡ mẫu hay không.

