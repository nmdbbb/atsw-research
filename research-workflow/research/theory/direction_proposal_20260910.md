# Bản lập luận chọn hướng nghiên cứu — sau khi đóng pha prototype

Ngày: 2026-09-10. Trạng thái: **đề xuất chờ user xác nhận trước khi tiêu compute**.
Tài liệu này trả lời bốn câu hỏi cổng do đánh giá điều phối 2026-09-10 đặt ra,
và chọn một trong ba nhánh: cơ chế thuật toán mới / kết quả miền con / định lý giới hạn.
Không đăng ký giả thuyết, không chạy probe, không mở grid trong tài liệu này.

## Tóm tắt quyết định

**Chọn nhánh cơ chế thuật toán mới: tinh chỉnh đồng thời upper/lower theo quy trách
gap chính xác tại gốc (gap-guided joint refinement), với đường chứng nhận
outward-rounded là nghĩa vụ đi kèm.** Hai nhánh còn lại giữ làm fallback có điều
kiện kích hoạt rõ (mục 7). Trước mọi đầu tư lớn, hai probe rẻ có gate đóng băng
phải qua (mục 6); trượt gate nào thì dừng theo đúng tiêu chí đã khai ở câu hỏi 4.

## Câu hỏi 1 — Claim mới dự kiến là gì, khác phương pháp gần nhất ở đâu?

**Claim dự kiến (dạng khả kiểm):** trên mô hình k-window hữu hạn của adapted OT,
tồn tại thuật toán anytime duy trì đồng thời (a) một policy khả thi cho chặn trên
và (b) một Bellman subsolution cho chặn dưới, dùng đẳng thức quy trách chính xác

```
U_pi(root) - L_root = sum_n mu_n(pi) * (<pi_n, c_n + L_child> - L_n)
```

(đã kiểm đại số độc lập trong `root_gap_priority_decision_20260910.md`) để chọn
node tinh chỉnh, và tại node được chọn **cải cả hai phía**: giải lại bài OT địa
phương trên continuation upper hiện hành (policy improvement — máy móc đã được
verify pointwise-nonincrease trong `upper_policy_verification_20260910.md`) VÀ
cập nhật dual/subsolution địa phương cho lower. Kết quả công bố ở một trong hai
dạng: (i) đạt khoảng chứng nhận tại gốc <=0.5% với ít local solve hoàn chỉnh hơn
DP đầy đủ trên baseline dispatch đã tăng cường, hoặc (ii) khoảng chứng nhận hẹp
hơn ở cùng tổng ngân sách. Phiên bản nghiêm ngặt yêu cầu số học outward-rounded
để khoảng tại gốc là certificate thật (nghĩa vụ W1, mục 5).

**Khác gì các phương pháp gần nhất:**

| Prior art gần nhất | Cái họ đã có | Cái claim này thêm |
|---|---|---|
| PNOT (Bontorno–Hou 2025) | Exact DP toàn lớp, prefix tree | Không anytime, không interval, không chọn lọc node; k=2/random root ngoài hỗ trợ stock |
| Pichler–Weinhardt 2021 (nested Sinkhorn) | Duality lồng nhau + bất đẳng thức xấp xỉ entropy | Certificate của họ là toàn cục theo epsilon, không định vị theo node, không có vòng tinh chỉnh chọn lọc |
| Bayraktar–Han (FVI) | Học continuation value từ lịch sử được chọn | Thống kê, không certificate; không kiểm soát sai số tại gốc |
| Calo et al. (occupancy coupling) | Occupancy formulation, warm start | Setting discounted stationary; không có kết quả finite-horizon certified |
| BRTDP / interval iteration (MDP) | Duy trì hai chặn giá trị, tinh chỉnh theo occupancy×gap | Bài toán con là min trên tập hành động hữu hạn; ở đây bài toán con là OT trên polytope coupling với ràng buộc marginal — chặn trên đòi policy coupling khả thi, chặn dưới đòi dual địa phương; chuyển giao không tự động |
| Các nhánh đã chết trong repo | Lower-only priority trên upper cố định; occupation-reachability envelope | Điểm khác quyết định: tinh chỉnh **cả policy (upper) lẫn dual (lower)** tại cùng node rồi quy trách lại; đối tượng bị nghẽn (upper vượt 5.178%) được xử lý trực tiếp thay vì giữ cố định |

Ba việc trong bảng trên (dòng cuối) là bằng chứng nội bộ rằng biến thể lower-only
KHÔNG đủ: `root_gap_priority_decision` đo được đổi score chỉ dịch -0.16% gap.
Không cái nào trong bảng bị coi là đã bị đánh bại; đây là bản đồ overlap để kiểm
tra novelty, chưa phải kết luận novelty. Nghĩa vụ W2 (mục 5) phải đóng vòng trích
dẫn quanh các cụm từ "anytime / bounded / interval" + "nested distance / bicausal
OT" trước khi viết claim vào hợp đồng.

