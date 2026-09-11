# Tri thức nền: adapted OT, biểu diễn và chứng nhận

Các định nghĩa, kết quả và điều kiện áp dụng cho nghiên cứu biểu diễn tái sử
dụng theo [mục tiêu](SCOPE.md). Mỗi kết quả dẫn nguồn và phạm vi kiểm chứng;
phiên bản mã và khả năng chạy comparator ở [thí nghiệm và công cụ](BENCHMARKS.md).

## 1. Đối tượng toán học và thông tin

Một task cố định horizon hữu hạn, hai luật quá trình (P,Q), filtration, chi phí
và chuẩn hóa. Với filtration tự nhiên, (X_{1:t}), (Y_{1:t}) là lịch sử quan sát.
Coupling π có biên (P,Q) là **causal từ X sang Y** nếu luật điều kiện của
(Y_{1:t}) biết toàn bộ (X_{1:T}) chỉ phụ thuộc (X_{1:t}), với mọi t.
**Bicausal** yêu cầu thêm điều kiện đối xứng từ Y sang X. Với filtration khác
filtration tự nhiên, phải khai rõ thông tin có ở mỗi thời điểm và dùng định nghĩa
coupling tương ứng; một cây lưu path tự nó không bảo đảm điều kiện này.

Đại lượng tham chiếu là

```text
D(P,Q) = inf_{π ∈ Π_bc(P,Q)} E_π[Σ_t c_t(X_t,Y_t)].
```

Chỉ gọi (D=AW_p^p) khi (c_t), metric và chuẩn hóa khớp định nghĩa đó.
(AW_p=D^{1/p}) có cùng thứ tự với D khi p cố định; sai số tuyệt đối và hằng số
distortion phải được chuyển đúng đơn vị. Không so thứ tự các giá trị thuộc
những horizon, filtration hoặc cost khác nhau như một task đồng nhất.

Trên mô hình hữu hạn, trạng thái h phải chứa đủ thông tin cho luật chuyển tiếp.
Với chi phí cộng theo thời gian, backward recursion tại cặp trạng thái có dạng
V_t(h,g) = c_t(h,g) + min_γ ⟨γ,V_{t+1}⟩, với γ coupling hai luật
chuyển tiếp có điều kiện tại h,g. Root ngẫu nhiên cần phép coupling ban đầu;
root tất định dùng giá trị tại cặp trạng thái đã khai. Với mô hình Markov phù hợp,
có thể tìm coupling tối ưu Markov theo cặp trạng thái; điều này không nói mọi
coupling bicausal đều là Markov.

Hai quá trình có hình học path gần nhau vẫn có thể khác về thời điểm lộ thông tin
hoặc luật tương lai có điều kiện. Biểu diễn chỉ giữ marginal, nhãn quan sát hiện
tại hoặc cây hình học cần một cầu nối riêng tới tập coupling bicausal.

## 2. Luật hữu hạn, dữ liệu quan sát và population

Cần phân biệt ba đối tượng: luật population P; luật thực nghiệm lượng tử hóa giữ
toàn bộ prefix; luật hữu hạn tái dựng bằng pooling theo cửa sổ k. Hàm
[`build_window_model`](../adapters/common_model.py) dùng tối đa k trạng thái lượng
tử hóa cuối để gom transitions. Solver tính D của luật tái dựng đó.

Certificate hữu hạn không tự bao sai số lấy mẫu, lượng tử hóa hoặc cửa sổ.
Quá trình gốc Markov chưa bảo đảm quá trình sau lượng tử hóa vẫn Markov; pooling
k có thể đổi cả luật và cấu trúc thông tin. Định lý cho estimator full-prefix
hoặc một estimator Markov cụ thể cần được đối chiếu với phép dựng thực tế.

Generators dùng Gaussian innovations có support không bị chặn. Các row được sinh
độc lập; phụ thuộc thời gian trong một row khác với mixing giữa các path quan sát.
Min/max của mẫu không tạo support compact cho population. Chuẩn hóa theo chúng
cũng không tự chứng minh lưới đang dùng khớp lưới trong một định lý thống kê.

