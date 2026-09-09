# ATSW — adapted OT từ đường đi, với chứng nhận tại gốc

Repo đóng gói từ artifact store (không phải từ workspace tạm). Mọi file là bản mới nhất.

## Cấu trúc

    algo/      estimator và các biến thể inner solver theo chu kỳ thiết kế lại
    certify/   pipeline chứng nhận hai phía (cận trên = đánh giá chính sách, cận dưới = pool đối ngẫu)
    probes/    thí nghiệm phán quyết, mỗi file có TIÊU CHÍ GIẾT trong docstring
    lean/      chứng minh nhất quán đã máy kiểm (Lean 4.33 + mathlib v4.33)
    data/      số đo thô + sổ tuyên bố
    figs/      hình đã dùng để báo cáo
    notes/     tài liệu vận hành, đọc literature, packet advisor

## Điểm vào

    python certify/run_all_cells.py     # lưới 5 ô, k=1 và k=2, kế toán một đồng hồ
    python certify/certify5.py          # pipeline chứng nhận, đã sửa 4 lỗi cận dưới
    python probes/probe_hypotheses.py   # ba probe tầng giả thuyết (H1/H2/H3)

Phụ thuộc: numpy, scipy, POT (`pip install pot`).

## Trạng thái (bản chạy mới nhất, seed base 70M)

| ô | trạng thái | U0 lệch | chứng nhận (U-L)/L | đạt ≤0,5% | %LP so DP chính xác |
|---|---|---|---|---|---|
| k=1 δ=0,5  T=50 | 23  | 0,182% | 0,241% | có | 37,6% |
| k=1 δ=0,3  T=50 | 37  | 0,048% | 0,054% | có | 101,9% |
| k=1 δ=0,18 T=50 | 60  | 0,072% | 0,117% | có | 117,7% |
| k=2 δ=1,0  T=15 | 61  | 0,004% | 0,037% | có | 48,7% |
| k=2 δ=0,7  T=15 | 101 | 0,003% | 0,743% | KHÔNG | 74,9% |

Tính hợp lệ (L0 <= V* <= U0): 5/5 ô. Điều kiện dừng dùng (U0-L0)/L0, không dùng V*.

## Việc còn mở

1. Giữ pool đối ngẫu xuyên các bước leo thang — hiện giải lại từ đầu, nên hai ô k=1 mịn
   dùng nhiều bài con hơn cả DP chính xác (101,9% và 117,7%); ba ô còn lại tiết kiệm được
   (37,6% / 48,7% / 74,9%), nhưng giờ chạy chỉ tốt hơn ở ô k=1 δ=0,5 (0,71x).
2. Chưa chạy: cost trị tuyệt đối, họ quá trình khác AR(1), nhiều seed mỗi ô.
3. Thư mục Lean (atswproof/ + .elan) không còn; muốn build lại phải dựng lại toolchain.
