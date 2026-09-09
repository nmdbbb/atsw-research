# Cycle 3 — Tra literature: TÁI CÔNG THỨC cho nested / bicausal distance
Bài toán đích: nested distance (Pflug–Pichler) giữa hai chuỗi Markov rời rạc, T = 50, n = 20 và m = 23
trạng thái (n·m = 460 cặp/tầng, ~22 540 bài LP nhỏ 20×23 tổng cộng).

Ngày tra: 2026-09-08. Mọi con số thời gian trong mục "Số liệu đã công bố" là trích từ bài báo, không phải
đo lại. Mọi con số trong mục "Kiểm chứng" là đo trên máy local (20 core, numpy/POT 0.9.7, single thread),
script nằm ngay trong spec.

---

## 0. Quan sát cấu trúc là cái mở ra tất cả các spec dưới đây

Với chi phí cộng dồn theo tầng (dạng chuẩn của nested distance / AW_p), quy nạp lùi là

    V_T(x,y) = 0
    V_t(x,y) = min_{π ∈ Cpl(P(x,·), Q(y,·))}  Σ_{x',y'} π(x',y') · [ c(x',y') + V_{t+1}(x',y') ]

**Ma trận chi phí của bài toán trong, W_t(x',y') := c(x',y') + V_{t+1}(x',y'), KHÔNG phụ thuộc vào (x,y).**
Cả 460 bài toán ở một tầng dùng đúng một ma trận chi phí; chỉ hai biên (P(x,·), Q(y,·)) là khác nhau.

Đây không phải nhận xét mới trong literature — nó chính là dạng của bước "transition coupling improvement"
trong O'Connor–McGoff–Nobel (JMLR 2022), Algorithm 1b/2b: `d²` bài OT với cùng ma trận bias `h` làm chi phí,
"decoupled and thus may be computed in parallel". Nhưng cách cài hiện tại (gọi POT từng cặp) *không* khai
thác nó: 460 lần gọi solver với cùng một ma trận chi phí là 460 lần dựng lại cùng một bài toán đối ngẫu.
Ba trong năm spec dưới đây chỉ là những cách khác nhau để tiêu thụ dữ kiện này.

Hệ quả trực tiếp cho câu hỏi "tại sao 0,66–0,70x chỉ là hằng số": vì nó vẫn giữ nguyên kiến trúc
"một solver / một cặp". Trần hằng số nằm ở kiến trúc đó, không ở solver.

---

## SPEC 1 — Một LP duy nhất: LP độ đo chiếm dụng (occupation-measure / MDP-LP)

**Ý tưởng cốt lõi.** Bicausal OT giữa hai chuỗi Markov là một MDP: trạng thái là cặp (x,y), *hành động*
là một coupling của P(x,·) và Q(y,·) (một điểm trong đa diện vận chuyển), chi phí một bước là c. Với MDP
hữu hạn chân trời, LP độ đo chiếm dụng biến toàn bộ bài toán thành MỘT LP: biến là
z_t(x,y,x',y') ≥ 0 (khối lượng chung tại tầng t).

    min  Σ_t Σ_{x,y,x',y'} z_t(x,y,x',y') · c_t(x',y')
    s.t. Σ_{y'} z_t(x,y,x',y') = P(x,x') · μ_t(x,y)      ∀ t,x,y,x'      (biên hàng)
         Σ_{x'} z_t(x,y,x',y') = Q(y,y') · μ_t(x,y)      ∀ t,x,y,y'      (biên cột)
         μ_{t+1}(x',y')        = Σ_{x,y} z_t(x,y,x',y')  ∀ t,x',y'       (bảo toàn luồng)
         μ_1 = δ_{(x_0,y_0)}
với μ_t(x,y) := Σ_{x',y'} z_t(x,y,x',y'). Hai họ ràng buộc biên là *tuyến tính* (μ_t là hàm tuyến tính
của z_t), nên đây là LP thật, không phải bilinear.

**Cấu trúc được khai thác.** Tính Markov (đủ để index theo (x,y) thay vì theo lịch sử) + tính đệ quy của
nested distribution.

**Kích thước tuyên bố (tính đúng cho T=50, n=20, m=23).**
- biến: T·(n·m)² = 50 · 460² = **10 580 000**
- hàng: T·n·m·(n+m) + T·n·m = 989 000 + 23 000 = **1 012 000**
- nonzero ước lượng: ~3 · số biến ≈ **31 740 000**

**Phán quyết: KHÔNG nên đi đường này, và literature nói thẳng như vậy.**
- O'Connor–McGoff–Nobel, Remark 8: trong các thuật toán MDP thay thế cho policy iteration, LP "does not
  admit a computationally tractable implementation". Họ chọn policy iteration chính vì lý do đó.
