# Nhờ kiểm: định lý nhất quán của ước lượng ATSW (đã hình thức hóa trong Lean 4)

**Bài:** *Adapted Tree-Sliced Wasserstein: a path-only estimator for adapted optimal transport, with a machine-checked consistency proof* (working draft).
**Đối tượng nhờ kiểm:** Theorem (Consistency), Section "Theory" — trong Lean là `Vdp_consistent_ae`.
**File kèm:** `paper.tex` (bản thảo), `Atsw.lean` (613 dòng, Lean 4.33.0 + mathlib v4.33.0), `LEAN_README.md`, `atsw_fixedgrid.py` (thuật toán mà định lý phủ), `atsw_kmarkov.py` (bản có cửa sổ $k$).

---

## 0. Em cần gì ở thầy/cô

Chứng minh **đã được máy kiểm**, nên em *không* nhờ kiểm tính đúng của các bước suy luận — Lean kernel đã làm việc đó (0 `sorry`; `#print axioms` chỉ ra ba tiên đề chuẩn `propext`, `Classical.choice`, `Quot.sound`, không có `sorryAx`).

Chỗ máy **không** kiểm được, và là chỗ em cần một người đọc có kinh nghiệm:

1. **Phát biểu hình thức có trung thực với điều bài báo tuyên bố không?** (mục 3, 4)
2. **Bộ giả thiết có phòng thủ được trước reviewer không?** (mục 5)
3. **Khoảng cách giữa định lý và thuật toán thực chạy có được khai báo đủ trung thực không?** (mục 6)

Đường đọc ngắn (~20 phút): mục 2 → mục 4 → mục 6 → checklist mục 8.
Đường đọc đầy đủ (~90 phút): thêm mục 3 và 5.

---

## 1. Bối cảnh trong một trang

Khoảng cách adapted (bicausal) giữa hai quá trình trên $\mathbb{R}^T$:

$$\mathcal{AW}_p^p(\mu,\nu) = \inf_{\pi \in \mathrm{Cpl}_{bc}(\mu,\nu)} \int \sum_{t=1}^T |x_t - y_t|^p \, d\pi,$$

phân rã được thành quy nạp lùi, với $V_T \equiv 0$:

$$V_t(x_{1:t}, y_{1:t}) = \inf_{\pi_t \in \mathrm{Cpl}(\mu_{t+1|x_{1:t}}, \nu_{t+1|y_{1:t}})} \int \big[c_{t+1}(x_{t+1},y_{t+1}) + V_{t+1}\big] d\pi_t, \qquad \mathcal{AW}_p^p = V_0.$$

ATSW làm hai việc để rẻ hơn: (a) thay $\inf$ bên trong bằng **ghép comonotone** dạng đóng, và (b) chỉ điều kiện trên $k$ chỉ số ô gần nhất thay vì toàn bộ quá khứ. Trọng số comonotone:

$$\ell_{ij}(p,q) = \big(\min(F_i, G_j) - \max(F_{i-1}, G_{j-1})\big)^+.$$

Nhân chuyển được ước lượng bằng đếm từ đường đi quan sát được; ô nguồn chưa bao giờ được thăm thì trả **hàng đều**.

**Định lý này nói về (a) và về việc đếm — không nói về (b), cũng không nói về khoảng cách từ surrogate tới $\mathcal{AW}$.** Xem mục 4 và 6.

---

## 2. Phát biểu, dạng người đọc

Ký hiệu: $n, m$ = số ô của hai quá trình (cố định); $B$ = chặn trên $|c|$; $\hat K_M$ = nhân chuyển ước lượng bằng đếm từ $M$ cặp chuyển tiếp, có hàng đều làm fallback; $K^0$ = nhân chuyển thật; $V^{dp}$ = giá trị quy nạp lùi **với ghép comonotone ở bước trong**.

> **Assumption 1 (Reachability).** Mọi ô nguồn có xác suất dương dưới luật của toạ độ thứ nhất của một cặp chuyển tiếp.
>
> **Assumption 2 (Sampling).** Các cặp chuyển tiếp gộp lại là độc lập đôi một, cùng phân phối, đo được.
>
> **Theorem (Consistency).** Dưới Assumption 1, Assumption 2 và chi phí bị chặn, giá trị quy nạp lùi tính từ $\hat K_M$ hội tụ **hầu chắc chắn**, khi $M \to \infty$, về giá trị tính từ $K^0$.

