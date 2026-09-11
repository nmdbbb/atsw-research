# Bằng chứng và giới hạn của kết quả nghiên cứu

Dự án có một candidate cây điều kiện tái sử dụng, với chặn hai phía đúng trên
mô hình hữu hạn đã khai và primitive tree transport thưa chính xác đã được
review. Chưa có kết quả định lượng đủ sức nặng về đánh đổi kích thước biểu diễn,
độ sắc bảo đảm và chi phí; chưa có lợi thế thực nghiệm được xác nhận ở cùng
guarantee/coverage. Theo [hợp đồng](../objective.json), mục tiêu nghiên cứu và
cả năm delivery vẫn chưa hoàn thành trọn vẹn.

## Claim nào hiện được bằng chứng hỗ trợ?

| Claim | Bằng chứng hiện có | Giới hạn |
|---|---|---|
| Cây và probe cho `L≤D≤U` trên finite k-window AW₁ | [Review construction](../research/theory/shared_tree_design_01_review.md) chấp nhận hai induction, pair-min và feature-MST; [verdict](../research/theory/shared_tree_design_01_verdict.json) ghim artifact. | Full window được quan sát, cost tuyệt đối, mô hình hữu tỉ hợp lệ. Chưa có population, squared-cost hoặc arbitrary-float certificate. |
| Virtual tree tính đúng cùng tree-OT với dense traversal | [Kết quả exact](../research/theory/shared_tree_design_01_checks_final.json): 231 edge/root queries bằng nhau; review chứng minh nén đường bảo toàn tổng imbalance. | Tính đúng primitive không chứng minh cây ít méo hoặc thứ tự thường xuyên tách được. |
| Tránh dựng bảng exact conditional OT mọi cặp | Review chấp nhận degree bound và `O(F E_t log(2+N_next))` transport cân cạnh với feature width cố định. | Phải cộng index, graph/MST, probe, đọc input, root và bit complexity; dữ liệu dense vẫn đắt. Một số graph nhỏ đầy đủ. |
| Candidate sử dụng thông tin điều kiện có tác dụng | Reconvergence: lower `3/16` vượt ordinary path OT `1/16`; genuine k2: pair-min khôi phục thứ tự mà singleton bank bỏ sót. [Audit](../research/theory/shared_tree_design_01_audit.json), [review](../research/theory/shared_tree_design_01_review.md). | Thành công genuine k2 riêng nó không chứng minh adapted/ordinary gap: hai khoảng cách trùng nhau ở control đó. |
| Một số thứ tự được chứng nhận | Sáu controls cố định trong bảng dưới, 18 pair intervals chứa exact reference; layer audit kiểm 372 conditional pairs. | Các controls được dùng để sửa thiết kế. Không có held-out coverage, runtime win, break-even, long-horizon usefulness hoặc SOTA. |
| Toàn bộ thuật toán là đóng góp khoa học mới | Chưa có bằng chứng đủ. [Review](../research/theory/shared_tree_design_01_review.md) ghi rõ Bellman lifting, tree-OT, metric domination và lower Lipschitz là thành phần đã biết. | Cần đối chiếu trực tiếp recursive WL/OTM/bisimulation và tree embeddings cho claim cụ thể. |

## Số đo trực tiếp của candidate

Các số dưới là giá trị hữu tỉ chính xác của **ba họ control được chọn, mỗi họ
với hai reconstruction k1/k2**. `D_A=D(Q,A)`, `D_B=D(Q,B)`; khoảng là đầu ra
candidate pair-min, feature-MST, virtual transport. Nguồn chung:
[verdict và các cặp query](../research/theory/shared_tree_design_01_verdict.json),
[kết quả đầy đủ](../research/theory/shared_tree_design_01_checks_final.json).