- Mốc so sánh thực nghiệm: Bayraktar–Han (arXiv:2306.12658, Table 1 + văn bản) chạy LP một-lần của
  Eckstein–Pammer ở T=10 trên cây nhị phân *không tái hợp*; Gurobi báo 701 098 hàng / 1 048 576 cột /
  23 068 672 nonzero **sau presolve** và không xong trong 1000 s. LP của ta lớn hơn ~10x về cột và ~1,4x
  về nonzero. Không có ai báo giải được ở T=50.
- Lưu ý phân biệt: LP một-lần trong Eckstein–Pammer, Lemma 3.11 là LP trên **không gian đường đi**
  (biến π_{x,y} với x,y là đường đi đầy đủ) → 20^50 biến, hoàn toàn vô nghĩa ở đây. LP ở trên là bản
  Markov-hoá, tốt hơn nhiều nhưng vẫn thua quy nạp lùi.

**Pseudocode (để đo, không để dùng).**
```
build_oneshot_lp(P, Q, c, T):
  vars z[t,x,y,xp,yp] >= 0                        # T*(n*m)^2
  for t, x, y:
      mu = sum(z[t,x,y,:,:])
      for xp: add_eq( sum_yp z[t,x,y,xp,yp] - P[x,xp]*mu == 0 )
      for yp: add_eq( sum_xp z[t,x,y,xp,yp] - Q[y,yp]*mu == 0 )
  for t < T, xp, yp: add_eq( sum_{x,y} z[t,x,y,xp,yp] - sum_{a,b} z[t+1,xp,yp,a,b] == 0 )
  add_eq( sum_{xp,yp} z[1,x0,y0,xp,yp] == 1 )
  minimize sum_t sum z[t,x,y,xp,yp]*c[t,xp,yp]
```

**Nguồn.**
- V. Moulos, *Bicausal Optimal Transport for Markov Chains via Dynamic Programming*, arXiv:2010.06831;
  IEEE ISIT 2021, pp. 1688–1693, doi:10.1109/ISIT45174.2021.9517977 — quan hệ bicausal OT ↔ MDP, điều kiện
  cần và đủ, value iteration.
- K. O'Connor, K. McGoff, A. B. Nobel, *Optimal Transport for Stationary Markov Chains via Policy
  Iteration*, JMLR 23(45):1–52, 2022 (arXiv:2006.07998) — TC-MDP (Prop. 6), Thm 7, **Remark 8** (LP không
  khả thi), ExactOTC O(d⁶) mỗi vòng đánh giá + O(d⁵ log d) mỗi vòng cải thiện, EntropicOTC Õ(d⁴ε⁻⁴)/vòng.
- S. Eckstein, G. Pammer, *Computational methods for adapted optimal transport*, Ann. Appl. Probab.
  34(1A):675–713, 2024, doi:10.1214/23-AAP1975 — Lemma 3.11 (LP một-lần trên không gian đường đi).
- Chuẩn LP-của-MDP: M. Puterman, *Markov Decision Processes*, ch. 6.9 (LP formulation).

**Điều gì phải đúng để áp dụng ở đây:** phải có solver LP giải nổi 10,6 triệu cột / 1 triệu hàng nhanh hơn
22 540 bài LP 20×23 — literature và mốc Gurobi ở trên nói là không. Ghi nhận đây là **kết quả âm tính**.

---

## SPEC 2 — Nghiệm dạng đóng khi nhân chuyển đơn điệu ngẫu nhiên (KHÔNG LP, KHÔNG quy nạp lùi cần solver)

**Đây là spec duy nhất phá được asymptotics, và nó có nguồn + đã kiểm chứng số ở đúng T=50, n=20, m=23.**

**Ý tưởng cốt lõi.** Nếu (i) không gian trạng thái là 1-D có thứ tự, (ii) chi phí tầng c là *submodular*
(điều kiện Monge: c(x,y)+c(x̄,ȳ) ≤ c(x,ȳ)+c(x̄,y) với x ≤ x̄, y ≤ ȳ — đúng cho |x−y|^p, p ≥ 1), và
(iii) cả hai nhân chuyển *đơn điệu ngẫu nhiên* (mỗi hàng tăng theo thứ tự trội bậc nhất FOSD khi trạng thái
hiện tại tăng), thì:
- nghiệm bài toán trong là **monotone rearrangement** (quy tắc góc tây-bắc / quantile coupling) — dạng đóng,
  O(n+m), không solver;
- và tính submodular **tự truyền ngược** qua quy nạp: W_t = c + V_{t+1} vẫn submodular ở mọi tầng. Đây là
  bước then chốt: nó có nghĩa là ta không cần kiểm tra lại giả thiết ở mỗi tầng, và không cần LP ở tầng nào.
