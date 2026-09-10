# Sửa đổi hướng nghiên cứu theo phản hồi advisor — nén phần tương tác của continuation

Ngày: 2026-09-10. Thay thế trạng thái của
[direction_proposal_20260910.md](direction_proposal_20260910.md) (giữ nguyên
làm lịch sử). Hai claim văn liệu trong phản hồi advisor đã được audit mức định
lý: [MOULOS_BACKHOFF_AUDIT_20260910.md](../sota/MOULOS_BACKHOFF_AUDIT_20260910.md)
— cả hai đứng vững. Chưa chạy thí nghiệm, chưa đổi scope, chưa đăng ký giả thuyết.

## Quyết định

1. **Hạ joint refinement** từ hướng chính xuống **công cụ thực thi + nền so
   sánh**. Lý do đã kiểm chứng: Moulos 2020 làm cầu nối bicausal OT = MDP
   (Bellman, VI, điều kiện tối ưu) thành prior art tường minh — headline
   "transfer BRTDP" không còn đủ khoảng cách. Bằng chứng gap concentration và
   5 stop-gate của đề xuất cũ vẫn hợp lệ, tái sử dụng khi cơ chế chính cần
   vòng thực thi.
2. **Hướng chính mới: một vòng lý thuyết CÓ GIỚI HẠN về nén phần tương tác
   của continuation với chứng nhận cho mô hình gốc** — chạy TRƯỚC W1, P1 và
   mọi grid. Câu hỏi trung tâm: các continuation có thể khác nhau ở mọi nút,
   nhưng phần thực sự ảnh hưởng lựa chọn coupling có đơn giản hơn nhiều không?
3. **Câu hỏi estimand tạm đóng ngã ba cũ:** Backhoff Thm 6.1 (Markov, d=1:
   N^(−1/3), số mũ không phụ thuộc T) gỡ lập luận "phải smoothing"; không
   chuyển smooth AW lúc này. Ranh giới chuyển giao (compact support, Lipschitz
   kernel, khớp đối tượng) ghi trong audit.

## Task card vòng lý thuyết (ba đầu ra bắt buộc, theo phản hồi advisor)

### Đầu ra 1 — Phát biểu toán học ứng viên

Nền chuẩn (không claim mới, dùng làm khung):

- Tách V_t(x,y) = f_t(x) + g_t(y) + R_t(x,y). Với marginals cố định, phần
  additive f⊕g dịch giá trị OT đúng ⟨p,f⟩+⟨q,g⟩ và không đổi argmin; bài OT
  địa phương chỉ phụ thuộc c_t + (P⊗Q)[R_{t+1}].
- Giá trị OT là 1-Lipschitz theo ‖·‖∞ của cost khi marginals cố định; toán tử
  Bellman lùi nonexpansive theo ‖·‖∞ ⇒ nếu thay R_{t+1} bằng biểu diễn R̃ có
  sai số chứng nhận ε_{t+1} thì sai số gốc truyền cộng tính: e_t ≤ ε_t + e_{t+1}
  (cùng dạng envelope H-A nhưng CHỈ trên phần tương tác, sau khi loại phần một
  phía — đây là điểm khác đã khai với H-A và H-B).

Đại lượng cấu trúc ứng viên (chọn một, đóng băng trước khi đo): (a) hạng thấp
của R_t trên support; (b) sai số truncation τ-bước: R_t^{(τ)} tính với
V_{t+τ} thay bằng xấp xỉ additive tốt nhất, đo ‖R_t − R_t^{(τ)}‖∞ theo τ.

**Mục tiêu lemma (phần mở thật sự):** điều kiện Dobrushin-kiểu trên HAI kernel
có kiểm soát được span/suy giảm của R_t cho bài hữu hạn KHÔNG discount, kernel
không thuần nhất? Trở ngại đã biết phải xử lý tường minh: (i) Moulos Lemma 3 ở
dạng stationary/vô hạn — không tự chuyển; (ii) coupling trong Bellman bị TỐI ƯU
HÓA, không cố định — span contraction qua phép min không tự động; (iii) mixing
của TỪNG quá trình chưa chứng minh chặn cần thiết cho Bellman tối ưu (phản
biện số 1 của advisor).

### Đầu ra 2 — Phản ví dụ đối kháng (nghĩa vụ, không phải tùy chọn)

1. Marginals mixing nhanh nhưng phần tương tác bền — kiểm xem điều kiện ứng
   viên có bỏ sót thay đổi coupling.
2. Họ nonlinear bậc hai: hai k-window cùng tọa độ hiện tại, luật bước sau
   ngược nhau (tái dùng thiết kế probe của thẻ H-A) — cấm lấy AR1 làm bằng
   chứng thay thế.
3. Bảng chỉ rõ **entry/cặp nào được bỏ**: "nhìn trước ít bước hơn" đơn thuần
   có thể tăng tính lặp — DP hiện tại đã dùng chung bảng theo thời gian.

### Đầu ra 3 — Bảng công việc

Thuật toán dự kiến bỏ/chia sẻ phép tính nào; chi phí phát hiện + duy trì +
chứng nhận đại lượng cấu trúc; so với baseline dispatch đã tăng cường
(binary-direct + strict support-Monge), không phải all-LP.

### Điều kiện KHÔNG cấp ngân sách triển khai (đóng băng, từ phản hồi advisor)

- Chỉ chứng minh được trường hợp Gauss (đã có nghiệm đóng).
- Kiểm điều kiện cấu trúc đòi biết toàn bộ continuation (chi phí kiểm = chi
  phí tính).
- Chặn quá rộng để dùng ở mục tiêu 0.5%.

## Các hướng giữ trạng thái

- **Hướng đối chiếu:** information-complexity của chứng nhận — giữ; nếu vòng
  nén thất bại, phản ví dụ của nó nuôi phát biểu giới hạn. Cấm biến probe
  thất bại thành "bài báo âm tính" tự động.
- **Hướng dự phòng nặng-lý-thuyết:** sai số + phân bổ ngân sách cho pipeline
  k-window (window bias × quantization × solver error) — chưa chọn vì đổi
  trọng tâm sang estimator track; định lý Markov Backhoff là NỀN BẮT BUỘC nếu
  mở, không phải claim.
- **Không ưu tiên (lý do trong phản hồi advisor, đã đồng thuận):** joint
  refinement score mới; warm-start/cache/tối ưu hệ thống; Gauss/comonotone làm
  claim trung tâm (KR near-optimality: 2 định danh ứng viên đã pin trong
  audit, chưa đọc); chuyển smooth AW ngay.

## Bước tiếp theo

Vòng lý thuyết trên là việc giấy-và-review: root thực hiện Đầu ra 1+3, một
reviewer độc lập tấn công bằng Đầu ra 2 (đúng mẫu theorist→skeptic của
WORKFLOW). Không mở thí nghiệm cho tới khi task card này có phán quyết.
