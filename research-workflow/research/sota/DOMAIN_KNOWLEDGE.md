# Tri thức domain — đọc toàn văn 7 công trình (2025–2026)

> **Audit 2026-09-10:** Đọc [DOMAIN_RATE_AUDIT_20260910.md](DOMAIN_RATE_AUDIT_20260910.md) trước khi dùng các suy luận bên dưới để ra quyết định. Hệ số rate không chứng minh sàn nhiễu/bất khả nhận dạng; định lý compact/full-prefix/AW1 chưa khớp pipeline Gaussian/fixed-k/AW2². Định lý smooth fast-rate có điều kiện exponential moment, không chỉ moment bậc q. Các suy luận trái audit được rút lại; giữ phần gốc để truy lịch sử. [Oracle Gauss đã kiểm tra](../theory/GAUSSIAN_ORACLE_20260910.md) đo riêng discrepancy population. Giữ estimand solver hiện tại.

Ngày đọc: 2026-09-09. Tải toàn văn từ arXiv và Project Euclid, trích bằng pypdfium2,
**242 trang / 665k ký tự**. Mọi con số dưới đây đã đối chiếu ngược lại văn bản gốc bằng
tìm kiếm chuỗi; chỗ nào chỉ từ trích xuất tự động thì ghi rõ.

| công trình | định danh | trang |
|---|---|---|
| Cao, Hoekstra, R. Xu, Y. Xu, Zhang — Scalable Bi-causal OT | `arXiv:2605.17271` | 71 |
| Kršek, Pammer — General duality and dual attainment for adapted transport | `arXiv:2401.11958v2` | 45 |
| Mirmominov, Wiesel — Convergence of the adapted empirical measure for mixing observations | `arXiv:2512.18838` | 38 |
| Jiang, Lim — A transfer principle for computing AW | `arXiv:2505.21337` | 32 |
| Larsson, Park, Wiesel — Fast rate of the smooth adapted Wasserstein distance | `arXiv:2503.10827` | 27 |
| Acciaio, Hou, Pammer — Entropic adapted Wasserstein on Gaussians | `arXiv:2412.18794v2` | 15 |
| Gunasingam, Wong — Adapted OT between Gaussian processes in discrete time | `doi:10.1214/25-ecp654` | 14 |

Chưa đọc: Kirui–Pflug–Pichler (`doi:10.1007/s10287-025-00542-5`) — không có bản arXiv,
không open access.

---

## Phát hiện 1 (quyết định): đại lượng dự án đang tối ưu **gần như không nhận dạng được** ở T=50

Mirmominov–Wiesel, biểu thức (1) và (15)–(16), Định lý 4.2/4.6 — trích nguyên văn:

> `E AW(µ, µ̂^N) ≤ C · sqrt(1 + 2 Σ_{s=1}^{N−1} η_X̂(s)) · rate∞(N)`
> `rate∞(N) := N^(−1/(T+1)) khi d=1;  N^(−1/(2T)) log(N+1) khi d=2;  N^(−1/(dT)) khi d≥3`

Đây là **độ đo thực nghiệm adapted trên lưới**, tức đúng đối tượng dự án dựng. Thay số của
lưới đã đóng băng (d=1):

| N (paths) | T=8 | **T=50** |
|---|---|---|
| 4000 | 0.3979 | **0.8499** |
| 6000 | 0.3804 | **0.8432** |
| 8000 | 0.3684 | **0.8384** |
| 20000 | 0.3327 | **0.8235** |

Ở T=50 tốc độ nằm quanh **0,84–0,85** — thực tế là không hội tụ. Muốn `rate∞` xuống 0,50
cần N = 2^51 ≈ 2,3·10^15 paths; xuống 0,10 cần N = 10^51.

**Hệ quả trực tiếp cho scope.** Tỉ lệ tương phản/sàn nhiễu đo được trong bổ chính 1
(1,51× cho ar1 và 1,31× cho họ bậc hai, ở T=8) **không phải** hiện tượng lạ của một thiết
lập nhỏ — nó là điều literature dự đoán, và ở T=50 nó **tệ hơn**, không tốt lên. Chứng nhận
tới 0,005 tương đối trên đại lượng đó là chứng nhận **vòng trong của solver**, không phải
chứng nhận khoảng cách giữa hai quá trình. Câu hỏi "scope có đủ sức nặng không" giờ có câu
trả lời từ literature chứ không chỉ từ một phép đo nội bộ.

Mirmominov cũng chốt bề rộng lưới lý thuyết, biểu thức (5): `Δ_N := N^(−r)`, `r = 1/(T+1)`
khi d=1. Dự án dùng δ ∈ {0,5; 0,3; 0,18}. Hai con số này **không so trực tiếp được** cho tới
khi chuẩn hoá giá đỡ về [0,1] — nhưng đó là một phép kiểm rẻ và phải làm, vì nếu lưới của dự
án mịn hơn mức N cho phép thì phần "trạng thái" thừa ra chỉ là nhiễu.

