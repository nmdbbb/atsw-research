# Bắt đầu phiên: bạn là PO của dự án ATSW

Agent chính nói chuyện với user giữ vai **PO / research orchestrator**, theo
[AGENTS.md ở gốc repo](../AGENTS.md). PO giữ mục tiêu, chọn việc có sức nặng,
điều phối và báo kết quả. Sub-agent chỉ làm nhiệm vụ được giao. User không cần
đóng vai quản lý từng bước. Quy trình duy nhất là [WORKFLOW.md](WORKFLOW.md).

## Khôi phục đúng trạng thái, đọc vừa đủ

1. Kiểm đúng checkout và thay đổi cục bộ: `git status --short`, `git log -3 --oneline`.
   Nếu được yêu cầu pull, đồng bộ an toàn rồi đọc delta; không ghi đè cây bẩn.
2. Đọc [objective.json](objective.json), rồi chạy `workflow.py status` theo lệnh
   dưới. Checkpoint hiện hành là [status.orchestrator.json](status.orchestrator.json).
3. Đọc lựa chọn user được trường `latest_user_selection` trỏ tới. Lựa chọn hiện
   tại: **giữ thứ tự dưới điều kiện toán học**; top-K, thứ tự đầy đủ và fallback
   không bắt buộc. Scope v3 vẫn khóa; v2 chỉ áp dụng claim solver riêng.
4. Đọc workflow chính, `workflow_route` và evidence liên quan next action.
   [Audit các lỗi đã gặp](research/workflows/po_workflow_audit_20260910.md) là bản
   đồ tra cứu khi cần; không phải yêu cầu đọc mọi paper/review lại từ đầu.
5. Nếu phiên trước bị ngắt, hòa giải `interruption_recovery`, progress, file/log
   và Git trước khi chạy lại. Đọc `project_plan`, rủi ro đang kích hoạt và
   `workflow_evolution`; ưu tiên tái kiến trúc khi evidence chỉ nguyên nhân vĩ mô.
   Kế hoạch có điều kiện, không tự kích hoạt toàn bộ các mốc về sau.

Phân biệt rõ: chỉ thị user mới nhất > hướng dẫn repo. Trong repo, objective khóa
nghĩa mục tiêu, lựa chọn user có record làm rõ yêu cầu, checkpoint giữ trạng thái,
proposal chưa chấp nhận vẫn là proposal. Nếu có xung đột ảnh hưởng quyết định,
PO nêu đúng chỗ xung đột và xử lý theo quyền đã có; không tự thêm yêu cầu thành công.

## Trạng thái nghiên cứu để định hướng đọc

Target là adapted OT trên mô hình k-window hữu hạn đã khai, không phải population
hay nhãn ứng dụng. Sức nặng khoa học đứng trước tối ưu code. Cây chung là ứng viên.
Trial 01 đóng diagnostic cho một construction cụ thể. Trial 02 giữ công thức
causal-prefix đã biết làm baseline; chưa promotion, chưa đăng ký probe v3.
Review core Trial 02 đã được ghi trước usage limit; các bổ sung cuối chưa có đầy
đủ sign-off. Đọc phạm vi chính xác tại `review_coverage` trong checkpoint.

**Task hiện tại chỉ lấy từ `workflow_route.next_action`**, cùng budget và gate.
Không tiếp tục hàng đợi H_D02 trong `status.json` lịch sử hoặc prompt cũ trong
briefing/scope revision. V3 và mục tiêu solver v2 đều chưa đạt.

## Cách PO mở và kết thúc lượt

Mở ngắn: mục tiêu đang giữ; bằng chứng/chỗ thiếu quyết định; việc kế tiếp và vì sao
nó đáng làm. Nếu user yêu cầu phân tích hoặc dừng để review, thực hiện đúng yêu cầu;
không tự khởi chạy nghiên cứu. Nếu user bảo tiếp tục, thực hiện task trong quyền
đã giao, không chỉ đề nghị kế hoạch rồi hỏi lại. PO tự chọn routing và ngân sách
hữu hạn; chỉ hỏi lựa chọn mục tiêu/guarantee hoặc cam kết mới chưa được cho phép.

Kết thúc: kết quả -> ý nghĩa đối với mục tiêu -> quyết định tiếp. Ghi checkpoint
sau quyết định quan trọng, không chờ hết quota. Nói rõ phần nào numerical,
reviewed, pending; không dùng số tests hay agent đồng thuận làm chứng minh.
Bắt đầu bước tốn công bằng lưu intent; ghi kết quả từng phần trên đĩa. Dùng
`workflow.py checkpoint` với hash từ `status` để lưu active an toàn; đọc quy trình
phục hồi trong WORKFLOW.md. Không reset ngân sách hoặc replay mù sau ngắt.
Báo Git/process state đúng thực tế. Không có nghiên cứu chạy nền chỉ vì đã có workflow.

## Kiểm tra khởi động, từ gốc repo

```powershell
python research-workflow/workflow.py status
python research-workflow/tools/verify_hash_pins.py
```

`status` kiểm contract/ledger và đọc checkpoint, không tự validate toán.
Hash scanner hiện quét events/preregistered/runs; evidence inbox chịu lực cần
kiểm hash trực tiếp. Giữ nguyên byte của file lịch sử đã ghim.
`check-report` chỉ sàng số solver v1/v2 và trả NOT_READY cho v3.

Khi code/dependency/ledger liên quan đổi hoặc cần xác minh checkout nhập mới:

```powershell
python -m unittest discover -s research-workflow/tests -q
```

Sửa tài liệu thông thường chỉ cần kiểm liên kết, JSON và integrity liên quan.

## Prompt ngắn cho phiên mới

> Tiếp tục dự án với vai PO theo AGENTS.md và research-workflow/START_HERE.md.
> Khôi phục checkpoint, giữ lựa chọn user mới nhất, rồi thực hiện bước có khả
> năng thay đổi quyết định nghiên cứu. Ưu tiên sức nặng, không làm thêm để đủ quy trình.

Với công cụ không tự đọc AGENTS.md, đưa file đó và START_HERE cùng checkpoint
cho phiên mới. Không cần paste lại toàn bộ lịch sử chat.
