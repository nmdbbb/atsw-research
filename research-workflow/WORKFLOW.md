# Workflow chính: PO, scope v3 và điều kiện rẽ nhánh

Cập nhật 2026-09-10 theo yêu cầu user: cải tiến workflow hiện có bằng điều kiện
rẽ nhánh. Mọi vòng dùng chung quy trình này, checkpoint và sổ bằng chứng.
Đọc `objective.json`, [scope v3](SCOPE_REVISION_3.md) và
[lựa chọn mới nhất của user](DECISION_ORDER_PRESERVATION_20260910.md).
Đích đang chọn là **giữ thứ tự dưới điều kiện toán học trên mô hình hữu hạn**;
top-K, thứ tự đầy đủ và fallback không bắt buộc. Sức nặng khoa học đứng trước
đầu tư triển khai. Các trạng thái dưới đây là quyết định của orchestrator;
`workflow.py` không tự gọi agent hoặc tự đánh giá chứng minh.

## Vai PO, quyền quyết định và cách làm việc với user

Root là PO trực tiếp làm việc với user; sub-agent chỉ giữ vai đã giao. PO chịu
trách nhiệm chọn câu hỏi có sức nặng, nối bằng chứng với quyết định, phân công,
tích hợp và báo kết quả. User không cần giao từng agent hay tự nhắc lịch sử.

Trong tài liệu dự án: objective khóa định nghĩa mục tiêu; lựa chọn user mới hơn
được ghi nguồn rõ để áp dụng; checkpoint ghi trạng thái; advisor/agent proposal
chưa được chấp nhận không có quyền đổi scope. Chỉ thị hiện tại của user ưu tiên
hơn các file này. Không tự sửa byte objective/hash; nếu user đổi mục tiêu thật,
ghi amendment theo quy trình sẵn có, không xin phép lại việc đã được cho phép.

| PO tự quyết trong phạm vi đã giao | Cần lựa chọn user nếu chưa được ủy quyền |
|---|---|
| Task kế tiếp, construction, ngân sách diagnostic, reviewer, sửa lỗi, đóng một nhánh có bằng chứng | Đổi target/estimand, loại guarantee hoặc tiêu chí hoàn thành |
| Miền con và ngưỡng probe khai trước với lý do; không biến thành claim toàn miền | Đổi ưu tiên khoa học của dự án hoặc cam kết chi phí ngoài quyền đã có |
| Tích hợp, kiểm tra và git theo quyền hiện có | Xuất bản/gửi người khác nếu chưa được cho phép |

“Phân tích/review/brainstorm” yêu cầu kết luận và đề xuất trong phạm vi câu hỏi;
không tự thành lệnh chạy nghiên cứu hoặc đổi objective. “Cải tiến workflow” cho
phép sửa quy trình. “Tiếp tục” nối checkpoint đang mở. Khi user hỏi trạng thái
trong lúc đang làm, trả lời ngắn rồi tiếp tục công việc đã giao trừ khi họ yêu cầu
dừng. Chỉ hỏi câu hỏi quyết định thật chưa có đáp án; không đẩy lựa chọn kỹ thuật
thường lệ về user. Báo kết quả, mức tin cậy, hệ quả và bước tiếp; tests/commit/số
trang đọc chỉ là validation, không phải thước đo sức nặng nghiên cứu.

PO xét trước: **nếu bước này thành công hoàn hảo, nó có gỡ một điều kiện đang
chặn mục tiêu không?** Nếu chỉ làm đẹp baseline hoặc bỏ qua nghẽn khác đã biết,
giữ làm công cụ phụ hoặc chọn câu hỏi khác. Không chọn hướng chỉ vì khớp code có sẵn.

## Tiến hóa workflow và định hướng: vĩ mô trước vi mô

PO đánh giá lại hướng khi có bằng chứng đổi quyết định, trước tăng ngân sách hay
promotion, hoặc khi sửa nhỏ liên tiếp không gỡ nghẽn. Không tái kiến trúc chỉ vì
một bug hay một lượt đo nhiễu; nhưng một sai lệch target/filtration hoặc nghẽn
cấu trúc đã xác nhận đủ để dừng đầu tư phụ thuộc vào nó ngay.

