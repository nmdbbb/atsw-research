# Review độc lập: amendment scope v4

Ngày 2026-09-11. Vai trò: reviewer hợp đồng, không giữ quyền PO. Phạm vi được
giao: tính nhất quán giữa scope người đọc và hợp đồng máy đọc; bảo toàn lựa chọn
user; tiêu chí bàn giao và tính công bằng so sánh. Không chạy nghiên cứu, code,
tests, literature search hoặc thẩm định định lý/novelty.

**Verdict: APPROVE_CONTRACT_AMENDMENT. Không có blocker nội dung đối với các
phiên bản v4 đã đọc dưới đây.** Approval này cho phép root tích hợp amendment
được user cho phép; không phải xác nhận D1–D5 hoàn thành, không phê duyệt một
claim khoa học mới hoặc kế thừa sign-off của prototype.

## Phiên bản đã đọc

Các path tính từ `research-workflow/`; SHA256 của byte đã đọc:

| Artifact | SHA256 |
|---|---|
| `SCOPE_REVISION_4.md` | `c536371a22450e1b9d77acb939b8ef7f59c6f99518d40f54fadac3326440b5b6` |
| `ledger/contracts/objective_v4.json` | `6e8e8c5ccaf77eca872e899fca232f4c028ef17bd2c8a6e3f53eda1b285e3e78` |
| `objective.json` — v3 đang active lúc đọc | `58324e8cb0dea0db8790a67a16f56c6ad38876a49aab95ff3e4471f5cf74e627` |
| `DECISION_ORDER_PRESERVATION_20260910.md` | `b0a63f5f04ad3a2f914b342fd0e74de9033d605536001ab1f561924055750997` |
| `WORKFLOW.md` — hướng dẫn admission/review tham chiếu | `2acb56a19c0fb11778f996c7e3d5ea29ac9d2cea0d667616d30f896d0a447d13` |

Đã đọc thêm `START_HERE.md` để xác định vai trò; không review hay sign off trạng
thái tích hợp cuối của startup, workflow, ledger hoặc checkpoint. Chỉ root sở
hữu các thay đổi đó. Tại lúc review, active objective vẫn v3 đúng trạng thái
draft được giao; điều này không phải bằng chứng amendment đã được kích hoạt.

## Đối chiếu claim và quyền hạn

1. Scope §1–2 và JSON `purpose`, `target`, `mechanism_policy.candidate` cùng
   nhắm tới biểu diễn tái sử dụng cho luật quá trình và đánh đổi kích thước,
   độ sắc, chi phí quyết định. Cây là khoản đầu tư hiện hành có thể thay; AW1,
   số hữu tỉ, k-window và fixtures không trở thành trần dự án. Không khóa một
   ứng dụng hoặc yêu cầu hỗ trợ mọi p/cost/filtration để hoàn thành miền con.
2. Scope §2 và `guarantees.primary` bảo toàn lựa chọn deterministic mới hơn
   wording v3: chỉ khẳng định strict order có điều kiện kiểm được, cho phép
   unresolved; top-K, full ranking và fallback optional. Interval separation
   được nhận diện là hệ quả sơ cấp, không tự được tính là đóng góp. Điều kiện
   giữ thứ tự có chi phí và không được đòi sẵn khoảng cách cần tránh tính.
3. Định nghĩa bicausal additive target và filtration được cố định trong từng
   task. Việc mở đối tượng nghiên cứu vượt prototype không nâng certificate
   hữu hạn hiện có thành population guarantee. Access model phải khai riêng;
   oracle/supplied-model không được tính thành lợi thế từ paths. Statistical
   ranking hoặc đổi estimand vẫn cần lựa chọn riêng; solver v2 vẫn parked.
4. Scope §6 là kế hoạch packet D1–D2 tiếp theo, không ghi như nghiên cứu đã
   chạy. Ngân sách một packet/kiểm hữu hạn/review delta là lựa chọn PO hữu hạn,
   không là nghĩa vụ hoàn thành thêm của toàn dự án. Lượt user đang yêu cầu
   lưu scope, công cụ và deliveries không tự cấp lệnh chạy packet đó.

## Tiêu chí bàn giao và khả năng nghiệm thu

