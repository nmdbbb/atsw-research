# Mục tiêu nghiên cứu

Xây dựng **biểu diễn tái sử dụng của quá trình ngẫu nhiên** để chứng nhận quan hệ
gần–xa theo adapted optimal transport với tổng chi phí thấp hơn giải transport
riêng cho từng cặp. Đóng góp trung tâm là quan hệ giữa **kích thước biểu diễn,
độ sắc của bảo đảm và chi phí quyết định**.

## Bài toán

Cho các luật quá trình với filtration được khai rõ trên horizon hữu hạn. Trong
mỗi task, cố định cost, đơn vị, chuẩn hóa và định nghĩa

\[
D(P,Q)=\inf_{\pi\in\Pi_{bc}(P,Q)}\mathbb E_\pi\!\left[\sum_t c_t(X_t,Y_t)\right].
\]

Khi cost tương ứng, đại lượng này là \(AW_p^p\). Với query \(Q\), thuật toán cần
khẳng định đúng các quan hệ \(D(Q,A)<D(Q,B)\) dưới giả thiết kiểm được. Các trường
hợp chưa phân biệt được trả `unresolved`. Top-K, full ranking và fallback là
mở rộng tùy chọn. Tương quan thực nghiệm là số đo phụ.

Một certificate có thể dùng \(U(Q,A)<L(Q,B)\). Giá trị nghiên cứu nằm ở cách
tính thông tin đủ sắc với công nhỏ, cùng điều kiện đảm bảo việc đó khả thi.

## Phạm vi

- Chọn lớp quá trình có ý nghĩa bằng cấu trúc toán học hoặc nhu cầu ứng dụng;
  khai rõ các trường hợp được phủ. Không chọn miền chỉ từ những cặp mà bound
  tình cờ phân biệt được.
- Kiến trúc đang đầu tư là cây trạng thái điều kiện dùng chung. Có thể nâng cấp
  hoặc thay kiến trúc theo mục tiêu. AW1, số hữu tỉ và k-window là phạm vi của
  implementation hiện tại, không giới hạn toàn bộ đề tài.
- Bước thực thi đầu tiên dùng adapted OT trên mô hình hữu hạn. Certificate của
  mô hình dựng từ paths áp dụng cho mô hình đó. Claim population cần một cầu
  nối xấp xỉ/thống kê riêng và lựa chọn estimand rõ ràng.
- Khai chế độ dữ liệu: observed paths, supplied model hay generator oracle.
  Tính đủ chi phí dựng mô hình, nhãn, calibration và truy cập oracle.
- Scenario reduction, đánh giá mô hình sinh và retrieval là các workload có
  thể chọn. Không yêu cầu phục vụ đồng thời mọi ứng dụng, p, cost hoặc filtration.

## Tiêu chí bàn giao

| ID | Kết quả | Điều kiện nghiệm thu |
|---|---|---|
| D1 | Claim và miền có sức nặng | Lớp quá trình rõ; đối chiếu nearest theorem/algorithm; đóng góp còn lại và phép bác bỏ quyết định; review độc lập. |
| D2 | Bảo đảm định lượng | Proof trên đúng target/filtration, tới root; điều kiện kiểm được có tính công; quan hệ độ sắc hoặc distortion với độ phức tạp biểu diễn/cấu trúc quá trình trên một họ không tầm thường. |
| D3 | Thuật toán tái sử dụng | Implementation khớp định nghĩa; chỉ rõ conditional work tránh/chia sẻ được; tính build, index, query, update, certification, memory và số học; phân tích điểm hòa vốn. |
| D4 | Bằng chứng so sánh | Probe khai trước và confirmation held-out; coverage không tầm thường; lợi ích tổng chi phí đáng kể ở cùng guarantee/coverage; đối thủ mạnh, adversarial controls và ablation. |
| D5 | Gói kết quả tái lập | Báo cáo nghiên cứu, code/data/protocol được ghim, bảng claim–evidence và giới hạn; tái lập được các bảng chính. |

Nhánh dương cần đủ D1–D5 trên miền đã khai. Một kết quả âm tính hoàn chỉnh cần
**định lý giới hạn có sức nặng được review độc lập** cho lớp biểu diễn/thuật toán,
access model và domain rõ ràng. Nhánh này vẫn cần D1/D5; thay yêu cầu dương của
D2–D4 bằng theorem, construction đối chứng và bằng chứng độ sắc/phạm vi phù hợp.
Kết quả đó được công bố riêng với việc đạt mục tiêu
thuật toán dương. Thất bại của một construction chỉ đóng construction đó.

## Đánh giá và ưu tiên đầu tư

Đóng băng trước mỗi probe: domain/split, margin và ties, coverage tối thiểu, mức
cải thiện chi phí đáng kể, reference precision, sample size, ngân sách và stop-gate.
Giữ unresolved/near ties trong mẫu số. Báo cold start, query-only, amortized,
fallback nếu dùng, cùng chi phí nhãn và cập nhật. Protocol đầy đủ và baseline
ở [BENCHMARKS.md](BENCHMARKS.md).

Thứ tự ưu tiên: sức nặng khoa học → bảo đảm hữu ích → cơ chế tiết kiệm conditional
work → chi phí/coverage → tối ưu implementation. Dùng diagnostic rẻ để kiểm
conjecture; đầu tư lớn sau khi claim, bằng chứng và đối thủ đủ rõ.

## Tài liệu liên quan

[KNOWLEDGE.md](KNOWLEDGE.md) định nghĩa và prior art;
[METHOD.md](METHOD.md) mô tả candidate;
[EVIDENCE.md](EVIDENCE.md) ghi mức đạt D1–D5.
Hợp đồng máy đọc là [objective.json](../objective.json). Văn bản này diễn giải
cùng hợp đồng; record phê duyệt lưu tại [contract revision](../ledger/contract_revision_4.json).
Mục tiêu solver cũ ≤0.5% là hồ sơ riêng, không bổ sung điều kiện cho bài toán này.