| Tầng nguyên nhân | Dấu hiệu kích hoạt | Quyết định ưu tiên |
|---|---|---|
| Mục tiêu / claim | Kết quả dù tốt nhất vẫn không có sức nặng; giả thiết nguồn không phủ đối tượng; user đổi ưu tiên | Kiểm lại luận điểm đóng góp và domain; đề xuất amendment nếu thật sự cần đổi target/guarantee |
| Biểu diễn / thuật toán | Mất thông tin cần giữ thứ tự; điều kiện đòi giải OT đầy đủ; chi phí chuyển biểu diễn xóa savings; cải lower không gỡ upper | Ưu tiên thay representation, decomposition hoặc cơ chế trên cùng target; một diagnostic so trực tiếp với kiến trúc đang dùng |
| Workflow / điều phối | Lặp review, tiếp tục task sai, ngân sách reset, candidate tự được promotion, mất bằng chứng khi ngắt | Sửa quyền sở hữu/trạng thái/cổng/handoff gây lỗi; giữ những cổng toán đang có ích |
| Implementation | Bug định vị được, code không thực hiện thuật toán đã nêu, overhead sau khi cơ chế sống sót | Sửa tối thiểu và kiểm đúng lỗi; chỉ tối ưu hằng số khi tác động mục tiêu đã rõ |

**Chu kỳ tiến hóa:** ghi triệu chứng + evidence → xác định tầng nguyên nhân →
so giữ kiến trúc/sửa cục bộ/tái kiến trúc bằng giá trị khoa học, rủi ro và công
chuyển đổi → chọn một thay đổi → thử tại quyết định liên quan kế tiếp → giữ,
sửa hoặc hoàn tác phần quy trình nếu không hữu ích. Ghi `workflow_evolution`
trong checkpoint: trigger, rationale, thay đổi, kỳ vọng quan sát được, điều kiện
review lại và đường về phiên bản trước. Git giữ lịch sử; không thêm sổ trùng lặp.

Khi nguyên nhân thuộc vĩ mô, đóng băng tối ưu vi mô không liên quan. PO được
tái kiến trúc workflow/biểu diễn trong scope đã giao; sửa quy trình không tự
cho quyền hạ tiêu chí khoa học, bỏ review độc lập hay sửa đăng ký sau kết quả.
Một thay đổi workflow chỉ được coi hữu ích khi giảm sai quyết định, việc lặp
hoặc công bỏ phí quan sát được. Nhiều file mới không là tiến bộ. Không mở vòng
“tối ưu workflow” vô hạn: sửa chỗ chặn rồi trở về câu hỏi nghiên cứu.

## Kế hoạch dự tính và xử lý rủi ro

`project_plan` giữ ba chân trời; chi tiết hiện tại nằm ở `workflow_route`, không
chép lại hàng đợi. **Now:** một quyết định đang được cấp công. **Next:** nhánh
nếu bằng chứng đạt/không đạt. **Later:** mốc xác nhận đóng góp, chỉ cấp ngân sách
khi các phụ thuộc đã qua. Mốc là evidence/gate, không là cam kết ngày có định lý.

Mỗi dự tính ghi đơn vị công, căn cứ, mức chắc chắn và điều gì có thể làm nó đổi.
Khi chưa có pilot, dự tính bằng số packet/đối chứng/review; thời gian, tokens và
compute chưa đo ghi unknown. Trước run lớn, đo một đơn vị đại diện để ước lượng
khoảng chi phí, kèm giả thiết scaling và checkpoint từng phần. Trần budget có
thể cấp được khác với dự báo sẽ tốn bao nhiêu. Không suy ra “còn quota” từ việc
lệnh trước vừa chạy được; không tiêu hết ngân sách cho đủ kế hoạch.

Risk register chỉ giữ rủi ro có thể đổi quyết định. Mỗi mục có owner, bằng chứng
hoặc giả định, tác động, tín hiệu kích hoạt, biện pháp, rủi ro còn lại và bước
tiếp bị chặn. Không bịa xác suất. Rà lại khi có evidence mới, nhận external
update, trước promotion/chạy đắt hoặc đổi kiến trúc; không đọc mọi mục mỗi tool.
Lỗi correctness/scope chặn claim phụ thuộc; rủi ro novelty/chi phí chặn đầu tư
lớn; quota chặn thực thi và cần phục hồi, không là kết luận toán. Rủi ro trở
thành sự cố thì ghi actual outcome; chỉ đóng khi evidence cho thấy đã xử lý.

## Luồng điều phối và cổng đầu tư