Sườn chứng minh trong bài (6 bước, mỗi bước ứng với một kết quả Lean — mục 4):

| # | Bước | Kết quả Lean |
|---|---|---|
| i | c.d.f. là $1$-Lipschitz theo vector khối lượng; mỗi trọng số comonotone Lipschitz hằng $2$ | `cdf_lipschitz`, `ell_lipschitz` |
| ii | $\lvert QC(p,q;M) - QC(p',q';M)\rvert \le 2nmB(\lVert p-p'\rVert_1 + \lVert q-q'\rVert_1)$ | `QC_lipschitz` |
| iii | một bước recursion Lipschitz đồng thời theo nhân chuyển và theo continuation value | `QC_step_lipschitz` |
| iv | hợp thành $s$ bước → chặn Lipschitz với hằng số đệ quy tường minh | `Vdp_lipschitz` |
| v | chặn Lipschitz với input tiến về 0 → giá trị hội tụ | `Vdp_tendsto` |
| vi | luật số lớn cho tần suất thực nghiệm; dưới Assumption 1 tỉ số tần suất hội tụ về nhân chuyển thật | `empirical_freq_ae`, `Khat_ae_tendsto` |

---

## 3. Các định nghĩa hình thức (nguyên văn `Atsw.lean`)

Đây là phần cần đối chiếu: **nếu định nghĩa lệch, định lý vẫn "xanh" nhưng nói chuyện khác.**

```lean
/-- Hàm phân phối tích lũy: tổng khối lượng ở các chỉ số < i. -/
def cdf (p : Fin n → ℝ) (i : ℕ) : ℝ :=
  ∑ j ∈ univ.filter (fun j : Fin n => (j : ℕ) < i), p j

/-- Chuẩn ℓ¹ của hiệu hai vector khối lượng. -/
def l1 (p p' : Fin n → ℝ) : ℝ := ∑ j, |p j - p' j|

/-- Trọng số ghép comonotone (dạng Fréchet–Hoeffding rời rạc). -/
noncomputable def ell (p : Fin n → ℝ) (q : Fin m → ℝ) (i : Fin n) (j : Fin m) : ℝ :=
  max 0 (min (cdf p ((i : ℕ) + 1)) (cdf q ((j : ℕ) + 1))
         - max (cdf p (i : ℕ)) (cdf q (j : ℕ)))

/-- Chi phí của ghép comonotone dưới ma trận chi phí M. -/
noncomputable def QC (p : Fin n → ℝ) (q : Fin m → ℝ) (M : Fin n → Fin m → ℝ) : ℝ :=
  ∑ i, ∑ j, M i j * ell p q i j

/-- Vector khối lượng là phân phối xác suất. -/
def IsProb (p : Fin n → ℝ) : Prop := (∀ i, 0 ≤ p i) ∧ ∑ i, p i = 1

/-- Giá trị quy nạp lùi: `s` bước còn lại, xuất phát từ mốc thời gian `t`. -/
noncomputable def Vdp (KA : ℕ → Fin n → Fin n → ℝ) (KB : ℕ → Fin m → Fin m → ℝ)
    (Mt : ℕ → Fin n → Fin m → ℝ) : ℕ → ℕ → Fin n → Fin m → ℝ
  | 0, _, _, _ => 0
  | (s + 1), t, i, j =>
      QC (KA t i) (KB t j) (fun i' j' => Mt t i' j' + Vdp KA KB Mt s (t + 1) i' j')

/-- Tần suất thực nghiệm của giá trị `a` trong `N` quan sát đầu. -/
noncomputable def freq {Ω κ : Type*} [DecidableEq κ]
    (W : ℕ → Ω → κ) (a : κ) (N : ℕ) (ω : Ω) : ℝ :=
  (N : ℝ)⁻¹ * ∑ k ∈ Finset.range N, ind a (W k ω)

/-- Ước lượng nhân chuyển từ mẫu cặp chuyển tiếp; ô chưa thăm trả hàng đều. -/
noncomputable def Khat {Ω : Type*} {N : ℕ} [NeZero N]
    (Z : ℕ → Ω → Fin N × Fin N) (M : ℕ) (ω : Ω) (i j : Fin N) : ℝ :=
  if freq (fun k ω => (Z k ω).1) i M ω = 0 then ((N : ℝ))⁻¹
  else freq Z (i, j) M ω / freq (fun k ω => (Z k ω).1) i M ω

/-- Nhân chuyển thật: xác suất có điều kiện của ô đích khi biết ô nguồn. -/
noncomputable def K0 {Ω : Type*} [MeasurableSpace Ω] (μ : Measure Ω) {N : ℕ}
    (Z0 : Ω → Fin N × Fin N) (i j : Fin N) : ℝ :=
  μ.real (Z0 ⁻¹' {(i, j)}) / μ.real ((fun ω => (Z0 ω).1) ⁻¹' {i})
```

