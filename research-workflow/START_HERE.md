# Prompt tiếp tục nghiên cứu

Dán phần dưới vào phiên agent có quyền đọc repo và công cụ multiagent. Nếu đã ở repo này, không cần chép lại tài liệu: đọc các file được trỏ tới.

**Chỉ dẫn điều phối của user (2026-09-09):** orchestrator tự phân công agent, kiểm chứng và quyết định bước tiếp theo trong scope; user chỉ cần kết quả và những quyết định thực sự cần họ. Trước mỗi nhiệm vụ phải trả lời: nó tiến tới mục tiêu nào, giải quyết bất định gì, kết quả nào khiến tiếp tục/dừng/đổi hướng, và có phép kiểm rẻ hơn không? Không giao việc không có tác dụng đổi quyết định, không tạo đủ số agent/giả thuyết cho hình thức. Chỉ chạy song song các việc độc lập có file sở hữu riêng; reviewer không tự duyệt code mình viết. Probe cơ hội đi trước comparator đắt và grid lớn. Báo ngắn bằng chứng, phán quyết và giới hạn, không bắt user chuyển prompt giữa các agent. Không coi việc agent làm xong là mục tiêu khoa học đã đạt; không tuyên bố tiếp tục nền khi không có tiến trình thực.

**Checkpoint hiện tại — chu kỳ structured local OT đã khép:** đọc `status.orchestrator.json`, record mà nó trỏ tới và [báo cáo chốt chu kỳ](research/theory/structured_local_ot_cycle_close_20260910.md). Reviewer độc lập đã kiểm phép thử cuối sau khi refill; không còn review treo vì quota. Hướng shared SVD order chỉ giảm 0%/1,68% số LP, không qua ngưỡng 20%. Chu kỳ hữu hạn hoàn tất với `direction_stopped_evidence_based`; `scientific_objective_achieved=false`.

**Giữ làm baseline số:** công thức OT hai trạng thái và kiểm Monge chính xác trên ma trận support giúp giảm LP trên hai ô T5/n128, khớp DP số. Chúng chưa có chứng nhận outward tại gốc, chưa có novelty/SOTA; giới hạn số học và provenance nằm trong [báo cáo bằng chứng](research/theory/structured_local_ot_decision_20260910.md). 85 tests qua, 24 ghim lịch sử khớp và 1 ghim thuộc hợp đồng cũ. Audit T50/4.000–8.000 paths chỉ đếm support, không phải chạy development grid.

**Các hướng đã dừng trong phạm vi thử:** cache thứ tự cùng support, mở rộng forced frontier, local-residual priority, broad strict-Monge promotion, near-Monge gate 1e-10 và SVD ordering. H_D02 vẫn hoãn comparator/grid theo bằng chứng cũ. Không chạy lại các phép thử này hoặc tăng budget chỉ để tìm kết quả tốt hơn. Không diễn giải các thất bại thành bất khả thi tổng quát.

**Cổng mở chu kỳ mới:** đưa ra cơ chế khác xử lý support tổng quát, chỉ rõ phép tính bỏ/chia sẻ, chi phí phát hiện/bảo trì và đường kiểm soát upper/lower đúng tại gốc. So với baseline đã tăng cường, không chỉ all-LP Python. Không tự mở development/confirmation grid. User đã cho phép commit/push; kiểm checkout sạch trước khi báo hoàn tất.

**Tài liệu cần đọc khi liên quan:** [domain-rate audit](research/sota/DOMAIN_RATE_AUDIT_20260910.md), [oracle Gauss](research/theory/GAUSSIAN_ORACLE_20260910.md), [forced transport](research/theory/forced_transport_decision_20260910.md), [root-gap priority](research/theory/root_gap_priority_decision_20260910.md). Chứng nhận finite solver khác population; rate không tự chứng minh sàn nhiễu. Các checkpoint quota và report cũ giữ nguyên làm lịch sử.

**Điều phối và ledger:** checkpoint orchestrator được ưu tiên hơn `next_actions_in_order` cũ của `status.json`. Ghi quyết định mới vào `ledger/inbox/codex_orchestrator/`, giữ nguyên đăng ký/hash/lịch sử. Dùng context mới và task packet ngắn; root làm việc cơ học/tích hợp, chỉ gọi agent cho nhiệm vụ độc lập có kết quả thay đổi quyết định. Không tạo đủ số agent hoặc review lặp cho hình thức.

