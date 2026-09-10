# Tri thức ngoài — quét W2 vòng 1 cho đề xuất hướng gap-guided joint refinement

Ngày: 2026-09-10. Thực thi nghĩa vụ W2 khai trong
[direction_proposal_20260910.md](../theory/direction_proposal_20260910.md).
Nguồn: OpenAlex API (có key), arXiv toàn văn, fetch DOI qua Unpaywall/S2/Crossref.
Đây là quét vòng 1 có mục tiêu, KHÔNG phải tuyên bố đầy đủ literature (giới hạn ở mục 7).

## 1. Cụm novelty của cơ chế đề xuất: định danh đã xác minh, chưa thấy va chạm

Các phương pháp MDP duy trì hai chặn giá trị và tinh chỉnh chọn lọc — prior art
phải trích khi phát biểu claim, đã xác minh định danh qua OpenAlex:

| Công trình | Định danh | Năm | Trích dẫn | Cơ chế |
|---|---|---|---:|---|
| McMahan–Gordon–Blum, Bounded RTDP | `doi:10.1145/1102351.1102423` | 2005 | 136 | hai chặn giá trị, ưu tiên theo hiệu chặn × occupancy |
| Smith–Simmons, Focused RTDP | `openalex:W4199186` | 2006 | 101 | như trên, ưu tiên hội tụ |
| Hansen–Zilberstein, LAO* | `doi:10.1016/s0004-3702(01)00106-0` | 2001 | 387 | heuristic search với chặn chấp nhận được |
| Haddad–Monmege, Interval iteration MDP | `doi:10.1007/978-3-319-63387-9_8` | 2017 | 71 | lặp đồng thời chặn trên/dưới có bảo đảm dừng |
| Givan et al., Bounded-parameter MDP | `doi:10.1016/s0004-3702(00)00047-3` | 2000 | 313 | khoảng giá trị dưới bất định tham số |
| Moore–Atkeson, Prioritized sweeping | `doi:10.1023/a:1022635613229` | 1993 | 712 | hàng đợi ưu tiên theo Bellman residual |

**Kết quả tra va chạm:** các truy vấn "anytime/interval/bounded bounds" ×
"nested distance / bicausal / adapted OT" (6 truy vấn, mục 7 ghi rõ) KHÔNG trả
về phương pháp anytime certified nào cho nested distance. Quét 2026 (mục 5)
cũng không có. Novelty của cơ chế **sống sót vòng 1** với điều kiện phát biểu
claim là *chuyển giao có mở rộng không tầm thường* sang lớp bài bicausal
(bài toán con là OT trên polytope coupling, không phải min trên tập hành động
hữu hạn; chặn dưới cần dual khả thi địa phương + Kršek–Pammer cho nền đối ngẫu),
KHÔNG phải phát minh khung interval refinement. Điểm khác biệt phải chứng minh
bằng đo: chi phí duy trì hai phía trên polytope và đường chứng nhận outward tại gốc.

## 2. Nhập kỹ thuật cho W1 (số học chứng nhận): bài toán đã có lời giải chuẩn

| Công trình | Định danh | Truy cập | Nội dung chịu lực (đã xác minh ở mức abstract) |
|---|---|---|---|
| Neumaier–Shcherbina, Safe bounds in LP/MILP | `doi:10.1007/s10107-003-0433-3`, Math. Programming 2004, 166 trích dẫn | **closed** | hậu xử lý nghiệm LP xấp xỉ thành chặn an toàn bằng directed rounding, không cần giải lại |
| Jansson, Rigorous lower/upper bounds in LP | `doi:10.1137/S1052623402416839`, SIAM J. Optim. | **closed** | với simple bounds hữu hạn, chặn dưới nghiêm ngặt của giá trị tối ưu tốn O(n²) phép toán |
| Keil, Lurupa | `doi:10.4230/dagsemproc.05391.6`, 2006 | OA | triển khai phần mềm của các chặn trên |

**Hệ quả cho dự án:** W1 không phải nghiên cứu mở — nó là engineering có trích
dẫn. Bài OT địa phương của ta là transportation LP với 0 ≤ π ≤ 1 (simple bounds
hữu hạn), đúng lớp bài Jansson xử lý rẻ: từ MỘT vector dual xấp xỉ bất kỳ, đánh
giá interval của residual cho chặn dưới nghiêm ngặt, không giải lại LP. Phần
việc riêng của dự án còn lại là **truyền outward các khoảng địa phương qua đệ quy
Bellman tới gốc** (bao gồm normalization và bảo toàn khối lượng nhỏ) — chưa thấy
tài liệu làm sẵn cho nested OT. Blocker trung thực: cả hai bài chính closed
access; trước khi implement W1 cần bản toàn văn hợp lệ HOẶC tự dẫn lại chặn cho
transportation LP (ngắn) kèm review độc lập; không code theo trí nhớ không kiểm.

## 3. Audit mức định lý Schmitzer (mục REQUIRED còn treo) — ĐÃ LÀM

Toàn văn arXiv:1510.05466v2 (36 trang), trích và đối chiếu nguyên văn:

- **Definition 3.3 (Shielding Condition):** (xs,ys) shields xA khỏi yB khi
  `c(xA,yB) − c(xs,yB) > c(xA,ys) − c(xs,ys)` — tức {(xA,ys),(xs,yB)} là
  c-cyclically monotone chặt.
- **Proposition 3.4 / 3.6:** neighbourhood shielding ⇒ tồn tại short-cut cho mọi
  cặp ngoài N; **Corollary 3.10:** primal tối ưu ĐỊA PHƯƠNG trên N shielding ⇒
  tối ưu TOÀN CỤC (qua dual khả thi toàn cục, Prop 3.2).
