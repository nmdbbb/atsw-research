> Historical solver guidance extracted from WORKFLOW.md at bfbcbd1.
> Reference only. Paths in the retained text are relative to research-workflow/.
> Active PO workflow: [WORKFLOW.md](../../WORKFLOW.md).

# Workflow tìm thuật toán cây cho adapted OT

Mục tiêu giữ nguyên về bài toán, được sửa đúng về đối thủ: **nhanh hơn SOTA phù hợp ở cùng độ chính xác/chứng nhận, hoặc chứng nhận chặt hơn ở cùng ngân sách tính toán**. POT chỉ là một baseline triển khai. “SOTA” trong workflow là tập phương pháp mạnh, tương thích và đã tái lập tại ngày đánh giá; không phải tên của một thư viện hay một paper được chọn thuận tiện.

Đây là quy trình nghiên cứu có thể tiếp tục qua nhiều phiên. Nó không bảo đảm một thuật toán vượt SOTA tồn tại. Scope v2 đã được user cho phép sau khi có kết quả: ưu tiên chi phí/độ chặt chứng nhận tại gốc, cho phép kết quả miền con và nhánh giới hạn có phạm vi. Các nhánh này không tự hoàn thành mục tiêu thuật toán ban đầu. File `objective.json` giữ hợp đồng; `SCOPE_REVISION_2.md` và `ledger/contract_revision_2.json` ghi thay đổi; `START_HERE.md` là prompt giao việc cho orchestrator. Không sửa đăng ký hay hash lịch sử để hồi tố thành công.

## 1. Khoá đại lượng trước khi tối ưu

Hai đường đánh giá phải phân biệt:

| Đường | Đầu vào và đích | Phát biểu được phép |
|---|---|---|
| Solver | Cùng mô hình hữu hạn, cùng lưới, cùng k, cùng biên điều kiện, cùng cost, cùng quy ước V=AW_p^p | Khoảng [L0,U0] chứa nghiệm nested OT của mô hình này |
| Estimator từ paths | Cùng paths, quyền truy cập dữ liệu, preprocessing và ngân sách | Sai số/chi phí ước lượng adapted distance; tách lỗi lấy mẫu, cửa sổ/lưới và solver |

Không cho thuật toán mới dùng kernel thật khi đối thủ chỉ có paths. Không so giá trị regularized với unregularized mà bỏ bias. Không đồng nhất V với căn bậc p của V. Nếu xuất distance, biến đổi cả hai đầu khoảng trước khi tính tiêu chí. Không gọi chứng nhận mô hình hữu hạn là chứng nhận khoảng cách population.

Sáu ô lõi để đạt mục tiêu ban đầu gồm k∈{1,2}, δ∈{0.5,0.3,0.18}, T=50, kể cả ô đắt nhất. Mở rộng kiểm chứng sang hai cost và hai họ quá trình như `objective.json`; họ thứ hai phải kiểm tra được giả thiết mà AR(1) dễ làm đúng. Kết quả miền con được phép nếu khai rõ miền, điều kiện, lý do chọn và giới hạn; lựa chọn sau khi thấy thất bại phải công bố và cần held-out mới trước claim xác nhận. Không ngoại suy kết quả đó thành phủ toàn miền.

**“Thuật toán cây đúng bản chất” có tiêu chuẩn kiểm được:** mô tả rõ phần cây/đồ thị lịch sử hoặc toán tử điều kiện nào cho phép dùng chung/bỏ cả nhóm phép tính; chứng minh điều kiện hợp lệ; đo công việc thực sự tránh được; phá cấu trúc đó bằng ablation để xem lợi ích có mất không. Không ép phải có nghiệm đóng hay cải thiện worst-case asymptotic mới được nghiên cứu. Giảm công việc theo cấu trúc đầu vào cũng có thể là đóng góp, nhưng phải khai điều kiện và chi phí trường hợp xấu.

## 2. Đội bốn vị trí, vai trò thay theo pha

Orchestrator giữ mục tiêu, lịch chạy và sổ bằng chứng. Ba slot còn lại không phải ba người cùng viết một kernel.

