# Audit workflow và vai PO — 2026-09-10

## Kết luận và phạm vi

Lõi workflow có ích: target khóa, phản biện độc lập, khai trước, oracle, lưu kết
quả âm tính và tính đủ chi phí. Vấn đề chính là quyết định đầu tư và chuyển giao:
hướng dẫn chồng lớp, scope bị diễn giải quá tay, kiểm đúng một đối tượng khác,
và dễ nhầm tiến bộ hạ tầng với tiến bộ khoa học. Thêm biểu mẫu không tự sửa các lỗi này.

Audit này dựa trên hội thoại hiện có và các record dưới đây, không giả nhận đã
đọc toàn bộ phiên khác. “Đã ghi nhận” là có bằng chứng/đính chính trong repo;
“rủi ro” là suy luận vận hành. Không audit lại toàn bộ định lý nguồn và không có
kết quả nghiên cứu mới. Một reviewer độc lập đọc workflow/handoff trước khi sửa
và đọc draft đã tích hợp như người mở phiên mới. Reviewer xác nhận tìm được vai
PO, scope, next action và review còn thiếu; yêu cầu thêm bộ đếm ngân sách qua phiên
và làm rõ quyền tiếp nhận phần review chưa hoàn tất. PO đã sửa hai điểm đó; không
có lượt review lặp cho các sửa nhỏ này và không gọi đây là review toán mới.

## Cách phối hợp với user và điều phối

| Vấn đề | Bằng chứng / phân loại | Sửa tại workflow |
|---|---|---|
| Tự chốt mục tiêu từ một ý tưởng đang bàn | Hội thoại: user yêu cầu phân tích trước sau lần reframe; [Trial 01 review](../theory/relational_trial_01_independent_review_20260910.md) chỉ ra top-K/fallback dễ bị nâng thành yêu cầu. Lựa chọn mới nhất được ghi trong [PO decision](../../DECISION_ORDER_PRESERVATION_20260910.md). | Tách yêu cầu phân tích, lệnh thực hiện, lựa chọn scope và lời khuyên. PO không tự thêm completion gate; thay đổi target/guarantee chưa được phép mới cần hỏi. |
| User phải nhắc vai trò hoặc gõ “tiếp tục” nhiều lần | Có trong hội thoại; việc agent đánh mất checkpoint là rủi ro cần phòng, không quy lỗi cho user. Trước audit chưa có AGENTS.md tại gốc. | Root mặc định là PO; báo một quyết định tiếp theo rồi thực hiện khi được giao, tự chọn công việc thường lệ. Phiên chỉ hỏi trạng thái thì trả lời đúng trạng thái, không tự chạy một chiến dịch. |
| Hướng dẫn mới đè lên hàng trăm dòng chỉ dẫn cũ | WORKFLOW trước audit có cả nhánh v3 và đội bốn slot/ba hypothesis/full grid; START_HERE trỏ prompt v3 cũ. Đã ghi nhận. | Một entrypoint; hướng dẫn solver cũ chuyển sang tài liệu tham chiếu. Objective, lựa chọn user, checkpoint và proposal có vai trò riêng. |
| Dùng hết tài nguyên thành mục tiêu thay cho kết quả | Hội thoại có yêu cầu chạy gần trần quota; Trial 02 reviewer bị ngắt. Không có đo lường tiết kiệm quota giữa các phiên. | Ngân sách là trần, không là chỉ tiêu phải tiêu hết. Bounded task có đơn vị công việc và điểm checkpoint; không hứa dừng ở % quota không quan sát được. |
| Review bị ngắt nhưng dễ bị hiểu là duyệt toàn bộ | [Trial 02 verdict](../theory/relational_trial_02_verdict_20260910.md) ghi phần root bổ sung chưa sign-off. | Ghim phiên bản và phạm vi claim; unknown reviewed revision vẫn là unknown. Chỉ review delta chịu lực khi có quyết định promotion. |
| Ghi nhiều thẻ/đọc lại toàn repo làm loãng phán đoán | [Đối chiếu workflow trước](notes.md) đã yêu cầu một record/phép thử và bỏ fan-out cố định. Tái diễn là rủi ro. | Packet ngắn, review khi cần, checkpoint trỏ bằng chứng. Một lần review độc lập có câu hỏi rõ; không sinh thêm lớp framework. |

Đây là điều chỉnh trách nhiệm của PO, không yêu cầu user học cách viết prompt dài.
User giữ quyền chọn bài toán, mức bảo đảm và ưu tiên khoa học. PO tự quyết thứ tự
đầu tư, ngân sách công việc có giới hạn và đóng construction trong phạm vi đã giao.
Advisor/agent đề xuất là đầu vào phải kiểm; user paste đề xuất không tự có nghĩa
là thông qua mọi phát biểu hoặc mọi thao tác trong đó.

## Sai sót toán và suy luận cần chặn tại nguồn