Hằng số trong chặn Lipschitz:

```lean
noncomputable def Vb (n m : ℕ) (B : ℝ) : ℕ → ℝ
  | 0 => 0
  | (s + 1) => n * m * (B + Vb n m B s)

noncomputable def Cst (n m : ℕ) (B : ℝ) : ℕ → ℝ
  | 0 => 0
  | (s + 1) => 2 * n * m * (B + Vb n m B s) + n * m * Cst n m B s
```

---

## 4. Phát biểu hình thức của định lý đích (nguyên văn)

```lean
theorem Vdp_consistent_ae {Ω : Type*} [MeasurableSpace Ω] {μ : Measure Ω} [IsProbabilityMeasure μ]
    {n m : ℕ} [NeZero n] [NeZero m]
    (ZA : ℕ → Ω → Fin n × Fin n) (ZB : ℕ → Ω → Fin m × Fin m)
    (hmA : ∀ k, Measurable (ZA k)) (hmB : ∀ k, Measurable (ZB k))
    (hiA : Pairwise (Function.onFun (fun f g => IndepFun f g μ) ZA))
    (hiB : Pairwise (Function.onFun (fun f g => IndepFun f g μ) ZB))
    (hdA : ∀ k, IdentDistrib (ZA k) (ZA 0) μ μ) (hdB : ∀ k, IdentDistrib (ZB k) (ZB 0) μ μ)
    (hpA : ∀ i : Fin n, μ.real ((fun ω => (ZA 0 ω).1) ⁻¹' {i}) ≠ 0)
    (hpB : ∀ j : Fin m, μ.real ((fun ω => (ZB 0 ω).1) ⁻¹' {j}) ≠ 0)
    (Mt : ℕ → Fin n → Fin m → ℝ) (Bd : ℝ) (hB0 : 0 ≤ Bd) (hM : ∀ t i j, |Mt t i j| ≤ Bd)
    (s t : ℕ) (i : Fin n) (j : Fin m) :
    ∀ᵐ ω ∂μ, Tendsto
      (fun M => Vdp (fun _ => Khat ZA M ω) (fun _ => Khat ZB M ω) Mt s t i j) atTop
      (𝓝 (Vdp (fun _ => K0 μ (ZA 0)) (fun _ => K0 μ (ZB 0)) Mt s t i j))
```

### Đối chiếu giả thiết: bài báo ↔ Lean

| Bài báo | Lean | Loại trừ điều gì |
|---|---|---|
| Assumption 2, đo được | `hmA`, `hmB` | — |
| Assumption 2, độc lập đôi một | `hiA`, `hiB` | phụ thuộc giữa các cặp chuyển tiếp |
| Assumption 2, cùng phân phối | `hdA`, `hdB` | không dừng theo thời gian |
| Assumption 1, khả đạt | `hpA`, `hpB` | ô nguồn không bao giờ được thăm |
| chi phí bị chặn | `hB0`, `hM` | chi phí không bị chặn |
| $\mu$ là xác suất | `[IsProbabilityMeasure μ]` | — |
| lưới không rỗng | `[NeZero n]`, `[NeZero m]` | — |

### Ba điểm cần đọc kỹ trong phát biểu

**(a) Giới hạn là $V^{dp}$ tại $K^0$, không phải $\mathcal{AW}_p^p$.** Cả hai vế đều dùng `Vdp`, tức bước trong đã là ghép comonotone. Định lý nói: *ước lượng hội tụ về giá trị dân số của chính surrogate đó*. Sai số giữa surrogate và adapted distance thật là chuyện khác, được xử lý bằng thực nghiệm ở Section "Regime" (bias giảm như $n^{-0.19}$), **không** bằng định lý này. Em nghĩ bài báo cần nói câu này ra một cách tường minh ngay sau định lý; nhờ thầy/cô xác nhận cách diễn đạt.

