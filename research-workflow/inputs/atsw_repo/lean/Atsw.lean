/-
  ATSW — hình thức hóa lõi hữu hạn của mệnh đề nhất quán.

  Ý: chứng minh nhất quán của ước lượng k-Markov gồm hai phần.
  (i) Nhân chuyển thực nghiệm hội tụ về nhân chuyển thật (SLLN — sách giáo khoa).
  (ii) Giá trị của quy nạp lùi là hàm LIÊN TỤC của các nhân chuyển đó.
  Phần (ii) là chỗ có thể sai một cách tinh vi, và là phần được hình thức hóa ở đây.

  Điểm mấu chốt về phạm vi: nhất quán chỉ cần TÍNH LIÊN TỤC, không cần hằng số Lipschitz
  tối ưu. Nên một chặn thô nhưng đúng là đủ — và chứng minh được trọn vẹn.
-/
import Mathlib.Data.Real.Basic
import Mathlib.Algebra.Order.Group.MinMax
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Algebra.BigOperators.Ring.Finset
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Order.Filter.Basic
import Mathlib.Analysis.SpecificLimits.Basic
import Mathlib.Probability.StrongLaw

namespace ATSW

open Finset

variable {n m : ℕ}

/-- Hàm phân phối tích lũy: tổng khối lượng ở các chỉ số < i. -/
def cdf (p : Fin n → ℝ) (i : ℕ) : ℝ :=
  ∑ j ∈ univ.filter (fun j : Fin n => (j : ℕ) < i), p j

/-- Chuẩn ℓ¹ của hiệu hai vector khối lượng. -/
def l1 (p p' : Fin n → ℝ) : ℝ := ∑ j, |p j - p' j|

lemma l1_nonneg (p p' : Fin n → ℝ) : 0 ≤ l1 p p' :=
  Finset.sum_nonneg fun _ _ => abs_nonneg _

/-- CDF là 1-Lipschitz theo chuẩn ℓ¹ của vector khối lượng. -/
lemma cdf_lipschitz (p p' : Fin n → ℝ) (i : ℕ) :
    |cdf p i - cdf p' i| ≤ l1 p p' := by
  unfold cdf l1
  rw [← Finset.sum_sub_distrib]
  calc |∑ j ∈ univ.filter (fun j : Fin n => (j : ℕ) < i), (p j - p' j)|
      ≤ ∑ j ∈ univ.filter (fun j : Fin n => (j : ℕ) < i), |p j - p' j| :=
        Finset.abs_sum_le_sum_abs _ _
    _ ≤ ∑ j, |p j - p' j| :=
        Finset.sum_le_sum_of_subset_of_nonneg (Finset.filter_subset _ _)
          (fun _ _ _ => abs_nonneg _)

/-- Trọng số ghép comonotone (dạng Fréchet–Hoeffding rời rạc). -/
noncomputable def ell (p : Fin n → ℝ) (q : Fin m → ℝ) (i : Fin n) (j : Fin m) : ℝ :=
  max 0 (min (cdf p ((i : ℕ) + 1)) (cdf q ((j : ℕ) + 1))
         - max (cdf p (i : ℕ)) (cdf q (j : ℕ)))

lemma ell_nonneg (p : Fin n → ℝ) (q : Fin m → ℝ) (i : Fin n) (j : Fin m) :
    0 ≤ ell p q i j := le_max_left _ _

/-- Trọng số ghép liên tục theo (p, q): chặn thô nhưng đúng, đủ cho tính liên tục. -/
lemma ell_lipschitz (p p' : Fin n → ℝ) (q q' : Fin m → ℝ) (i : Fin n) (j : Fin m) :
    |ell p q i j - ell p' q' i j| ≤ 2 * (l1 p p' + l1 q q') := by
  have hmin : |min (cdf p ((i:ℕ)+1)) (cdf q ((j:ℕ)+1))
              - min (cdf p' ((i:ℕ)+1)) (cdf q' ((j:ℕ)+1))|
      ≤ l1 p p' + l1 q q' := by
    refine (abs_min_sub_min_le_max _ _ _ _).trans ?_
    refine max_le ?_ ?_
    · exact (cdf_lipschitz p p' _).trans (by linarith [l1_nonneg q q'])
    · exact (cdf_lipschitz q q' _).trans (by linarith [l1_nonneg p p'])
  have hmax : |max (cdf p (i:ℕ)) (cdf q (j:ℕ)) - max (cdf p' (i:ℕ)) (cdf q' (j:ℕ))|
      ≤ l1 p p' + l1 q q' := by
    refine (abs_max_sub_max_le_max _ _ _ _).trans ?_
    refine max_le ?_ ?_
    · exact (cdf_lipschitz p p' _).trans (by linarith [l1_nonneg q q'])
    · exact (cdf_lipschitz q q' _).trans (by linarith [l1_nonneg p p'])
  have hinner : |(min (cdf p ((i:ℕ)+1)) (cdf q ((j:ℕ)+1)) - max (cdf p (i:ℕ)) (cdf q (j:ℕ)))
        - (min (cdf p' ((i:ℕ)+1)) (cdf q' ((j:ℕ)+1)) - max (cdf p' (i:ℕ)) (cdf q' (j:ℕ)))|
      ≤ 2 * (l1 p p' + l1 q q') := by
    have e : (min (cdf p ((i:ℕ)+1)) (cdf q ((j:ℕ)+1)) - max (cdf p (i:ℕ)) (cdf q (j:ℕ)))
        - (min (cdf p' ((i:ℕ)+1)) (cdf q' ((j:ℕ)+1)) - max (cdf p' (i:ℕ)) (cdf q' (j:ℕ)))
        = (min (cdf p ((i:ℕ)+1)) (cdf q ((j:ℕ)+1)) - min (cdf p' ((i:ℕ)+1)) (cdf q' ((j:ℕ)+1)))
          + -(max (cdf p (i:ℕ)) (cdf q (j:ℕ)) - max (cdf p' (i:ℕ)) (cdf q' (j:ℕ))) := by ring
    rw [e]
    refine (abs_add_le _ _).trans ?_
    rw [abs_neg]
    calc _ ≤ (l1 p p' + l1 q q') + (l1 p p' + l1 q q') := add_le_add hmin hmax
      _ = 2 * (l1 p p' + l1 q q') := by ring
  unfold ell
  refine (abs_max_sub_max_le_max 0 _ 0 _).trans ?_
  refine max_le ?_ hinner
  simp only [sub_self, abs_zero]
  have := l1_nonneg p p'
  have := l1_nonneg q q'
  linarith