## Câu hỏi 2 — Cấu trúc cần khai thác có hiện diện đáng kể ở miền mục tiêu không?

Cấu trúc cần khai thác là **độ tập trung của gap tại gốc vào ít cặp node**, không
phải sparsity support hay tỷ lệ binary/Monge (những thứ đã đo là co lại mạnh ở
T=50: binary nonforced 71.13%→27.62% ô mịn, 24.31%→10.23% ô thô; census
`structured_local_ot_decision_20260910.md`).

Bằng chứng hiện có (T5/n128, `root_gap_decomposition`):

- Ô mịn: 89.40% gap nằm trong 16 cặp nonforced lớn nhất; 17 cặp phủ 90%; riêng
  cặp chuyển tiếp t=0 (mass 1) chiếm 40.23%.
- Ô thô: tập trung yếu hơn — 37.23% trong top-16, cần 114 cặp cho 90%.

**Trả lời trung thực: hiện diện rõ ở quy mô nhỏ, CHƯA đo ở miền mục tiêu
T=50 / 4,000–8,000 paths.** Đây đúng là loại ngoại suy mà census T50 vừa bác cho
sparsity — nên không được giả định. Vì vậy probe quyết định số 1 (mục 6) là đo
chính phổ tập trung này ở quy mô mục tiêu, trước khi xây bất kỳ vòng tinh chỉnh
nào. Điểm thuận lợi: đẳng thức quy trách chỉ cần MỘT policy khả thi + MỘT
subsolution, không cần DP đầy đủ; forced fraction ở T50 đã đo (15.10% thô /
39.19% mịn) cho phần forced được xử lý rẻ.

## Câu hỏi 3 — Nó giảm phần chi phí nào sau khi baseline đã được tối ưu hợp lý?

Đơn vị chi phí bị nhắm: **số local OT solve hoàn chỉnh (LP calls thật, đếm theo
`dispatch.rejected`) và số entry continuation được vật chất hóa**, so với DP đầy
đủ dùng chính baseline đã tăng cường (binary-direct + strict support-Monge
dispatch — không phải all-LP Python). Cơ chế giảm: thay quét đủ mọi cặp ở mọi
layer bằng (a) sweep khởi tạo rẻ cho policy/subsolution thô, (b) vòng lặp
{quy trách → chọn top node → giải lại local OT hai phía → truyền lại}. Chi phí
phát hiện/duy trì được tính đủ: cache kỳ vọng policy theo layer đã đo cỡ 0.43s
và 5,080 edge-read trên ô mịn T5 (`residual_priority_screen`) — rẻ so với LP;
overhead outward rounding sẽ được đo riêng trong W1 và tính vào mọi so sánh.

Điều kiện để tiết kiệm là thật: phổ quy trách phải tập trung (câu hỏi 2) và
policy improvement tại ít node phải kéo được phần upper vượt 5.178% xuống — nếu
phần vượt này trải đều trên nhiều node thì cơ chế chết (đưa vào tiêu chí dừng).

## Câu hỏi 4 — Bằng chứng nào sẽ khiến ta dừng hướng đó?

Gate đóng băng trước khi chạy, mỗi gate trượt là một quyết định dừng có hồ sơ:

1. **Gap khuếch tán ở miền mục tiêu:** probe P1 (T50, path counts đóng băng) cho
   thấy cần >20% số cặp nonforced để phủ 90% gap trên CẢ hai ô đại diện, và
   không có tập trung early-horizon bù lại → cơ chế không có headroom; dừng.
2. **Upper không sửa được cục bộ:** trên hai case lưu trữ T5, giải lại local OT
   tại top-16 node theo quy trách không giảm phần upper-vượt-tham-chiếu xuống
   dưới 2% (từ 5.178%) ở ô mịn → nghẽn upper không phải hiện tượng cục bộ; dừng
   biến thể chọn lọc, ghi lại như ràng buộc cấu trúc.
3. **Vòng lặp không thắng ngân sách khớp:** ở cùng số LP call với DP-baseline
   tăng cường, khoảng (numerical trước, certified sau W1) không hẹp hơn ít nhất
   25% tương đối trên cả hai case nhỏ → không đầu tư grid; dừng hoặc quay lại
   thiết kế.
4. **Chứng nhận nghiêm ngặt nuốt hết lợi ích:** sau W1, khoảng outward-rounded
   rộng hơn 2 lần khoảng float64 cùng ngân sách → claim certified chết; chỉ còn
   claim numerical, phải hạ cấp hợp đồng hoặc dừng.