| Pha | Slot A | Slot B | Slot C | Orchestrator |
|---|---|---|---|---|
| Đọc và đặt giả thuyết | Literature/SOTA: đọc phương pháp, định lý, code | Theorist: cơ chế + lemma + phép đo | Skeptic: phản ví dụ + kiểm giả thiết | Khóa câu hỏi và phạm vi |
| Probe | Implementer: prototype nhỏ | Verifier: oracle và kiểm chứng độc lập | Literature/SOTA: tái lập đối thủ | Chạy có kiểm soát, phân loại lỗi |
| Xác nhận | Implementer: đóng băng candidate | Verifier: certificate + held-out | Comparator: đối thủ và fairness | Chỉ mình orchestrator tích hợp và phán quyết |

Người viết candidate không được tự phê duyệt chứng chỉ của nó. Sự đồng ý giữa các agent không thay cho bằng chứng. Luân chuyển vai trò giữa chu kỳ để giảm việc một agent bảo vệ hướng mình đã đề xuất. Có thể tạo agent mới với ngữ cảnh hẹp cho phản biện; không chia sẻ kết luận mong muốn, nhưng phải đưa đầy đủ định nghĩa và bằng chứng cần thiết.

**Giao tiếp bắt buộc, không chỉ giao bài rồi gom đáp án:**

1. Reader gửi `SOURCE_NOTE` trực tiếp cho theorist và skeptic: URL, phiên bản, mục/định lý đã đọc, giả thiết, điểm có thể chuyển sang bài này, điểm không thể chuyển.
2. Theorist gửi `HYPOTHESIS` có công thức và prediction cho skeptic trước khi implementer code benchmark.
3. Skeptic gửi `OBJECTION` hoặc phản ví dụ tối thiểu cho theorist và verifier. Theorist phải trả lời `RESOLUTION`: sửa, rút, hoặc chỉ ra lemma giải quyết. Không giải quyết bằng bỏ qua.
4. Implementer gửi `ARTIFACT` gồm hash code và lệnh tái lập. Verifier gửi `VERDICT` kèm output, không chỉ “pass”.
5. Orchestrator ghi unresolved objections và quyết định. Khi đổi vai, agent mới đọc phần còn tranh chấp trước.

Mẫu thông điệp: `{type, hypothesis_id, claim, evidence_paths_or_urls, assumptions, objection_id, requested_action}`. Dùng công cụ giao tiếp nội bộ của agent trong phiên; ghi nội dung quan trọng vào `ledger/`. Không cần Slack/email.

## 3. Vòng ngoài: tìm cơ chế

```text
Mục tiêu + bản đồ SOTA + kho phản ví dụ
                 ↓
Đọc full text / code liên quan → 3 giả thuyết KHÁC CƠ CHẾ
                 ↓                    ↑
Phản biện chéo → khai trước → probe nhỏ ─┘ khi giả thuyết chết
                 ↓
Lemma + cơ chế sống sót → vòng triển khai bên trong
                 ↓
Kiểm chứng độc lập → so sánh toàn phạm vi → phân tích thất bại
                 ↓                                  │
Đạt đủ cổng: đóng gói kết quả       Chưa đạt: trở lại câu hỏi cấu trúc
```

### Pha 0 — Literature và tái lập SOTA

Mỗi phương pháp có một thẻ comparator: quantity, filtration, cost, input access, representation, guarantee, code/version, hardware, oracle calls, cách chuyển về target chung và chi phí của phép chuyển. Đọc phần thuật toán/định lý/limitations; abstract không đủ để tuyên bố tương đương hoặc mới.

Tập đối thủ ban đầu phải xem xét NestedOT/PNOT, adapted Sinkhorn, nested Sinkhorn và DP chính xác được tối ưu hợp lý. Phương pháp fitted value iteration có thể nằm ở track khác quyền truy cập dữ liệu. Kết luận eligibility chỉ sau kiểm tra toán và implementation. Các nguồn cụ thể nằm trong `research/`.