**(b) Thuần nhất theo thời gian.** Trong phát biểu, nhân chuyển được đưa vào dưới dạng `fun _ => Khat ...` — cùng một nhân chuyển ở mọi mốc $t$. Đúng cho ca $k$-Markov dừng. Bản không thuần nhất phải dùng `Vdp_tendsto` (tổng quát hơn, đã chứng minh, ở dòng (v)) cộng một chặn đều trên hữu hạn mốc; hiện chưa ráp.

**(c) Hội tụ theo từng điểm $(s,t,i,j)$, lưới cố định.** $s, t, i, j$ là tham số của định lý, và $n, m$ cố định. Không có tính đều theo $(i,j)$, và **không** có giới hạn khi làm mịn lưới ($n, m \to \infty$).

---

## 5. Hai chỗ hình thức hóa làm lộ ra giả thiết ngầm

Đây là phần em nghĩ đáng giá nhất về mặt học thuật của việc dùng Lean, và cũng là phần cần thầy/cô đánh giá xem có đáng đưa lên main text hay không.

1. **Khả đạt là điều kiện thật, không phải điều kiện kỹ thuật.** `Khat_ae_tendsto` không đứng được nếu bỏ `μ.real (ô nguồn) ≠ 0`: ô không bao giờ được thăm thì $K^0$ là $0/0$, nhân chuyển thật không xác định. Chứng minh viết tay rất dễ bỏ qua vì "hiển nhiên mẫu số dương".

2. **Hàng mặc định không phải chi tiết trang trí.** Với $M$ hữu hạn, mẫu số có thể bằng 0. `Khat` trả hàng đều trong ca đó, nhờ vậy **mọi hàng là phân phối xác suất ở mọi $M$** (`Khat_isProb` không cần giả thiết nào cả) — mà giả thiết `IsProb` chính là thứ định lý hợp thành `Vdp_lipschitz` đòi. Nếu định nghĩa estimator trả $0/0 = 0$, chuỗi lập luận vỡ ở $M$ nhỏ. Hội tụ vẫn đúng vì mẫu số khác 0 *cuối cùng* (`Tendsto.eventually_ne`).

3. **"Xác suất biên = tổng xác suất khớp" phải chứng minh.** Cần cho `K0_isProb`; trong Lean phải đi qua tích phân chỉ báo (`sum_measure_real`, `integral_ind_eq`), không hiển nhiên về mặt hình thức.

Một điểm mạnh nên nhắc trong bài: luật số lớn dùng ở bước (vi) là `strong_law_ae` của mathlib, chỉ cần **độc lập đôi một** (phiên bản Etemadi), không cần độc lập hoàn toàn. Giả thiết Sampling nhờ đó yếu hơn mức thường thấy.

---

## 6. Khoảng cách giữa định lý và thuật toán thực chạy

Em liệt kê thẳng, vì đây là chỗ reviewer sẽ đánh và em muốn khai báo trước:

| # | Khoảng cách | Trạng thái |
|---|---|---|
| 1 | **Lưới cố định vs lưới theo phân vị mẫu.** Bản dùng phân vị mẫu chính xác hơn ở một số chế độ, nhưng biên ô trở thành ngẫu nhiên và định lý không còn phủ. Bài báo chọn chạy bản mà định lý phủ (`atsw_fixedgrid.py`). | đã khai báo trong bài |
| 2 | **Cửa sổ $k$.** Định lý nói về nhân chuyển trên không gian trạng thái đã cho; việc chọn $k$ (đánh đổi hai chiều, có cực trị trong) không nằm trong định lý. | chưa nói rõ trong Section Theory |
| 3 | **Lấy trung bình trên các dịch lưới.** Estimator thực chạy lấy trung bình hữu hạn nhiều giá trị dạng $V^{dp}$. Hội tụ h.c.c. bảo toàn qua tổng hữu hạn, nhưng bài báo hiện không viết câu đó. | cần thêm 1–2 dòng? |
| 4 | **Cặp chuyển tiếp i.i.d.** Thực tế các cặp được gộp từ **cùng** một đường đi nên phụ thuộc nhau. Giả thiết hiện tại là lý tưởng hóa chuẩn của việc gộp. | ranh giới đã biết, chưa xử lý |
| 5 | **Hằng số $\mathrm{Cst} \sim (nm)^s$.** Định lý chứng minh *tính liên tục*, không phải *tốc độ hội tụ*. Chặn này quá thô để dùng làm rate. | ranh giới đã biết |
| 6 | **Không gian trạng thái cùng kích thước ở mọi mốc.** Đúng cho lưới cố định sau khi đệm ô khối lượng 0. | kỹ thuật |

