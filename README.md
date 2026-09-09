# atsw-research

Hai phần công việc quanh adapted optimal transport và thuật toán cây.

## [`research-workflow/`](research-workflow/)

Workflow nghiên cứu thuật toán cây hướng tới SOTA: hợp đồng mục tiêu, đăng ký giả thuyết trước khi chạy, ledger trao đổi giữa các agent, và log của từng chu kỳ.

- [`WORKFLOW.md`](research-workflow/WORKFLOW.md) — quy trình đầy đủ
- [`START_HERE.md`](research-workflow/START_HERE.md) — điểm vào để agent tiếp tục thực thi
- [`objective.json`](research-workflow/objective.json) — hợp đồng mục tiêu đã khóa
- [`inputs/atsw_repo/`](research-workflow/inputs/atsw_repo/) — repo nguồn giữ nguyên gốc, không sửa

## [`deck-source/`](deck-source/)

Nguồn của deck ATSW 55 slide. Chạy `python deck-source/build.py` từ thư mục gốc để ghép thành `atsw-deck-de-hieu.html` — một file HTML tự chứa, mở trực tiếp bằng trình duyệt, không cần mạng.

Chi tiết ở [`deck-source/README.md`](deck-source/README.md).

## Trạng thái

Đây là nghiên cứu đang tiến hành. Các kết quả trong `runs/` và `hypotheses/` là log của quá trình, không phải kết luận đã được kiểm chứng độc lập. Điều kiện dừng và phạm vi hiệu lực của từng phán quyết được ghi trong chính file phán quyết đó.
