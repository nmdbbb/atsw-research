# Workflow nghiên cứu thuật toán cây — mục tiêu SOTA

**Mở [WORKFLOW.md](WORKFLOW.md) để đọc quy trình đầy đủ; [START_HERE.md](START_HERE.md) để giao cho agent tiếp tục thực thi.** Hợp đồng nằm ở [objective.json](objective.json). Đích là nhanh hơn ở cùng chứng nhận, hoặc chứng nhận chặt hơn ở cùng ngân sách, so với tập đối thủ mạnh phù hợp đã tái lập. POT không đại diện SOTA.

## Lấy gì từ workflow đã có?

| Nguồn sơ cấp đã đọc | Thành phần sử dụng ở đây | Điều cần điều chỉnh cho nghiên cứu toán |
|---|---|---|
| [FunSearch](https://www.nature.com/articles/s41586-023-06924-6) | Bộ đánh giá thực thi được; kho chương trình đa dạng | Cho phép đổi representation/recurrence; không khóa mọi ý tưởng vào skeleton của solver hiện tại |
| [AlphaEvolve, §2](https://arxiv.org/html/2506.13131v1) | Nhiều mức trừu tượng, đánh giá theo tầng, lưu nhánh có ưu thế khác nhau | Giữ riêng bất biến correctness và mục tiêu SOTA; không để score bù một ô thất bại |
| [AI Co-Scientist, §3](https://arxiv.org/html/2502.18864v1) | Agent chuyên vai trao đổi giả thuyết, phản biện, sửa và tổng hợp | Phán quyết toán dựa trên proof/oracle; xếp hạng bằng ngôn ngữ chỉ chọn thứ nên thử |
| [AI Scientist-v2](https://arxiv.org/html/2504.08066v1) | Quản lý nhánh thí nghiệm và lưu kết quả trung gian | Kiểm độc lập quan hệ giữa ý tưởng, implementation và số đo; không dùng tự-review để công bố thành công |
| [OpenEvolve](https://github.com/algorithmicsuperintelligence/openevolve) | Tham khảo cách lưu quần thể, chia nhóm tìm kiếm và phản hồi artefact | Chỉ ứng viên cho vòng tối ưu bên trong; chưa cần cài framework trước khi adapter và bộ kiểm đúng |

Đây là thiết kế kết hợp của dự án, chưa có nguồn nào chứng minh workflow này chắc chắn tìm được thuật toán adapted OT vượt SOTA. Review chi tiết và đối chiếu workflow cũ ở [research/workflows/notes.md](research/workflows/notes.md).

## Một vòng thực tế

```text
Đọc nguồn và code SOTA → nêu cơ chế bỏ phép tính → phản biện chéo
       ↑                                             ↓
đổi câu hỏi theo thất bại ← probe khai trước ← giải quyết phản biện
       ↑                                             ↓
so toàn phạm vi + held-out ← verifier độc lập ← prototype sống sót
```

Bốn slot: orchestrator + ba vai theo pha (literature, lý thuyết, phản biện/kiểm chứng, triển khai). Reader phải gửi điều kiện của paper cho theorist; skeptic phải phản hồi một chỗ có thể sai; implementer trả code/test; verifier đối chiếu raw output; root giữ quyết định. Có nhánh được viết lại representation, không bắt tất cả lai từ champion.

Thất bại được lưu thành phản ví dụ hoặc câu hỏi tiếp theo. “Hai chu kỳ chưa tiến bộ” dẫn đến đổi tầng/cơ chế, không giảm phạm vi hay độ chính xác. Dừng thành công cần hiệu quả SOTA, cơ chế cây có bằng chứng và đối chiếu đóng góp. Một tiến trình/phiên kết thúc chỉ tạo checkpoint; không đồng nghĩa mục tiêu khoa học đã đạt.

## Đã làm và trạng thái hiện tại

- Ba agent đã đọc literature thuật toán/workflow và trao đổi kết quả; bản đồ SOTA gồm PNOT, adapted/nested Sinkhorn và các reformulation liên quan, chưa có xếp hạng tái lập.
- Đã đọc repo nén và workflow cũ. Giữ nguồn gốc ở `inputs/atsw_repo`, không sửa lịch sử.
- Đã tái lập lỗi target của builder k=2: ví dụ có giá trị đúng 4/3 nhưng bản cũ trả 0. [Bằng chứng chạy lại được](research/sota/check_imported_root.py).
- Có công cụ khóa objective, đăng ký giả thuyết trước chạy và sàng báo cáo đủ phạm vi. Tests là fixture tổng hợp, không phải số thắng SOTA.
- Đã chạy smoke nhỏ k=1 qua mã archive và kiểm khoảng với DP tham chiếu; chỉ xác nhận tích hợp số học ở T=2, không chứng nhận toàn grid. [Output](runs/cycle_0/archive_smoke.json).
- Có [ba thẻ cơ chế](research/theory/notes.md): quotient theo tương lai, refinement theo khối, occupancy-flow hữu hạn. Đây là giả thuyết chưa đo, không phải ba biến thể SVD.
- Vòng H_A01 đã chạy: exact future classes đúng trên fixture nhưng trượt ngưỡng giảm công việc ở 4/6 ô k=2. Xem [phán quyết](runs/cycle_1/H_A01_verdict.md). Cơ chế được giữ như thành phần phụ, không còn là hướng hiệu năng độc lập.
- PNOT C++ gốc đã qua audit số nhỏ ở k=1 với deterministic root; [review độc lập](research/sota/pnot_result_review.md) tái lập đủ 14 lời gọi nhỏ. PNOT stock không hỗ trợ target k=2 tùy ý hoặc random initial law, và output hiện không đủ certificate cho bảng certified.
- Chưa chạy benchmark SOTA hoặc tìm được thuật toán mới. Bước kế tiếp cụ thể nằm trong [status.json](status.json).

## Lệnh

Từ `C:/Users/Admin/Downloads/build`:

```powershell
python research-workflow/workflow.py init
python research-workflow/workflow.py status
python -m unittest discover -s research-workflow/tests -v
python research-workflow/research/sota/check_imported_root.py
python research-workflow/adapters/archive_smoke.py
```

`check_imported_root.py` exit 0 nghĩa là tái lập được lỗi; JSON vẫn ghi target gate FAIL. Không suy luận pass khoa học từ exit code.

`workflow.py` không tự gọi LLM hoặc tự chạy nền. Nó hỗ trợ orchestrator trong phiên multiagent và giữ checkpoint cho phiên sau. [Định dạng báo cáo](REPORT_FORMAT.md) nói rõ phần máy kiểm được và phần reviewer còn phải xác nhận.
