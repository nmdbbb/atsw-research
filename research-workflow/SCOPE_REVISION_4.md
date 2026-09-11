# Scope v4 — Biểu diễn tái sử dụng cho adapted OT có bảo đảm

Ngày 2026-09-11. User yêu cầu định vị theo kết quả đáng đạt, không theo những gì
prototype đã làm được; sau đó chỉ thị **“hãy lưu scope này, thu thập các công cụ
để sau này thí nghiệm so sánh, xác định những kết quả cần delivery”**. Đây là
amendment được cho phép, không phải đăng ký mù hoặc công nhận kết quả khoa học.
Hợp đồng máy đọc là [objective.json](objective.json); lịch sử v3 được giữ nguyên
trong `ledger/contracts/objective_v3.json`. Quy trình vẫn là [WORKFLOW.md](WORKFLOW.md).

## 1. Mục tiêu và sức nặng cần đạt

**Xây dựng biểu diễn tái sử dụng của quá trình ngẫu nhiên, giữ đủ cấu trúc thông
tin theo thời gian để chứng nhận các quan hệ gần–xa theo adapted OT, với tổng
chi phí thấp hơn giải các bài toán transport riêng rẽ.**

Định vị: representation và computational geometry của adapted OT. Câu hỏi trung
tâm là quan hệ giữa **kích thước biểu diễn — độ sắc của bảo đảm — chi phí quyết
định**. Đóng góp phải giải thích điều kiện nào cho phép tiết kiệm, tiết kiệm do
đâu, và ở đâu biểu diễn không còn đủ thông tin hoặc không còn đáng dùng.

Luận điểm bài báo mong muốn, **chưa phải kết quả**: trên một lớp quá trình có
ý nghĩa, được mô tả bằng cấu trúc thay vì danh sách fixture, một biểu diễn dùng
lại được chứng nhận một phần đáng kể quan hệ adapted OT và tránh được công
transport thực sự; lý thuyết và thí nghiệm xác định giới hạn đánh đổi đó.

Cây chung là kiến trúc đang đầu tư, được nâng cấp hoặc thay nếu không đạt mục
tiêu. Công thức tree-Wasserstein, một lower bound đúng, interval sorting, nhiều
tests qua hay tốc độ trên toy data không tự tạo thành đóng góp này.

## 2. Đối tượng và ranh giới claim

- Đối tượng nghiên cứu: các luật quá trình có filtration được khai rõ trên
  horizon hữu hạn. Mỗi task cố định
  `D(P,Q) = inf_{pi bicausal} E_pi[sum_t c_t(X_t,Y_t)]`.
  Chỉ gọi `D=AW_p^p` khi cost/chuẩn hóa thực sự tương ứng. Không trộn p, horizon,
  filtration hoặc đơn vị khác nhau vào một task giữ thứ tự.
- Bảo đảm chính vẫn là **giữ thứ tự dưới điều kiện toán học kiểm được**. Với
  query q, mỗi kết luận `D(q,a)<D(q,b)` phải đúng dưới giả thiết đã nêu; trường
  hợp chưa phân biệt được trả unresolved. Top-K, full ranking và fallback là
  khả năng mở rộng, không phải nghĩa vụ hoàn thành.
- Một cách đạt bảo đảm là `U(q,a)<L(q,b)`. Nội dung nghiên cứu phải nằm ở việc
  tạo thông tin đủ sắc với chi phí thấp, không ở suy luận sơ cấp này. Cho phép
  định lý distortion/ordering khác nếu có phép kiểm điều kiện không vòng tròn.
- Phạm vi thực thi đầu tiên vẫn là finite-model adapted OT. Khi đầu vào là
  paths và dựng mô hình k-window, certificate chỉ nói về mô hình đó. Population,
  empirical-to-population hoặc smooth AW cần cầu nối riêng; sửa scope này
  **không** cung cấp cầu nối và không tự đổi estimand của các thí nghiệm cũ.
- AW1, số hữu tỉ, k-window, transductive batch và sáu controls hiện tại là giới
  hạn prototype, **không phải trần mục tiêu dự án**. Chọn lớp theorem/probe theo
  ý nghĩa khoa học; cho phép miền con khai rõ. Không đòi hỗ trợ mọi p, mọi cost,
  mọi filtration hay population để hoàn thành một kết quả có miền xác định.