Không loại đối thủ vì chưa có adapter rồi gọi phần còn lại là SOTA. Ghi “chưa tái lập/chưa so được”, để cổng SOTA còn mở. Không cần chạy mọi paper trong lịch sử: phải giải thích panel đại diện cho các phương pháp mạnh phù hợp thế nào. Kiểm lại literature khi mở cơ chế mới và trước xác nhận cuối.

### Pha 1 — Mỗi chu kỳ ba giả thuyết, không phải 24 biến thể cùng khung

Ba giả thuyết và trần 25% vi mô là mặc định điều phối, không phải cổng khoa học. Có thể phân bổ lại trước run khi một phép thử quyết định cần nhiều công hơn; ghi lý do, không sinh thêm giả thuyết nông để đủ số. Giữ một record cho mỗi thí nghiệm để sinh mọi bảng, không bắt agent chép cùng số vào nhiều sổ.

Một giả thuyết phải trả lời đủ:

- Phép tính nào sẽ biến mất hoặc được dùng chung? Trên nút, nhóm nút, subtree, cửa sổ hay toán tử nào?
- Quan hệ cấu trúc nào làm điều đó hợp lệ? Nêu điều kiện định lượng, không nói “trơn” chung chung.
- Invariant hoặc lemma nào nối thao tác cục bộ với nghiệm tại gốc?
- Trên đầu vào nào prediction đúng, và phản ví dụ nào có khả năng giết nó?
- Đối thủ gần nhất đã làm điều gì? Phần mới còn lại ở đâu?
- Chi phí phát hiện cấu trúc, chứng nhận, sửa và fallback có xoá lợi ích không?

Ba họ câu hỏi mở đầu: (A) tương đương/xấp xỉ tương đương phần tương lai để nén có chứng nhận; (B) phân giải phân cấp theo ảnh hưởng tại gốc với chặn hợp lệ cho cả khối; (C) tái sử dụng phép giải/toán tử qua lịch sử với kiểm điều kiện rẻ. Đây là ứng viên, chưa phải phát hiện hoặc lời hứa. Thẻ cụ thể do literature và phản biện quyết định.

### Pha 2 — Khai trước rồi mới probe

Đóng băng thẻ bằng `workflow.py register`. Ghi threshold, oracle, seed, điều kiện giết, công việc cần giảm, chi phí đầy đủ và giả thiết. Probe độ đúng dùng bài nhỏ có thể giải chính xác, ma trận không Monge, xác suất nhỏ/0, cost đổi họ, k=2 và horizon ngắn có nhánh phụ thuộc quá khứ. Chỉ đo SVD rank hoặc cosine là kiểm cấu trúc mô tả, chưa kiểm được một thuật toán.

Nếu code sai: ghi `implementation_invalid`, sửa cùng giả thuyết và chạy lại; không gọi giả thuyết chết. Nếu dữ kiện bác prediction: `falsified`, lưu phản ví dụ. Nếu probe yếu: `inconclusive`, thiết kế phép đo phân biệt tốt hơn. Không hồi sinh một giả thuyết đã chết bằng đổi tên và cùng điều kiện.

### Pha 3 — Vòng trong, chỉ sau khi cơ chế có cơ sở

Prototype nhỏ → verifier độc lập → end-to-end dễ → ô phá giả thiết → toàn grid. Tinh chỉnh hằng số, SVD, cache, warm start được phép nhưng ngân sách mặc định tối đa 25% của chu kỳ. Khi chi phí xác nhận/sửa lớn hơn công việc bỏ được, quay về cơ chế thay vì thêm wave tối ưu vô hạn.

Không buộc phải chứng minh mọi định lý tiệm cận trước khi chạy probe. Cần đủ lập luận về tính đúng của kết quả xuất ra, hoặc oracle nhỏ để nghiên cứu phần còn conjecture. Một prototype chưa chứng nhận không được nâng thành champion certified.

## 4. Cổng toán học và cổng thực nghiệm

**Cổng toán học:** dùng chính sách khả thi để có U; cận dưới phải hợp lệ với cùng continuation lower. Với biên xác suất cố định, Bellman đơn điệu và không giãn theo chuẩn sup. Occupation của chính sách đề xuất được dùng để xếp ưu tiên, không tự cho phép bỏ vùng khác khỏi cận dưới. Cận hợp lệ cũ được giữ bằng max cho L, min cho U trên cùng instance. C-transform/dual feasibility phải kiểm sai số số học; “LP chạy xong” không phải chứng nhận exact trong số thực.