Nhánh dương D1–D5 có đầu ra kiểm được: miền định nghĩa bằng cấu trúc, bảng đối
chiếu prior art và falsifier; guarantee có định lượng; thuật toán nêu công tránh
được; held-out comparison; report và artifact tái lập. D2 không chỉ yêu cầu
đúng trên fixtures. D4 của JSON nêu rõ coverage không tầm thường và lợi ích tổng
chi phí đáng kể; bảng scope phải đọc cùng mục tiêu §1 và protocol §5. Cần đóng
băng các ngưỡng cụ thể trước probe, như hợp đồng đã yêu cầu. Chưa có ngưỡng
số tại giai đoạn định vị không là lỗi nghiệm thu: phải chọn claim/domain trước.
Không hứa nhánh dương sẽ khả thi về khoa học hoặc về ngân sách chưa đo.

Nhánh âm có nghĩa độc lập: theorem giới hạn được review cho lớp biểu diễn/
thuật toán, target, access model và domain rõ; kèm evidence kiểm độ sắc phù hợp.
Nó thay nghĩa vụ positive algorithm/speedup của D2–D4, vẫn cần D1/D5 và không
gắn nhãn đạt mục tiêu dương. JSON `research_outcomes` và scope §4 cùng ghi điều
này, nên `completion.required` được hiểu cho nhánh dương. Probe thất bại chỉ
đóng construction, không trở thành theorem bất khả thi.

Panel so sánh giữ đúng target, guarantee và coverage; cho phép solver dừng khi
đủ quyết định thay vì ép precision v2. Cả candidate lẫn baseline phải tính
build, labels, calibration, query insertion, certification, updates và fallback
nếu dùng; báo cold/amortized và điểm hòa vốn. Solver numerical và certificate
eligibility được phân biệt, adapter có tính công; không loại đối thủ mạnh chỉ
vì API thiếu certificate. Comparator chưa làm được sẽ hạ phạm vi claim. Ordinary
tree và bỏ conditional information/bỏ sharing là controls liên quan cơ chế.
Không có nghĩa vụ cài mọi nguồn WL/OTM/SVI/FVI trước probe. Review này không
xác nhận toolkit cụ thể đã cài được, license, pin hoặc target alignment từng repo.

## Ghi chú biên tập và tích hợp cho root

- `research_outcomes.empirical_surrogate_result` còn ghi “not v3 completion”;
  nên đổi “not v4 completion” để nhánh kết quả đọc đúng contract hiện tại.
- `completion.deliverables_record` dùng anchor ASCII cho heading tiếng Việt;
  nên dùng link toàn file hoặc anchor ổn định được định nghĩa rõ. Đây là lỗi
  điều hướng nhỏ, không đổi nghĩa D1–D5.
- Khi kích hoạt v4, đồng bộ `objective.json`, revision record, startup/workflow
  và guarded checkpoint để phiên sau không quay về giới hạn v3. Giữ snapshot
  v3 và evidence bytes, không nói active đã đổi trước khi bước này xong.

Các sửa chỉ đổi nhãn v3→v4 trong nhánh surrogate hoặc điều hướng link có thể
được root ghi delta biên tập; chúng không cần được hiểu là review lại khoa học.
Thay đổi nội dung target, guarantee, completion hoặc baseline fairness sau các
hash trên cần review phần delta chịu lực. Reviewer không sửa shared contract,
scope hoặc checkpoint và không tuyên bố đã xác minh integration cuối.

## Xác nhận delta cuối cùng trong lượt review

Root đã sửa hai điểm biên tập. Reviewer đọc lại đúng hai trường:

- `completion.deliverables_record = "SCOPE_REVISION_4.md"`.
- `research_outcomes.empirical_surrogate_result = "Useful correlation/retrieval
  evidence without the required deterministic guarantee; exploratory, not v4
  completion."`

SHA256 snapshot `ledger/contracts/objective_v4.json` sau delta:
`77a842967a6f94c53d4c9974d124310c34ee7821ab9e8db3a042286d9f6236ce`.
Hai lỗi biên tập đã được giải quyết; giữ verdict
**APPROVE_CONTRACT_AMENDMENT** cho bản nền đã đọc cộng hai delta trên. Hash
snapshot ban đầu vẫn giữ trong bảng để truy vết, không ghi đè lịch sử review.
Root báo đã tích hợp startup/workflow; những chỉnh sửa đó không nằm trong
coverage của review này và không được gắn sign-off hồi tố.
