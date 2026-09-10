# Scope v3 — so sánh các tập chuỗi có bảo đảm

Ngày 2026-09-10. User yêu cầu pull, đọc thay đổi và reframe scope sau khi cho phép
điểm số gần đúng nếu quan hệ giữa các cặp được bảo đảm. Đây là thay đổi mục tiêu
có khai báo sau dữ liệu. Hợp đồng hiện hành: `tree-adapted-ot-relational-v3` trong
`objective.json`; v2 giữ nguyên tại `ledger/contracts/objective_v2.json`.

## 1. Kết luận từ bản mới `56fd25b`

Hai commit `8e447b0` và `56fd25b` hạ joint refinement thành baseline, nhập audit
Moulos/Backhoff, và nộp vòng lý thuyết nén tương tác. Báo cáo lý thuyết còn
`awaiting_independent_review`; không được gọi là định lý bất khả thi đã đóng.

- Proposition 4.3 về TV = 1 cần có hai trạng thái khác cell hiện tại trong
  window k>=2. Đây là trở ngại cho hệ số TV một bước trên biểu diễn này, không
  bác mọi hệ số nhiều bước, metric khác hay mọi cách nén. Với k>2, cell hiện tại
  nằm ở thành phần áp chót của successor window, không nhất thiết thành phần đầu;
  lập luận support rời nhau vẫn áp dụng dưới điều kiện đã nêu.
- Hệ số Wasserstein từ generator population không phải hệ số kernel thực nghiệm
  của `build_window_model`; root đã sửa luật generator của theorist. Các con số
  đó chưa tự chứng minh thất bại cho mọi mô hình hữu hạn trong grid.
- Hệ số 2 qua toàn đệ quy, chi phí lookahead và các phản ví dụ còn cần review.
  Tạm ngừng construction hiện tại là hợp lý; không nâng thành chặn dưới tổng quát.
- `direction_revision_20260910.md` còn dòng `(P⊗Q)[R]` trong mô tả nền:
  kỳ vọng product kernel không thay được tối ưu coupling. Dùng OT(p,q,c+R)
  sau khi tách additive; đọc statement chi tiết và review.
- Không tái sử dụng nguyên năm gate cũ: DP exact chưa có interval comparator
  thích hợp; LP count không phải matched total cost; tỷ số outward/float và
  kết luận từ top-16 quá rộng. Revision này thay thứ tự đầu tư.

Đổi mục tiêu theo nhu cầu user về gần–xa và sức nặng khoa học, không vì suy luận
solver cũ đã được chứng minh bất khả thi. Các nguồn gốc mới nằm trong
`research/sota/MOULOS_BACKHOFF_AUDIT_20260910.md`; không mở smoothing vì rate factor.

## 2. Câu hỏi nghiên cứu mới

**Có thể biểu diễn các tập chuỗi để xác nhận quan hệ gần–xa hoặc top-K theo
adapted OT với ít tính toán hơn giải riêng các khoảng cách, và chỉ tinh chỉnh
những trường hợp chưa phân biệt được hay không?**

Reference mặc định là V=AW_p^p của cùng mô hình hữu hạn k-window, cùng cost,
horizon và quy tắc lưới. Một ranking task phải dùng target thống nhất; không
trộn cost/k/normalization. Population hoặc nhãn ứng dụng là target khác, chưa chọn.
Đơn vị bài toán là database các tập chuỗi và query mới. Chia sẻ tree giữa nhiều
truy vấn được phép; báo build/query/cold-start/amortized/break-even. Không bắt
từng giá trị đạt 0.5%. V2 vẫn nguyên nghĩa cho claim solver riêng.

## 3. Bảo đảm được nhắm tới

Mặc định: **partial ordering có chứng nhận xác định trên miền khai rõ**.
Xuất score, quyết định đã xác nhận và unresolved/fallback. Có thể dùng interval:
U(q,a)<L(q,b) suy ra a gần q hơn b. Đây là suy diễn chuẩn, không phải novelty;
đóng góp là cách có thông tin đủ mạnh với chi phí thấp. Cho phép định lý giữ thứ
tự trực tiếp, không ép mọi phương pháp dựng interval hay khôi phục giá trị chính xác.

Top-K chỉ certified khi chứng minh ranh giới chọn/loại; khai tie-aware output
nếu cần. Cặp gần hòa vẫn nằm trong báo cáo, không được xóa. Khóa coverage có ý
nghĩa; đếm riêng coverage trước/sau fallback. Abstain mọi nơi hoặc gọi exact mọi
cặp không đạt. Tree-Wasserstein closed form chưa tự bảo đảm bicausal.

Statistical ranking risk có thể chọn trước run bằng amendment riêng: khai
population lấy mẫu, sự kiện sai, confidence, calibration, coverage và hiệu lực
khi có nhiều/query thích nghi. Tương quan hoặc bootstrap CI không tự thành bảo
đảm ngoài mẫu. Không đổi loại guarantee sau khi fail.