```text
Checkpoint + câu hỏi quyết định
  → Sàng lọc có giới hạn
      ├─ Sai / trùng kết quả đã biết / không còn đóng góp đáng theo → đóng nhánh hoặc giữ baseline
      ├─ Chưa phân biệt được → một phép kiểm bổ sung có lý do, hoặc checkpoint
      └─ Có cơ chế và đóng góp khả dĩ → review độc lập
          ├─ Phản đối chưa giải quyết → quay lại sàng lọc, rút claim hoặc checkpoint
          └─ Đủ cơ sở đầu tư → khai trước probe → triển khai và kiểm nhỏ
              ├─ Code sai → sửa cùng hypothesis, ghi implementation_invalid
              ├─ Prediction bị bác → ghi falsified và đóng nhánh
              ├─ Chưa kết luận → chỉ chạy tiếp nếu có phép đo thay đổi quyết định
              └─ Sống sót → đóng băng candidate/protocol → xác nhận độc lập
                  → phân loại kết quả theo hợp đồng đang áp dụng
```

| Bước | Điều kiện vào và đầu ra tối thiểu | Điều kiện chuyển tiếp |
|---|---|---|
| Sàng lọc | Một câu hỏi, claim/điều kiện cụ thể, prior art gần nhất, phép bác bỏ rẻ nhất và giới hạn công việc | Có cơ chế khả dĩ và phần đóng góp còn lại; đã kiểm phản ví dụ trực tiếp và chi phí kiểm điều kiện |
| Review đầu tư | Reviewer nhận định nghĩa, bằng chứng, phản đối và phần chưa biết của packet | Không còn phản đối chặn probe; nêu rõ điều gì đã chứng minh, điều gì còn conjecture và oracle nào sẽ phân biệt |
| Probe | Đăng ký hypothesis bằng `workflow.py register` trước thực nghiệm đo prediction; đóng băng oracle, ngưỡng, dữ liệu và ngân sách | Độ đúng phù hợp mức claim, tín hiệu vượt baseline và công việc thực sự tránh được đủ để đầu tư tiếp |
| Xác nhận | Candidate, comparator và protocol đóng băng; dữ liệu held-out chưa dùng chọn hướng | Review độc lập về guarantee/implementation, chi phí đầy đủ, coverage và các cổng hoàn thành của scope đang áp dụng |

**Ranh giới sàng lọc/probe:** phép tính đại số, phản ví dụ hữu hạn và script oracle
nhỏ phục vụ kiểm một phát biểu được làm trước đăng ký. Ghi rõ là diagnostic,
đầu vào đã xem và giới hạn; không dùng chúng như xác nhận mù hay số đo coverage,
hiệu năng hoặc thắng SOTA. Khi bắt đầu đo prediction bằng mẫu, seed hoặc sweep
để quyết định hiệu quả thực nghiệm, phải khai trước. Không đổi tên benchmark
thành diagnostic để bỏ qua cổng. Không bắt một diagnostic phải có định lý mới
hoàn chỉnh; cổng sức nặng chặn đầu tư lớn, không chặn phép kiểm cần để ra quyết định.

Với hướng hiện tại, cổng sang prototype cần một lemma không vòng tròn, một
fixture có phụ thuộc điều kiện thực sự vượt baseline agreement + marginal/range,
và bảng công việc tính cả kiểm điều kiện. Đây là điều kiện cấp ngân sách probe,
chưa chứng minh novelty hay hoàn thành mục tiêu. Trial 02 giữ làm baseline;
task kế tiếp lấy từ checkpoint hiện hành, không từ hàng đợi lịch sử trong workflow.

**Tiếp tục qua mốc nội bộ:** khi user yêu cầu chạy/tiếp tục, checkpoint, commit,
review xong hoặc đóng một construction là mốc lưu trạng thái, không tự là điểm
kết thúc lượt. PO tích hợp verdict rồi thực hiện bước phụ thuộc đã được cấp quyền
nếu có căn cứ cụ thể. Giới hạn một packet áp vào task đó, không áp vào toàn lượt;
chuyển task phải ghi disposition, lý do đầu tư và budget mới, không reset task cũ.
Không dùng quy tắc này để mở biến thể vô hạn: sau một lần xác định nghẽn, bước
nghiên cứu kế tiếp phải thử construction/phát biểu hoặc phép bác bỏ cụ thể, không
chỉ viết lại cùng câu hỏi. Dừng khi có kết quả đáp ứng yêu cầu đang giao, cần lựa
chọn user thật, gặp giới hạn tài nguyên/thực thi, hoặc không còn bước được biện
minh sau khi đã thực hiện phép kiểm quyết định. Nêu rõ lý do dừng; giữ nguyên
cổng correctness, novelty và preregistration trước những công việc phụ thuộc.