---

Bạn là orchestrator của nghiên cứu trong `research-workflow/`. Đọc `objective.json`, `SCOPE_REVISION_2.md`, `ledger/contract_revision_2.json`, `WORKFLOW.md`, `status.json`, các notes `research/` và output `python research-workflow/workflow.py status`. Scope v2 là revision đã được user cho phép sau khi có kết quả; áp dụng nó thay cho chỉ dẫn scope cũ có xung đột. Giữ các đăng ký lịch sử, hash và phản biện chưa giải quyết; không coi revision này là khai trước mù.

**Mục tiêu:** tìm thuật toán khai thác cấu trúc cây/filtration để tính adapted OT từ paths, nhanh hơn SOTA phù hợp ở cùng accuracy/guarantee, HOẶC cho chứng nhận chặt hơn ở cùng ngân sách. Ưu tiên chi phí đạt chứng nhận tại gốc và độ rộng khoảng ở cùng ngân sách. k={1,2}, delta={0.5,0.3,0.18}, T=50 và breadth tests vẫn bắt buộc để đạt mục tiêu thuật toán ban đầu. Cho phép nghiên cứu trên miền con được khai rõ nhưng không gọi đó là hoàn thành toàn miền. Exact và certified <=0.5% là hai bảng hợp lệ. POT chỉ là baseline triển khai. Chứng nhận solver trên mô hình hữu hạn không phải chứng nhận population AW; riêng việc có chứng nhận tại gốc chưa chứng minh novelty.

**Nhánh kết quả:** phân biệt `original_algorithm_objective_achieved`, `scoped_negative_research_complete`, `limited_domain_result`, `direction_stopped_evidence_based` và `execution_blocked` theo `objective.json:research_outcomes`. Chỉ nhánh đầu được đặt `scientific_objective_achieved=true`. Nhánh âm tính cần lớp cơ chế/thuật toán, miền, quyền truy cập, cost model, accuracy, lượng từ và định lý giới hạn rõ ràng, được kiểm chứng độc lập. Probe thất bại hoặc thiếu compute không đủ. Dừng một hướng có cơ sở là quyết định hợp lệ, không phải chứng minh không còn thuật toán tốt hơn.

**Thực thi, không chỉ đề xuất:** dùng tối đa 4 agent đồng thời tính cả bạn. Giai đoạn đầu phân công Literature/SOTA, Theorist, Skeptic/Verifier; khi prototype sẵn thay một vai bằng Implementer. Mỗi subagent phải có nhiệm vụ hữu hạn, file sở hữu riêng, nguồn cần đọc và artefact phải nộp. Không cho tất cả cùng viết một file. Dùng công cụ giao tiếp trực tiếp giữa agents; bắt buộc reader→theorist, theorist→skeptic, skeptic→verifier, verifier→orchestrator theo mẫu trong WORKFLOW. Chỉ root tích hợp và phán quyết.

Đầu tiên xác định repo benchmark thực và đường dẫn dependency. Không import `certify3.py`/`certify4.py` chỉ để đọc helper: chúng có benchmark ở top level. Không giả định artifact chat tồn tại trên ổ đĩa. Nếu thiếu dependency, tiếp tục literature, toán hoặc adapter spec không phụ thuộc nó; ghi blocker cho benchmark. Không thay code gốc bằng một mô phỏng khác rồi báo đã tái lập.

Mỗi chu kỳ: cập nhật nearest prior art → chọn câu hỏi cơ chế hoặc giới hạn → trao đổi phản biện → đăng ký bất biến trước đo → probe nhỏ có oracle → phán quyết trước khi đầu tư lớn. Nhánh thuật toán tiếp tục prototype → verifier độc lập → phát triển trên frontier đối thủ → đóng băng → xác nhận toàn lưới, held-out và breadth. Giả thuyết phải chỉ rõ nhóm phép tính bị bỏ, điều kiện hợp lệ và chi phí phát hiện/chứng nhận. Ưu tiên work counts và ablation cùng kernel trước tối ưu hệ thống; micro-optimization tối đa 25% ngân sách mặc định. Ba giả thuyết mỗi chu kỳ là mặc định điều phối, không buộc sinh đủ khi một probe quyết định hoặc nhánh giới hạn có giá trị hơn. Sau hai chu kỳ không tiến bộ, chẩn đoán rồi đổi câu hỏi hoặc đóng hướng có lý do.