5. **Novelty đổ:** W2 tìm thấy phương pháp anytime certified cho nested
   distance với cùng cơ chế chọn lọc → chuyển thành so sánh/cải tiến có trích
   dẫn hoặc dừng claim.

Thất bại các gate này KHÔNG được diễn giải thành "không tồn tại thuật toán cấu
trúc" — chúng chỉ đóng lớp cơ chế "bounded refinement điều khiển bởi quy trách
occupation-residual" trên miền thử.

## 5. Hai nghĩa vụ đi kèm (không phải hướng riêng)

- **W1 — số học chứng nhận tại gốc:** normalization, bảo toàn khối lượng nhỏ,
  feasibility repair (hướng rational/Fraction đã có tiền lệ trong support-Monge
  predicate), truyền sai số outward tới gốc. Bị chặn bởi: chưa nhánh nào được
  gọi "certified" khi thiếu nó (giới hạn đã ghi trong mọi record cycle_2).
  Phạm vi bounded: làm trên đúng pipeline policy-eval + shared-dual hiện có.
- **W2 — đóng vòng prior art:** quét trích dẫn tiến/lùi quanh 6 công trình nền
  (pipeline OpenAlex đã dựng trong `BASELINES.md`) với từ khóa bổ sung:
  anytime bounds, interval iteration, bounded value iteration, prioritized
  sweeping, dual bounds nested distance. Nộp bảng overlap trước khi đăng ký
  hợp đồng claim.

## 6. Hai probe quyết định, rẻ, chưa chạy (cần đăng ký trước)

- **P1 — census quy trách gap ở quy mô mục tiêu:** T=50, seed/shift development,
  path counts đóng băng 4,000–8,000, hai ô đại diện (thô AR1-k1-δ0.5-squared;
  mịn nonlinear-k2-δ0.18-absolute). Xây policy khả thi rẻ (dispatch baseline +
  NW/greedy fallback) + subsolution forced-node + một lượt shared-dual; tính
  phổ quy trách; KHÔNG mở development grid, KHÔNG chạm confirmation seeds.
  Ngân sách trần và số LP call phải khai trước khi chạy. Đầu ra: đường cong
  "số cặp cần cho X% gap" + phân bố theo t.
- **P2 — micro-screen tinh chỉnh hai phía trên case lưu trữ:** hai case T5/n128
  cũ, so ba arm cùng kernel: (a) DP-baseline tăng cường, (b) lower-only priority
  (control đã có), (c) joint refinement tại top-K node quy trách. Gate chính là
  tiêu chí dừng 2 và 3 ở trên. Toàn bộ trên máy này, giây-cấp như các screen cũ.

Thứ tự: P1 trước (nó rẻ hơn thiết kế vòng lặp đầy đủ và có thể giết hướng ngay);
P2 chỉ chạy nếu P1 qua gate tập trung.

## 7. Hai nhánh không chọn bây giờ và điều kiện kích hoạt

- **Kết quả miền con (Gaussian/AR1 với oracle Gunasingam–Wong):** oracle đã
  dựng và review (`GAUSSIAN_ORACLE_20260910.md`); discrepancy finite/population
  15–27x trên một seed là câu hỏi estimand thú vị nhưng mỏng về thống kê, và
  không dùng máy móc solver mới. Kích hoạt nếu: hướng chính dừng ở gate 1–3 VÀ
  user muốn một kết quả công bố được ngắn hạn về tách bias sampling/quantization/
  window trên họ Gaussian (khi đó cần thiết kế đo đủ seed, khai miền rõ).
- **Định lý giới hạn:** hiện chưa có lớp thuật toán được định nghĩa đủ chặt để
  phát biểu định lý (bài học H_B01C1: relaxation lạc quan còn cho 87–96% entries
  lọt ngân sách — không có target bất khả thi rõ). Kích hoạt nếu: hướng chính
  chết ở gate 1 hoặc 2 — chính các gate đó khi trượt sẽ ĐỊNH NGHĨA lớp cơ chế
  (selection-rule-based bounded refinement với quy trách occupation-residual)
  và cung cấp phản ví dụ định lượng làm hạt giống cho phát biểu giới hạn.

## 8. Điều tài liệu này không làm

Không đăng ký giả thuyết, không sửa code solver, không chạy OT, không mở grid,
không nâng số liệu cũ thành kết quả mới, không tuyên bố novelty. Mọi con số
trích từ các record bất biến trong `research/theory/` và `runs/cycle_2/`.
Bước tiếp theo thuộc về user: xác nhận (hoặc bác) lựa chọn hướng; chỉ sau đó
mới đăng ký P1 làm thẻ giả thuyết có gate đóng băng và chạy.
