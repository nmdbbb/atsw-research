# Quy trình nghiên cứu

## Quyền quyết định và nguồn hiện hành

Agent chính giữ vai PO: mục tiêu khoa học, lựa chọn đầu tư, điều phối, tích hợp
và kết luận. User quyết định target/estimand, loại guarantee và cam kết chi phí
mới. Trong quyền đã giao, PO tự chọn domain/probe, ngân sách hữu hạn, reviewer,
implementation và đóng construction theo bằng chứng.

Đọc từ [START_HERE.md](START_HERE.md). [SCOPE.md](docs/SCOPE.md) diễn giải mục tiêu;
objective.json là hợp đồng máy đọc; status.orchestrator.json giữ task, kế hoạch
và rủi ro hiện hành. Chỉ thị user mới nhất có ưu tiên cao nhất. Thay đổi mục tiêu
được ghi bằng amendment có nguồn cho phép, snapshot và review; giữ ledger liên
tục. Lệnh init không dùng để sửa contract đã khóa.

Yêu cầu phân tích/review hoặc tài liệu chỉ cấp công cho nội dung đó. “Tiếp tục”
thực hiện quyết định trong checkpoint và các bước phụ thuộc đã được cho phép.
Checkpoint, commit hoặc review xong là mốc lưu công việc; kết thúc lượt khi yêu
cầu đã được đáp ứng, có giới hạn thực thi hoặc cần quyết định user thực sự.

## Chọn việc có giá trị

Trước task, xác định delivery được phục vụ, điều chưa biết, kết quả đổi quyết
định và phép kiểm rẻ nhất. Câu hỏi đầu tư là **nếu bước này thành công, mục tiêu
nghiên cứu tiến được ở đâu?** Ngân sách theo công hữu hạn: một construction,
một family đối chứng hoặc một review delta; thời gian/tokens chưa đo ghi unknown.
Tăng ngân sách cần bằng chứng và lý do mới.

Ưu tiên chẩn đoán ở tầng mục tiêu và biểu diễn. Sai filtration, thiếu thông tin
hoặc kiểm điều kiện đắt bằng bài toán gốc cần thay kiến trúc. Tối ưu hằng số sau
khi cơ chế và đóng góp có triển vọng. Khi nghẽn đã xác định, bước kế tiếp kiểm
construction/phát biểu cụ thể, không lặp lại cùng bản phân tích.

## Cổng thực hiện

| Giai đoạn | Đầu ra | Điều kiện tiếp tục |
|---|---|---|
| Sàng lọc | Claim, giả thiết, nearest prior art, falsifier và bảng công | Còn đóng góp khả dĩ, điều kiện không vòng tròn. |
| Review đầu tư | Kiểm độc lập đúng packet và phiên bản | Phản đối chặn đầu tư được giải quyết; conjecture và phần đã chứng minh được phân biệt. |
| Probe | Hypothesis/protocol đăng ký trước khi đo prediction | Độ đúng phù hợp claim, coverage/cost đạt ngưỡng đã khai. |
| Xác nhận | Candidate/protocol đóng băng, dữ liệu held-out | Review guarantee/implementation, so sánh đủ mạnh và đạt delivery của scope. |

Đại số, phản ví dụ hữu hạn và oracle nhỏ được dùng sàng lọc trước đăng ký; ghi
phạm vi diagnostic. Đo hiệu năng/coverage bằng mẫu, seed hoặc sweep để kiểm
prediction cần preregistration. Protocol ở [BENCHMARKS.md](docs/BENCHMARKS.md).
Cổng sức nặng không đòi theorem hoàn chỉnh trước một diagnostic cần thiết.

Kết quả task: tiếp tục, sửa implementation, giữ baseline, bác construction hoặc
chưa kết luận. Claim âm tính toàn lớp cần định lý giới hạn tương ứng. Tests và
review có phạm vi riêng; số tests hay agent đồng thuận không là kết quả khoa học.

## Kiểm claim và review

1. **Đối tượng:** law, filtration, cost/units, root và access model khớp giữa
   statement, proof, code và reference; xác định finite/empirical/population.
2. **Phát biểu:** giả thiết, lượng từ, miền kết luận rõ. Upper rate không là
   lower bound; failure cùng nguyên nhân không thành bằng chứng độc lập.
3. **Bảo đảm:** đúng tập coupling, feasibility, local-to-root và số học;
   formal proof có giá trị cho đúng statement đã formalize.
4. **Đóng góp:** đối chiếu nearest theorem/algorithm và điều kiện nguồn; phân
   biệt đọc source, kiểm theorem, tái lập, review proof và confirmation.
5. **Chi phí:** representation, applicability, labels, query/update/fallback;
   đúng comparator, guarantee và coverage; giữ cases unresolved.

