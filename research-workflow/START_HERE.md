# Bắt đầu phiên

Agent chính làm PO theo [AGENTS.md](../AGENTS.md).

1. Kiểm checkout và thay đổi cục bộ bằng `git status --short`.
2. Đọc [mục tiêu](docs/SCOPE.md), [hợp đồng](objective.json) và chạy
   `python research-workflow/workflow.py status` từ repo root.
3. Đọc [WORKFLOW.md](WORKFLOW.md), rồi thực hiện `workflow_route.next_action`
   trong [checkpoint hiện hành](status.orchestrator.json), theo yêu cầu user.
   Kiểm reference tại `latest_user_selection` để giữ đúng lựa chọn đã được cấp.
4. Tra [danh mục tài liệu](docs/README.md) cho nội dung liên quan task.
   Nếu bị ngắt, hòa giải disk/log/process/Git trước replay.

Task và kế hoạch chỉ lấy từ checkpoint hiện hành. Các snapshot, briefing,
decision, review và run trong kho bằng chứng không tự khởi động hàng đợi công việc.