## Routing và ghi nhận trong cùng workflow

- Orchestrator trước mỗi task ghi: mục tiêu được phục vụ, điều chưa biết, kết quả
  nào đổi quyết định và phép kiểm rẻ nhất. Task không trả lời được thì chưa cấp.
- Mặc định root làm sàng lọc; một reviewer độc lập khi có packet cụ thể. Chỉ giao
  implementer sau cổng đầu tư. Bốn vai trò ở hướng dẫn cũ là năng lực có thể dùng,
  không phải bốn agent luôn hoạt động; không có quota ba hypothesis mỗi vòng.
- Giao agent đúng file/định nghĩa cần đọc, tái sử dụng kết quả đã có và chỉ tra cứu
  phần tri thức còn thiếu. Dùng script cho phép tính lặp. Không lặp review/test
  nếu không có thay đổi, lỗi hoặc phản đối chưa giải quyết làm căn cứ.
- Một packet giữ bằng chứng; verdict và checkpoint trỏ về packet. SOURCE_NOTE,
  OBJECTION/RESOLUTION và ARTIFACT/VERDICT áp dụng khi có trao đổi tương ứng,
  không phải nghĩa vụ tạo thêm agent hay chép cùng nội dung nhiều lần.
- Người viết không tự phê duyệt guarantee để nâng claim. Review bị gián đoạn
  ghi rõ phạm vi đã review và phần còn thiếu; không vượt cổng do hết quota.
- Active checkpoint là `status.orchestrator.json`: ghi bước đang ở, bằng chứng,
  điều kiện chuyển tiếp, blocker và một next action. `status.json` là lịch sử.
  Thiếu tài nguyên dẫn tới checkpoint; sai một construction chỉ đóng construction
  đó, không chứng minh bất khả thi cho cả lớp. Không tự chuyển sang ranking thống kê.

**Giới hạn công việc phải cụ thể trước khi bắt đầu:** trong packet hoặc checkpoint
ghi claim/câu hỏi, đầu ra, nguồn liên quan, trần công việc và điều kiện đổi quyết
định. Ví dụ một construction, một họ phản ví dụ hữu hạn, một lần sửa có căn cứ;
đây là ngân sách từng task, không là quota chung cho mọi nghiên cứu. Chạm trần
thì ghi verdict/inconclusive. PO chỉ gia hạn khi có bằng chứng mới và giải thích
giá trị của phép kiểm tiếp; “chưa thành công” không đủ để gia hạn vô hạn.
Task có ID ổn định và progress (chưa bắt đầu/đang làm/đã chốt, allowance đã dùng,
evidence). Ghi lần bắt đầu construction/giao review/dùng lần sửa trước khi thực
thi; cập nhật output sau đó. Phiên mới tiếp tục task đang làm, không reset counter.
Nếu bị ngắt chưa ghi được kết quả, đối chiếu artifact/log; phần chưa biết để unknown,
không coi là chưa tiêu ngân sách. Thay task cần verdict hoặc lý do chuyển rõ ràng.
Không đổi ngưỡng probe đã đóng băng sau khi xem kết quả. Dùng model theo khả năng
cần thiết và công cụ đang có; không giả đã route model rẻ hoặc tiết kiệm quota
nếu không có số đo. Không mở agent thay thế để lặp phần review đã hoàn tất hoặc
lách giới hạn tài nguyên đang hết. Khi tài nguyên cho phép, reviewer sau được
nhận phần claim chưa kiểm và delta liên quan; vẫn ghi đúng phạm vi và phiên bản.

## Cổng claim: kiểm đúng đối tượng trước khi tin kết quả

Một packet chỉ cần các mục sau ở mức phù hợp claim; dùng lại evidence đã có:

1. **Đối tượng:** law, filtration, cost, units, root và quyền truy cập. Viết rõ
   claim về population, empirical paths hay reconstructed k-window. Đặt target
   cạnh đại lượng code/proof thực tính, chỉ ra cầu nối còn thiếu.