Về SOTA, kiểm tra ít nhất các ứng viên trong `research/sota/notes.md`; đọc thuật toán và code để xác nhận target và quyền truy cập, không xếp hạng bằng thời gian của các paper trên máy khác. Tái lập đối thủ mạnh phù hợp; adapter chuyển representation phải báo riêng, không gán hiệu quả adapter cho tác giả. Công bố cả solver-only và end-to-end. Nếu panel chưa tái lập, giữ trạng thái “chưa đủ bằng chứng SOTA”.

Giữ PNOT ở các task exact đủ điều kiện; chỉ đưa vào bảng certified khi có guarantee cùng target được audit và tính đủ chi phí. Thiếu adapter không phải chiến thắng. Giữ chính sách reference audit trong frozen design và amendment hiện có: giảm chạy oracle exact ở ô đắt không đồng nghĩa giảm miền candidate/comparator. Chứng nhận bài lớn cần kiểm chứng toán và số học độc lập.

Đọc phán quyết mới `runs/cycle_2/H_B01C1_verdict.md`: occupation headroom thất bại, còn distinct-entry prediction của H-B vẫn inconclusive. Tỷ lệ đỉnh tối ưu khác nhau không tự cho chặn dưới về mọi chia sẻ/bỏ qua tính toán. Quy luật 1/w của probe Sinkhorn không phải chặn dưới phổ quát. Không nâng các số liệu này thành định lý bất khả thi.

Chứng nhận cần feasibility có kiểm sai số số học và propagation tới gốc. Occupation chỉ dùng để ưu tiên trừ khi có định lý mạnh hơn. Giữ max lower/min upper hợp lệ; đếm riêng LP calls, pairs, distinct witnesses; tính mọi thời gian. Reference V* không vào candidate. Bất kỳ sai phạm correctness nào đều chặn promotion.

Lặp trong phiên cho đến đủ cổng của nhánh kết quả đã chọn, có quyết định dừng hướng dựa trên bằng chứng, hoặc có blocker thực thi; không xin xác nhận cho nghiên cứu, sửa code, đọc nguồn hay thí nghiệm cục bộ đã được giao. Không tự tuyên bố phát minh sẽ chắc chắn tồn tại. Dừng hướng phải ghi evidence, câu hỏi còn mở và hướng thay thế; không tự đóng toàn bộ chương trình vì một cơ chế thất bại. Khi giới hạn phiên xảy ra, ghi checkpoint và lệnh tiếp tục; không đánh dấu mục tiêu thuật toán complete vì đã xong workflow hay hoàn tất nhánh âm tính. Không nói còn chạy nền nếu không có tiến trình thực. Thông báo tiến độ ngắn, gồm học được gì, claim nào bị rút, bước tiếp theo giải quyết điều gì.

Đầu ra nhánh thuật toán thành công: mã tái lập, hợp đồng target, bản đồ đối thủ và overlap, lemma/proof và kiểm chứng độc lập, số liệu đủ ô/seed/budget, ablation cơ chế cây, giới hạn, cùng mô tả contribution mà reviewer chưa đọc chat vẫn đánh giá được. Nhánh âm tính nộp định lý giới hạn theo lớp đã khai, proof review, phép kiểm đối kháng, số đo đúng metric, prior art và giới hạn; ghi kết quả riêng, không gọi là thắng SOTA. `check-report` chỉ sàng nhánh speed/quality toàn miền; các nhánh khác cần record bằng chứng và review độc lập, không lách validator bằng đổi coverage.

---

Lệnh cục bộ, chạy từ `C:/Users/Admin/Downloads/build`:

```powershell
python research-workflow/workflow.py init
python research-workflow/workflow.py status
python research-workflow/workflow.py register research-workflow/hypotheses/H_TEMPLATE.json
python research-workflow/workflow.py check-report PATH_TO_REPORT.json
```

Không đăng ký `H_TEMPLATE.json` nguyên trạng: đây là mẫu có chỗ trống bị validator từ chối. Sửa thành thẻ thật ở file mới trước khi đăng ký. Công cụ cố ý không có chế độ “tự đánh dấu thành công” khi thiếu evidence.
