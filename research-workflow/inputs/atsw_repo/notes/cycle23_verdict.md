# Chu kỳ 2–3: phán quyết hướng đi — XÁC NHẬN

> **Tài liệu này là bản chi tiết của một phần. Bức tranh đầy đủ và hiện hành: `STATUS_REPORT.md`.**

> **TRẠNG THÁI (09/2026): đã bị thay thế một phần.** Hai kết quả sau tài liệu này đổi kết luận:
> (1) tuyên bố tốc độ ×1 700 **đã rút** — nó so với bản EP do tôi tự cài, không phải runtime công bố
> của họ (xem `sota_speed_note.md`); (2) phát hiện thêm một yếu tố giới hạn — ở T sâu với đường đi
> lấy mẫu, bản đọc lịch sử đầy đủ chệch +42…+79% (xem `paper_readiness.md` mục 8), và cách sửa là
> bản k-Markov (mục 9). Đọc `paper_readiness.md` để có bức tranh hiện hành.


![Hình phán quyết]({{artifact:efaa4864-166f-4520-9263-6cc842b8ebd6}})

## Bốn yếu tố giết — trạng thái cuối

| # | Yếu tố giết | Kiểm bằng | Kết cục |
|---|---|---|---|
| K1 | Nested Sinkhorn (Eckstein–Pammer 2022) đã đủ nhanh → cây thừa | So găng cùng dữ liệu, T=10, n=100–800 | **LOẠI.** EP chính xác hơn (lệch +0.1% vs +5%) nhưng phải thăm mọi cặp nút (~n²: 79k→4.4M khi n 100→800). n=800: EP-dense-do-tôi-cài 50,3 s vs ATSW 0,03 s. **Tỷ lệ này đã rút**: runtime CÔNG BỐ của EP là n=10⁴ trong 14,38 s (T=3); so găng đúng cách nằm ở `paper_table1_headtohead.csv`. Ở n=100k (ATSW: 290 s) EP không chạy nổi. |
| K2 | ATSW gãy trên họ quá trình thường gặp | 5 họ × 12 cặp cây, so exact ND | **LOẠI.** Spearman 0.90–0.98 mọi họ. Điểm yếu duy nhất: đuôi nặng t(3) — và phân tách chỉ ra lệch do δ thô, không phải cấu trúc: δ=0.02 đưa 0.916→0.951, phần dư lượng tử hóa 0.004. |
| K3 | Chi phí adapted nổ n² | Đếm mảnh + benchmark | **LOẠI (chu kỳ trước).** Mảnh ~n^1.33; n=100k, T=100 chạy 10 phút CPU laptop. |
| K4 | Đã có người làm | 2 nhóm khảo sát + nhóm xác minh, ~50 truy vấn | **LOẠI (chu kỳ trước).** 0 hit tree/sliced trong adapted OT; bẫy thuật ngữ đã bắt (dòng entropic đổi tên, không chết — thành baseline, không thành người chiếm chỗ). |

## Phát biểu hướng đi (đã đủ điều kiện "có thực nghiệm chứng minh")

**Adapted Tree-Sliced Wasserstein: metric adapted đầu tiên tính được ở quy mô n≥10⁵ đường đi.**
Cây lượng tử hóa phi-dự-đoán (cấu trúc TTSW) + readout lồng theo tầng bằng ghép quantile
+ trung bình shift lưới. Bằng chứng thực nghiệm đầy đủ: đúng topology (ε-example khớp 1+ε
chính xác; sập về W tĩnh nếu đổi readout — counterexample sẵn), xấp xỉ tốt (Spearman 0.90–0.996
với exact ND — sàn 0.895 ở họ lognormal trước tinh chỉnh δ; lệch KR bị chặn +2–8%), nhanh hơn phương pháp hiện có 3 bậc ở n=800 và ở n≥10⁴ trên cây cho trước thì DPP chính xác không chạy nổi trong thời gian hợp lý.

**Trade-off trung thực (ghi thẳng trong paper):** EP-Sinkhorn chính xác hơn ở quy mô nhỏ
(n≲500) — ATSW đổi ~5% lệch KR lấy 3 bậc tốc độ. Người cần giá trị chính xác ở bài toán bé
vẫn nên dùng EP; ATSW dành cho learning/screening/đánh giá quy mô lớn.

## Phần lý thuyết còn mở (việc của advisor — không phải yếu tố giết)

1. Chứng minh ATSW → giá trị KR-nested khi δ→0 (số liệu: phần dư lượng tử hóa 0.004).
2. Chặn gap KR trên cây đa nhánh (số liệu: liên hệ Monge-violation, chu kỳ trước).
3. Topology mà ATSW metric hóa; tính tách điểm.

## Việc tiếp theo theo thứ tự giá trị

1. Viết bản thảo pitch hợp nhất (bài toán → 4 yếu tố giết đã loại → xây dựng → số liệu → câu hỏi lý thuyết) mang gặp advisor.
2. Ứng dụng minh chứng đầu tiên: metric đánh giá generative time series (Base F — gap hẹp đã xác minh) hoặc OT-reward RL (Base E — gap rộng đã xác minh). Cả hai dùng đúng ATSW này.
3. Bản biên dịch (numba/C) nếu cần mốc <1 phút ở n=100k.

*Sinh bởi workflow lặp, chu kỳ 2–3: 2 thí nghiệm so găng + 1 quét độ bền, không thẻ nào còn ở trạng thái nghi vấn với hướng chính.*
