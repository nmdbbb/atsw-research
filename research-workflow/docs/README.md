# Tài liệu dự án

## Tài liệu hiện hành

| Cần biết | Nguồn duy nhất |
|---|---|
| Bài toán, phạm vi và kết quả phải bàn giao | [SCOPE.md](SCOPE.md) |
| Định nghĩa, kết quả domain và prior art | [KNOWLEDGE.md](KNOWLEDGE.md) |
| Toán và thuật toán của candidate | [METHOD.md](METHOD.md) |
| Claim đã có bằng chứng, kết quả đo và giới hạn | [EVIDENCE.md](EVIDENCE.md) |
| Protocol, baseline và chuẩn bị công cụ | [BENCHMARKS.md](BENCHMARKS.md) |
| Lựa chọn đầu tư, điều phối, review và phục hồi | [WORKFLOW.md](../WORKFLOW.md) |
| Task, kế hoạch và rủi ro đang thực hiện | [Checkpoint](../status.orchestrator.json) |

Đọc scope và bằng chứng để đánh giá dự án; đọc knowledge/method cho nội dung kỹ
thuật. Agent bắt đầu ở [START_HERE.md](../START_HERE.md). Các trang dùng tên ổn
định và được cập nhật tại đúng chủ đề; không tạo briefing theo phiên hoặc hậu tố
phiên bản làm một nguồn hiện hành khác.

## Nguồn máy đọc và bằng chứng

| Vị trí | Vai trò |
|---|---|
| objective.json, ledger/contract.json | Hợp đồng khóa; SCOPE diễn giải cùng nội dung. |
| ledger/contracts/, contract_revision_*.json, SCOPE_REVISION_*.md | Hồ sơ phê duyệt, không phải nhiều scope cùng hiệu lực. |
| research/theory/, runs/, ledger/inbox/, ledger/preregistered/ | Proof, review, diagnostics, preregistration và raw results. |
| research/sota/ | Source notes, audit và manifest công cụ; kiến thức hiện hành ở KNOWLEDGE/BENCHMARKS. |
| research/workflows/, docs/archive/ | Hồ sơ đánh giá và hướng dẫn vận hành đã lưu trữ. |
| BRIEFING_*, PROJECT_REVIEW_*, HANDOVER.md, DECISION_*, status.json | Snapshot quyết định/trạng thái; không dùng làm next action. |
| inputs/, third_party/, .cache/ | Nguồn nhập/upstream; README đi kèm mô tả nguồn đó, không quản trị dự án. |

Giữ proof/review/run đóng băng tại đường dẫn gốc để hash và trích dẫn còn kiểm
được. [Catalog](catalog.json) phân loại Markdown thuộc dự án theo vai trò và
tài liệu hiện hành tương ứng. Hồ sơ lịch sử không tự là hướng dẫn thực thi.
Lựa chọn user và amendment còn hiệu lực vẫn ràng buộc theo hợp đồng và reference
trong checkpoint.
Source import và deck có vòng đời riêng.

## Quy ước biên tập

Tài liệu chuyên đề viết kết luận hiện hành, định nghĩa, điều kiện áp dụng, bảng
so sánh và nguồn. Fact định lượng có evidence; theorem có giả thiết và đúng
target. Correction phản ánh bằng phát biểu đúng trong mục liên quan, provenance
ở evidence/Git. Giữ lịch sử khi đó là dữ liệu nghiên cứu cần kiểm tra, không
kể lại hội thoại hoặc biện minh quyết định.

Task, quota, số commit và hành trình từng phiên nằm trong checkpoint. Mức đạt
delivery và kết quả có ý nghĩa nằm ở EVIDENCE, không sao chép vào mọi entrypoint.