| Control | `D_A ; D_B` | Khoảng A ; khoảng B | Quyết định được chứng nhận |
|---|---|---|---|
| Divergence–reconvergence, k1 | `3/16 ; 1/2` | `[3/16,5/16] ; [1/2,3/4]` | A gần hơn: `5/16<1/2`. |
| Divergence–reconvergence, k2 | `3/16 ; 1/2` | `[3/16,5/16] ; [1/2,3/4]` | A gần hơn: `5/16<1/2`. |
| Timing thông tin, k1 | `1 ; 2` | `[1,5/2] ; [2,7/2]` | Unresolved dù có thứ tự thật. |
| Timing thông tin, k2 | `2 ; 2` | `[2,3] ; [2,4]` | Unresolved; reference là tie thật. |
| Phụ thuộc bậc hai sau reconstruction k1 | `0 ; 0` | `[0,0] ; [0,0]` | Không khẳng định thứ tự nghiêm; mô hình k1 đã mất phụ thuộc. |
| Phụ thuộc bậc hai, k2 | `2 ; 1` | `[2,2] ; [1,1]` | B gần hơn: `1<2`. |

Mọi lower trong các pair diagnostics này trùng reference là quan sát hữu hạn,
chưa phải tính đầy đủ của probe bank. Thay k2 bằng k1 thay mô hình đích; đó là
ablation về thông tin, không phải certificate cho mô hình k2 ban đầu.

Timing k2 dùng 164 virtual nodes trong 48 queries, so với 447 dense audit nodes,
đồng thời cần 104 index entries và 72 LCA table lookups. Đây là các đơn vị công
khác nhau, không được lấy tỷ số làm speedup. 96 tests của gói candidate tại
[verdict](../research/theory/shared_tree_design_01_verdict.json) là kiểm tra phần
mềm tại artifact đó, không phải kết quả coverage hoặc completion khoa học.

## Các phát hiện giữ lại làm tri thức và đối chứng

Những kết quả dưới xác định nơi một cơ chế đúng, yếu hoặc không đáng đầu tư
trong miền đã kiểm. Chúng không cộng lại thành định lý bất khả thi cho mọi cây
hoặc mọi thuật toán giữ thứ tự.

| Cơ chế / đối chứng | Kết quả có thể dùng | Phạm vi và hàm ý |
|---|---|---|
| Ordinary prefix-tree score | [Trial 01](../research/theory/relational_trial_01_verdict_20260910.md) có phản ví dụ đảo thứ tự và ordinary/bicausal mismatch. | Raw tree score cần cầu nối đúng coupling và numeric cost trước khi dùng cho adapted order. |
| Causal prefix overlap | [Trial 02](../research/theory/relational_trial_02_verdict_20260910.md): `m_h=m_parent·min(p_h,q_h)` cho tree-cost; range upper và marginal lower đều đúng theo lập luận trong packet. 12 kiểm tree-cost và 12 kiểm numeric-cost hữu tỉ; không phân biệt được ba so sánh query temporal đã chọn. | Core overlap thuộc prior art. Review đã xử lý prefix formula/compact aggregation; sign-off cuối cho toàn packet và phần range/marginal implementation còn thiếu. Không kế thừa review từ cây mới. |
| Trọng số trie cố định và numeric geometry | Trial 02: paths `(0,0)` và `(ε,0)` có AW₁=`ε` nhưng unit-prefix score=`4` với mọi `ε>0`. | Bác uniform multiplicative bridge cho chính biểu diễn/trọng số đó; không bác mọi tree metric. |
| Full-state reset chung | [Reset verdict](../research/theory/geometry_condition_screen_01_verdict.json): bound được review và giải được control điều kiện mà bound thô bỏ sót; bốn exact checks trên một họ T6. | Baseline composition có giả thiết reset mạnh; chưa có central novelty hoặc lợi thế comparator. |
| Signed-prefix comparison | [Verdict](../research/theory/signed_prefix_comparison_01_verdict.json): bound đúng; dưới squared cost, lớp candidate khớp hai moment theo thời điểm khiến interval chứa zero, dù ví dụ có thứ tự thật đảo chiều. | Giới hạn của signed construction không điều kiện này; phép so sánh trực tiếp khác vẫn là hướng mở. |
| Triệt tiêu residual chung | [Conditional-offset verdict](../research/theory/conditional_offset_comparison_01_verdict.json): trên lớp location mixture có component quan sát được và residual centered chung, `D=common residual AW₂² + OT(mean paths)`; recognizer kiểm kernel không cần mở mọi paths. | Bảo đảm exact subclass đã review; implementation ranking dùng hai initial components. Hai root transports và 72 edge visits so với 42 reference transports chưa là so sánh thời gian đầy đủ. |
| Sai lệch residual và noise scale | [Robustness verdict](../research/theory/residual_robustness_01_verdict.json): exact gap `2−4σε+ε²`; tolerance residual tuyệt đối bất kỳ có thể đảo naive order khi noise scale đủ lớn. Hai feasible witnesses cho certificate đủ hợp lệ. | Standard metric stability; chưa có scalable witness discovery, robust general coverage hoặc theorem mới về optimizer. |
| Binary và strict support-Monge OT | [Structured-local verdict](../research/theory/structured_local_ot_decision_20260910.md): general LP calls `543→164`, `1067→298` ở hai case T5/n128; bảng khớp reference trong `1e−8`. | Baseline số hữu ích. Predicate exact không sửa floating feasibility/rounding của toàn recurrence; không phải outward certificate hay SOTA. |
| Dense optimal-face reuse | [H_D02](../research/theory/HD02_opportunity_decision.md): 2/383 changed support hits được rescue trong trace đã chọn, tức 0.52%. | Đóng đầu tư implementation đó; không bác nguyên lý optimal-face reuse hoặc cho lower bound mọi solver. |
| Fixed-upper refinement | [Root-gap decision](../research/theory/root_gap_priority_decision_20260910.md): upper cố định riêng nó vượt numerical reference 5.178% tại case mịn. | Lower hoàn hảo cũng không cứu target value 0.5% của case đó. Target cũ không là ngưỡng bắt buộc cho partial order hiện tại. |
| Nén phần tương tác continuation | [Record nhập](../ledger/inbox/codex_orchestrator/theory_round_theorist_20260910.json) chứa đề xuất/kết quả đang chờ independent review. | Parked; không nhận là negative theorem đã kiểm hoặc nền chứng minh của candidate hiện tại. |