Nếu cận số học không chặt tuyệt đối, dùng hiệu chỉnh bảo thủ hoặc interval/rational checking theo triển khai đã chọn. Công bố rõ mức đảm bảo: chứng minh thuật toán + kiểm khả thi có sai số được chặn; không lấy tolerance tuỳ ý để xoá vi phạm. Với ML thay đổi phải kiểm lại feasibility của dual. Sàn cũ chỉ tái sử dụng khi cùng target. k=2 phải biểu diễn đủ lịch sử; không giả sử chung một M cho mọi cặp nếu successor indexing không hỗ trợ.

Chứng nhận tương đối cho output U, khi L>0: `(U-L)/L <= 0.005`. Khi L<=0, dùng một ngưỡng tuyệt đối có đơn vị đã khai trước; không tự thay mẫu số bằng U hoặc V* để báo đạt. Nếu target là căn của V, đánh giá trên khoảng đã lấy căn. V* chỉ ở evaluator kiểm tra, không được candidate dùng để dừng/chọn nhánh.

**Cổng phạm vi:** confirmation cho mục tiêu thuật toán toàn miền không loại ô đắt. Giữ chính sách `reference_audit_policy` trong frozen design và các amendment hiện có: có thể giới hạn tham chiếu exact trong khi candidate/comparator vẫn chạy đủ miền; bài lớn cần audit chứng nhận độc lập, không chỉ khớp oracle nhỏ. Kết quả miền con báo riêng và không vượt cổng toàn miền. Sàng rẻ không được dùng để công bố thắng. Holdout chỉ mở sau khi code, comparator tuning và chính sách chọn solver đã đóng băng; sau khi xem kết quả, tập đó là dữ liệu phát triển. Lần xác nhận mới cần giữ nguyên nghĩa bài toán và khai rõ số lần thử, không quay seed đến khi có kết quả đẹp.

**Cổng so sánh:** đo cả from-paths và solver-only; thời gian tính μ, SVD, tất cả ngân sách trước, xây lưới/cây, chứng nhận, fallback đều có mặt ở from-paths. Đối thủ cũng được cùng cơ hội tuning; so sánh theo cùng hardware/resource cap, xác định cold/amortized. Frontier là bao tốt nhất của các đối thủ hợp lệ trên từng task, không chọn một baseline yếu làm mẫu số chung.

Speed track: cùng ε và guarantee, so thời gian đạt. Quality track: cùng tổng budget, so độ rộng chứng nhận; exact đạt được trong budget có gap 0 nên không thể bị thắng bằng “gap nhỏ hơn”. Không đem exact solver mặc định chạy quá chính xác so với candidate rồi gọi đó là thắng SOTA certified. Nếu một đối thủ chỉ có empirical error, báo ở bảng khác; sự thiếu certificate của họ không tự chứng minh phương pháp mới tốt hơn toàn bộ SOTA.

Ưu tiên probe về chi phí chứng nhận tại gốc, work counts và ablation dùng cùng kernel trước đầu tư hệ thống. Wall-clock vẫn cần cho claim hiệu năng thực tế; khác biệt Python/C++ không thay thế được giải thích cơ chế. Giữ PNOT ở task exact đủ điều kiện, audit adapter/guarantee trước bảng certified và tính đủ chi phí. Truyền cận tới gốc, tách finite/population và đo đầy đủ thời gian là yêu cầu nghiêm túc, chưa tự chứng minh novelty.

Geometric mean để tóm tắt, không bù cho ô thua. Mặc định kiểm không thoái lui trên mỗi ô và cải thiện thực chất vượt nhiễu ở phạm vi đã khai. Khoảng tin cậy phải dùng các lần chạy/seed độc lập, so ghép cặp hợp lý; khi claim đồng thời nhiều ô cần xử lý multiplicity, không lấy 24 CI riêng 95% làm CI toàn cục 95%. Ngưỡng kỹ thuật đề xuất nằm trong config, được phép sửa có lý do TRƯỚC kết quả.