- Toàn cục: coupling tối ưu là **Knothe–Rosenblatt rearrangement**, nên có thể tính bằng một lượt xuôi
  (occupation measure) hoặc một lượt lùi rẻ — cả hai đều không có LP.

**Cấu trúc được khai thác.** Tính đơn điệu ngẫu nhiên của nhân chuyển (Daley 1968) + submodularity của chi
phí. Ghi chú quan trọng: **TP2 / totally positive bậc 2 ⟹ MLR ordering ⟹ FOSD ordering ⟹ đơn điệu ngẫu
nhiên**, nên câu hỏi "nhân totally positive thì sao" trả lời được qua đúng định lý này (TP2 là điều kiện
đủ, mạnh hơn cần thiết).

**Độ phức tạp tuyên bố.** O(T · n · m · (n+m)) = 49 · 460 · 43 ≈ **9,7 · 10⁵** phép tính, thay cho
T·n·m bài LP. Không có LP nào.

**Pseudocode.**
```
# tiền kiểm tra, O(T n^2 + T m^2)
assert submodular(c)                                      # c[1:,1:]-c[1:,:-1]-c[:-1,1:]+c[:-1,:-1] <= 0
assert stoch_monotone(P) and stoch_monotone(Q)            # cumsum ngược mỗi hàng phải không giảm theo x

cumA[x] = cumsum(P[x]); cumB[y] = cumsum(Q[y])            # tính 1 lần, dùng cho mọi tầng
for each pair (x,y):                                      # tiền xử lý 1 lần
    U[x,y]  = sort(concat(cumA[x], cumB[y]))              # n+m điểm gãy
    Wd[x,y] = diff(U[x,y], prepend=0)                     # bề rộng đoạn
    Ix[x,y] = searchsorted(cumA[x], U[x,y]).clip(0,n-1)
    Jy[x,y] = searchsorted(cumB[y], U[x,y]).clip(0,m-1)

V = zeros(n,m)
for t = T-1 down to 1:
    W = c + V
    V[x,y] = sum_s Wd[x,y,s] * W[ Ix[x,y,s], Jy[x,y,s] ]  # einsum, không vòng lặp Python
return V[x0,y0]
```

**Kiểm chứng số (local, T=50, n=20, m=23, c = |x−y|², nhân Gauss rời rạc hoá — đơn điệu ngẫu nhiên).**
| phương pháp | giá trị V(x₀,y₀) | wall |
|---|---|---|
| quy nạp lùi + POT `emd2` từng cặp (22 540 LP) | 0.0903221584 | 2.27 s |
| dạng đóng NW-corner, vòng lặp Python | 0.0903221584 | 0.24 s |
| dạng đóng, vector hoá (einsum) | 0.0903221584 | **0.0051 s** |

sai khác lớn nhất trên toàn bộ 460 cặp: **5,8 · 10⁻¹⁵** (chính xác đến sai số máy); tăng tốc **445×** so với
gọi POT từng cặp. `W_t` submodular ở cả 49 tầng — đúng như định lý dự đoán.

**Kiểm chứng âm (giả thiết là load-bearing, không phải trang trí).** Xáo hàng của P để phá đơn điệu ngẫu
nhiên: NW-corner cho 6.2366 trong khi nghiệm đúng là 4.7069 → **vượt 32,5%**, và submodularity không còn
truyền được. Nghĩa là: phải kiểm tra giả thiết, không được giả định.

**Nguồn.**
- B. A. Robinson, M. Szölgyenyi, *Adapted Wasserstein distance between the laws of SDEs*,
  arXiv:2209.03243 — **Proposition 3.5** (KR rearrangement tối ưu khi hai luật *stochastically
  co-monotone* và c thoả (2.3) + (3.3) = submodular); Definition 3.4 (đơn điệu ngẫu nhiên); đoạn quy nạp
  quanh (3.3) chính là chứng minh submodularity truyền ngược; **Remark 3.8** rất quan trọng: với quá trình
  Markov, co-monotonicity thu về điều kiện trên nhân chuyển, nhưng họ đưa phản ví dụ cho thấy phát biểu
  của [Backhoff-Veraguas–Beiglböck–Lin–Zalashko, Prop. 5.3] "does not hold under the stated assumptions"
  và Prop. 3.5 là bản **sửa và mở rộng**. → nếu trước đây trích Prop. 5.3, phải trích bản sửa này.
- J. Backhoff-Veraguas, M. Beiglböck, Y. Lin, A. Zalashko, *Causal transport in discrete time and
  applications*, SIAM J. Optim. 27(4):2528–2562, 2017 — Prop. 5.3 (bản gốc, đa tầng Markov; xem cảnh báo
  trên).