| Lỗi / giới hạn đã ghi nhận | Nguồn nội bộ | Phép kiểm khi claim phụ thuộc vào nó |
|---|---|---|
| Lean kiểm nhất quán Vdp nhưng hai vế đều là surrogate, không có infimum coupling của AW | [STATUS_REPORT nhập, bảng định lý](../../inputs/atsw_repo/notes/STATUS_REPORT.md) | Viết cạnh nhau target, phát biểu hình thức và kết luận muốn báo; chỉ rõ định lý cầu nối còn thiếu. Không đồng nhất 0 sorry với đúng statement nghiên cứu. |
| Upper cho OT(c+L_child) bị dùng như upper của continuation thật | [Interval reuse skeptic](../theory/interval_reuse_skeptic_20260910.md) nêu hạng thiếu `<p,U_child-L_child>` | Kiểm local-to-root bằng chính sách khả thi và cùng continuation; bao gồm root/initial law, trường hợp biên và sai số số học. |
| Tối ưu lower không gỡ được phần upper vượt mục tiêu | [Briefing lịch sử, mục 4](../../BRIEFING_20260910.md): upper vượt tham chiếu số 5.178% trong case đã đo | Trước đầu tư, hỏi kể cả bước này thành công hoàn hảo thì tiêu chí đích có thể đạt không. Chặn numerical ở case đó không phải định lý toàn miền. |
| Khớp float hoặc predicate Fraction bị nâng thành certificate toàn pipeline | [Permuted Monge review](../theory/permuted_monge_final_review_20260910.md): predicate exact nhưng plan/value vẫn float | Phân biệt proof thuật toán, feasibility, arithmetic và truyền sai số. Số tests/hash chỉ kiểm phần được thiết kế để kiểm. |
| N^(-1/51) khoảng 0.84 bị đọc thành sai số/sàn nhiễu; smoothing thành bắt buộc | [Domain rate audit](../sota/DOMAIN_RATE_AUDIT_20260910.md), [Moulos/Backhoff audit](../sota/MOULOS_BACKHOFF_AUDIT_20260910.md) | Chặn trên không là chặn dưới; giữ hằng số, giả thiết, lớp mô hình và estimator. Kiểm kết quả Markov thích hợp trước ngoại suy từ rate tổng quát. |
| Trộn population, empirical full-prefix law và reconstructed k-window law; generator khác fitted kernels | Hai audit rate trên và [Trial 02 review](../theory/relational_trial_02_independent_review_20260910.md) | Nêu law/filtration/units/quyền truy cập chính xác; điều kiện phải kiểm trên đối tượng candidate thực dùng. Quá trình Markov không tự còn Markov sau quantization. |
| Ordinary tree OT bị dùng như bicausal OT; unit-prefix geometry bỏ gần/xa số học | [Trial 01 review](../theory/relational_trial_01_independent_review_20260910.md) | Kiểm cả cost và tập coupling; giữ ví dụ timing thông tin và tách-rồi-gần-lại. Phản ví dụ chỉ bác construction đã nêu. |
| Nhiều failure, đỉnh khác nhau hoặc TV=1 bị kéo thành bất khả thi tổng quát | [H_B01C1 verdict](../../runs/cycle_2/H_B01C1_verdict.md), [scope analysis](../../SCOPE_REVISION_3.md), Trial 01 | Khai lớp thuật toán, quantifier, access model, đơn vị công; failure có thể chung nguyên nhân. Cho phép đóng đầu tư mà không bịa lower bound. |
| Công thức đúng nhưng đã biết hoặc không hữu ích về định lượng | [Trial 02 verdict](../theory/relational_trial_02_verdict_20260910.md), [H_C02 prior art](../../ledger/inbox/B/H_C02_prior_art_review.md) | Tách đúng / khác prior art / đủ sắc / rẻ. Cận tồn tại hay điều kiện margin sơ cấp không tự là đóng góp; fixture dễ chưa là coverage. |
| Full trie nhỏ trên n paths nhưng có thể nổ khi khai triển luật k-window; đồng thời không phải mọi weights đều buộc khai triển | [Trial 02 review](../theory/relational_trial_02_independent_review_20260910.md) | Chỉ rõ representation và weights; kiểm khả năng gom trên DAG. Tính cả applicability, build, labels, query, fallback và bit complexity khi liên quan. |
| Đếm proxy như LP thực; timing một lượt thành speedup; T5 thành T50 | [Permuted Monge review](../theory/permuted_monge_final_review_20260910.md), [Briefing mục 5](../../BRIEFING_20260910.md) | Metric phải khớp prediction; kiểm counter có đo solve thật. Tách diagnostic, benchmark và confirmation; so cùng target/guarantee/coverage. |

Các điều kiện này kích hoạt theo claim, không phải checklist bắt buộc làm mọi
thứ cho mỗi sửa tài liệu. Lỗi đang chặn quyết định nào thì kiểm lỗi đó trước.
Nhánh âm tính hữu ích có thể là quyết định dừng; muốn claim giới hạn khoa học
vẫn phải có phát biểu riêng đủ sức nặng và review.

## Chuyển thành vận hành

- `AGENTS.md` tại gốc: vai root PO và ranh giới sub-agent, ngắn để tự nạp.
- `START_HERE.md`: trình tự khởi động và prompt duy nhất cho phiên mới.
- `WORKFLOW.md`: nhánh chính, cổng claim, review đúng phiên bản, quyết định và handoff.
- `status.orchestrator.json`: một next action có work limit, lựa chọn user và review còn thiếu.
- Hướng dẫn solver trước đây giữ tại `legacy_solver_workflow_v2.md`; snapshots,
  run và chứng cứ đã ghim không chỉnh sửa.

Đã biết giới hạn hạ tầng: `verify_hash_pins.py` quét events/preregistered/runs,
không tự quét toàn bộ inbox. Khi dùng inbox làm evidence chịu lực, kiểm các hash
được tham chiếu trực tiếp; không gọi 26 ghim là xác minh mọi file nghiên cứu.

Kiểm bản sửa bằng đọc entrypoint như phiên mới, đối chiếu đường dẫn, load JSON,
verify contract/ledger và byte pins. Đây là kiểm handoff/tài liệu; không đo quota
và không chứng minh agent tương lai luôn tuân thủ. Không có daemon PO chạy nền.