/-- Chi phí của ghép comonotone dưới ma trận chi phí M. -/
noncomputable def QC (p : Fin n → ℝ) (q : Fin m → ℝ) (M : Fin n → Fin m → ℝ) : ℝ :=
  ∑ i, ∑ j, M i j * ell p q i j

/-- QC tuyến tính theo ma trận chi phí. -/
lemma QC_linear_M (p : Fin n → ℝ) (q : Fin m → ℝ) (a b : ℝ) (M N : Fin n → Fin m → ℝ) :
    QC p q (fun i j => a * M i j + b * N i j) = a * QC p q M + b * QC p q N := by
  simp only [QC, add_mul, Finset.sum_add_distrib, ← Finset.mul_sum, mul_assoc]

/-- **Định lý chính (lõi hữu hạn).** QC liên tục theo (p, q): chặn Lipschitz tường minh
với hằng số `2 * n * m * B`, trong đó B chặn trên |M|. Đây là bước duy nhất không phải
sách giáo khoa trong chứng minh nhất quán; phần còn lại là SLLN cộng ánh xạ liên tục. -/
theorem QC_lipschitz (p p' : Fin n → ℝ) (q q' : Fin m → ℝ)
    (M : Fin n → Fin m → ℝ) (B : ℝ) (hB0 : 0 ≤ B) (hB : ∀ i j, |M i j| ≤ B) :
    |QC p q M - QC p' q' M| ≤ 2 * n * m * B * (l1 p p' + l1 q q') := by
  have key : QC p q M - QC p' q' M
      = ∑ i, ∑ j, M i j * (ell p q i j - ell p' q' i j) := by
    simp only [QC, mul_sub, Finset.sum_sub_distrib]
  rw [key]
  have hstep : ∀ i : Fin n, ∀ j : Fin m,
      |M i j * (ell p q i j - ell p' q' i j)| ≤ B * (2 * (l1 p p' + l1 q q')) := by
    intro i j
    rw [abs_mul]
    exact mul_le_mul (hB i j) (ell_lipschitz p p' q q' i j) (abs_nonneg _) hB0
  calc |∑ i, ∑ j, M i j * (ell p q i j - ell p' q' i j)|
      ≤ ∑ i, |∑ j, M i j * (ell p q i j - ell p' q' i j)| :=
        Finset.abs_sum_le_sum_abs _ _
    _ ≤ ∑ _i : Fin n, ∑ _j : Fin m, B * (2 * (l1 p p' + l1 q q')) := by
        refine Finset.sum_le_sum fun i _ => ?_
        refine (Finset.abs_sum_le_sum_abs _ _).trans ?_
        exact Finset.sum_le_sum fun j _ => hstep i j
    _ = 2 * n * m * B * (l1 p p' + l1 q q') := by
        simp only [Finset.sum_const, Finset.card_univ, Fintype.card_fin, nsmul_eq_mul]
        ring

/-! ## Phần 2 — hợp thành qua quy nạp lùi

Phần 1 cho: QC liên tục theo (p, q). Phần này ghép các bước lại: giá trị của quy nạp lùi
T bước cũng liên tục theo toàn bộ họ nhân chuyển. Vẫn thuần hữu hạn chiều, không đo lý thuyết.
-/

/-- Vector khối lượng là phân phối xác suất. -/
def IsProb (p : Fin n → ℝ) : Prop := (∀ i, 0 ≤ p i) ∧ ∑ i, p i = 1

lemma cdf_nonneg {p : Fin n → ℝ} (hp : ∀ i, 0 ≤ p i) (i : ℕ) : 0 ≤ cdf p i :=
  Finset.sum_nonneg fun j _ => hp j

lemma cdf_le_one {p : Fin n → ℝ} (hp : IsProb p) (i : ℕ) : cdf p i ≤ 1 := by
  rw [← hp.2]
  exact Finset.sum_le_sum_of_subset_of_nonneg (Finset.filter_subset _ _)
    (fun j _ _ => hp.1 j)

/-- Mỗi trọng số ghép nằm trong [0, 1]. -/
lemma ell_le_one {p : Fin n → ℝ} {q : Fin m → ℝ} (hp : IsProb p) (hq : IsProb q)
    (i : Fin n) (j : Fin m) : ell p q i j ≤ 1 := by
  unfold ell
  refine max_le (by norm_num) ?_
  have h1 : min (cdf p ((i:ℕ)+1)) (cdf q ((j:ℕ)+1)) ≤ 1 :=
    le_trans (min_le_left _ _) (cdf_le_one hp _)
  have h2 : 0 ≤ max (cdf p (i:ℕ)) (cdf q (j:ℕ)) :=
    le_trans (cdf_nonneg hp.1 _) (le_max_left _ _)
  linarith

