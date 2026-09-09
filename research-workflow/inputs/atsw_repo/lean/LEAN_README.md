# Chứng minh Lean: nhất quán của ước lượng ATSW k-Markov

Lean 4.33.0 + mathlib (tag v4.33.0). `Atsw.lean` — **35 định lý/bổ đề, 613 dòng, 0 `sorry`**.
`#print axioms` cho mọi kết quả chỉ ra ba tiên đề chuẩn của Lean (`propext`,
`Classical.choice`, `Quot.sound`) — không có `sorryAx`.

## Định lý đích

```
Vdp_consistent_ae :
  hai mẫu cặp chuyển tiếp (ZA, ZB) độc lập đôi một, cùng phân phối, đo được,
  mọi ô nguồn có xác suất dương, chi phí bị chặn
  ⟹ ∀ᵐ ω, Vdp (Khat ZA M ω) (Khat ZB M ω) ⟶ Vdp (K0 ZA) (K0 ZB)  khi M → ∞
```


> ## ĐỌC KỸ PHẦN NÀY TRƯỚC KHI TRÍCH DẪN
>
> **Đích của định lý là surrogate, KHÔNG phải adapted distance.** Hai vế của
> `Vdp_consistent_ae` là **cùng một** hàm `Vdp`, chỉ khác ở chỗ một bên dùng nhân chuyển ước
> lượng và một bên dùng nhân chuyển thật. `Vdp` được dựng trên `QC` — ghép comonotone — nên
> **trong toàn bộ file không có `iInf`/`sInf` nào**: không có chỗ nào lấy infimum trên tập ghép
> nối. Vậy điều được máy kiểm là `Vdp(K̂) → Vdp(K)`, tức *ước lượng hội tụ về giá trị dân số của
> chính surrogate*, **không** phải `→ AW_p^p`. Khoảng cách còn lại là chệch do ghép comonotone:
> đã **đo** (10–20% trên cây cho trước) và **chưa có chặn**.
>
> Ba hạn định còn lại: hằng số Lipschitz `(n·m)^s` chứng minh *tính liên tục* chứ không phải
> *tốc độ*; phát biểu là ca **thuần nhất thời gian** (nhân chuyển vào dưới dạng `fun _ => …`);
> và hội tụ **từng điểm** `(s,t,i,j)` ở **lưới cố định** — δ không xuất hiện trong phát biểu nên
> không có kết luận nào về giới hạn làm mịn lưới.
>
> Đây đúng là loại lỗi máy kiểm không bắt được: kernel kiểm rằng chứng minh thiết lập được
> *phát biểu của nó*, không kiểm rằng phát biểu nói đúng điều tác giả muốn nói.


Tức: **giá trị quy nạp lùi tính từ nhân chuyển ước lượng bằng đếm hội tụ hầu chắc chắn về
giá trị tính từ nhân chuyển thật.** Đây là mệnh đề nhất quán, hoàn chỉnh, được máy kiểm.

## Sáu phần

| Phần | Nội dung | Kết quả chính |
|---|---|---|
| 1 | Toán tử ghép comonotone | `QC_lipschitz`: `\|QC(p,q;M) − QC(p',q';M)\| ≤ 2nmB(‖p−p'‖₁+‖q−q'‖₁)` |
| 2 | Hợp thành quy nạp lùi | `Vdp_lipschitz`: `\|Vdp s − Vdp' s\| ≤ Cst s · ε` |
| 3 | Chặn → hội tụ | `Vdp_tendsto` |
| 4 | Luật số lớn | `empirical_freq_ae` (từ `strong_law_ae` của mathlib) |
| 5 | Ráp ca thuần nhất | `Vdp_tendsto_homog`, `l1_tendsto_of_pointwise` |
| 6 | Ước lượng đếm thật | `ind_sum_snd`, `Khat_isProb`, `sum_measure_real`, `K0_isProb`, `Khat_ae_tendsto`, **`Vdp_consistent_ae`** |

## Ba chỗ Lean buộc phải nói rõ, mà chứng minh viết tay hay lướt qua

1. **Giả thiết khả đạt.** `Khat_ae_tendsto` không đứng được nếu thiếu
   `μ.real (ô nguồn) ≠ 0`. Ô không bao giờ được thăm thì nhân chuyển không xác định.
2. **Hàng mặc định.** Với N hữu hạn, mẫu số có thể bằng 0. `Khat` trả **hàng đều** trong ca đó,
   nhờ vậy hàng là phân phối với *mọi* N — nếu không, giả thiết `IsProb` của định lý hợp thành
   sẽ hỏng ở N nhỏ. Hội tụ vẫn đúng vì mẫu số khác 0 **cuối cùng** (`Tendsto.eventually_ne`).
3. **Xác suất biên = tổng xác suất khớp.** Cần cho `K0_isProb`; chứng minh qua tích phân chỉ báo
   (`sum_measure_real`), không phải hiển nhiên về mặt hình thức.

## Ranh giới còn lại

- **Thuần nhất theo thời gian**: một nhân chuyển dùng chung mọi mốc — đúng ca k-Markov dừng.
  Bản không thuần nhất dùng `Vdp_tendsto` (tổng quát hơn, đã có) với chặn đều trên hữu hạn mốc.
- **Cặp chuyển tiếp i.i.d.**: mẫu được mô hình hóa là dãy cặp (ô nguồn, ô đích) độc lập cùng
  phân phối — lý tưởng hóa chuẩn của việc gộp cặp từ nhiều đường đi. Chưa mô hình hóa sự phụ
  thuộc giữa các cặp lấy từ **cùng một** đường đi.
- **Hằng số `Cst ~ (n·m)^s`** rất thô: chứng minh *tính liên tục*, không phải *tốc độ hội tụ*.
- Không gian trạng thái cùng kích thước ở mọi mốc — đúng cho lưới cố định sau khi đệm ô
  khối lượng 0.

## Dựng lại

```bash
export ELAN_HOME=$PWD/.elan; export PATH="$ELAN_HOME/bin:$PATH"
cd atswproof && lake exe cache get && lake build
lean Check.lean    # in danh sách tiên đề của từng định lý
```
Mạng cần: `releases.lean-lang.org`, `github.com`, `lakecache.blob.core.windows.net`.
Lưu ý: `import Mathlib` (toàn bộ) làm OOM ở 8 GiB — file này nhập chọn lọc 6 module.