- L. Rüschendorf, *Optimal solutions of multivariate coupling problems*, Appl. Math. (Warsaw) 23:325–338,
  1995 — Corollary 2 (trường hợp hai tầng, c = f(x−y) với f lồi); Corollary 3 (rearrangement đơn điệu tối
  ưu cho chi phí submodular trên đường thẳng).
- A. J. Hoffman, *On simple linear programming problems*, in: Convexity, Proc. Symp. Pure Math. VII,
  AMS 1963, pp. 317–327 — NW-corner tối ưu ⟺ ma trận chi phí Monge.
- D. J. Daley, *Stochastically monotone Markov chains*, Z. Wahrsch. Verw. Geb. 10:305–317, 1968.

**Điều gì phải đúng để áp dụng ở đây:** trạng thái phải là (hoặc nhúng được vào) một trục 1-D có thứ tự;
c phải submodular theo thứ tự đó; và cả hai nhân chuyển phải đơn điệu ngẫu nhiên — kiểm được trong
O(T n²) bằng cumsum trước khi chạy. Nếu ATSW dùng chi phí không submodular (ví dụ c(x,y) = sin(xy) như
c₂ của Eckstein–Pammer) hoặc trạng thái là nhãn không thứ tự / đa chiều, spec này **không** áp dụng —
sang SPEC 3/4.

---

## SPEC 3 — Dãy Monge dùng chung: một lần dò cho cả tầng, greedy O(n+m) mỗi cặp

**Ý tưởng cốt lõi.** Tổng quát hoá SPEC 2 cho trường hợp trạng thái *không* có thứ tự tự nhiên. Định lý
Hoffman: bài vận chuyển giải được bằng greedy cho *mọi* cặp biên ⟺ ma trận chi phí có một **dãy Monge**
(một phép hoán vị các ô sao cho greedy theo thứ tự đó tối ưu). Vì cả 460 bài ở một tầng **dùng chung ma
trận W_t** (mục 0), ta chỉ cần dò dãy Monge **một lần mỗi tầng**, rồi 460 bài giải bằng greedy tuyến tính.
Nếu tồn tại dãy Monge thì đây là *chính xác*, không xấp xỉ. SPEC 2 là ca đặc biệt (thứ tự tự nhiên là dãy
Monge).

**Cấu trúc được khai thác.** Ma trận chi phí dùng chung + tính greedily-solvable của bài vận chuyển.

**Độ phức tạp tuyên bố.** Mỗi tầng: một lần dò/dựng dãy Monge (Alon–Cosares–Hochbaum–Shamir, thời gian đa
thức, "better than that of the best known algorithms for the transportation problem") + n·m lượt greedy
O(n+m). Với n=20, m=23: dò trên ma trận 460 ô + 460 · 43 phép ≈ 2·10⁴ phép/tầng.

**Pseudocode.**
```
for t = T-1 down to 1:
    W = c + V
    seq = monge_sequence(W)                 # Alon et al. 1989; None nếu không tồn tại
    if seq is None: fallback(SPEC 4 hoặc 5) for tầng này; continue
    for (x,y) in pairs:                     # song song hoá được, không share state
        a, b = P[x].copy(), Q[y].copy(); v = 0
        for (i,j) in seq:                   # greedy theo dãy Monge
            f = min(a[i], b[j])
            if f > 0: v += f*W[i,j]; a[i] -= f; b[j] -= f
        Vnew[x,y] = v
    V = Vnew
```

**Nguồn.**
- A. J. Hoffman 1963 (như trên) — điều kiện cần và đủ.
- N. Alon, S. Cosares, D. S. Hochbaum, R. Shamir, *An algorithm for the detection and construction of
  Monge sequences*, Linear Algebra Appl. 114/115:669–680, 1989, doi:10.1016/0024-3795(89)90487-4 — thuật
  toán đa thức đầu tiên để dò/dựng dãy Monge.
- R. Shamir, *A fast algorithm for constructing Monge sequences in transportation problems with forbidden
  arcs*, Discrete Math. 114:435–444, 1993 — bản cho ma trận có ô cấm (dùng khi nhân chuyển thưa).
- W. W. Bein, P. Brucker, J. K. Park, P. K. Pathak, *A Monge property for the d-dimensional transportation
  problem*, Discrete Appl. Math. 58:97–109, 1995 — Thm 3.1 (phát biểu lại Hoffman cho NW-corner, O(m+n)).
- R. E. Burkard, B. Klinz, R. Rudolf, *Perspectives of Monge properties in optimization*, Discrete Appl.
  Math. 70:95–161, 1996 — tổng quan.

**Điều gì phải đúng để áp dụng ở đây:** W_t phải có dãy Monge ở (gần như) mọi tầng. Chưa tra được kết quả
nào nói tính "có-dãy-Monge" **tự truyền ngược** qua quy nạp (SPEC 2 chỉ chứng minh cho submodularity theo
một thứ tự cố định) → phải dò lại mỗi tầng, và phải có nhánh dự phòng khi dò thất bại. **Chưa kiểm chứng
số trong cycle này.**