## Phát hiện 2: có đường thoát, và nó nằm ở việc **đổi estimand**

Larsson–Park–Wiesel, Định lý 4 — nguyên văn phần tóm tắt: *"If µ is subgaussian, then
`E[AW^(σ)_p(µ, µ̂_n)] ≲ 1/√n`, i.e., the fast rate of convergence holds for the smooth
adapted Wasserstein distance."* Điều kiện: mô men `q > 8p(2p−1)(T+9)`.

Đối chiếu với bản **không** làm mịn, cùng bài trích lại kết quả đã biết:
`E[AW_1(µ̂_n, µ)] ≤ C n^(−1/(dT))` với d≥3, và ghi rõ **các tỉ lệ này là sharp**.

Giá phải trả của làm mịn là chệch có kiểm soát:
`|AW^(σ)_p(µ,ν) − AW_p(µ,ν)| ≤ C(ω_µ(σ) + ω_ν(σ))`, và `≤ Cσ` khi kernel Lipschitz.

Nghĩa là: **sàn nhiễu không phải cố hữu của bài toán, nó cố hữu của estimand hiện tại.**
Chuyển sang `AW^(σ)_p` biến tốc độ từ phụ thuộc chiều-và-horizon thành `n^(−1/2)` không phụ
thuộc chiều, đổi lấy một chệch O(σ) **định lượng được**. Đây là quyết định ở tầng scope, không
phải tầng thuật toán.

## Phát hiện 3: giờ đã có **oracle nghiệm đóng** cho cả hai track — và cho cả bài toán gap comonotone

**Gunasingam–Wong, Định lý 1.1.** Với µ = N(a,A), ν = N(b,B) không suy biến, Cholesky
A = LLᵀ, B = MMᵀ:

    AW₂²(µ,ν) = ‖a−b‖² + d²_ABW(A,B),   d²_ABW(A,B) = tr(A) + tr(B) − 2‖diag(LᵀM)‖₁

Họ ar1 của dự án **là Gauss**, nên giá trị population của target có công thức đóng. Dự án hiện
suy ra chệch lượng tử hoá + chệch lấy mẫu một cách gián tiếp; với công thức này đo được **trực
tiếp**. Đây là phép kiểm rẻ nhất và có giá trị nhất mà bảng baseline trước chưa khai thác.

Quan trọng không kém, cùng bài, (3.4) và (5.3) — xác minh nguyên văn:

    d²_KR(A,B) = tr(A) + tr(B) − 2 tr(LᵀM) = ‖L−M‖²_F
    d²_ABW(A,B) = d²_KR(A,B) − 4 Σ_{t:(LᵀM)_tt<0} |(LᵀM)_tt|

Và Hệ quả 4.6: **ghép Knothe–Rosenblatt tối ưu khi và chỉ khi (LᵀM)_tt ≥ 0 với mọi t**, kèm
khẳng định tồn tại lân cận mở của A mà điều kiện này luôn đúng.

Trên đường thẳng, KR chính là ghép comonotone. Nên trong họ Gauss, **gap ghép comonotone có
nghiệm đóng**: nó bằng đúng `4·Σ` trên các thời điểm mà `(LᵀM)_tt < 0`, và bằng 0 khi và chỉ
khi mọi số hạng đó không âm. Chương trình đo gap comonotone bằng thực nghiệm và đi tìm chặn
theo vi phạm Monge, trong họ Gauss, đã có lời giải đóng sẵn.

**Acciaio–Hou–Pammer, Định lý 2.4** mở rộng sang nhiều chiều **và** sang bản entropic:

    AW²_{2,λ}(µ,ν) = |a−b|² + tr(A+B) − 2 tr(D_λ S) − (λ/2) log det(I − D_λ²)

với `D_λ = f_λ(S)`, `f_λ(x) = sign(x)·sqrt((λ/(4|x|))² + 1) − λ/(4|x|)`, và S là ma trận giá
trị kỳ dị theo khối. Ở λ=0 rút về công thức AW₂². Nghĩa là **nested Sinkhorn kiểm được bằng
công thức đóng ở mọi λ**, thay vì chỉ bằng oracle tiny 20 instance như lane D đã làm.

## Phát hiện 4: Cao và cộng sự 2026 — phán quyết eligibility, ở mức định lý

Cấu trúc bài: Bổ đề 1 (tập Markov bicausal coupling **trùng** toàn bộ tập bicausal coupling khi
hai biên là Markov — điều này biện minh cho khung k-window), Bổ đề 2/3 (DPP cho bài gốc và bài
nới lỏng), Định lý 1 (**Γ-hội tụ** khi β→∞), Định lý 2 (policy gradient), Định lý 3 (chặn regret
trung bình và last-iterate dưới smoothness + PL), Nhận xét 5 (tỉ lệ O(1/K) với η_k = O(k^{−1})).

