# Định dạng báo cáo và giới hạn của bộ kiểm

`workflow.py check-report FILE.json` chỉ sàng **điều kiện số cần thiết**. Output tốt nhất là `NUMERICAL_SCREEN_PASSED_REVIEW_REQUIRED`; không có nhãn “đã vượt SOTA”. Tính đúng của witness, equivalence target, panel SOTA, thống kê và tính mới cần review độc lập có artefact. Việc một file tồn tại và khớp hash không chứng minh nội dung đúng.

Top-level report:

```json
{
  "objective_sha256": "hash từ ledger/contract.json",
  "route": "speed",
  "split": "confirmation",
  "comparison_issues": [],
  "eligible_competitors": ["method_A_pinned", "method_B_pinned"],
  "frontier_review": {"path": "runs/ID/frontier_review.md", "sha256": "..."},
  "independent_certificate_review": {"path": "runs/ID/certificate_review.json", "sha256": "..."},
  "frozen_experiment_manifest": {"path": "runs/ID/manifest.json", "sha256": "..."},
  "rows": []
}
```

Đây là mô tả schema, không phải report hoàn chỉnh. `rows` phải có mọi task/seed cần thiết. Một row:

```json
{
  "task": {"cost": "squared_distance", "process": "ar1", "k": 1, "delta": 0.5, "T": 50},
  "seed": 123,
  "candidate": {"lower": 100.0, "upper": 100.2, "total_seconds": [0.8, 0.81, 0.79, 0.8, 0.8]},
  "competitors": [
    {"id": "method_A_pinned", "lower": 100.0, "upper": 100.2, "total_seconds": [1.0, 1.01, 0.99, 1.0, 1.0]},
    {"id": "method_B_pinned", "lower": 100.0, "upper": 100.0, "total_seconds": [2.0, 2.01, 1.99, 2.0, 2.0]}
  ]
}
```

Các số ở mẫu là **giả lập để giải thích schema**, không phải kết quả. Code chọn đối thủ nhanh nhất đã đạt ε, không lấy đối thủ yếu hơn làm mẫu số. Với route `quality`, mỗi row thêm `total_budget_seconds`, mọi phép chạy phải nằm trong budget; so gap với đối thủ có khoảng chặt nhất. Exact gap=0 không thể bị cải thiện bằng gap dương.

Mặc định bảng confirmation phủ 24 task = 2 cost × 2 process × 6 ô, ít nhất 5 seed/task và 5 lần đo thời gian/seed. Cùng seed ID trong một task chỉ đếm một lần. Một ô thiếu, một khoảng đảo, NaN, khoảng không giao nhau cho cùng target, hoặc một regression đều chặn numerical screen. Thời gian là tổng pipeline; bộ kiểm không thể biết có giấu preprocessing hay không nếu không audit raw trace.

Các giới hạn cố ý:

- Không tính hoặc kiểm interval witness từ các số L/U. Verifier riêng phải dựng output này từ artefact candidate trên cùng model hash.
- Không tự kết luận ý nghĩa thống kê từ median. Review phải dùng dữ liệu ghép cặp, nhiễu thời gian, CI đồng thời và lịch sử thử.
- Screen đơn giản yêu cầu cùng panel eligible đầy đủ ở mọi task. Phương pháp chỉ phù hợp một phần phải có báo cáo frontier phân tầng đã review; đừng loại nó bằng đổi danh sách cho tiện.
- Timeout, L=0<U và chứng nhận tuyệt đối cần một protocol riêng đã khai trước; screen này trả NOT_READY thay vì tự diễn giải có lợi.
- Manifest cần ghim code/data/adapter/checker/environment hashes, units, input access, root/filtration, cost, shift protocol, splits, tuning budget, certificate arithmetic, cold/amortized và authors/reviewers. Screen chỉ kiểm file manifest tồn tại/khớp hash; review nội dung vẫn bắt buộc.

Candidate không được quyền sửa objective, evaluator, manifest đã đóng băng hoặc reference. Hash chain hỗ trợ phát hiện sửa vô ý, không phải sandbox bảo mật hay chữ ký. Các agent cùng quyền filesystem thì holdout là phân tách theo quy trình; không được gọi là bí mật mật mã.