## 4. Cổng sức nặng đứng trước code và compute

Nộp một packet ngắn trước đầu tư implementation:

1. Nếu thành công, bài báo khẳng định gì và vì sao đáng làm?
2. Prior art gần nhất đã có gì; phần nào còn mới và không tầm thường?
3. Biểu diễn giữ thông tin điều kiện nào; phép tính nào bị bỏ/chia sẻ?
4. Định lý ứng viên, giả thiết, cách kiểm giả thiết và phản ví dụ quyết định.
5. Chi phí học/dựng cây, labels, chứng nhận, updates và fallback.

Tree-Wasserstein, generic embedding, interval sorting và BRTDP là nền. Tương
quan vài cặp không đủ. Miền con có điều kiện/giới hạn rõ được phép; không gọi
AR1/Gauss-only là toàn miền. Cơ chế thời gian cần ablation tách lợi ích.

## 5. Đánh giá cần khóa trước probe

- Split train/development/calibration/confirmation theo process/tập paths;
  pair/triplet kế thừa split object. Không tính cặp chung object như mẫu độc lập.
- Khai database/query regime, tree construction, K, margin/tie, coverage/risk,
  cost threshold, seeds và trần compute. Chưa có ngưỡng số nào đã qua bằng run v2.
- Challenge theo claim: khác timing thông tin dù hình học gần; cùng current
  khác future; k=2 nonmonotone; near/exact ties; absolute và squared trừ miền
  con khai rõ. T=50 dành cho claim horizon dài, không tự là bước đầu.
- Oracle float nhỏ cho nhãn numerical. Reference intervals chồng nhau không
  xác nhận strict order. Large-case guarantee cần proof/numerics review.
- So matched guarantee VÀ coverage với adapted-OT solver dừng khi quyết định
  đã rõ, không ép đối thủ đạt 0.5% vô ích. Tính đầy đủ fallback. Thêm
  tree-Wasserstein/tree-sliced, learned trees thích hợp, simple summaries và
  ablation bỏ conditional information.
- Báo correctness/risk, coverage, fallback, unresolved, cost/decision, số OT
  đắt, memory và break-even. Kendall/Spearman/recall là chỉ số phụ.

Prior art cần đối chiếu có mục tiêu (chưa audit novelty đầy đủ):
[Tree-Sliced Wasserstein 2019](https://proceedings.neurips.cc/paper/2019/file/2d36b5821f8affc6868b59dfc9af6c9f-Paper.pdf),
[Supervised Tree-Wasserstein 2021](https://proceedings.mlr.press/v139/takezawa21a.html),
[UltraTWD 2025](https://proceedings.mlr.press/v267/yu25a.html),
và adapted-OT/MDP baselines trong repo. Vắng lexical hit không chứng minh novelty.

## 6. Hợp đồng, lịch sử và công cụ

`objective.json` là v3. Snapshot v1/v2, manifest, preregistration, runs và báo
cáo cũ giữ nguyên. `ledger/contract_revision_3.json` nối hash/snapshot; event
chỉ append. `status.orchestrator.json` là checkpoint hiện tại; `status.json`
là lịch sử, không dùng để tự tiếp tục H_D02. `workflow.py status` phân biệt rõ.

V3 và v2 đều chưa đạt. Guarantee + novelty + structural mechanism + held-out
advantage trên miền đã khai là điều kiện hoàn thành v3. Tương quan thuần túy
là exploratory. Nhánh âm tính cần định lý giới hạn riêng và review.

`workflow.py check-report` chỉ là numerical screen v1/v2. Với v3 trả NOT_READY,
không dùng report speed cũ để công nhận ranking. Tests legacy dùng snapshot v2.
Validator ranking chỉ xây sau khi protocol cụ thể được khóa.

## 7. Prompt cho phiên đang chạy

```text
User đã cho phép reframe scope sang tree-adapted-ot-relational-v3. Ở checkpoint
an toàn, đọc objective.json, SCOPE_REVISION_3.md, START_HERE.md và
ledger/contract_revision_3.json; chạy workflow.py status. Tiếp nhận v3, không
xin xác nhận lại và không khởi tạo lại ledger. Run đang chạy giữ contract cũ.

Ưu tiên sức nặng claim: ordering/top-K theo adapted OT hữu hạn có bảo đảm với
chi phí thấp; không bắt mọi giá trị đạt 0.5%. Tree chung chỉ là ứng viên. Nộp
một packet claim + nearest prior art + phản ví dụ timing thông tin + bảng công.
Sau review và cổng sức nặng mới đăng ký probe có coverage/risk, ties, cost gate
và budget. Không tự chạy P1/P2/grid hoặc xây W1 lớn.

Interaction-compression là imported theory còn chờ review độc lập; TV=1 và hệ
số generator không phải bất khả thi tổng quát. Giữ v2 và hash lịch sử; không
nâng số numerical cũ thành ranking certified. Báo kết quả thay đổi quyết định.
```