---

## SPEC 4 — Một hạt nhân Sinkhorn dùng chung cho cả tầng: 460 bài → 2 phép GEMM mỗi vòng

**Ý tưởng cốt lõi.** Khi không có cấu trúc đơn điệu, chuyển sang chính quy hoá entropy nhưng **không** gọi
Sinkhorn 460 lần. Vì W_t dùng chung, hạt nhân K = exp(−W_t/ε) cũng dùng chung; xếp 460 cặp biên thành hai
ma trận A (460×n), B (460×m) rồi chạy Sinkhorn theo lô: mỗi vòng là **hai phép nhân ma trận** với cùng K.
Đây chính là EntropicTCI của O'Connor et al. viết dưới dạng batched BLAS.

**Cấu trúc được khai thác.** Ma trận chi phí (⇒ hạt nhân) dùng chung + tính tách rời của 460 bài.

**Độ phức tạp tuyên bố.** Mỗi vòng Sinkhorn mỗi tầng: 2 · (n·m) · (n·m) flop dưới dạng 2 GEMM
= 2 · 460 · 460 ≈ 4,2 · 10⁵ flop. O'Connor et al. chứng minh Õ(d⁴ε⁻⁴)/vòng cho EntropicOTC, "nearly-linear
in the dimension d⁴ of the transition couplings", so với O(d⁵ log d) của bước cải thiện chính xác.

**Pseudocode.**
```
A = repeat(P, m, axis=0)          # (n*m, n)
B = tile(Q, (n,1))                # (n*m, m)
V = zeros(n,m)
for t = T-1 down to 1:
    W = c + V;  K = exp(-W/eps)                       # MỘT hạt nhân cho cả tầng
    u = ones_like(A)/n
    repeat until converged:
        v = B / (u @ K)                               # GEMM 1
        u = A / (v @ K.T)                             # GEMM 2
    V = einsum('pi,ij,pj,ij->p', u, K, v, W).reshape(n,m)
```

**Kiểm chứng số (local, trên ca KHÓ: nhân đã xáo, không đơn điệu; T=50, n=20, m=23).**
ε = 0,01, 200 vòng: V = 4.8552 so với nghiệm đúng 4.7069 → lệch **+3,15%**, wall **0,43 s** so với
2,29 s của quy nạp lùi chính xác từng cặp (**5×**). Đây là dạng có *thiên lệch*: dùng khi cần khảo sát
nhanh, không dùng làm số cuối. Với ε nhỏ hơn thì thiên lệch giảm nhưng cần nhiều vòng hơn và dễ mất ổn
định số (Bayraktar–Han quan sát đúng hiện tượng này khi T tăng: họ phải nâng ε từ 0,1 lên 1,0 khi T đi từ
1 lên 10).

**Nguồn.**
- O'Connor–McGoff–Nobel, JMLR 23(45), 2022 — Algorithm 2b (EntropicTCI: "performing Sinkhorn iterations
  with the bias h as a cost matrix for each R((x,y),·)"), Theorem 12, và ghi chú "the d² entropic OT
  problems to be solved are decoupled and thus may be computed in parallel"; ApproxOT lấy từ Altschuler–
  Weed–Rigollet, NeurIPS 2017.
- Eckstein–Pammer, Ann. Appl. Probab. 34(1A), 2024 — adapted Sinkhorn, Lemma 6.4, Remark 6.12 (Sinkhorn
  làm solver *bên trong* quy nạp lùi), Table 1–2.
- A. Pichler, M. Weinhardt, *The nested Sinkhorn divergence to learn the nested distance*, Comput. Manag.
  Sci. 19(2):269–293, 2022 (arXiv:2102.05413) — Prop. 3.4–3.5 cho chặn hai phía giữa Sinkhorn divergence
  và Wasserstein (dùng được để biến thiên lệch thành chặn có kiểm soát).

**Điều gì phải đúng để áp dụng ở đây:** phải chấp nhận thiên lệch entropy (hoặc bọc nó bằng chặn hai phía
của Pichler–Weinhardt), và ε phải giữ được ổn định số qua 50 tầng — kinh nghiệm đã công bố cho thấy ε phải
tăng theo T, tức thiên lệch tăng theo T. Không dùng spec này để báo con số cuối.

---

## SPEC 5 — Một đối ngẫu dùng chung ⇒ chặn dưới đồng thời cho MỌI cặp ⇒ bỏ qua phần lớn các cặp