- **Algorithm 4.1 (solveSparse):** lặp {solve local, dựng shield}; dừng vì chi
  phí đơn điệu giảm trên không gian hữu hạn; **Algorithm 4.6** ghép multiscale.
- Hai giới hạn tác giả TỰ KHAI, quan trọng cho ta: (i) shield map hiệu quả phải
  khai thác **cấu trúc hình học của cost** (Sect. 5: squared Euclidean trên lưới
  Cartesian, v.v.); (ii) **complexity tổng thể là câu hỏi mở**.

**Phán quyết overlap với cơ chế đề xuất:** khác mục tiêu — Schmitzer chứng nhận
tối ưu toàn cục của MỘT bài OT tĩnh bằng công việc thưa; cơ chế của ta nhắm
khoảng chứng nhận TẠI GỐC của đệ quy khi các bài địa phương chỉ được giải một
phần. Không va chạm claim. Điểm nối tiềm năng (chưa đo): dùng shielding làm
solver địa phương exact-thưa thay LP đầy đủ; rào cản đúng như thẻ H-B đã đoán —
cost của ta là `c + V_child`, continuation có thể phá cấu trúc hình học mà
shield map cần, và ở T50 census đã cho thấy cấu trúc địa phương co lại. Giữ làm
ghi chú, không mở nhánh.

## 4. Nâng cấp trích dẫn prior-art cho support-Monge dispatch

Tham chiếu Monge trước đây "chỉ có abstract": đã lấy được abstract đầy đủ có
phát biểu định lý của **Bein–Brucker–Park–Pathak 1995**
(`doi:10.1016/0166-218X(93)E0121-E`, Discrete Applied Mathematics): NW-corner
greedy giải bài transportation d-chiều ⟺ mảng chi phí có tính Monge d-chiều
(theo nghĩa Aggarwal–Park); trường hợp 2-D là **định lý Hoffman 1963** (điều kiện
cần và đủ, họ thuật toán greedy O(mn)). Trang publisher vẫn 403 — toàn văn chưa
có, nhưng mức abstract-có-định-lý đủ để dòng trích dẫn của dispatch ghi
Hoffman 1963 + Bein et al. 1995 thay vì "abstract-accessible reference".

## 5. Cập nhật panel 2026 — 7 mục mới, không mục nào là đối thủ solver có certificate

Từ truy vấn `adapted Wasserstein` / `bicausal` lọc 2026 (OpenAlex):

| Công trình | Định danh | Triage một dòng |
|---|---|---|
| Adapted Wasserstein Barycenters of Gaussian Processes | `arXiv:2604.22453` | mở rộng dòng Gaussian oracle sang barycenter; liên quan fallback miền con, không phải solver |
| Adapted OT between Filtered Gaussian Processes | `arXiv:2604.22159` | AW₂ như bài Procrustes ràng buộc trên nhân tử Cholesky; nối dài trực tiếp Gunasingam–Wong — đọc toàn văn nếu kích hoạt fallback Gauss |
| A probabilistic view on the adapted Wasserstein distance | `doi:10.1016/j.spa.2026.105032` | lý thuyết; không thuật toán |
| Empirical martingale projections via adapted W | `doi:10.1214/25-aap2239` | smoothed empirical + tốc độ tham số — bổ sung câu chuyện estimand (Phát hiện 2 của DOMAIN_KNOWLEDGE) |
| T1 inequality for adapted W | `doi:10.1214/26-ecp750` | lý thuyết concentration; không thuật toán |
| Bicausal OT for SDEs with irregular coefficients | `doi:10.3150/26-bej1985` | thời gian liên tục; nguồn instance kiểm thử, không đối thủ lưới |
| Graph Causal OT and Wasserstein Distances | `arXiv:2608.13716` | tổng quát hoá theo DAG, có DPP; đọc phần DPP khi viết related work |

Không mục nào cung cấp per-instance root certificate hoặc anytime bounds cho
nested distance — nhất quán với kết quả tra va chạm ở mục 1.

## 6. Điều lượt quét này đổi trong đề xuất hướng

1. Bảng overlap ở câu hỏi 1 của direction_proposal nay có **định danh xác minh**
   thay vì trí nhớ mô hình; wording claim phải là "transfer + extension" với
   trích dẫn đủ dòng MDP ở mục 1.
2. W1 hạ độ khó: từ "nghiên cứu số học" xuống "engineering theo Neumaier–
   Shcherbina/Jansson + phần truyền gốc tự làm", kèm blocker truy cập đã ghi.
3. Stop-gate 5 (novelty đổ) chưa kích hoạt sau vòng 1.
4. Mục REQUIRED audit Schmitzer đã đóng; thẻ H-B có thêm căn cứ nguyên văn cho
   rào cản "continuation phá cấu trúc cost".

## 7. Giới hạn của quét này

- Tìm kiếm lexical (OpenAlex search), 10 truy vấn chủ đích + 2 truy vấn 2026;
  chưa quét backward citation của cụm MDP, chưa quét kỷ yếu không DOI
  (AAAI/ICAPS/NeurIPS workshop), chưa quét theo tác giả. Vắng mặt trong kết quả
  ≠ không tồn tại.
- Neumaier–Shcherbina, Jansson, Kirui–Pflug–Pichler: **closed access, chưa đọc
  toàn văn** — nội dung ghi ở mức abstract đã xác minh, cấm code trực tiếp từ đó.
- Toàn văn duy nhất đọc trong lượt này là Schmitzer 1510.05466v2; các trích
  nguyên văn ở mục 3 đối chiếu bằng tìm chuỗi trên bản PDF arXiv.
- Không chạy thí nghiệm, không đăng ký giả thuyết, không sửa code.