/-- QC là 1-Lipschitz theo ma trận chi phí, sai khác thừa số n·m (chặn thô, đủ dùng). -/
lemma QC_cost_lipschitz {p : Fin n → ℝ} {q : Fin m → ℝ} (hp : IsProb p) (hq : IsProb q)
    (M M' : Fin n → Fin m → ℝ) (D : ℝ) (hD0 : 0 ≤ D) (hD : ∀ i j, |M i j - M' i j| ≤ D) :
    |QC p q M - QC p q M'| ≤ n * m * D := by
  have key : QC p q M - QC p q M' = ∑ i, ∑ j, (M i j - M' i j) * ell p q i j := by
    simp only [QC, sub_mul, Finset.sum_sub_distrib]
  rw [key]
  calc |∑ i, ∑ j, (M i j - M' i j) * ell p q i j|
      ≤ ∑ i, |∑ j, (M i j - M' i j) * ell p q i j| := Finset.abs_sum_le_sum_abs _ _
    _ ≤ ∑ _i : Fin n, ∑ _j : Fin m, D := by
        refine Finset.sum_le_sum fun i _ => ?_
        refine (Finset.abs_sum_le_sum_abs _ _).trans ?_
        refine Finset.sum_le_sum fun j _ => ?_
        rw [abs_mul, abs_of_nonneg (ell_nonneg p q i j)]
        calc |M i j - M' i j| * ell p q i j
            ≤ D * ell p q i j :=
              mul_le_mul_of_nonneg_right (hD i j) (ell_nonneg p q i j)
          _ ≤ D * 1 := mul_le_mul_of_nonneg_left (ell_le_one hp hq i j) hD0
          _ = D := mul_one D
    _ = n * m * D := by
        simp only [Finset.sum_const, Finset.card_univ, Fintype.card_fin, nsmul_eq_mul]
        ring

/-- **Bước quy nạp.** Một bước của quy nạp lùi liên tục đồng thời theo nhân chuyển
(p, q) và theo giá trị nối tiếp M. Đây chính là bổ đề mà phép quy nạp trên T cần. -/
theorem QC_step_lipschitz {p p' : Fin n → ℝ} {q q' : Fin m → ℝ}
    (hp' : IsProb p') (hq' : IsProb q')
    (M M' : Fin n → Fin m → ℝ) (B D : ℝ) (hB0 : 0 ≤ B) (hD0 : 0 ≤ D)
    (hB : ∀ i j, |M i j| ≤ B) (hD : ∀ i j, |M i j - M' i j| ≤ D) :
    |QC p q M - QC p' q' M'| ≤ 2 * n * m * B * (l1 p p' + l1 q q') + n * m * D := by
  have h1 : |QC p q M - QC p' q' M| ≤ 2 * n * m * B * (l1 p p' + l1 q q') :=
    QC_lipschitz p p' q q' M B hB0 hB
  have h2 : |QC p' q' M - QC p' q' M'| ≤ n * m * D :=
    QC_cost_lipschitz hp' hq' M M' D hD0 hD
  have e : QC p q M - QC p' q' M' = (QC p q M - QC p' q' M) + (QC p' q' M - QC p' q' M') := by
    ring
  rw [e]
  exact (abs_add_le _ _).trans (add_le_add h1 h2)

lemma QC_zero (p : Fin n → ℝ) (q : Fin m → ℝ) : QC p q (fun _ _ => 0) = 0 := by
  simp [QC]

lemma QC_abs_le {p : Fin n → ℝ} {q : Fin m → ℝ} (hp : IsProb p) (hq : IsProb q)
    (M : Fin n → Fin m → ℝ) (B : ℝ) (hB0 : 0 ≤ B) (hB : ∀ i j, |M i j| ≤ B) :
    |QC p q M| ≤ n * m * B := by
  have h := QC_cost_lipschitz hp hq M (fun _ _ => 0) B hB0 (by simpa using hB)
  simpa [QC_zero] using h

/-- Giá trị quy nạp lùi: `s` bước còn lại, xuất phát từ mốc thời gian `t`. -/
noncomputable def Vdp (KA : ℕ → Fin n → Fin n → ℝ) (KB : ℕ → Fin m → Fin m → ℝ)
    (Mt : ℕ → Fin n → Fin m → ℝ) : ℕ → ℕ → Fin n → Fin m → ℝ
  | 0, _, _, _ => 0
  | (s + 1), t, i, j =>
      QC (KA t i) (KB t j) (fun i' j' => Mt t i' j' + Vdp KA KB Mt s (t + 1) i' j')

/-- Chặn trên cho giá trị sau `s` bước. -/
noncomputable def Vb (n m : ℕ) (B : ℝ) : ℕ → ℝ
  | 0 => 0
  | (s + 1) => n * m * (B + Vb n m B s)

/-- Hằng số Lipschitz tích lũy sau `s` bước. -/
noncomputable def Cst (n m : ℕ) (B : ℝ) : ℕ → ℝ
  | 0 => 0
  | (s + 1) => 2 * n * m * (B + Vb n m B s) + n * m * Cst n m B s

lemma Vb_nonneg (n m : ℕ) {B : ℝ} (hB0 : 0 ≤ B) : ∀ s, 0 ≤ Vb n m B s
  | 0 => le_refl 0
  | (s + 1) => by
      have := Vb_nonneg n m hB0 s
      have : (0:ℝ) ≤ B + Vb n m B s := by linarith
      unfold Vb
      positivity

lemma Cst_nonneg (n m : ℕ) {B : ℝ} (hB0 : 0 ≤ B) : ∀ s, 0 ≤ Cst n m B s
  | 0 => le_refl 0
  | (s + 1) => by
      have h1 := Cst_nonneg n m hB0 s
      have h2 := Vb_nonneg n m hB0 s
      have h3 : (0:ℝ) ≤ B + Vb n m B s := by linarith
      unfold Cst
      positivity

variable {KA KA' : ℕ → Fin n → Fin n → ℝ} {KB KB' : ℕ → Fin m → Fin m → ℝ}
  {Mt : ℕ → Fin n → Fin m → ℝ} {B : ℝ}

lemma Vdp_bound (hKA : ∀ t i, IsProb (KA t i)) (hKB : ∀ t j, IsProb (KB t j))
    (hB0 : 0 ≤ B) (hM : ∀ t i j, |Mt t i j| ≤ B) :
    ∀ s t i j, |Vdp KA KB Mt s t i j| ≤ Vb n m B s
  | 0, t, i, j => by simp [Vdp, Vb]
  | (s + 1), t, i, j => by
      have ih := Vdp_bound hKA hKB hB0 hM s
      have hbd : ∀ i' j', |Mt t i' j' + Vdp KA KB Mt s (t + 1) i' j'| ≤ B + Vb n m B s := by
        intro i' j'
        exact (abs_add_le _ _).trans (add_le_add (hM t i' j') (ih (t + 1) i' j'))
      have h0 : (0:ℝ) ≤ B + Vb n m B s := by
        have := Vb_nonneg n m hB0 s; linarith
      simpa [Vdp, Vb] using QC_abs_le (hKA t i) (hKB t j) _ (B + Vb n m B s) h0 hbd

/-- **Định lý hợp thành.** Giá trị của quy nạp lùi `s` bước là hàm Lipschitz của toàn bộ
họ nhân chuyển, với hằng số tường minh `Cst n m B s`. Cùng với `QC_lipschitz` (phần 1),
đây là toàn bộ phần "ánh xạ liên tục" của chứng minh nhất quán; phần còn lại là luật số lớn. -/
theorem Vdp_lipschitz
    (hKA' : ∀ t i, IsProb (KA' t i)) (hKB' : ∀ t j, IsProb (KB' t j))
    (hKA : ∀ t i, IsProb (KA t i)) (hKB : ∀ t j, IsProb (KB t j))
    (hB0 : 0 ≤ B) (hM : ∀ t i j, |Mt t i j| ≤ B)
    (ε : ℝ) (hε0 : 0 ≤ ε)
    (hε : ∀ t i j, l1 (KA t i) (KA' t i) + l1 (KB t j) (KB' t j) ≤ ε) :
    ∀ s t i j, |Vdp KA KB Mt s t i j - Vdp KA' KB' Mt s t i j| ≤ Cst n m B s * ε
  | 0, t, i, j => by simp [Vdp, Cst]
  | (s + 1), t, i, j => by
      have ih := Vdp_lipschitz hKA' hKB' hKA hKB hB0 hM ε hε0 hε s
      have hVb := Vb_nonneg n m hB0 s
      have h0 : (0:ℝ) ≤ B + Vb n m B s := by linarith
      have hD0 : (0:ℝ) ≤ Cst n m B s * ε :=
        mul_nonneg (Cst_nonneg n m hB0 s) hε0
      have hBb : ∀ i' j', |Mt t i' j' + Vdp KA KB Mt s (t + 1) i' j'| ≤ B + Vb n m B s := by
        intro i' j'
        exact (abs_add_le _ _).trans
          (add_le_add (hM t i' j') (Vdp_bound hKA hKB hB0 hM s (t + 1) i' j'))
      have hDd : ∀ i' j',
          |(Mt t i' j' + Vdp KA KB Mt s (t + 1) i' j')
            - (Mt t i' j' + Vdp KA' KB' Mt s (t + 1) i' j')| ≤ Cst n m B s * ε := by
        intro i' j'
        simpa using ih (t + 1) i' j'
      have step := QC_step_lipschitz (n := n) (m := m)
        (p := KA t i) (p' := KA' t i) (q := KB t j) (q' := KB' t j)
        (hKA' t i) (hKB' t j)
        (fun i' j' => Mt t i' j' + Vdp KA KB Mt s (t + 1) i' j')
        (fun i' j' => Mt t i' j' + Vdp KA' KB' Mt s (t + 1) i' j')
        (B + Vb n m B s) (Cst n m B s * ε) h0 hD0 hBb hDd
      have hle : 2 * (n:ℝ) * m * (B + Vb n m B s) * (l1 (KA t i) (KA' t i) + l1 (KB t j) (KB' t j))
          ≤ 2 * (n:ℝ) * m * (B + Vb n m B s) * ε := by
        refine mul_le_mul_of_nonneg_left (hε t i j) ?_
        positivity
      calc |Vdp KA KB Mt (s + 1) t i j - Vdp KA' KB' Mt (s + 1) t i j|
          ≤ 2 * (n:ℝ) * m * (B + Vb n m B s)
              * (l1 (KA t i) (KA' t i) + l1 (KB t j) (KB' t j))
            + (n:ℝ) * m * (Cst n m B s * ε) := by simpa [Vdp] using step
        _ ≤ 2 * (n:ℝ) * m * (B + Vb n m B s) * ε + (n:ℝ) * m * (Cst n m B s * ε) := by
            linarith
        _ = Cst n m B (s + 1) * ε := by
            have hc : Cst n m B (s + 1)
                = 2 * (n:ℝ) * m * (B + Vb n m B s) + (n:ℝ) * m * Cst n m B s := rfl
            rw [hc]; ring

/-! ## Phần 3 — từ chặn Lipschitz sang hội tụ -/

open Filter Topology

/-- **Chuyển tiếp.** Nếu họ nhân chuyển hội tụ đều theo ℓ¹ thì giá trị quy nạp lùi hội tụ.
Đây là dạng dùng được của `Vdp_lipschitz`: đầu vào duy nhất còn lại là `ε N → 0`. -/
theorem Vdp_tendsto
    (KA : ℕ → Fin n → Fin n → ℝ) (KB : ℕ → Fin m → Fin m → ℝ)
    (KAN : ℕ → ℕ → Fin n → Fin n → ℝ) (KBN : ℕ → ℕ → Fin m → Fin m → ℝ)
    (Mt : ℕ → Fin n → Fin m → ℝ) (B : ℝ)
    (hKA : ∀ t i, IsProb (KA t i)) (hKB : ∀ t j, IsProb (KB t j))
    (hKAN : ∀ N t i, IsProb (KAN N t i)) (hKBN : ∀ N t j, IsProb (KBN N t j))
    (hB0 : 0 ≤ B) (hM : ∀ t i j, |Mt t i j| ≤ B)
    (ε : ℕ → ℝ) (hε0 : ∀ N, 0 ≤ ε N)
    (hεb : ∀ N t i j, l1 (KAN N t i) (KA t i) + l1 (KBN N t j) (KB t j) ≤ ε N)
    (hε : Tendsto ε atTop (𝓝 0)) (s t : ℕ) (i : Fin n) (j : Fin m) :
    Tendsto (fun N => Vdp (KAN N) (KBN N) Mt s t i j) atTop (𝓝 (Vdp KA KB Mt s t i j)) := by
  have hbound : ∀ N,
      |Vdp (KAN N) (KBN N) Mt s t i j - Vdp KA KB Mt s t i j| ≤ Cst n m B s * ε N := by
    intro N
    exact Vdp_lipschitz (KA := KAN N) (KB := KBN N) (KA' := KA) (KB' := KB)
      hKA hKB (hKAN N) (hKBN N) hB0 hM (ε N) (hε0 N) (fun t i j => hεb N t i j) s t i j
  have hzero : Tendsto (fun N => Cst n m B s * ε N) atTop (𝓝 0) := by
    simpa using hε.const_mul (Cst n m B s)
  have habs : Tendsto
      (fun N => |Vdp (KAN N) (KBN N) Mt s t i j - Vdp KA KB Mt s t i j|) atTop (𝓝 0) :=
    squeeze_zero (fun N => abs_nonneg _) hbound hzero
  have hsub : Tendsto
      (fun N => Vdp (KAN N) (KBN N) Mt s t i j - Vdp KA KB Mt s t i j) atTop (𝓝 0) :=
    (tendsto_zero_iff_abs_tendsto_zero _).mpr habs
  rwa [tendsto_sub_nhds_zero_iff] at hsub


/-! ## Phần 4 — luật số lớn cho tần suất thực nghiệm

Mảnh còn lại của chứng minh nhất quán: tần suất thực nghiệm của một biến ngẫu nhiên
hữu hạn giá trị hội tụ hầu chắc chắn về xác suất thật.
-/

open MeasureTheory ProbabilityTheory

/-- Chỉ báo giá trị: `1` nếu `x = a`, ngược lại `0`. -/
noncomputable def ind {κ : Type*} [DecidableEq κ] (a x : κ) : ℝ := if x = a then 1 else 0

lemma ind_measurable {κ : Type*} [Countable κ] [DecidableEq κ] [MeasurableSpace κ]
    [MeasurableSingletonClass κ] (a : κ) : Measurable (ind a) :=
  measurable_of_countable _

/-- **Luật số lớn cho tần suất.** Với dãy biến ngẫu nhiên hữu hạn giá trị, độc lập đôi một,
cùng phân phối, tần suất xuất hiện của mỗi giá trị hội tụ h.c.c. về xác suất thật. -/
theorem empirical_freq_ae {Ω : Type*} [MeasurableSpace Ω] {μ : Measure Ω}
    [IsProbabilityMeasure μ]
    {κ : Type*} [Fintype κ] [DecidableEq κ] [MeasurableSpace κ] [MeasurableSingletonClass κ]
    (X : ℕ → Ω → κ) (hmeas : ∀ i, Measurable (X i))
    (hindep : Pairwise (Function.onFun (fun f g => IndepFun f g μ) X))
    (hident : ∀ i, IdentDistrib (X i) (X 0) μ μ) (a : κ) :
    ∀ᵐ ω ∂μ, Tendsto (fun N : ℕ => (N:ℝ)⁻¹ * ∑ i ∈ Finset.range N, ind a (X i ω)) atTop
      (𝓝 (μ.real (X 0 ⁻¹' {a}))) := by
  have hmY : ∀ i, Measurable (fun ω => ind a (X i ω)) :=
    fun i => (ind_measurable a).comp (hmeas i)
  have hint : Integrable (fun ω => ind a (X 0 ω)) μ := by
    refine (integrable_const (1:ℝ)).mono' (hmY 0).aestronglyMeasurable ?_
    filter_upwards with ω
    simp only [Real.norm_eq_abs, ind]
    split_ifs <;> simp
  have hindY : Pairwise
      (Function.onFun (fun f g => IndepFun f g μ) (fun i ω => ind a (X i ω))) := by
    intro i j hij
    exact (hindep hij).comp (ind_measurable a) (ind_measurable a)
  have hidY : ∀ i, IdentDistrib (fun ω => ind a (X i ω)) (fun ω => ind a (X 0 ω)) μ μ :=
    fun i => (hident i).comp (ind_measurable a)
  have hsl := strong_law_ae (fun i ω => ind a (X i ω)) hint hindY hidY
  have hval : ∫ ω, ind a (X 0 ω) ∂μ = μ.real (X 0 ⁻¹' {a}) := by
    have hset : MeasurableSet (X 0 ⁻¹' {a}) := (hmeas 0) (measurableSet_singleton a)
    have he : (fun ω => ind a (X 0 ω)) = (X 0 ⁻¹' {a}).indicator 1 := by
      funext ω
      by_cases h : X 0 ω = a <;>
        simp [ind, Set.indicator_apply, Set.mem_preimage, h]
    rw [he, integral_indicator_one hset]
  filter_upwards [hsl] with ω hω
  rw [← hval]
  simpa [smul_eq_mul] using hω


/-! ## Phần 5 — ráp lại: nhất quán hầu chắc chắn -/

/-- Hội tụ từng thành phần kéo theo hội tụ theo chuẩn ℓ¹ (không gian hữu hạn chiều). -/
lemma l1_tendsto_of_pointwise {p : Fin n → ℝ} {pN : ℕ → Fin n → ℝ}
    (h : ∀ i, Tendsto (fun N => pN N i) atTop (𝓝 (p i))) :
    Tendsto (fun N => l1 (pN N) p) atTop (𝓝 0) := by
  have hsum : Tendsto (fun N => ∑ i, |pN N i - p i|) atTop (𝓝 (∑ _i : Fin n, (0:ℝ))) := by
    refine tendsto_finset_sum _ fun i _ => ?_
    have h1 : Tendsto (fun N => pN N i - p i) atTop (𝓝 (p i - p i)) :=
      (h i).sub tendsto_const_nhds
    simpa using h1.abs
  simpa [l1] using hsum

/-- Ước lượng nhân chuyển bằng tỉ số đếm hội tụ, **với điều kiện** xác suất mẫu số dương.
Đây chính là giả thiết khả đạt: ô không bao giờ được thăm thì nhân chuyển không xác định. -/
lemma kernel_entry_tendsto {num den : ℕ → ℝ} {a b : ℝ} (hb : b ≠ 0)
    (hn : Tendsto num atTop (𝓝 a)) (hd : Tendsto den atTop (𝓝 b)) :
    Tendsto (fun N => num N / den N) atTop (𝓝 (a / b)) := hn.div hd hb

/-- **Nhất quán (trường hợp thuần nhất theo thời gian).** Nếu mọi hàng của nhân chuyển ước
lượng hội tụ về hàng thật, thì giá trị quy nạp lùi hội tụ. Ghép với `empirical_freq_ae` và
`kernel_entry_tendsto`, đây là mệnh đề nhất quán cho ước lượng k-Markov trên lưới cố định. -/
theorem Vdp_tendsto_homog
    (KA0 : Fin n → Fin n → ℝ) (KB0 : Fin m → Fin m → ℝ)
    (KAN0 : ℕ → Fin n → Fin n → ℝ) (KBN0 : ℕ → Fin m → Fin m → ℝ)
    (Mt : ℕ → Fin n → Fin m → ℝ) (B : ℝ)
    (hKA : ∀ i, IsProb (KA0 i)) (hKB : ∀ j, IsProb (KB0 j))
    (hKAN : ∀ N i, IsProb (KAN0 N i)) (hKBN : ∀ N j, IsProb (KBN0 N j))
    (hB0 : 0 ≤ B) (hM : ∀ t i j, |Mt t i j| ≤ B)
    (hA : ∀ i, Tendsto (fun N => l1 (KAN0 N i) (KA0 i)) atTop (𝓝 0))
    (hB' : ∀ j, Tendsto (fun N => l1 (KBN0 N j) (KB0 j)) atTop (𝓝 0))
    (s t : ℕ) (i : Fin n) (j : Fin m) :
    Tendsto (fun N => Vdp (fun _ => KAN0 N) (fun _ => KBN0 N) Mt s t i j) atTop
      (𝓝 (Vdp (fun _ => KA0) (fun _ => KB0) Mt s t i j)) := by
  set ε : ℕ → ℝ :=
    fun N => (∑ i', l1 (KAN0 N i') (KA0 i')) + (∑ j', l1 (KBN0 N j') (KB0 j')) with hεdef
  have hε0 : ∀ N, 0 ≤ ε N := by
    intro N
    simp only [hεdef]
    exact add_nonneg (Finset.sum_nonneg fun i' _ => l1_nonneg _ _)
      (Finset.sum_nonneg fun j' _ => l1_nonneg _ _)
  have hεb : ∀ (N : ℕ) (_t' : ℕ) (i' : Fin n) (j' : Fin m),
      l1 (KAN0 N i') (KA0 i') + l1 (KBN0 N j') (KB0 j') ≤ ε N := by
    intro N _t' i' j'
    simp only [hεdef]
    have h1 : l1 (KAN0 N i') (KA0 i') ≤ ∑ x, l1 (KAN0 N x) (KA0 x) :=
      Finset.single_le_sum (f := fun x => l1 (KAN0 N x) (KA0 x))
        (fun x _ => l1_nonneg _ _) (Finset.mem_univ i')
    have h2 : l1 (KBN0 N j') (KB0 j') ≤ ∑ y, l1 (KBN0 N y) (KB0 y) :=
      Finset.single_le_sum (f := fun y => l1 (KBN0 N y) (KB0 y))
        (fun y _ => l1_nonneg _ _) (Finset.mem_univ j')
    exact add_le_add h1 h2
  have hεlim : Tendsto ε atTop (𝓝 0) := by
    have hA' : Tendsto (fun N => ∑ i', l1 (KAN0 N i') (KA0 i')) atTop (𝓝 (∑ _i' : Fin n, (0:ℝ))) :=
      tendsto_finset_sum _ fun i' _ => hA i'
    have hB'' : Tendsto (fun N => ∑ j', l1 (KBN0 N j') (KB0 j')) atTop (𝓝 (∑ _j' : Fin m, (0:ℝ))) :=
      tendsto_finset_sum _ fun j' _ => hB' j'
    simpa [hεdef] using hA'.add hB''
  exact Vdp_tendsto (fun _ => KA0) (fun _ => KB0) (fun N _ => KAN0 N) (fun N _ => KBN0 N)
    Mt B (fun _ i' => hKA i') (fun _ j' => hKB j') (fun N _ i' => hKAN N i')
    (fun N _ j' => hKBN N j') hB0 hM ε hε0 hεb hεlim s t i j


/-! ## Phần 6 — hàn mắt xích cuối: ước lượng đếm trên mẫu cặp chuyển tiếp

Ước lượng thật sự dùng trong code: đếm cặp (ô nguồn, ô đích) rồi chia cho đếm ô nguồn.
Ô chưa từng được thăm (mẫu số 0) trả về hàng đều — đúng như hiện thực, và nhờ vậy hàng
luôn là phân phối với **mọi** N, không chỉ N lớn.
-/

lemma ind_nonneg {κ : Type*} [DecidableEq κ] (a x : κ) : 0 ≤ ind a x := by
  unfold ind; split <;> norm_num

lemma ind_le_one {κ : Type*} [DecidableEq κ] (a x : κ) : ind a x ≤ 1 := by
  unfold ind; split <;> norm_num

/-- Tổng chỉ báo theo ô đích bằng chỉ báo của ô nguồn. -/
lemma ind_sum_snd {N : ℕ} (i : Fin N) (z : Fin N × Fin N) :
    ∑ j, ind (i, j) z = ind i z.1 := by
  unfold ind
  simp only [Prod.ext_iff]
  by_cases h : z.1 = i
  · simp [h, Finset.sum_ite_eq]
  · simp [h]

/-- Tần suất thực nghiệm của giá trị `a` trong `N` quan sát đầu. -/
noncomputable def freq {Ω κ : Type*} [DecidableEq κ]
    (W : ℕ → Ω → κ) (a : κ) (N : ℕ) (ω : Ω) : ℝ :=
  (N : ℝ)⁻¹ * ∑ k ∈ Finset.range N, ind a (W k ω)

lemma freq_nonneg {Ω κ : Type*} [DecidableEq κ]
    (W : ℕ → Ω → κ) (a : κ) (N : ℕ) (ω : Ω) : 0 ≤ freq W a N ω := by
  unfold freq
  exact mul_nonneg (by positivity) (Finset.sum_nonneg fun k _ => ind_nonneg _ _)

lemma freq_sum_snd {Ω : Type*} {N : ℕ} (Z : ℕ → Ω → Fin N × Fin N)
    (i : Fin N) (M : ℕ) (ω : Ω) :
    ∑ j, freq Z (i, j) M ω = freq (fun k ω => (Z k ω).1) i M ω := by
  unfold freq
  rw [← Finset.mul_sum]
  congr 1
  rw [Finset.sum_comm]
  exact Finset.sum_congr rfl fun k _ => ind_sum_snd i (Z k ω)

/-- Ước lượng nhân chuyển từ mẫu cặp chuyển tiếp; ô chưa thăm trả hàng đều. -/
noncomputable def Khat {Ω : Type*} {N : ℕ} [NeZero N]
    (Z : ℕ → Ω → Fin N × Fin N) (M : ℕ) (ω : Ω) (i j : Fin N) : ℝ :=
  if freq (fun k ω => (Z k ω).1) i M ω = 0 then ((N : ℝ))⁻¹
  else freq Z (i, j) M ω / freq (fun k ω => (Z k ω).1) i M ω

lemma Khat_isProb {Ω : Type*} {N : ℕ} [NeZero N]
    (Z : ℕ → Ω → Fin N × Fin N) (M : ℕ) (ω : Ω) (i : Fin N) :
    IsProb (Khat Z M ω i) := by
  have hN : (N : ℝ) ≠ 0 := Nat.cast_ne_zero.mpr (NeZero.ne N)
  unfold Khat
  by_cases h : freq (fun k ω => (Z k ω).1) i M ω = 0
  · refine ⟨fun j => by simp [h], ?_⟩
    simp only [h, if_true]
    rw [Finset.sum_const, Finset.card_univ, Fintype.card_fin, nsmul_eq_mul]
    field_simp
  · have hpos : 0 < freq (fun k ω => (Z k ω).1) i M ω :=
      lt_of_le_of_ne (freq_nonneg _ _ _ _) (Ne.symm h)
    refine ⟨fun j => by simp only [h, if_false]; exact div_nonneg (freq_nonneg _ _ _ _) hpos.le, ?_⟩
    simp only [h, if_false]
    rw [← Finset.sum_div, freq_sum_snd]
    exact div_self h


lemma ind_integrable {Ω κ : Type*} [MeasurableSpace Ω] {μ : Measure Ω} [IsProbabilityMeasure μ]
    [Fintype κ] [DecidableEq κ] [MeasurableSpace κ] [MeasurableSingletonClass κ]
    (W : Ω → κ) (hW : Measurable W) (a : κ) : Integrable (fun ω => ind a (W ω)) μ := by
  refine (integrable_const (1:ℝ)).mono' (((ind_measurable a).comp hW).aestronglyMeasurable) ?_
  filter_upwards with ω
  simp only [Real.norm_eq_abs, ind]
  split_ifs <;> simp

lemma integral_ind_eq {Ω κ : Type*} [MeasurableSpace Ω] {μ : Measure Ω} [IsProbabilityMeasure μ]
    [Fintype κ] [DecidableEq κ] [MeasurableSpace κ] [MeasurableSingletonClass κ]
    (W : Ω → κ) (hW : Measurable W) (a : κ) :
    ∫ ω, ind a (W ω) ∂μ = μ.real (W ⁻¹' {a}) := by
  have hset : MeasurableSet (W ⁻¹' {a}) := hW (measurableSet_singleton a)
  have he : (fun ω => ind a (W ω)) = (W ⁻¹' {a}).indicator 1 := by
    funext ω
    by_cases h : W ω = a <;> simp [ind, Set.indicator_apply, Set.mem_preimage, h]
  rw [he, integral_indicator_one hset]

/-- Xác suất biên là tổng xác suất khớp — chứng minh qua tích phân chỉ báo. -/
lemma sum_measure_real {Ω : Type*} [MeasurableSpace Ω] {μ : Measure Ω} [IsProbabilityMeasure μ]
    {N : ℕ} (Z0 : Ω → Fin N × Fin N) (hZ : Measurable Z0) (i : Fin N) :
    ∑ j, μ.real (Z0 ⁻¹' {(i, j)}) = μ.real ((fun ω => (Z0 ω).1) ⁻¹' {i}) := by
  have h1 : ∑ j, μ.real (Z0 ⁻¹' {(i, j)}) = ∑ j, ∫ ω, ind (i, j) (Z0 ω) ∂μ :=
    Finset.sum_congr rfl fun j _ => (integral_ind_eq Z0 hZ (i, j)).symm
  rw [h1, ← integral_finsetSum _ (fun j _ => ind_integrable Z0 hZ (i, j))]
  have h2 : (fun ω => ∑ j, ind (i, j) (Z0 ω)) = fun ω => ind i ((Z0 ω).1) := by
    funext ω; exact ind_sum_snd i (Z0 ω)
  rw [h2, integral_ind_eq (fun ω => (Z0 ω).1) (measurable_fst.comp hZ) i]

/-- Nhân chuyển thật: xác suất có điều kiện của ô đích khi biết ô nguồn. -/
noncomputable def K0 {Ω : Type*} [MeasurableSpace Ω] (μ : Measure Ω) {N : ℕ}
    (Z0 : Ω → Fin N × Fin N) (i j : Fin N) : ℝ :=
  μ.real (Z0 ⁻¹' {(i, j)}) / μ.real ((fun ω => (Z0 ω).1) ⁻¹' {i})

lemma K0_isProb {Ω : Type*} [MeasurableSpace Ω] {μ : Measure Ω} [IsProbabilityMeasure μ]
    {N : ℕ} (Z0 : Ω → Fin N × Fin N) (hZ : Measurable Z0) (i : Fin N)
    (hpos : μ.real ((fun ω => (Z0 ω).1) ⁻¹' {i}) ≠ 0) : IsProb (K0 μ Z0 i) := by
  refine ⟨fun j => div_nonneg measureReal_nonneg measureReal_nonneg, ?_⟩
  unfold K0
  rw [← Finset.sum_div, sum_measure_real Z0 hZ i]
  exact div_self hpos

/-- **Ước lượng đếm hội tụ h.c.c. về nhân chuyển thật**, với giả thiết khả đạt
(mọi ô nguồn có xác suất dương). -/
theorem Khat_ae_tendsto {Ω : Type*} [MeasurableSpace Ω] {μ : Measure Ω} [IsProbabilityMeasure μ]
    {N : ℕ} [NeZero N] (Z : ℕ → Ω → Fin N × Fin N)
    (hmeas : ∀ k, Measurable (Z k))
    (hindep : Pairwise (Function.onFun (fun f g => IndepFun f g μ) Z))
    (hident : ∀ k, IdentDistrib (Z k) (Z 0) μ μ)
    (hpos : ∀ i : Fin N, μ.real ((fun ω => (Z 0 ω).1) ⁻¹' {i}) ≠ 0) :
    ∀ᵐ ω ∂μ, ∀ i j, Tendsto (fun M => Khat Z M ω i j) atTop (𝓝 (K0 μ (Z 0) i j)) := by
  have hfst : ∀ k, Measurable (fun ω => (Z k ω).1) := fun k => measurable_fst.comp (hmeas k)
  have hmarg : ∀ i : Fin N, ∀ᵐ ω ∂μ,
      Tendsto (fun M => freq (fun k ω => (Z k ω).1) i M ω) atTop
        (𝓝 (μ.real ((fun ω => (Z 0 ω).1) ⁻¹' {i}))) := by
    intro i
    refine empirical_freq_ae (fun k ω => (Z k ω).1) hfst ?_ ?_ i
    · intro a b hab; exact (hindep hab).comp measurable_fst measurable_fst
    · intro k; exact (hident k).comp measurable_fst
  rw [ae_all_iff]; intro i
  rw [ae_all_iff]; intro j
  filter_upwards [empirical_freq_ae Z hmeas hindep hident (i, j), hmarg i] with ω h1 h2
  have hne : ∀ᶠ M in atTop, freq (fun k ω => (Z k ω).1) i M ω ≠ 0 := h2.eventually_ne (hpos i)
  have hratio : Tendsto
      (fun M => freq Z (i, j) M ω / freq (fun k ω => (Z k ω).1) i M ω) atTop
      (𝓝 (K0 μ (Z 0) i j)) := h1.div h2 (hpos i)
  refine Tendsto.congr' ?_ hratio
  filter_upwards [hne] with M hM
  simp [Khat, hM]

/-- **Nhất quán, phát biểu đầy đủ.** Hai mẫu cặp chuyển tiếp độc lập cùng phân phối, mọi ô
nguồn khả đạt ⟹ giá trị quy nạp lùi tính từ nhân chuyển ước lượng hội tụ **hầu chắc chắn**
về giá trị tính từ nhân chuyển thật. -/
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
      (𝓝 (Vdp (fun _ => K0 μ (ZA 0)) (fun _ => K0 μ (ZB 0)) Mt s t i j)) := by
  filter_upwards [Khat_ae_tendsto ZA hmA hiA hdA hpA,
                  Khat_ae_tendsto ZB hmB hiB hdB hpB] with ω hA hB
  refine Vdp_tendsto_homog (K0 μ (ZA 0)) (K0 μ (ZB 0)) (fun M => Khat ZA M ω)
    (fun M => Khat ZB M ω) Mt Bd
    (fun i' => K0_isProb (ZA 0) (hmA 0) i' (hpA i'))
    (fun j' => K0_isProb (ZB 0) (hmB 0) j' (hpB j'))
    (fun M i' => Khat_isProb ZA M ω i') (fun M j' => Khat_isProb ZB M ω j')
    hB0 hM ?_ ?_ s t i j
  · exact fun i' => l1_tendsto_of_pointwise (fun j' => hA i' j')
  · exact fun j' => l1_tendsto_of_pointwise (fun i' => hB j' i')


end ATSW