2. **Phát biểu:** giả thiết, lượng từ, domain và kết luận. Chặn trên/rate không
   là lower bound; một construction sai không bác mọi cây; failure cùng nguyên
   nhân không là nhiều bằng chứng độc lập. Không lấy empirical correlation thay
   bảo đảm đã chọn. AW_p và AW_p^p cần đúng đơn vị khi chuyển sai số.
3. **Cầu nối:** local-to-root, feasibility và số học nếu dùng certificate;
   đúng cost và đúng tập coupling nếu dùng tree score. Chứng minh formal chỉ
   chứng minh statement đã formalize. Khớp float/toy tests chưa là guarantee.
4. **Giá trị:** nearest theorem/algorithm, giả thiết đã đọc và phần đóng góp còn
   lại. Phân biệt source_read, theorem_checked, reproduced, proof_reviewed và
   confirmed; vắng kết quả tìm kiếm không là novelty. Cận có tồn tại nhưng lỏng
   mọi nơi hay điều kiện cần biết nghiệm OT không đủ để đầu tư.
5. **Chi phí và phép bác bỏ:** kích thước representation, applicability test,
   build/calibration/query/update/fallback; đếm solve thật thay proxy. So với
   baseline phù hợp ở cùng target, guarantee và coverage. Kiểm ví dụ biên đã biết
   có liên quan; không ngoại suy từ T5, một seed hoặc terminal-only lên toàn miền.

Chi tiết lỗi đã gặp và đường dẫn bằng chứng ở
[audit PO](research/workflows/po_workflow_audit_20260910.md). Chỉ mở các hàng liên
quan task, không đọc lại toàn bộ lịch sử cho mỗi phiên.

## Review, promotion và sửa sai

Review record chỉ rõ claim IDs/mục, path + commit hoặc hash của artifact thực
đã đọc, phần chưa đọc, objections/resolutions và gate đang đánh giá. Nếu không
biết phiên bản đã review, ghi unknown; hash file cuối không được dùng hồi tố như
hash đã review. Thay đổi sau review cần kiểm delta chịu lực trước promotion,
không tự mất hiệu lực các claim không đổi, cũng không tự kế thừa sign-off.
Reviewer cần đường kiểm độc lập: phép suy ra khác, oracle hoặc kiểm trực tiếp
định nghĩa; gọi lại cùng hàm của candidate chưa đủ làm xác nhận độc lập.

Tách bốn câu hỏi: statement đúng? khác prior art? đủ sắc trên miền hữu ích?
chi phí đủ thấp? Một câu trả lời “có” không thay ba câu còn lại. Cho phép probe
nghiên cứu conjecture đã khai với oracle nhỏ, nhưng không nâng nó thành certified.
Một thay đổi ý nghĩa claim cần record đính chính liên kết bản cũ; không sửa run
lịch sử hoặc biến diagnostic thành confirmation sau khi thấy số đẹp.

Các kết quả hợp lệ gồm baseline, diagnostic, implementation_invalid, falsified,
inconclusive, direction_stopped_evidence_based, limited_domain_result và kết quả
khoa học theo đúng `objective.json`. Hết quota là trạng thái thực thi. Chỉ claim
hoàn thành khi từng cổng của hợp đồng có bằng chứng; không tự kết thúc vì nhiều
tests qua hoặc nhiều nhánh đã đóng.

## Khởi động, đồng bộ và handoff

[START_HERE.md](START_HERE.md) là entrypoint duy nhất. Root kiểm checkout/HEAD,
đọc objective + lựa chọn user được checkpoint trỏ tới, rồi workflow và evidence
cần cho một next action. Nhận patch/pull mới thì đọc delta từ mốc đang biết;
không coi summary của phiên trước là nguồn thay cho file hiện có. Không reset
hoặc ghi đè cây bẩn để “đồng bộ”; chỉ dùng Git sync có kiểm tra trong quyền đã có.

Checkpoint sau mỗi quyết định đổi hướng và trước run đắt: ghi stage, evidence,
decision, next action + budget, review còn thiếu, blocker và process thực đang
chạy (ID/log nếu có). Một nguồn cho task hiện tại: `workflow_route.next_action`;
tránh thêm hàng đợi trùng ở đầu nhiều tài liệu. Kiểm JSON/contract và hash các
evidence được dùng. `verify_hash_pins.py` hiện không quét toàn inbox; pass của nó
không chứng minh mọi artifact đã được kiểm. Kiểm đúng phần bị thay đổi; chỉ chạy
toàn suite khi code/dependency/ledger liên quan thay đổi hoặc có nghi vấn chưa giải.

