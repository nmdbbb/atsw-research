# Bản đồ tri thức cross-domain — nhập theo quyết định, không nhập để phủ rộng

Ngày: 2026-09-10. Bổ sung cho [EXTERNAL_KNOWLEDGE_20260910.md](EXTERNAL_KNOWLEDGE_20260910.md).
Nguyên tắc: một mục tri thức ngoài domain chỉ được nhập khi trả lời được
"nó đổi quyết định nào của dự án?". Mỗi dòng dưới đây ghi rõ quyết định bị đổi
và điều kiện kích hoạt. Định danh xác minh qua OpenAlex trong phiên này trừ khi
ghi khác.

## Đã nhập (phiên 2026-09-10, xem EXTERNAL_KNOWLEDGE)

| Domain nguồn | Công trình | Quyết định đã đổi |
|---|---|---|
| Planning/MDP, model checking xác suất | BRTDP 2005, Focused RTDP 2006, LAO* 2001, interval iteration 2017, prioritized sweeping 1993 | Chính cơ chế đề xuất là transfer từ dòng này; wording claim buộc là "transfer + extension"; stop-gate novelty |
| Verified numerical computing | Neumaier–Shcherbina 2004, Jansson (SIAM JO), Lurupa 2006 | W1 từ "nghiên cứu mở" thành "engineering có trích dẫn + phần truyền gốc tự làm" |
| Computational OT đa thang | Schmitzer arXiv:1510.05466 (Def 3.3, Cor 3.10) | Đóng audit REQUIRED; xác nhận nguyên văn rào cản của thẻ H-B; ghi chú solver địa phương exact-thưa |

## Xác minh đợt này — kích hoạt khi hướng được user chốt

**Goal-oriented a-posteriori error estimation / dual-weighted residual (giải tích số PDE).**
Becker–Rannacher, *An optimal control approach to a posteriori error estimation
in FEM*, Acta Numerica 2001, `doi:10.1017/s0962492901000010` (1.201 trích dẫn);
cùng họ: Oden–Prudhomme 2001 `doi:10.1016/s0898-1221(00)00317-5`.
Paradigm: sai số toàn cục của một phiếm hàm đích = tổng residual địa phương
nhân trọng số adjoint; tinh chỉnh lưới ở phần tử có tích lớn nhất. Đẳng thức
quy trách của ta (`mu_n` × Bellman residual) là bản rời rạc cùng cấu trúc, với
occupation đóng vai adjoint weight. **Quyết định bị đổi:** thiết kế và cách
đánh giá P1/P2 — literature này có sẵn khái niệm effectivity index (tỷ số sai
số ước lượng/thật), hiện tượng cancellation giữa residual trái dấu, và bài học
"chỉ số địa phương tốt trên lưới thô không ngoại suy" — đúng loại thất bại mà
census T50 đã dạy. Cần trích trong related work của claim.
**Kích hoạt:** ngay khi user chốt hướng (P1 design). Toàn văn OA có trên
Cambridge/CiteSeer — đọc phần định nghĩa effectivity trước khi cố định metric P1.

**Abstraction refinement và tương đương trạng thái (verification, RL theory).**
CEGAR: Clarke–Grumberg–Jha–Lu–Veith, JACM 2003, `doi:10.1145/876638.876643`
(994). Model minimization MDP: Givan–Dean–Greig, AIJ 2003,
`doi:10.1016/s0004-3702(02)00376-4` (319). Bisimulation metrics: Ferns–
Panangaden–Precup (bản finite: arXiv:1207.4114; bản continuous: SIAM J. Comput.
2011 `doi:10.1137/10080484x`); panel đã có Calo et al. 2024 nối bisimulation
metrics = OT distances. **Quyết định bị đổi:** nếu thẻ H-A (certified quotient)
mở lại, khung "merge lạc quan → phản ví dụ → split" của CEGAR và các chặn sai
số approximate-bisimulation là prior art bắt buộc trích và là nguồn thiết kế
phép kiểm. **Kích hoạt:** CHỈ khi H-A mở lại — hiện đang parked, không đọc thêm.

## Định danh CHƯA xác minh — quét lại khi kích hoạt, không dùng từ trí nhớ

- **Warm-start/reoptimization cho chuỗi transportation LP gần nhau (OR).** Vòng
  tinh chỉnh sẽ giải lại LP tại node với continuation thay đổi nhẹ — dual warm
  start là kỹ thuật chuẩn của network simplex nhưng hai truy vấn lexical đợt này
  không trả về công trình gốc. **Quyết định sẽ đổi:** chi phí mỗi bước refine
  trong P2. **Kích hoạt:** thiết kế P2. Ghi chú: POT không expose warm start
  cho LP exact; nếu cần sẽ phải đo lợi ích trước khi đổi solver.
- **Column generation / pricing (Lübbecke–Desrosiers và họ Dantzig–Wolfe).**
  Chỉ liên quan nếu thẻ H-C (occupancy flow, sparse pricing) mở lại. Parked.

## Điều bản đồ này KHÔNG nói

Không mục nào ở trên chứng minh cơ chế chạy được trên bicausal OT — P1/P2 mới
quyết định. Không mở nhánh mới, không đọc thêm ngoài điều kiện kích hoạt đã ghi.
Vắng hit trong truy vấn lexical không phải bằng chứng vắng mặt prior art.