## 5. Chọn nhánh và lặp theo bằng chứng

```python
while not selected_research_outcome_reviewed:
    restore_contract_and_evidence()
    resolve_open_comparator_and_correctness_issues()
    route = choose_algorithm_or_scoped_obstruction_question()
    if route == "scoped_obstruction":
        define_class_access_cost_accuracy_and_quantifiers()
        prove_then_independently_review_and_adversarially_check()
        record_scoped_outcome_without_algorithm_success()
        checkpoint()
        continue
    papers = read_sources_for_the_current_structural_bottleneck()
    hypotheses = propose_distinct_mechanisms(papers, counterexamples)
    exchange_objections_and_preregister(hypotheses)
    for h in hypotheses:
        result = run_small_falsification_probe(h)
        if result.is_valid_and_supports_mechanism:
            implement_then_independently_verify(h)
            evaluate_on_development_frontier_and_breadth(h)
    update_archive_by_mechanism_and_evidence()
    if candidate_ready_for_confirmation:
        freeze_everything_then_run_all_required_tasks()
    classify_failure_and_choose_next_structural_question()
    if evidence_justifies_stopping_this_direction:
        archive_decision_limits_and_alternatives()
        checkpoint()
        break  # Dừng hướng này, không suy ra chương trình hay mục tiêu đã hoàn thành.
    checkpoint()
```

“Không cải thiện sau hai chu kỳ” kích hoạt chẩn đoán, không tự động dừng hoặc suy ra đã tối ưu hết hằng số. Phân biệt: hypothesis sai; representation không biểu diễn nổi; certificate quá đắt; policy kém; thống kê lấy mẫu chi phối; baseline mạnh hơn dự kiến; hoặc lỗi code. Sau review có thể đổi cơ chế, nghiên cứu giới hạn của một lớp rõ ràng, hoặc đóng hướng hiện tại có lý do. Nếu mở chu kỳ thuật toán mới, một agent đề xuất hướng không thừa kế kiến trúc champion.

Không dừng chỉ vì score không giảm, nhưng không chạy lại cùng thí nghiệm không có thông tin mới. Lặp khi phiên/compute hoạt động; hết phiên thì checkpoint đúng trạng thái và tiếp tục ở phiên sau. Thiếu repo, dữ liệu, công cụ hoặc ngân sách là blocker thực thi, không phải chứng minh bài toán không giải được. Không tự động phát sinh chi phí cloud hay giả vờ còn agent chạy sau khi phiên kết thúc.

## 6. Phân biệt các kết quả kết thúc

### 6.1. Hoàn thành mục tiêu thuật toán ban đầu

`original_algorithm_objective_achieved` phải đồng thời thoả ba điều:

1. **Hiệu quả:** thắng panel SOTA đã tái lập theo speed hoặc certified-quality, qua toàn phạm vi và held-out; công bố mọi ô và mọi chi phí.
2. **Cơ chế cây:** có phát biểu toán, điều kiện, phản ví dụ biên, work counts và ablation giải thích phần tính toán được loại bỏ/dùng chung. Solver nhanh nhờ vectorization thôi không hoàn tất nhánh nghiên cứu này.
3. **Đóng góp:** đối chiếu nearest prior art, độc lập kiểm tra proof và implementation; phân biệt kết quả đã có với phần thực sự mới. Không dùng một agent tự gắn nhãn novel để vượt cổng.

Nếu đạt hiệu quả nhưng chưa có đóng góp cấu trúc, lưu như baseline mạnh. Nếu có định lý nhưng không thắng thực nghiệm, lưu như kết quả lý thuyết riêng. Chỉ nhánh này được đặt `scientific_objective_achieved=true`; các nhánh dưới không bỏ qua ba cổng này.

### 6.2. Kết quả giới hạn có phạm vi