**Ý tưởng cốt lõi.** Vì W_t dùng chung, miền khả thi đối ngẫu {(u,v) : u_i + v_j ≤ W_t(i,j)} là **y hệt
nhau cho cả 460 cặp**. Do đó *một* cặp đối ngẫu khả thi (u,v) cho ngay chặn dưới hợp lệ cho **tất cả**
các cặp:  LB(x,y) = ⟨P(x,·), u⟩ + ⟨Q(y,·), v⟩ ≤ V_t(x,y).
Đối xứng: *bất kỳ* coupling khả thi cố định (ví dụ NW-corner theo một thứ tự tuỳ ý, hoặc coupling tích
P(x,·)⊗Q(y,·)) cho chặn trên UB(x,y). Toán tử Bellman của bài toán này đơn điệu theo ma trận chi phí
(Moulos, Thm 1), nên chặn hai phía **truyền ngược** được: V^lb ≤ V_{t+1} ≤ V^ub ⟹ chặn tương ứng cho V_t.
Đó là động cơ đúng đắn cho branch-and-bound trên cặp trạng thái: chỉ giải chính xác những cặp mà
(UB−LB) × khối lượng chiếm dụng còn đáng kể.

**Cấu trúc được khai thác.** Miền đối ngẫu dùng chung + tính đơn điệu của toán tử Bellman + trọng số theo
độ đo chiếm dụng (nhiều cặp (x,y) gần như không được thăm nên sai số ở đó không vào tổng).

**Độ phức tạp tuyên bố.** Một lần lấy đối ngẫu mỗi tầng (một bài 20×23) + hai phép nhân ma trận-vector để
có LB và UB cho cả 460 cặp: O(n·m·(n+m)) ≈ 2·10⁴ phép/tầng. Sau đó chỉ số cặp còn hở mới cần solver.

**Pseudocode.**
```
for t = T-1 down to 1:
    W = c + V
    u,v = dual_of( emd(P[x_rep], Q[y_rep], W) )         # MỘT bài đại diện
    u = min_j (W[:,j] - v[j]);  v = min_i (W[i,:] - u[i])   # c-transform -> đảm bảo khả thi đối ngẫu
    assert all(u[:,None] + v[None,:] <= W + tol)
    LB = P @ u  (+)  Q @ v                              # (n,m), chặn dưới hợp lệ mọi cặp
    UB = nw_corner_cost(P[x], Q[y], W) for all pairs     # O(n+m) mỗi cặp, chặn trên hợp lệ
    mass = occupation_measure_estimate[t]                # từ một lượt xuôi rẻ
    for (x,y) in pairs:
        if (UB-LB)[x,y] * mass[x,y] <= budget/(n*m): V[x,y] = UB[x,y]   # bỏ qua, không gọi solver
        else:                                           V[x,y] = exact_ot(P[x], Q[y], W)
    # sai số tích luỹ bị chặn bởi sum của các (UB-LB)*mass đã bỏ qua
```

**Kiểm chứng số (local, ca KHÓ không đơn điệu, một tầng đại diện, 460 cặp).**
- một đối ngẫu dùng chung: LB hợp lệ ở **100%** các cặp; trung bình LB/nghiệm-đúng = **0,963**; xấu nhất
  0,860.
- NW-corner làm UB: hợp lệ ở 100% các cặp; trung bình UB/nghiệm-đúng = **1,007**.
- số cặp có (UB−LB)/nghiệm-đúng < 5% (tức bỏ qua được, không gọi LP): **67,2%**.

Nghĩa là ngay trên ca xấu (không đơn điệu), hai phép nhân ma trận-vector đã kẹp được 2/3 số cặp trong
5%. Đây là đòn bẩy thật, nhưng nó *đổi độ chính xác lấy tốc độ* — phải mang theo một chứng thư sai số
(tổng các (UB−LB)·mass đã bỏ qua) chứ không được báo là nghiệm đúng.

**Nguồn.**
- Đối ngẫu LP của bài vận chuyển + c-transform: chuẩn; xem G. Peyré, M. Cuturi, *Computational Optimal
  Transport*, Found. Trends ML 11(5–6), 2019, §3.1–3.4 (§3.4.2 cho NW-corner).
- Tính đơn điệu của toán tử Bellman cho bicausal OT: Moulos, arXiv:2010.06831, Thm 1–2.
- Chặn có bảo đảm cho bài đa tầng theo hướng chặn trên/dưới: F. Maggioni, G. Ch. Pflug, *Guaranteed bounds
  for general non-discrete multistage risk-averse stochastic optimization programs*, SIAM J. Optim.
  29(1):454–483, 2019.
- Tính Lipschitz của giá trị theo AW (để chặn theo continuation value): D. Bartl, J. Wiesel, *Sensitivity
  of multiperiod optimization problems with respect to the adapted Wasserstein distance*, SIAM J. Financial
  Math. 14(2):704–720, 2023.