**Không có cận theo từng instance cho giá trị tại gốc.** Bảo đảm là Γ-hội tụ tiệm cận theo β
cộng regret theo K — không phải khoảng bao hợp lệ cho một instance cụ thể. Đánh giá trong
`BASELINES.md` viết từ abstract **đứng vững sau khi đọc toàn văn**.

Ba giới hạn tác giả tự khai, đáng ghi: (i) khung Markov chỉ là "technical and notational
convenience"; (ii) Γ-hội tụ cần Giả thiết 1 (chi phí không âm, nửa liên tục dưới, infimum hữu
hạn); (iii) hướng KL là reference‖candidate nên **buộc liên tục tuyệt đối** và phạt vô hạn khi
giá đỡ không khớp — với mô hình lượng tử hoá thưa của dự án, đây là ràng buộc thật.

Mã nguồn: bài nói "publicly available on GitHub" (chú thích 1) nhưng URL không xuất hiện trong
phần văn bản đã trích — chưa pin được revision.

## Phát hiện 5: đối ngẫu cho adapted transport là **prior art đã có**, và mạnh

Kršek–Pammer chứng minh đối ngẫu **và đạt cực trị đối ngẫu** cho: causal và bicausal OT
(Định lý 2.1, chi tiết ở 4.6 và 4.8), multicausal (2.6 / 4.13), barycenter causal (2.8) và
bicausal (2.11). Công cụ: Choquet capacitability, bổ đề Komlós, bổ đề Fatou. Không có thuật toán.

Hệ quả cho dự án: cơ chế cận dưới miễn phí — *khả thi đối ngẫu ⇒ cận dưới hợp lệ* — không chỉ là
kiến thức sách giáo khoa mà nay đã được hình thức hoá cho đúng lớp bài toán này. Phần **còn có
thể tuyên bố mới** thu hẹp lại còn: độ chặt, chi phí, hoặc chứng nhận **khi đã bỏ bớt** tính toán.
Nhận xét 2.2(iii) cũng đáng nhớ: bài toán primal **không nhất thiết đạt cực trị**; chỉ đối ngẫu
được bảo đảm đạt.

## Phát hiện 6: Jiang–Lim — nguyên lý chuyển, nhưng ở thời gian liên tục

Định lý 4.3 cho công thức AW₂² qua phân tích nhân quả (K, µ) của toán tử hiệp phương sai; Định lý
1.1 áp cho chuyển động Brown phân thứ: `AW₂(B^{H1}, B^{H2})² = ‖K_{H1} − K_{H2}‖²_HS`, đạt bởi
**ghép đồng bộ**. Định lý 5.5 mở sang fSDE. Bài **không** bàn tốc độ hội tụ của độ đo thực nghiệm.

Liên quan tới dự án là gián tiếp: nó là nguồn instance kiểm thử có nghiệm đóng ở thời gian liên
tục, không phải đối thủ trên lưới hữu hạn.

---

## Điều này đổi gì trong dự án, theo thứ tự giá trị

1. **Dựng oracle Gauss** (Gunasingam–Wong Thm 1.1) cho họ ar1 và đo trực tiếp tổng chệch
   lượng-tử-hoá + lấy mẫu của pipeline hiện tại. Rẻ, và nó biến "sàn nhiễu" từ suy đoán thành số.
2. **Quyết định estimand.** Giữ AW không làm mịn thì phải chấp nhận `N^(−1/(T+1))` và nói thẳng
   trong bài rằng chứng nhận là về solver. Chuyển sang `AW^(σ)` thì được `n^(−1/2)` với chệch O(σ).
   Đây là chỗ quyết định bài báo nói về cái gì.
3. **Tính lại gap comonotone bằng (5.3)** trong họ Gauss và đối chiếu với các số đã đo.
4. **Kiểm bề rộng lưới**: chuẩn hoá giá đỡ rồi so δ hiện dùng với `Δ_N = N^(−1/(T+1))`.
5. **Kiểm nested Sinkhorn bằng Acciaio Thm 2.4** thay vì chỉ bằng oracle tiny.
6. **Trích Kršek–Pammer** trước mọi phát biểu về tính mới của cơ chế chứng nhận.

## Điều lượt đọc này KHÔNG thiết lập

- Chưa đọc Kirui–Pflug–Pichler (không OA).
- Chưa chạy đối thủ nào; **không có tuyên bố tốc độ hay SOTA**.
- Chưa quét backward citation; tính đầy đủ literature vẫn chưa đạt.
- Các số của Cao và cộng sự về thực nghiệm chưa được tái lập ở đây.
- Trích xuất có cấu trúc do mô hình thực hiện; các khẳng định **chịu lực** ở trên đã được đối
  chiếu ngược văn bản gốc, nhưng các chi tiết phụ trong tài liệu này thì chưa từng dòng một.
