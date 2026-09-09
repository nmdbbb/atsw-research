# H_A01 — phán quyết sau phép thử đã khai trước

Trạng thái: **giả thuyết hiệu năng độc lập bị bác ở development; bổ đề exact và cơ chế dùng chung vẫn sống như một thành phần phụ**.

Tiêu chí đã khoá yêu cầu giảm ít nhất 25% số Bellman value requests ở **mỗi** ô k=2, lấy trung vị hai seed cho cả hai họ quá trình. Kết quả:

| process | δ=0.5 | δ=0.3 | δ=0.18 |
|---|---:|---:|---:|
| AR(1) | 14.844% | 22.931% | 27.219% |
| second-order nonmonotone | 14.811% | 23.172% | 27.934% |

Bốn trong sáu ô trượt ngưỡng. Vì vậy exact future-class quotient **không được nâng thành hướng hiệu năng chính** trên phạm vi khai trước. Nó có thể được dùng bên trong cơ chế khác nếu chi phí và lợi ích của tổ hợp được khai lại.

Phần sống sót: fixture exact cho giá trị đúng ở cả cost bình phương và trị tuyệt đối; trường hợp duplicate giảm logical Bellman requests từ 12 xuống 3. Negative control gộp terminal mà bỏ output trả sai 0 thay vì 2, và test k=2 giữ được thông tin mà k=1 đánh mất.

Giới hạn: đây là work-count trên 256 paths, không phải runtime, certificate hay SOTA benchmark. Các request có kích thước LP khác nhau; chi phí dựng chữ ký, root coupling và arithmetic certificate chưa được giải quyết. Approximate quotient bằng TV chưa được thử. [Review độc lập](../../research/theory/quotient_review_v1.md) chấp nhận đúng phán quyết hẹp này và bác mọi diễn giải phổ quát hơn.

Nguồn số: `H_A01_future_classes.json`; đăng ký bất biến: `ledger/preregistered/H_A01_future_classes.json`.