**Điều gì phải đúng để áp dụng ở đây:** phải chấp nhận nghiệm có chứng thư sai số thay vì nghiệm đúng
tuyệt đối, và độ đo chiếm dụng phải thực sự tập trung (nếu cả 460 cặp đều được thăm với khối lượng tương
đương thì việc bỏ qua không giúp gì). **Chưa tra được** bài báo nào làm branch-and-bound trên cặp trạng
thái cho nested distance — spec này là suy dẫn từ đối ngẫu LP + đơn điệu Bellman, đã kiểm chứng số một
tầng, chưa có tiền lệ trong literature.

---

## Số liệu thời gian ĐÃ CÔNG BỐ cho nested / bicausal distance

Câu hỏi đặt ra là "ai từng báo wall-clock ở T ≥ 20". Trả lời ngắn: **gần như không ai**, và bài duy nhất
có T ≥ 20 dùng xấp xỉ neural, trên cây nhị phân (2 nhánh/nút), không phải 20 trạng thái.

| nguồn | cấu hình | thuật toán | wall-clock |
|---|---|---|---|
| Bayraktar–Han arXiv:2306.12658 Table 1 | cây nhị phân không tái hợp, OT 2×2 mỗi nút | LP + quy nạp lùi (Gurobi) | T=5: 2,9 s · T=8: 32,2 s · T=9: 83,3 s · T=10: 248,2 s · T=11: 794,0 s · T=12: ≈2600 s |
| cùng nguồn, Table 2 | như trên | adapted Sinkhorn (Eckstein–Pammer impl.) | T=5: 8,1 s (ε=0,1) · T=8: 205,0 s (ε=0,6) · T=9: 518,0 s (ε=0,8) · T=10: 1443,6 s (ε=1,0) |
| cùng nguồn, Table 3 | như trên | **FVI (mạng neural)** | T=10: 66,4 s · **T=20: 131,4 s** · **T=40: 257,7 s** (sai số: T=20 ước lượng 72,02 ± 8,17 so với đúng 72,5; T=40: 235,3 ± 38,3 so với 245,0) |
| cùng nguồn, văn bản §1 | — | LP & adapted Sinkhorn | "for time horizons T ≥ 20, the LP and adapted Sinkhorn methods failed to converge within a reasonable time frame" |
| cùng nguồn, văn bản | T=10, LP một-lần (Eckstein–Pammer Lemma 3.11) | Gurobi | 701 098 hàng / 1 048 576 cột / 23 068 672 nonzero sau presolve, **>1000 s** |
| Eckstein–Pammer Ann. Appl. Probab. 34(1A) Table 1–2 | **T=3 (N=3)**, cây Markov, n_b nhánh | LP một-lần | n_b=10: 1,61 s · n_b=25: 205,1 s · n_b=50: không xong |
| cùng nguồn | T=3 | DPP (quy nạp lùi, LP trong) | n_b=10: 0,60 s · 25: 21,6 s · 50: 315,7 s · 75: 1285,5 s · 100: 3784,4 s |
| cùng nguồn | T=3 | adapted Sinkhorn ε=0,01 | n_b=10: 4,59 s (0,10%) · 25: 22,1 s · 50: 105,9 s · 75: 230,4 s · 100: 500,1 s (0,04%) |
| Pichler–Weinhardt Comput. Manag. Sci. 19(2) Table 1 | cây [1 2 3 2 3 4] vs [1 2 2 1 3 2] (144 vs 24 lá), i5-3210M | Wasserstein LP đệ quy | T=3: 0,50 s · T=4: 1,54 s · **T=5: 10,29 s** |
| cùng nguồn | như trên | nested Sinkhorn λ=20 | T=3: 0,062 s · T=4: 0,368 s · **T=5: 2,873 s** (tăng tốc 3,6–10×) |
| Bontorno–Hou arXiv:2509.06702 | T=5 (OU) và T=3 (fake BM), AMD EPYC 7763 64 core | quy nạp lùi song song hoá (gói `PNOT`) | chỉ báo dưới dạng hình, **không có số wall-clock trong văn bản** |
| O'Connor–McGoff–Nobel JMLR 23(45) §7.1 | vô hạn chân trời (average cost), d=100 | EntropicOTC vs ExactOTC | tiết kiệm ~80% thời gian ở d=100, ξ=100 (không có số giây tuyệt đối trong văn bản) |

**Đọc bảng này thế nào cho đúng.** Mọi số T lớn ở trên đều đến từ *cây không tái hợp* (số nút ~2^t), nên
chi phí bùng nổ theo T là do không gian đường đi, không do bài toán trong. Bài toán của ATSW là **Markov
tái hợp**: đúng 460 cặp mỗi tầng bất kể T, tức tuyến tính theo T. Nói cách khác: 22 540 bài LP nhỏ ở T=50
đã tốt hơn về scaling so với mọi con số đã công bố ở trên; trần mà lane này cần phá không phải là trần của
literature mà là trần "một solver / một cặp" của mục 0.

