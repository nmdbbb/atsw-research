# Audit mức định lý: Moulos 2020 và Backhoff et al. — hai claim của phản hồi advisor

Ngày: 2026-09-10. Toàn văn tải từ arXiv, trích và đối chiếu nguyên văn bằng tìm
chuỗi trên PDF. Cả hai claim của phản hồi advisor **đứng vững**, với các ranh
giới giả thiết ghi dưới đây.

## 1. Moulos, *Bicausal OT for Markov Chains via Dynamic Programming* (arXiv:2010.06831, 10 trang)

**Setting đã xác minh:** state space S **hữu hạn**, hai Markov chain **thuần
nhất thời gian** (kernel dừng P, P'), horizon **vô hạn**, chi phí chiết khấu
β∈(0,1) hoặc β=1. Policy = bicausal coupling, phân rã thành chuỗi phân phối
điều kiện — đúng cầu nối MDP.

**Theorem 1 (nguyên văn đã đối chiếu):** W_bc là nghiệm của phương trình điểm
bất động V = T(V) (duy nhất khi β<1; khi β=1: nghiệm không âm bất kỳ ≥ W_bc,
và W_bc là nghiệm cực tiểu). Value iteration từ V₀=0: hội tụ tuyến tính
‖V_k−W_bc‖∞ ≤ β^k‖W_bc‖∞ khi β<1; **đơn điệu V_k ↑ W_bc khi β=1** (tức mỗi
iterate là chặn dưới hợp lệ). Tồn tại optimal Markovian coupling; điều kiện
cần-đủ tối ưu T_Q(W_bc)=W_bc. Chứng minh dựa Bertsekas 1977.

**Lemma 3 (nguyên văn):** với hệ số Doeblin–Dobrushin
δ(P) = max_{x,x'} ‖P(x,·)−P(x',·)‖_TV < 1 thì ‖W_bc‖∞ ≤ 1/(1−δ(P))
(qua Wasserstein coupling, hitting time trội bởi Geometric(1−δ)).

**Không có trong bài (kiểm bằng đọc toàn văn):** mô hình hữu hạn chiều thời
gian không thuần nhất từ dữ liệu (k-window empirical); duy trì ĐỒNG THỜI hai
chặn; tinh chỉnh chọn lọc/anytime; giải một phần bài OT địa phương; chứng nhận
số học; đơn vị chi phí LP/entry.

**Hệ quả cho novelty map:** cầu nối "bicausal OT = MDP + Bellman + VI" là
**prior art tường minh từ 2020** — phải trích trong mọi phát biểu liên quan.
Phần headline "transfer BRTDP sang OT" của đề xuất joint refinement yếu đi
đúng như advisor nhận định; phần còn trống thu hẹp về: anytime hai chặn có
chứng nhận, tinh chỉnh chọn lọc, trên mô hình hữu hạn không discount từ dữ
liệu. Điều này ủng hộ quyết định hạ joint refinement xuống vai công cụ thực
thi/so sánh.

**Điểm dùng được ngay cho lý thuyết:** (i) VI đơn điệu từ dưới ở β=1 nhất quán
với máy móc Bellman-subsolution hiện có; (ii) Lemma 3 là mẫu lập luận
"Dobrushin ⇒ chặn giá trị" — nhưng ở dạng stationary/vô hạn/chiết khấu; chuyển
sang finite-horizon undiscounted với kernel không thuần nhất và coupling được
TỐI ƯU HÓA (không cố định) là đúng phần việc mở của vòng lý thuyết mới.

## 2. Backhoff–Bartl–Beiglböck–Wiesel, *Estimating processes in adapted Wasserstein distance* (arXiv:2002.07261, 23 trang)

**Assumption 1.4 (nguyên văn):** quá trình trên ([0,1]^d)^T — **support
compact** — với disintegration kernel **Lipschitz** theo Wasserstein.

**Theorem 1.5 (tổng quát):** E[AW(µ,µ̂^N)] ≤ C·N^(−1/(T+1)) cho d=1 — khớp
đúng họ rate mà DOMAIN_RATE_AUDIT đã kiểm qua Mirmominov–Wiesel.

**Theorem 6.1 (Markov, nguyên văn):** nếu µ Markov + Assumption 1.4 thì
E[AW(µ,µ̂^N)] ≤ C·N^(−1/3) (d=1), N^(−1/4)log N (d=2), N^(−1/(2d)) (d≥3),
kèm concentration P[AW ≥ C·rate+ε] ≤ 2T·exp(−cNε²). **Remark 6.2 nguyên văn:
"the dependence of the rate on T disappears"** — hằng số C, c vẫn phụ thuộc
d, T, Lipschitz constants. Cơ chế: chỉ cần phân hoạch bước cuối, không phân
hoạch toàn bộ quá khứ.

**Hệ quả cho câu hỏi estimand:** lập luận "phải chuyển smoothing vì
N^(−1/(T+1))" bị gỡ Ở DẠNG PHÁT BIỂU ĐÓ. Ngã ba estimand giờ là ba nhánh:
(i) unsmoothed tổng quát: N^(−1/(T+1)); (ii) unsmoothed + estimator khớp
Markov: N^(−1/3) ở d=1; (iii) smoothed AW^σ: n^(−1/2) + bias O(σ).

**Ranh giới KHÔNG được bỏ qua khi áp vào pipeline:** (a) support compact —
generators của repo là Gaussian innovation không bị chặn (cùng vấn đề đã ghi
với Mirmominov; cần truncation argument hoặc khai rõ); (b) Lipschitz kernel
phải kiểm cho cả họ nonlinear bậc hai; (c) đối tượng phải khớp: adapted
empirical measure của bài ≠ `build_window_model` pooling hiện tại
(DOMAIN_RATE_AUDIT điểm 2 — lượng tử hóa có thể phá Markov); (d) hằng số phụ
thuộc T chưa định lượng — không được đọc thành "sai số nhỏ ở T=50".

## 3. KR near-optimality: định danh ứng viên, CHƯA audit

Nguồn advisor dẫn là thông báo seminar (Vienna 2022). Quét OpenAlex pin được
hai ứng viên gần nhất: *The Knothe–Rosenblatt distance and its induced
topology* (arXiv:2312.16515, 2023) và *Adapted Wasserstein distance between
the laws of SDEs* (arXiv:2209.03243, 2022). Chưa đọc toàn văn — giữ nguyên
trạng thái "chưa dùng như định lý đã audit"; đọc khi fallback Gauss/comonotone
kích hoạt.

## 4. Giới hạn của audit này

Chỉ đối chiếu các phát biểu chịu lực nêu trên bằng tìm chuỗi trên PDF; không
kiểm từng dòng chứng minh của hai bài; không chạy thí nghiệm. PDF lưu tại
workspace phiên làm việc, tải lại được từ arXiv theo id.