## Trạng thái các delivery

Các yêu cầu đầy đủ nằm trong [scope](SCOPE.md); trạng thái dưới đây
đánh giá nội dung đã có, không tính phần trăm hoàn thành từ số file hay tests.

| Delivery | Phần đã có | Phần quyết định còn thiếu |
|---|---|---|
| D1 — Claim và miền có ý nghĩa | Đối tượng adapted order rõ; candidate và nearest-prior-art map có thể kiểm. | Luận điểm trung tâm trên lớp quá trình có tham số, điểm khác nearest theorem và falsifier có sức nặng được review. |
| D2 — Bảo đảm và đánh đổi | Certificate finite AW₁ và sparse primitive đã review; có diagnostics điều kiện. | Kết quả định lượng nối complexity/cấu trúc với độ sắc hoặc distortion và vùng unresolved trên họ không tầm thường. |
| D3 — Thuật toán tái sử dụng | Module, interface, shared trees/probes, virtual transport và operation bounds. | Kế toán đầy đủ, memory/update regime và bằng chứng khi nào amortization có lợi. |
| D4 — So sánh | Control thích nghi cùng exact references; toolkit đối thủ đã được lập. | Protocol khai trước, eligible early-stopping baselines, held-out confirmation, matched guarantee/coverage, scaling và ablations. |
| D5 — Gói nghiên cứu | Artifact có pin, review và bảng claim–evidence; kết quả thất bại được giữ. | Technical report/manuscript cho một đóng góp đã đạt, cùng tái lập các bảng xác nhận chính. |

## Câu hỏi nghiên cứu còn mở

Trên lớp quá trình nào được mô tả bằng cấu trúc thông tin có ý nghĩa, số lượng
probe và hình học cây đủ để bảo đảm độ sắc theo margin, trong khi tổng chi phí
build và query vẫn thấp hơn quyết định bằng adapted OT riêng rẽ? Đây là thiếu
hụt D1–D2 cần giải trước đầu tư probe hiệu năng lớn. Timing control chưa tách
được là một dấu hiệu cụ thể về upper stretch; chưa có lý do coi nó đại diện
cho toàn miền hoặc loại nó khỏi đánh giá.

Phạm vi review gắn với claim và artifact/hash trong nguồn bằng chứng tương ứng.
Task và kế hoạch thực thi lấy từ [checkpoint](../status.orchestrator.json).
