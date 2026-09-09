# Scope v2 — thông báo cho phiên workflow đang chạy

User đã cho phép sửa scope sau khi thảo luận các kết quả hiện có, ngày 2026-09-09. Đây là thay đổi định hướng có khai báo sau dữ liệu, không phải khai trước mù. Hợp đồng hiện tại là `tree-adapted-ot-sota-v2` trong `objective.json`; record chuyển hợp đồng là `ledger/contract_revision_2.json`. Bản cũ và bản mới được lưu tại `ledger/contracts/`; đăng ký, frozen design và kết quả cũ giữ nguyên hash.

## Quyết định áp dụng

1. Ưu tiên chi phí để đạt chứng nhận hợp lệ tại gốc hoặc độ rộng chứng nhận ở cùng tổng ngân sách. Trước tối ưu hệ thống, dùng probe quyết định, work counts và ablation với cùng kernel để tìm cơ chế có lợi. Chỉ có root certificate, tách finite/population hoặc timing đầy đủ chưa chứng minh novelty.
2. Giữ mục tiêu thuật toán toàn miền với k={1,2}, delta={0.5,0.3,0.18}, T=50 và breadth. Cho phép kết quả miền con với điều kiện và giới hạn được khai rõ. Nếu chọn miền sau thất bại, công bố việc đó và dùng held-out mới; không gọi là hoàn thành toàn miền.
3. Thêm nhánh `scoped_negative_research_complete`: phải có lớp thuật toán/cơ chế, miền mô hình, quyền truy cập, cost model, accuracy, lượng từ và định lý giới hạn rõ ràng; proof review độc lập, kiểm đối kháng, prior art và artefact tái lập. Không cần thuật toán mới cho nhánh này, nhưng probe thất bại chưa đủ để hoàn tất nó.
4. Cho phép `direction_stopped_evidence_based`: dừng đầu tư vào một hướng với lý do, evidence, giới hạn và hướng thay thế. Phân biệt với định lý bất khả thi, thiếu compute, và hoàn thành mục tiêu thuật toán. Chỉ `original_algorithm_objective_achieved` được đặt `scientific_objective_achieved=true`.
5. Giữ PNOT ở bảng exact trên task đủ điều kiện. Certified comparison cần guarantee cùng target được audit và tính đủ chi phí adapter/chứng nhận. Thiếu adapter không phải thắng đối thủ. Không so số end-to-end của mình với số solver-only công bố trên máy khác để xếp hạng.
6. Giữ `frozen_design.json:reference_audit_policy` và amendment hiện có. Giới hạn tham chiếu exact không phải giới hạn miền candidate/comparator. Bài lớn phải có audit toán và số học cho chứng nhận, không dựa riêng vào khớp oracle nhỏ. Không tự chạy thêm hàng chục giờ tham chiếu chỉ để thay thế certificate audit; probe nhỏ đi trước confirmation lớn.
7. Giữ đúng cấp bằng chứng: tỷ lệ đỉnh tối ưu phân biệt không suy ra mọi chia sẻ/bỏ qua đều bất khả thi; các probe liên quan chưa chắc độc lập; quy luật 1/w của một probe Sinkhorn chưa là chặn dưới phổ quát. Đọc `runs/cycle_2/H_B01C1_verdict.md`: occupation headroom thất bại, distinct-entry prediction vẫn inconclusive. Không triển khai full H-B với envelope hiện tại khi chưa có cận tốt hơn hoặc oracle đúng metric.

## Tiếp nhận trong phiên đang hoạt động

- Ở điểm checkpoint an toàn kế tiếp, đọc lại hợp đồng và hướng dẫn mới; không xoá kết quả đang có hoặc sửa metadata của run đã đóng băng. Nếu run đang hoạt động, lưu nó dưới đúng manifest/contract ban đầu, ghi run đó đã được khởi động trước revision. Không thay tiêu chí dừng giữa run để tạo claim xác nhận mới.
- Chạy `python research-workflow/workflow.py status`. Khóa hợp đồng đã được cập nhật có record và event; không khởi tạo lại hoặc sửa hash các preregistration cũ. Nếu dùng evidence cũ cho nghiên cứu v2, dẫn nguồn và khai nó là dữ liệu đã biết. Đăng ký mới dùng objective hash mới; trước khi dùng thẻ cũ cho claim v2 cần record nối phạm vi/tiêu chí, không ghi đè thẻ cũ.
- Tự cập nhật checkpoint hiện tại sau khi đọc revision: ghi revision đã tiếp nhận, nhánh nghiên cứu đang chọn, original objective còn đạt/chưa đạt theo bằng chứng, và việc kế tiếp. Phiên sửa scope không ghi đè `status.json` để tránh mất công việc của phiên đang chạy.
- Nếu H_C01 vẫn đang review, tiếp tục phần theorem/prior-art/probe còn hợp lệ; đánh giá nó theo ưu tiên chứng nhận v2. Không huỷ chỉ vì đổi scope và không tự nâng thành kết quả âm tính. Chỉ mở benchmark lớn sau khi probe nhỏ và review biện minh được chi phí.
- `workflow.py check-report` vẫn là bộ sàng toàn miền cho speed/quality; không tự kiểm nhánh âm tính hoặc miền con. Ghi outcome riêng với claim, phạm vi, evidence/hash và review độc lập theo `WORKFLOW.md` mục 6. Không sửa validator để tự công nhận nhánh mới.

## Prompt để dán vào phiên đang chạy

```text
Tôi đã cho phép sửa scope của research-workflow; bản v2 đã được cập nhật trực tiếp trong workspace. Ở checkpoint an toàn kế tiếp, đọc research-workflow/SCOPE_REVISION_2.md, objective.json, ledger/contract_revision_2.json, START_HERE.md và WORKFLOW.md, rồi chạy python research-workflow/workflow.py status. Áp dụng scope v2 thay cho chỉ dẫn scope cũ có xung đột; không xin xác nhận lại.

Ưu tiên chi phí/độ chặt chứng nhận tại gốc, probe cơ chế nhỏ, work counts và ablation cùng kernel trước tối ưu hệ thống. Cho phép kết quả miền con khai rõ và nhánh kết quả âm tính cho một lớp cơ chế được định nghĩa, nhưng không gọi chúng là hoàn thành mục tiêu thuật toán toàn miền. Chỉ nhánh đạt đủ cổng thuật toán ban đầu được đặt scientific_objective_achieved=true. Dừng một hướng dựa trên evidence là hợp lệ; không biến probe thất bại, tỷ lệ đỉnh tối ưu phân biệt hay quy luật 1/w đo được thành định lý bất khả thi.

Giữ PNOT ở các task exact đủ điều kiện và giữ chính sách reference audit hiện có. Không bỏ k=2/delta=0.18/T=50 khỏi claim toàn miền, không chạy thêm reference exact đắt chỉ vì hiểu nhầm cổng chứng nhận. Đọc phán quyết H_B01C1 mới: occupation headroom thất bại nhưng distinct-entry prediction vẫn inconclusive.

Bảo toàn các run, manifest, preregistration và hash lịch sử; không đổi tiêu chí giữa run. Tự cập nhật checkpoint với revision đã tiếp nhận, nhánh hiện tại và việc tiếp theo. Nếu H_C01 còn đang review, tiếp tục phần công việc hợp lệ dưới ưu tiên mới. Báo ngắn những gì thay đổi trong kế hoạch, rồi tiếp tục thực thi; không khởi động lại workflow từ đầu.
```