Trước khi kết thúc: lưu kết quả đang có, handoff phần thiếu và Git state; commit/
push nếu đã được cho phép, xác minh remote trước khi báo đồng bộ. Không chờ đến
trần quota mới ghi bằng chứng; không hứa quan sát quota khi công cụ không có số đó.

## Checkpoint khi phiên có thể ngắt bất kỳ lúc nào

Đơn vị phục hồi là một bước nhỏ có đầu ra trên đĩa. Trước đọc/chứng minh dài,
giao agent hoặc chạy tool đắt: lưu task ID, intent, budget đã dành/dùng, artifact
sẽ ghi và bước phục hồi nếu chưa nhận được phản hồi. Trong khi làm, ghi từng
bổ đề, source note hoặc output hữu ích với nhãn partial/unreviewed; không giữ
toàn bộ kết quả chỉ trong chat hoặc chờ cuối vòng mới viết. Sub-agent ghi vào
file được giao, root tích hợp checkpoint. Mốc checkpoint theo công việc có ý
nghĩa, không theo phần trăm quota không quan sát được.

Lưu trạng thái bằng **`workflow.py checkpoint`**, không ghi đè trực tiếp file
active. Lệnh nhận JSON đề xuất riêng và hash checkpoint đã đọc (từ `status`):

```text
python research-workflow/workflow.py checkpoint PATH_TO_PROPOSED_JSON --expected-sha256 HASH_FROM_STATUS
```

Công cụ kiểm contract/ledger, giữ các trường/top-level types hiện có, cấm reset
counter cùng task và đổi completion flags, yêu cầu disposition khi chuyển task.
Nó lưu byte bản trước vào `ledger/checkpoints/recovery_<sha256>.json`, flush/fsync
file tạm cùng filesystem rồi replace active nguyên tử. Bản trước là snapshot
khôi phục, không là sự kiện khoa học mới. PO là người ghi duy nhất: hash guard
không phải khóa phân tán cho nhiều phiên cùng ghi. Lệnh không kiểm tính đúng của
claim, không tự chạy task và không bảo đảm durability khi máy/ổ đĩa hỏng.

**Mở lại sau ngắt:** đọc active trước. Nếu JSON/contract không hợp lệ, kiểm Git
và snapshot có hash đúng, so artifact rồi phục hồi có chủ đích; không tự quay về
bản cũ chỉ vì command chưa trả lời. Save có thể đã thành công trước khi mất phản
hồi. Đối chiếu task ID, counters, output, manifest và tiến trình (ID kèm thời
điểm/command/log, tránh nhầm PID tái sử dụng). Không có log không đồng nghĩa task
chưa chạy. Ghi unknown/unreconciled khi chưa rõ; không replay solve đắt hoặc hành
động có side effect cho tới khi biết cần làm gì. Review dở vẫn là review dở.

Commit phần công việc nhất quán tại mốc quyết định và push trong quyền đã có;
work-in-progress phải được gắn nhãn, kiểm không chứa output rác/secret. Push fail
thì giữ commit cục bộ và ghi việc đồng bộ còn thiếu. Sau crash, Git status và
remote HEAD là nguồn xác minh; không tin cờ “đã push” cũ. Checkpoint cục bộ giảm
mất công khi quota ngắt, push bảo vệ thêm khỏi mất máy. Vẫn có thể mất phần suy
nghĩ chưa ghi của bước hiện tại; không hứa khôi phục tuyệt đối hay tự push sau
khi phiên đã bị cắt.

Giữ nguyên hash, snapshot và preregistration lịch sử. Công cụ `check-report` chỉ
sàng số liệu solver v1/v2 và trả NOT_READY cho v3; không dùng nó xác nhận ranking.
Các nguyên tắc độc lập, khai trước, giữ target, tính đủ chi phí và held-out trong
tài liệu tham chiếu vẫn áp dụng theo claim. Hướng dẫn solver lịch sử: ngưỡng 0.5%,
toàn grid và kết luận hoàn thành solver chỉ áp dụng hợp đồng v1/v2 tương ứng.
Các mô tả lịch chạy/đội hình lịch sử không áp vào routing hiện tại.

Legacy solver reference: [retained v1/v2 guidance](research/workflows/legacy_solver_workflow_v2.md).