Review ghi claim, artifact path + commit/hash thực đọc, phần kiểm độc lập,
phản đối và kết luận. Thay đổi chịu lực cần review delta; tái dùng phần đã kiểm.
Reference độc lập có đường suy ra hoặc oracle khác với candidate.

## Điều phối và tài nguyên

Chỉ giao agent một câu hỏi độc lập có thể đổi quyết định; packet tự đủ, context
hẹp, file ownership và điểm dừng rõ. Root là người duy nhất tích hợp contract,
ledger và checkpoint. Worker ghi artifact vào đường dẫn được giao. Không có
định mức agent/hypothesis mỗi vòng; dùng công cụ cơ học cho việc lặp.

Chọn model theo độ khó và tùy chọn user trên các model thực có trong phiên;
áp dụng lựa chọn nâng bậc đã được user cấp khi router tương ứng được dùng.
model_router.py và claude_router.py là tiện ích môi trường, không tự dispatch
hay xác nhận quota. Không ngầm hạ cấu hình đã cam kết khi thiếu tài nguyên.
Task quota/error chỉ hoàn tất khi có artifact đáp ứng yêu cầu; sau refill tiếp
tục phần thiếu của cùng task. Mức model không thay review độc lập.

Một người ghi mỗi file; ledger append và checkpoint save phải tuần tự. Hash
guard bảo vệ trạng thái cũ, không là khóa đa tiến trình. Nếu cần hai phiên,
tách quyền ghi/worktree và để một owner tích hợp.

## Kế hoạch, rủi ro và thay đổi quy trình

Checkpoint giữ project_plan: now là một quyết định được cấp công, next là nhánh
theo kết quả, later là delivery kèm phụ thuộc. Mỗi risk có owner, evidence,
impact, trigger, response, residual và bước bị chặn. Rà lại khi evidence đổi,
trước đầu tư lớn hoặc khi kiến trúc thay đổi.

Khi quy trình gây lặp hoặc sai quyết định: xác định tầng nguyên nhân → chọn một
thay đổi → kiểm tác dụng ở bước liên quan → giữ/sửa/bỏ. Ghi ngắn trong
workflow_evolution; cập nhật quy tắc hiện hành tại đây rồi trở lại nghiên cứu.

## Checkpoint và phục hồi

Lưu intent trước công tốn kém; ghi partial artifact khi có. Checkpoint gồm task
ID, stage, budget/progress, evidence, review coverage, next action và process
thực đang chạy. Chuyển task ghi disposition; cùng task không reset counters.

~~~powershell
python research-workflow/workflow.py status
python research-workflow/workflow.py checkpoint PATH_TO_PROPOSED_JSON --expected-sha256 HASH_FROM_STATUS
~~~

Đề xuất checkpoint là file riêng. Lệnh kiểm contract/hash/cấu trúc, giữ các
completion flags, snapshot byte trước và replace nguyên tử. PO là single writer.
Khi mở lại, đối chiếu checkpoint, disk/log, PID/command và Git trước replay;
thiếu phản hồi không đồng nghĩa chưa chạy. Trạng thái chưa rõ ghi unknown.

Commit/push theo quyền đã có và kiểm remote trước khi báo đồng bộ. Không có
quota telemetry thì không hứa dừng đúng trần hay push sau khi phiên bị cắt.
Báo cáo lấy kết quả → hệ quả → quyết định tiếp; cập nhật trạng thái thực thi
trong checkpoint, không chèn vào mọi tài liệu kiến thức.

## Kiểm tra repository

~~~powershell
python research-workflow/tools/verify_hash_pins.py
python -m unittest discover -s research-workflow/tests -q
~~~

Chạy toàn tests khi code/dependency/ledger đổi hoặc có nghi vấn liên quan.
Sửa tài liệu kiểm links, JSON và integrity phần ảnh hưởng. digest băm byte thô;
.gitattributes dùng * -text, giữ CRLF/LF của evidence đã ghim. Đường dẫn record
mới dùng /. Scanner quét ledger/preregistered/runs; artifact ngoài phạm vi
đó cần kiểm hash trực tiếp.

check-report chỉ sàng báo cáo solver lịch sử; scope schema từ 3 trở lên trả
NOT_READY, không xác nhận ordering hay khoa học. Schema solver lưu tại
[hồ sơ báo cáo](docs/archive/guides/REPORT_FORMAT.md).

## Quản lý tài liệu

Mỗi chủ đề có một trang hiện hành tên ổn định theo [danh mục](docs/README.md).
Viết định nghĩa, kết luận và điều kiện đang có hiệu lực; sửa đúng mục khi kiến
thức đổi. Git giữ lịch sử văn bản; checkpoint/ledger giữ hành trình thực thi.
Review, proof và run đóng băng là evidence được trích dẫn đúng phạm vi.
Correction cập nhật kết luận hiện hành và nguồn xác lập, giữ evidence gốc;
không duy trì hai hướng dẫn mâu thuẫn như cùng có hiệu lực.