- Chỉ có paths khi protocol nói paths. Nếu thí nghiệm dùng mô hình đã cho hoặc
  generator oracle, khai riêng chế độ truy cập và tính đủ chi phí; không dùng
  nhãn/reference miễn phí để thiết kế biểu diễn rồi báo lợi thế từ paths.

Lựa chọn deterministic của user trong
[decision trước](DECISION_ORDER_PRESERVATION_20260910.md) được giữ. Tương quan
thực nghiệm là số đo phụ, không thay được bảo đảm; đổi sang statistical ranking
hoặc estimand khác cần lựa chọn riêng. V2 solver ≤0.5% vẫn parked, chưa đạt và
chưa bị bác; không nhập full grid/T=50 của v2 thành nghĩa vụ v4.

## 3. Định vị với nhu cầu và prior art

So sánh luật quá trình là vấn đề rộng hơn một ứng dụng. Scenario reduction,
đánh giá mô hình sinh và retrieval là nơi kiểm tra giá trị, không khóa đề tài
vào một ứng dụng. Chọn workload có ý nghĩa sau khi xác định claim.

Các nguồn chịu lực cần đối chiếu:

| Nguồn | Điều phải phân biệt trong đóng góp |
|---|---|
| [Chen et al. 2023 — WL và stochastic processes](https://proceedings.mlr.press/v221/chen23a.html) | Biểu diễn điều kiện đệ quy và liên hệ bicausal đã có prior art; phải đối chiếu cost/filtration, không chỉ đổi tên cấu trúc. |
| [Brugère et al. 2024 — OTM/WL/OTC](https://proceedings.mlr.press/v237/brugere24a.html) | Framework khoảng cách Markov và phiên bản discounted/regularized là đối chiếu thuật toán và novelty; không mặc định cùng finite additive target. |
| [Backurs et al. 2020 — Flowtree](https://proceedings.mlr.press/v119/backurs20a.html) | Biểu diễn cây để tăng tốc tìm hàng xóm W1 đã có; cần đóng góp riêng về adapted information và guarantee. |
| [Scenario tree reduction via Wasserstein barycenters, 2026](https://link.springer.com/article/10.1007/s10479-026-07062-8) | Nguồn workload multistage và thuật toán liên quan; ranking khoảng cách không tự chứng nhận chất lượng quyết định downstream. |

Đây là bản đồ đối chiếu, không phải kết luận novelty đã sống sót. Danh mục mã
nguồn, pin, license, dependency và mức sẵn sàng ở
[comparison toolkit](research/sota/comparison_toolkit_v4.md).

## 4. Các kết quả phải bàn giao

Một file chỉ là vật chứa; nghiệm thu theo bằng chứng dưới đây. Trạng thái lúc
amendment: **chưa delivery nào hoàn thành trọn vẹn**; thiết kế cây đã review chỉ
là tài sản đầu vào cho D2/D3, không được nhận sign-off cho claim mới.

| ID | Kết quả phải delivery | Bằng chứng nghiệm thu |
|---|---|---|
| D1 — Claim và miền có ý nghĩa | Một luận điểm nghiên cứu cụ thể, lớp quá trình, chế độ dữ liệu/truy cập và phần khác nearest theorem/algorithm | Bảng đối chiếu giả thiết/kết luận; lý do miền quan trọng; một falsifier quyết định; review độc lập phần đóng góp còn lại. Không định nghĩa miền bằng “những instance mà bound thành công”. |
| D2 — Bảo đảm và đánh đổi | Định lý giữ thứ tự/approximation dẫn tới thứ tự trên đúng D, nêu giả thiết và vùng unresolved | Proof nối biểu diễn tới coupling/filtration và root; điều kiện kiểm được có tính công; kết quả định lượng về độ sắc theo độ phức tạp biểu diễn hoặc cấu trúc quá trình; ít nhất một họ không tầm thường, không chỉ fixture riêng lẻ. Review đúng phiên bản. |
| D3 — Thuật toán tái sử dụng | Thuật toán dựng biểu diễn và quyết định có interface, implementation đúng định nghĩa | Đếm build/index/query/update/certification/fallback, memory và số học; chỉ rõ phần conditional OT bị bỏ/chia sẻ; xác định khi amortization có lợi. Không che bảng exact all-pairs trong preprocessing. |
| D4 — Bằng chứng so sánh | Thực nghiệm khai trước cho giá trị quyết định và chi phí trên miền D1 | Held-out confirmation; coverage trước fallback, ties và unresolved trong mẫu số; chi phí đầy đủ ở matched guarantee/coverage; baseline đủ mạnh được early-stop; ablation bỏ conditional information và bỏ sharing; đồ thị quy mô/điểm hòa vốn; lưu thất bại. |
| D5 — Gói kết quả nghiên cứu | Manuscript/technical report cùng artifact tái lập, bảng claim–evidence và giới hạn | Người khác tái lập các bảng chính từ pin/protocol; phân biệt theorem, numerical evidence, diagnostic, negative và open; nêu miền chưa phủ, chi phí training và mọi correction. |

Nhánh thành công dương cần D1–D5. Một nhánh âm tính có sức nặng có thể là kết quả
nghiên cứu hoàn chỉnh nếu thay D2 bằng **định lý giới hạn được review** trên lớp
biểu diễn/thuật toán và access model rõ ràng, có hàm ý thực chất cho bài toán;
D3/D4 khi đó bàn giao construction đối chứng, kiểm độ sắc/phạm vi phù hợp thay
vì buộc phải có speedup. Nó không được gắn nhãn đạt mục tiêu thuật toán dương.
Một vài probe thất bại chỉ đủ đóng construction, không chứng minh bất khả thi.

## 5. Protocol và cổng đầu tư

Không bịa ngưỡng khoa học sau khi thấy số đẹp. Mỗi probe phải đóng băng trước:
miền/split, margins/ties, coverage tối thiểu, mức cải thiện chi phí có ý nghĩa,
reference precision, sample size, ngân sách và stop-gate, cùng lý do lựa chọn.
Sáu controls đã xem chỉ là development diagnostics, không thành confirmation.

Panel tối thiểu theo claim: solver adapted OT mạnh cùng target (dừng khi đủ
quyết định), nested Sinkhorn có certificate hợp lệ khi adapter sẵn sàng, bounds
đơn giản hợp lệ, ordinary-tree control và candidate bỏ sharing. Nếu một họ đối
thủ không thể triển khai hợp lệ trong ngân sách, ghi lý do và hạ mức claim so
sánh tương ứng; không tự tuyên bố SOTA từ việc bỏ đối thủ. WL/OTM, SVI và FVI là
đối chiếu tri thức quan trọng; không mặc định bắt buộc cài tất cả để chạy probe.

Tách panel **numerical solver** và **certified decisions**. Solver không xuất
certificate sẵn vẫn có thể là đối thủ mạnh; kiểm khả năng xây adapter và tính
công adapter. Regularized scalar, float residual hoặc cost khác chưa đủ tư
cách certificate cho D. Không so speed của hai đại lượng khác nhau như cùng task.

Thứ tự đầu tư: D1 cùng phần cốt lõi D2 → kiểm cơ chế/chi phí D3 → một probe D4 →
xác nhận và D5. Có thể thực hiện diagnostic rẻ để phân biệt conjecture trước
khi theorem hoàn chỉnh; không yêu cầu chứng minh toàn bộ bài báo trước phép thử.
Nếu nghẽn ở biểu diễn, ưu tiên đổi cây/thuật toán; không kéo dài chuỗi lemma phụ
hoặc sửa overhead khi thành công của chúng vẫn không cứu được luận điểm.

## 6. Quyết định PO kế tiếp

Chuẩn bị **một packet D1–D2 cho cây điều kiện tái sử dụng**: chọn một lớp quá
trình được tham số hóa có timing/conditional dependence thực sự; phát biểu
conjecture định lượng nối độ méo/cấu trúc cây, độ sắc bound và margin quyết định;
đối chiếu nearest WL/OTM/tree theorem. Tái dùng proof cây hiện có cho phần không
đổi. Chọn một family phản ví dụ hoặc phép tính hữu hạn để phân biệt conjecture,
rồi quyết định giữ/nâng cấp/thay cây trước probe hiệu năng.

Ngân sách task kế tiếp: một packet, một kiểm quyết định hữu hạn, một review delta
nếu còn đóng góp khả dĩ. Không review lại toàn lịch sử, không cài toàn bộ toolkit,
không chạy grid lớn. Đây là kế hoạch bước kế tiếp; lượt lưu scope/thu thập công cụ
không được ghi là đã thực hiện nghiên cứu đó.