`scoped_negative_research_complete` cần phát biểu rõ target, miền mô hình, lớp thuật toán/cơ chế, quyền truy cập/oracle, đơn vị công việc, accuracy và lượng từ (worst-case, theo phân phối hay từng instance). Nộp định lý giới hạn với proof và review độc lập, kiểm đối kháng, work counts đúng metric, nearest prior art và artefact tái lập. Claim thực nghiệm cần khai việc đã xem dữ liệu và xác nhận held-out. Không yêu cầu thuật toán mới cho nhánh này; không hứa bài báo sẽ được nhận.

Tỷ lệ đỉnh tối ưu khác nhau không tự chứng minh không thể chia sẻ tiền xử lý hoặc bỏ tính toán. Nhiều cơ chế thất bại không mặc nhiên là bằng chứng độc lập. Phán quyết `runs/cycle_2/H_B01C1_verdict.md` giữ distinct-entry prediction của H-B ở inconclusive dù occupation headroom thất bại. Quy luật 1/w đo trong `runs/cycle_1/D/sinkhorn_tiny.json` không phải chặn dưới phổ quát cho Sinkhorn. Phải giải quyết các khoảng trống này trước claim bất khả thi.

### 6.3. Miền con, đóng hướng và blocker

`limited_domain_result` ghi miền và giới hạn theo scope policy, không tuyên bố phủ miền ban đầu. `direction_stopped_evidence_based` ghi lý do dừng một hướng, evidence đúng metric, câu hỏi còn mở và hướng thay thế; không cần bịa định lý bất khả thi để dừng đầu tư. `execution_blocked` là thiếu tài nguyên/công cụ/phiên, không phải kết luận toán học.

Orchestrator ghi `research_outcome`, `original_algorithm_objective_achieved` và đường dẫn record bằng chứng/review trong checkpoint khi đã phân loại. Giữ `scientific_objective_achieved=false` cho mọi nhánh trừ 6.1. Không đổi loại một run lịch sử sau khi xem kết quả; kết quả cũ có thể được trích làm bằng chứng phát triển với nguồn gốc đầy đủ.

## 7. Sổ bằng chứng và phần chạy được

`workflow.py` là bộ quản lý checkpoint, hash khai trước và kiểm điều kiện báo cáo. Nó không thay verifier toán, không tự benchmark, không tự gọi model. Orchestrator dùng công cụ multiagent trong phiên để thực thi loop; xem `START_HERE.md`. Các artefact tối thiểu:

`check-report` vẫn chỉ sàng số liệu speed/quality cho toàn miền ban đầu; không phải validator nhánh âm tính hoặc miền con. Các nhánh đó cần record riêng nêu claim, phạm vi, evidence/hash, phản biện và phán quyết độc lập theo mục 6. Không sửa required tasks để lách bộ sàng. Revision v2 cập nhật contract lock có lịch sử trong ledger; không chạy lại init để xoá lịch sử.

- `research/`: notes có URL, phiên bản, phần đã đọc, assumptions và overlaps.
- `hypotheses/`: cơ chế, tiêu chí khai trước và mọi objection/resolution.
- `runs/`: config/hash, logs, timing components, certificate witnesses, data/seed ID.
- `ledger/`: sự kiện append-only, băm nối chuỗi để phát hiện sửa vô ý; không phải chữ ký chống giả mạo.
- `status.json`: pha hiện tại, việc tiếp theo, blocker, đường dẫn bằng chứng.

Archive `atsw_repo.tar.gz` đã được nhận và giải nén vào `inputs/atsw_repo/`, gồm `kmarkov_driver.py`, `certify5.py`, `certify6.csv` và workflow cũ. Archive giữ nguyên như nguồn lịch sử; kết quả bên trong chưa được tái lập chỉ vì file đã có.

Vòng kiểm đầu tiên đã tái lập một phản ví dụ bằng oracle giải tích: builder k=2 cũ trả 0 cho bài có giá trị gốc đúng 4/3, do bỏ bước ngẫu nhiên đầu tiên và chọn cửa sổ phổ biến làm root. Xem `research/sota/imported_root_counterexample.json`. Bộ điều khiển cũng được kiểm bằng các fixture tổng hợp; đó không phải benchmark thuật toán. Việc tiếp theo là adapter đúng target, rồi tái lập đối thủ, không đo tốc độ trên biểu diễn sai.