---

## 7. Nếu thầy/cô muốn tự kiểm phần máy

Không cần đọc chứng minh — chỉ cần kiểm ba thứ:

```bash
# 1. Không có lỗ hổng
grep -n "sorry\|admit\|axiom " Atsw.lean          # kỳ vọng: không có kết quả

# 2. Dựng lại từ đầu
export ELAN_HOME=$PWD/.elan; export PATH="$ELAN_HOME/bin:$PATH"
cd atswproof && lake exe cache get && lake build   # kỳ vọng: build sạch

# 3. Tiên đề mà mỗi định lý phụ thuộc
lean Check.lean
# kỳ vọng, cho mọi phát biểu kể cả Vdp_consistent_ae:
#   'Vdp_consistent_ae' depends on axioms: [propext, Classical.choice, Quot.sound]
```

Ba tiên đề đó là tiên đề chuẩn của Lean (extensionality của mệnh đề, tiên đề chọn, tính đúng của thương). Không có `sorryAx` nghĩa là không có bước nào bị bỏ trống.

Quy mô: 12 định nghĩa, 35 bổ đề/định lý, 613 dòng. Cần mạng tới `releases.lean-lang.org`, `github.com`, `lakecache.blob.core.windows.net`. Lưu ý `import Mathlib` (toàn bộ) làm hết 8 GiB RAM; file này nhập chọn lọc 6 module.

---

## 8. Checklist câu hỏi cụ thể

Mong thầy/cô đánh dấu và ghi chú trực tiếp:

- [ ] **Q1. Trung thực của phát biểu (quan trọng nhất).** Đọc mục 3 và 4: `Vdp`, `Khat`, `K0` có đúng là ba đối tượng mà bài báo muốn nói không? Đặc biệt: định nghĩa `Vdp` — thay $\inf$ bằng ghép comonotone ngay trong recursion — có phải là "giá trị của ATSW estimator" theo nghĩa bài báo dùng?
- [ ] **Q2. Cách diễn đạt điểm 4(a).** Định lý là nhất quán *về giá trị dân số của surrogate*, không phải về $\mathcal{AW}_p^p$. Nên viết câu này thế nào ngay sau định lý để không bị đọc quá lên? Tiêu đề bài có cụm "machine-checked consistency proof" — cụm đó có bị hiểu thành "đã chứng minh hội tụ về adapted distance" không?
- [ ] **Q3. Bộ giả thiết.** Có giả thiết nào dư (bỏ được) hoặc thiếu (định lý phát biểu mạnh hơn mức chứng minh cho phép)? Riêng "độc lập đôi một" — có nên nhấn mạnh là yếu hơn độc lập hoàn toàn không?
- [ ] **Q4. Khoảng cách #3 trong mục 6.** Việc lấy trung bình trên các dịch lưới có cần một bổ đề riêng (dù tầm thường) để phát biểu khớp thuật toán thực chạy?
- [ ] **Q5. Kỳ vọng về tốc độ.** Với hằng số $(nm)^s$ như hiện tại, reviewer ở venue mục tiêu có đòi một rate không? Nếu có thì nên (a) chứng minh rate cho ca đặc biệt, (b) đưa rate thực nghiệm, hay (c) khai báo giới hạn và dừng?
- [ ] **Q6. Vị trí trong bài.** Formalization nên nằm ở main text (như hiện tại: một tiểu mục + bảng 35 kết quả) hay đẩy hết xuống appendix và giữ main text một đoạn?

Nếu thầy/cô chỉ có thời gian cho một câu, xin chọn **Q1**: đó là chỗ duy nhất mà máy kiểm không giúp được gì, và cũng là chỗ nếu sai thì toàn bộ 613 dòng trở thành vô nghĩa.