Nếu đã có sai số khoảng cách tất định |d_hat-d| ≤ e, thì với p=2,
|d_hat²-d²| ≤ e(2d+e). Chặn kỳ vọng bậc một của sai số khoảng cách
không tự cho chặn moment bậc hai; certificate tương đối còn cần thông tin về scale
hoặc lower bound. Discrepancy hữu hạn trừ population trên một mẫu là một realization,
chưa là expected bias và chưa tách các nguồn sai số của pipeline.

Trong chế độ chỉ có paths, tham số generator và nhãn oracle là thông tin đặc quyền.
Dùng chúng cho diagnostic phải khai riêng; dùng để học biểu diễn/calibration phải
tính công và không diễn giải thành lợi thế chỉ từ paths. Các ranh giới trên được
kiểm chi tiết trong [audit estimator](../research/sota/DOMAIN_RATE_AUDIT_20260910.md).

## 3. Các định lý thống kê dùng được dưới điều kiện nào

**Adapted empirical measure tổng quát.** Backhoff–Bartl–Beiglböck–Wiesel xét support
(([0,1]^d)^T) và disintegration kernels Lipschitz theo Wasserstein. Với estimator
adapted của bài, Thm 1.5 cho expected AW1 error có rate (N^{-1/(T+1)}) khi d=1.
Đây là upper rate với hằng số phụ thuộc cấu trúc bài toán.
[Bài gốc](https://arxiv.org/abs/2002.07261).

**Estimator khai thác Markov.** Cùng giả thiết compact/Lipschitz và thêm P Markov,
Thm 6.1 cho các rate (N^{-1/3}) (d=1), N^(-1/4) log N (d=2),
(N^{-1/(2d)}) (d≥3), kèm concentration
P[AW1 ≥ C·rate+ε] ≤ 2T exp(-cNε²).
Số mũ không phụ thuộc T; C,c vẫn có thể phụ thuộc T,d và hằng số Lipschitz.
Kết quả áp cho phép dựng Markov của bài, chưa cho pooling k-window của repo.
[Phạm vi đã audit](../research/sota/MOULOS_BACKHOFF_AUDIT_20260910.md).

**Quan sát mixing.** Mirmominov–Wiesel, Thm 4.2, xét AW1 cộng theo thời gian,
support compact, kernels Lipschitz và adapted empirical measure full-prefix:

```text
E AW1(P,P̂_N) ≤ C sqrt(1 + 2 Σ_s η(s)) rate∞(N),
rate∞(N) = N^(-1/(T+1)) khi d=1.
```

η đo phụ thuộc giữa các quan sát path/block; bằng 0 trong trường hợp độc lập.
Thm 4.6 cho support không bị chặn dùng Assumption 4.5 và rate khác:
(N^{-(r-1)/(rT)}+N^{-1/((d+1)T)}) khi d=1,2; r ở đây là tham số moment,
không phải chỉ số biến target thành AW2². [Bài gốc, §§3–4](https://arxiv.org/html/2512.18838v1).

**Smooth AW.** Larsson–Park–Wiesel, Thm 4, cho C/sqrt(n) với iid paths,
1<p<∞, σ>0 cố định và
∫ exp(q|x|²/(2σ²)) P(dx)<∞, trong đó (q>8p(2p-1)(T+9)).
Đây là điều kiện exponential moment. C có thể tăng mạnh theo dimension và khi
σ nhỏ. Gaussian convolution làm đổi hai luật; smoothing bias được kiểm bằng
moduli của kernels, thành (O(σ)) khi có regularity Lipschitz thích hợp.
[Bài gốc, §§1.2–1.4](https://arxiv.org/html/2503.10827v2).

Với Gaussian tâm 0 có covariance A, điều kiện exponential moment trên tương
đương σ² > q λ_max(A). Với p=2,T=50, q phải lớn hơn 2832.
Không đạt điều kiện đủ này chỉ ngăn viện dẫn định lý đó; chưa chứng minh tốc độ
thật không nhanh. Tương tự, hệ số N^(-1/51) ≈ 0.84 không phải sai số đo
được, sàn nhiễu, lower bound hoặc bằng chứng bất khả nhận dạng. Các rate này
không buộc đổi estimand; cần target và cầu nối thống kê phù hợp trước khi dùng.

## 4. Oracle Gaussian và giới hạn của ghép đồng bộ

Gunasingam–Wong, Thm 1.1, xét paths Gaussian vô hướng rời rạc, filtration tự nhiên,
covariances xác định dương (A=LL^⊤,B=MM^⊤), Cholesky có đường chéo dương:

```text
AW2²(N(a,A),N(b,B)) = ||a-b||² + tr(A)+tr(B) - 2 Σ_j |(LᵀM)_jj|.
KR_cost - AW2² = 4 Σ_j max(0, -(LᵀM)_jj).
```

Ghép Knothe–Rosenblatt tuần tự dùng cùng innovations tối ưu khi mọi column product
(LᵀM)_jj ≥ 0. Công thức là oracle cho toàn bộ quadratic additive cost;
không bao absolute cost, luật phi Gaussian hoặc filtration tùy ý.
[Định lý gốc](https://arxiv.org/html/2404.06625v4).

Với AR1 của repo, (X_0=0) tất định ở cả hai phía; có thể bỏ coordinate này vì
chi phí bằng 0 và dùng X_1,...,X_T không suy biến. Innovation factor là
(L_{ij}=σ a^{i-j}) khi i≥j. Population KR tối ưu chưa kéo theo KR tối ưu cho
law lượng tử hóa/k-window hoặc một policy NW/SVD khác. Oracle đã triển khai dùng
float64; phạm vi và phép kiểm độc lập ở [Gaussian oracle](../research/theory/GAUSSIAN_ORACLE_20260910.md).

Acciaio–Hou–Pammer có công thức Gaussian theo khối cho adapted quadratic transport
có entropy và trường hợp không regularization. Dùng làm oracle cần khớp dimension,
filtration, quy ước KL, hệ số regularization và law Gaussian của theorem; không
đồng nhất giá trị continuous Gaussian với giá trị một cây mẫu hữu hạn.
[Bài gốc](https://arxiv.org/abs/2412.18794v2).

Jiang–Lim đưa nguyên lý chuyển qua causal covariance factorization; công thức
cho fractional Brownian motion dùng chuẩn Hilbert–Schmidt của hiệu kernels và
ghép đồng bộ trong setting của theorem. Đây là nguồn oracle thời gian liên tục,
không phải định lý rate empirical hoặc comparator cùng lưới hữu hạn.
[Bài gốc](https://arxiv.org/abs/2505.21337v2).

## 5. Bellman, đối ngẫu và certificate là nền đã có

Moulos xét Markov chains trên state space hữu hạn, kernels thuần nhất và horizon
vô hạn, discount β∈(0,1] với nonnegative cost. Thm 1 đặc trưng giá trị bicausal
bằng Bellman fixed point và sự tồn tại coupling tối ưu Markov. Value iteration
từ 0 tăng đơn điệu tới giá trị; khi β<1 có contraction và nghiệm bounded duy nhất.
Vì vậy cầu nối bicausal OT–MDP–Bellman đã là prior art tường minh. Chuyển các chặn
stationary sang mô hình không thuần nhất/horizon hữu hạn cần lập luận tương ứng.
[Bài gốc](https://arxiv.org/abs/2010.06831).

Kršek–Pammer thiết lập duality và dual attainment cho các lớp causal/bicausal
adapted transport dưới giả thiết của từng theorem; không cung cấp một thuật toán
chứng nhận rẻ cho mọi instance. Feasible dual cho lower bound, feasible bicausal
policy cho upper bound. Để thành certificate số học tại root còn phải kiểm
feasibility, normalization, local-to-root propagation và sai số tính toán.
[Bài gốc](https://arxiv.org/abs/2401.11958v2).

Tổng các marginal OT cho một lower bound của additive bicausal target; product
conditional coupling cho một upper bound khả thi trên mô hình đã khai. Khoảng
([L,U]) chứng nhận thứ tự strict khi (U(q,a)<L(q,b)); khoảng chồng nhau giữ
unresolved. Đây là phép suy ra sơ cấp. Đóng góp cần nằm ở độ sắc, điều kiện kiểm
được và công transport thật sự tránh được; lower bound đơn lẻ chưa chứng nhận thứ tự.

Pichler–Weinhardt và Qu–Tran đã nghiên cứu nested entropy/Sinkhorn và approximation.
Adapted Sinkhorn dùng causal projections ở path level khác nested Sinkhorn nằm
trong backward recursion. Scalar regularized hoặc residual float chưa là khoảng
cho target gốc: cần conversion, feasible primal/dual và kiểm truyền sai số.
[Nested Sinkhorn](https://doi.org/10.1007/s10287-021-00415-7), [END](https://arxiv.org/abs/2107.09864v1),
[Eckstein–Pammer](https://arxiv.org/abs/2203.05005v2).

## 6. Những đối chiếu gần nhất cho biểu diễn và thuật toán

| Dòng công trình | Phần đã có và điều cần đối chiếu |
|---|---|
| [Chen et al., WL cho stochastic processes](https://proceedings.mlr.press/v221/chen23a.html) | Biểu diễn điều kiện đệ quy và liên hệ bicausal; cần khớp cost/filtration trước claim mới. |
| [Brugère et al., OTM/WL/OTC](https://proceedings.mlr.press/v237/brugere24a.html) | Framework khoảng cách Markov; terminal-style, discounted và regularized recursions không tự bằng finite additive D. |
| [Tree-sliced Wasserstein](https://arxiv.org/abs/1902.00342v3), [Flowtree](https://proceedings.mlr.press/v119/backurs20a.html) | Shared tree, edge-mass L1 và tìm hàng xóm ordinary W1 đã có; cần bảo đảm riêng về adapted information. |
| [Scenario tree reduction](https://doi.org/10.1007/s10479-026-07062-8) | Compression và workload multistage; giảm cây cần tính conversion error và build cost; đúng ranking chưa chứng nhận quyết định downstream. |
| [NestedOT / PNOT](https://arxiv.org/abs/2509.06702v1) | Strong numerical DP comparator; eligibility k=1/root lịch sử không tự mở sang arbitrary k hoặc rigorous arithmetic. |
| [FVI, Bayraktar–Han](https://doi.org/10.1007/s00245-025-10283-1) | Xấp xỉ giá trị có khả năng scale; cần adapter để chứng nhận cùng D. |
| [SVI/SPI, Calo et al.](https://arxiv.org/abs/2406.04056v2) | Occupancy reformulation, stationary discounted Markov và reuse coupling; không đặt γ=1 trong theorem có ((1-γ)^{-1}). |
| [Cao et al., scalable bicausal OT](https://arxiv.org/abs/2605.17271v1) | KL relaxation, Γ-convergence khi penalty tăng và regret dưới giả thiết; coupling relaxed chưa khả thi cho D, không tự tạo upper bound theo instance. |

Tree-Wasserstein đóng dạng và generic recursive lifting chưa đủ xác lập novelty.
Cần một đánh đổi định lượng giữa kích thước biểu diễn, độ sắc và chi phí quyết định
trên lớp quá trình có cấu trúc. Chi phí gồm dựng/học, labels, insertion, query,
update, kiểm điều kiện và certificate; amortization phải nêu số đối tượng/truy vấn.
Tải được source, chạy được code và đủ tư cách certificate là ba trạng thái khác nhau.

## 7. Công cụ ngoài domain: dùng theo câu hỏi cụ thể

| Công cụ và nguồn gốc | Điều kiện dùng trong adapted OT |
|---|---|
| [BRTDP](https://doi.org/10.1145/1102351.1102423), [LAO*](https://doi.org/10.1016/S0004-3702(01)00106-0), [prioritized sweeping](https://doi.org/10.1023/A:1022635613229) | Khi cần hai chặn và refine theo residual/occupancy. Khung ưu tiên đã có; phải xử lý coupling polytope và công local OT cụ thể. |
| [Safe LP bounds](https://doi.org/10.1007/s10107-003-0433-3), [Jansson](https://doi.org/10.1137/S1052623402416839), [Lurupa](https://doi.org/10.4230/DagSemProc.05391.6) | Khi chuyển nghiệm xấp xỉ thành chặn an toàn bằng rounding/residual. Hai bài chính mới có evidence mức abstract trong hồ sơ; cần theorem đọc được hoặc dẫn lại riêng trước implementation. |
| [Schmitzer, shielding](https://arxiv.org/abs/1510.05466v2) | Def 3.3 và Cor 3.10 chứng nhận tối ưu global của OT tĩnh từ neighbourhood shielding. Cost (c+V_{child}) cần tự thỏa điều kiện; geometry của c riêng chưa đủ. Tổng complexity không được bảo đảm bởi kết quả này. |
| [Dual-weighted residual](https://doi.org/10.1017/S0962492901000010) | Khi thiết kế quy trách sai số root: residual × occupation có cấu trúc tương tự residual × adjoint. Cần dẫn riêng identity/Bellman bounds, kiểm cancellation và effectivity; phép tương tự chưa là theorem cho OT. |
| [CEGAR](https://doi.org/10.1145/876638.876643), [MDP minimization](https://doi.org/10.1016/S0004-3702(02)00376-4), [bisimulation metrics](https://arxiv.org/abs/1207.4114) | Khi nghiên cứu quotient/merge–split: cần điều kiện bảo toàn conditional future, approximation error và filtration. Chỉ kích hoạt khi construction abstraction được chọn. |
| Warm start, reoptimization, column generation | Chỉ khi repeated local LP hoặc sparse pricing là nghẽn đã xác nhận; nguồn theorem cụ thể còn cần pin, lợi ích phải đo sau chi phí quản lý trạng thái. |

Các nguồn cross-domain chưa chứng minh cơ chế phù hợp bicausal OT hoặc thắng chi
phí. Ranh giới đọc/kiểm từng nguồn ở [hồ sơ kỹ thuật](../research/sota/EXTERNAL_KNOWLEDGE_20260910.md)
và [bản đồ công cụ](../research/sota/CROSS_DOMAIN_MAP_20260910.md). Định lý Monge/NW-corner
là prior art; cần Monge của toàn bộ local cost, gồm continuation, trước dispatch.

## 8. Mức bằng chứng và những phần còn cần kiểm

Các rate và Gaussian scalar formula ở trên dựa vào audit statement/theorem được
dẫn; việc kiểm bằng tìm chuỗi toàn văn không tương đương kiểm từng dòng proof.
Các hồ sơ survey không thiết lập literature completeness hoặc tốc độ/SOTA. Khi
claim mới chịu lực vào một theorem, phải đối chiếu đúng phiên bản và giả thiết.

Kirui–Pflug–Pichler [tree approximation](https://doi.org/10.1007/s10287-025-00542-5)
mới được định danh, chưa có full-text audit. Các kết quả KR near-optimality ngoài
Gaussian chưa được nhận qua hai nguồn ứng viên
[KR topology](https://arxiv.org/abs/2312.16515) và [AW cho SDE](https://arxiv.org/abs/2209.03243).
Những nguồn này là đầu mối tra cứu có điều kiện, chưa là giả thiết đã giải quyết.