---

## not_found (tra không ra — ghi nhận là kết quả âm tính, không bịa nguồn)

1. **Một LP/luồng-chi-phí-nhỏ-nhất một-lần được báo là giải nổi ở quy mô T=50 × 20 trạng thái.** Không tìm
   thấy. Công thức LP một-lần thì có (SPEC 1), nhưng O'Connor et al. Remark 8 nói thẳng nó không khả thi và
   không có ai báo kết quả ở quy mô này.
2. **Quy về luồng chi phí nhỏ nhất trên đồ thị *tích* làm toàn bài trở thành một bài luồng thuần.** Không
   tìm thấy. Lý do cấu trúc: hai họ ràng buộc biên trong SPEC 1 nối khối lượng của (x,y) với biên P(x,·) và
   Q(y,·), tạo ràng buộc *phụ* trên mạng — đây là "network flow with side constraints", không phải min-cost
   flow thuần, nên không thừa hưởng thuật toán luồng. (Bài toán *trong*, đứng riêng, thì đúng là một bài
   Hitchcock = min-cost flow với n+m nút và n·m cung — nhưng đó là lane solver, không phải tái công thức.)
3. **Quy về bài toán gán (assignment) trong trường hợp tổng quát.** Không tìm thấy. Chỉ đúng khi hai biên
   đều đều (uniform) và n = m, khi đó đa diện vận chuyển là đa diện Birkhoff; nhân chuyển tổng quát không
   cho biên đều.
4. **Kết quả nói tính "có-dãy-Monge" của W_t tự truyền ngược qua quy nạp lùi** (analogue của định lý truyền
   submodularity trong SPEC 2 nhưng cho dãy Monge tổng quát). Không tìm thấy. Đây là một lỗ hổng lý thuyết
   nhỏ và cũng là một câu hỏi mở đáng làm: nếu đúng, SPEC 3 mạnh lên rất nhiều (dò một lần cho toàn bộ 49
   tầng thay vì mỗi tầng).
5. **Nghiệm dạng đóng cho bước trong khi nhân chuyển *hạng thấp*.** Không tìm thấy kết quả nào cho
   nested/bicausal. Literature low-rank OT (Scetbon–Cuturi–Peyré 2021 và tiếp nối) nói về hạng thấp của
   *coupling* hoặc của *ma trận chi phí*, không phải của nhân chuyển, và không có phát biểu nào về bước
   trong của quy nạp bicausal. Không suy diễn thêm.
6. **Branch-and-bound trên cặp trạng thái cho nested distance.** Không tìm thấy tiền lệ. SPEC 5 là suy dẫn
   riêng (đối ngẫu LP + đơn điệu Bellman), có kiểm chứng số một tầng, chưa có nguồn.
7. **Wall-clock đã công bố cho nested distance ở T ≥ 20 với ~20 trạng thái mỗi tầng (Markov tái hợp).**
   Không tìm thấy. Số T ≥ 20 duy nhất (Bayraktar–Han FVI) là trên cây nhị phân với OT 2×2 và là xấp xỉ
   neural có phương sai đáng kể (T=40: 235,3 ± 38,3 so với 245,0).

---

## Khuyến nghị thứ tự thực thi cho lane này

1. **Chạy tiền kiểm tra của SPEC 2 trên nhân chuyển thật của ATSW** (O(T n²), vài dòng cumsum). Nếu chi phí
   submodular và hai nhân đơn điệu ngẫu nhiên → xong: 445× và chính xác đến sai số máy, LP biến mất hoàn
   toàn. Đây là kiểm tra rẻ nhất với đòn bẩy lớn nhất, làm trước mọi thứ khác.
2. Nếu tiền kiểm tra thất bại: xem *thất bại ở đâu*. Nếu chỉ vì thứ tự trạng thái sai → thử SPEC 3 (dò dãy
   Monge một lần/tầng). Nếu vì chi phí không submodular về bản chất → SPEC 5 (kẹp hai phía + bỏ qua cặp,
   giữ chứng thư sai số) rồi SPEC 4 cho khảo sát nhanh.
3. **Bỏ SPEC 1.** Đã có phán quyết trong literature và mốc Gurobi để trích dẫn khi cần biện minh.
4. Dù đi nhánh nào: **cài lại vòng trong theo mục 0** (một ma trận chi phí dùng chung mỗi tầng, batched)
   trước khi đo lại hằng số. Con số 0,66–0,70x hiện tại đang đo một kiến trúc mà cả ba spec khả thi đều
   không dùng nữa.
