# ATSW: định vị, mục tiêu, và trạng thái sẵn sàng viết paper

> **Tài liệu này là bản chi tiết của một phần. Bức tranh đầy đủ và hiện hành: `STATUS_REPORT.md`.**

*Mọi số trong tài liệu này đến từ thí nghiệm chạy tại chỗ (CPU laptop, 09/2026) hoặc từ truy vấn
thật. Bảng số: paper_table1_headtohead.csv, paper_table2_delta_sweep.csv, paper_table3_eps_sweep.csv.*

![So găng cùng máy]({{artifact:3155a746-4cba-41c5-9428-e5ce42594a90}})

## 1. Vì sao "vẫn còn bài mới" — nguyên nhân kỹ thuật, đã tìm ra

Hai vòng khảo sát trước đi bằng **từ khóa** nên phủ theo xác suất. Vòng này đi bằng **bao đóng
trích dẫn** trên OpenAlex, 4 vòng từ 20 hạt giống: **6.059 bản ghi**, trong đó 70 bài nhóm
adapted-tính-toán và 63 bài nhóm adapted-lý-thuyết được coi là **đóng kín**.

Và đây là nguyên nhân thật: **bao đóng trích dẫn mù với biên 2026** — bài mới chưa ai trích dẫn nên
không thể tới được bằng đường trích dẫn. Nhóm khảo sát phải thêm một lượt rà 33 cụm từ có giới hạn
ngày và tìm thêm **162 bài**. Kết luận cho workflow lâu dài: cần **cả hai** — bao đóng trích dẫn
cho chiều sâu, và rà theo ngày định kỳ cho biên mới. Không có cách nào "đóng" biên 2026 một lần
rồi xong; nó phải được rà lại theo lịch.

## 2. Vị trí — không ai chiếm ô của mình, nhưng phải phát biểu cho đúng

Luật máy móc (n ≥ 10⁴ **và** T ≥ 20) chỉ gắn cờ "nguy cơ cao" cho **3 trong 70** bài nhóm A.
Đọc kỹ cả ba thì **không bài nào tính adapted distance**:

| Bài | Quy mô | Nó thực sự làm gì |
|---|---|---|
| Scalable Bicausal OT qua nới KL (2605.17271, 2026) | n≈20.000 mẫu test, Nx=299 | Học **coupling** bằng policy gradient; giá trị là bản **nới KL**, chỉ về bicausal khi β→∞ |
| Time-Causal VAE (2026) | n=50.000, T=5 (60 bước tháng) | **Sinh** chuỗi tài chính, dùng chặn adapted làm ràng buộc — không phải bộ tính khoảng cách |
| COT-GAN (2020) | n=10.000, T=100 | **Loss huấn luyện** vị nhân quả, không phải metric |

Vị trí đúng, phát biểu được: **ATSW là bộ *tính* adapted distance duy nhất chạy ở T lớn và n lớn
cùng lúc.** Phân biệt sắc: *tính khoảng cách* ≠ *học coupling* ≠ *dùng mục tiêu vị nhân quả để
huấn luyện generator*. Đây là câu phải nằm ở đoạn đầu related work.

## 3. Kết quả so găng — trên instance của họ, code của họ, cùng máy

Sinh cây bằng `rand_tree_pichler` (chính generator của Eckstein–Pammer), chi phí Σ_t(x_t−y_t)²/4·udrange²
(chính hàm chi phí của họ), chạy DPP của họ (`solve_dynamic`) và ATSW trên cùng instance.

**Kiểm chứng trước đã: DPP chính xác tôi cài lại khớp giá trị code gốc của họ tới 5,6·10⁻¹⁷
trên cả 15 instance** — nên phần chuyển đổi instance là trung thực, không phải so hai bài toán khác nhau.

| nb (T=2) | đường đi | DPP chính xác | DPP-Sinkhorn ε=0,01 | ATSW δ=1 | nhanh hơn | sai số ATSW δ=1 | sai số ATSW δ=5 |
|---|---|---|---|---|---|---|---|
| 10 | 100 | 0,054 s | 0,35 s | 0,74 ms | ×72 | +22,6% | +21,8% |
| 25 | 625 | 1,66 s | 3,72 s | 0,9 ms | ×1.776 | +13,9% | +8,8% |
| 50 | 2.500 | 22,96 s | 29,74 s | 2,4 ms | ×9.653 | +9,7% | +1,5% |
| 75 | 5.625 | 105,9 s | 119,5 s | 7,6 ms | ×13.966 | +14,8% | +0,5% |
| 100 | 10.000 | 258,9 s | 264,3 s | 8,2 ms | ×31.580 | +23,4% | **−0,4%** |
| 10 (T=3) | 1.000 | 3,22 s | 21,87 s | 2,1 ms | ×1.551 | +22,4% | +20,1% |

Điểm mấu chốt: ở nb=100, **ATSW (δ=5) sai −0,4% trong 31 ms; DPP chính xác mất 259 giây.**
Khoảng cách **nở theo nb** (×72 → ×31.580) đúng như kế toán độ phức tạp dự đoán: DPP thăm mọi cặp
nút (đo được 98 → 6.207 cặp), ATSW chỉ thăm cặp có khối lượng dương.

**δ=1 là lượng tử hóa không mất mát** (support của họ là số nguyên), nên cột "sai số ATSW δ=1" là
**độ chệch thuần của ghép quantile so với LP** — đã tách hẳn khỏi lỗi lượng tử hóa. Con số đó
9,7–23,4%.

## 4. Ba điều phải nói thẳng trong paper

1. **δ có cực trị trong** (bảng 2): sai số trung bình theo δ = 1 / 2 / 5 / 10 / 20 là
   11,8% / 10,2% / 5,3% / 2,4% / 5,8%. Nghĩa là lượng tử hóa **thô hơn lại chính xác hơn** tới một
   ngưỡng — hai nguồn lệch triệt tiêu nhau (KR chệch lên, gộp ô chệch xuống). Đây là điểm yếu thật:
   **không chọn được δ tối ưu mà không có tham chiếu.** Cách trung thực để trình bày: báo δ=1
   (không mất mát, chệch thuần KR) là con số chính, và đưa quét δ vào phụ lục như một quan sát.
2. **Số shift gần như không ảnh hưởng** (1 vs 64 shift: 11,84% vs 11,84% ở δ=1). Giả thuyết
   "trung bình theo shift giảm chệch KR" **bị bác**. Phần "sliced" chỉ khử hiện vật lưới, không sửa
   chệch coupling — phải viết đúng như vậy.
3. **Baseline entropic của họ có cửa sổ ε rất hẹp** (bảng 3): ε=0,01 → +16…+24%; ε=0,001 → −4…−16%;
   ε ≤ 10⁻⁴ **vỡ số học** (giá trị sập về gần 0) — đúng như docstring của họ cảnh báo. Tôi
   **không** dùng con số này để nói "phương pháp của họ tệ": bài gốc báo sai số 0,04–0,10% bằng một
   cài đặt Sinkhorn-Markov **riêng** (`sinkhorn_bicausal_markov`), mà cài đặt đó **lỗi trên instance
   của tôi** vì nó giả định số con đồng nhất giữa các nút. Nên phát biểu đúng là: *ở cấu hình chạy
   được trong tay tôi, nhánh DPP-Sinkhorn của họ không đạt độ chính xác dưới 4%.*

## 5. Tiềm năng Q1/Q2 và venue

Bức tranh venue của nhóm A+B (từ corpus đóng kín): **48 bài chỉ ở arXiv**; tạp chí phân tán —
Annals of Applied Probability (5), Electronic Communications in Probability (4), SIAM J. Financial
Mathematics (4), SIAM J. Optimization (4), Stochastic Processes and their Applications (4),
Mathematics of Operations Research (3), Probability Theory and Related Fields (3),
Applied Mathematics & Optimization (2), Bernoulli (2), Computational Management Science (2),
Annals of Operations Research (2).

Phân bố theo loại venue (133 bài, 47 venue): preprint/repository **74 bài (56%)**;
tạp chí OR/tài chính 27 bài (14 venue); tạp chí xác suất/thống kê 19 bài (6 venue);
tạp chí khác 8; **venue ML chỉ 5 bài** — AAAI 2, NeurIPS 1, tạp chí ML 2. Nghĩa là venue ML
không vắng mặt hoàn toàn nhưng ở mức bên lề (4%), trong khi dòng tree-sliced của chính nhóm bạn
đi ICML/ICLR. ATSW nằm đúng chỗ giao: *phương pháp* mang chất
ML (sliced, tree), *bài toán* mang chất OR/xác suất. Hai đường nộp, hai cách đóng khung:

- **Đường OR/tính toán (khuyến nghị cho Q1/Q2 chắc tay):** Applied Mathematics & Optimization,
  Annals of Operations Research, Computational Management Science, SIAM J. Financial Mathematics.
  Đóng khung: "bộ tính adapted distance mở rộng được quy mô", bảng so găng là trung tâm.
  Đây là nơi FVI (2306.12658) và nested Sinkhorn (2102.05413) đã đăng — tức reviewer đúng chuyên môn.
- **Đường ML:** AISTATS/ICML, hoặc tạp chí Machine Learning / TMLR. Đóng khung: metric adapted
  tính được cho học biểu diễn chuỗi; cần thêm một ứng dụng học máy.

*Lưu ý: phân loại Q1/Q2 ở trên là đánh giá của tôi theo hiểu biết chung về các tạp chí này, không
phải dữ liệu JCR truy được trong phiên này — bạn nên tự kiểm quartile trước khi chọn.*

## 6. Đã đủ để bắt tay viết chưa — có, cho một paper "thuật toán + thực nghiệm"

Đã có:
- **Đóng góp khái niệm**: cách đọc cây quyết định topology (counterexample: đọc phẳng → giới hạn
  sai 4,0 vs 1,30; lex → sập về W tĩnh; đọc lồng → khớp chính xác 1+ε).
- **Thuật toán**: đọc lồng vector hóa, chi phí output-sensitive theo số mảnh ghép S; khớp riêng từng độ sâu cho S ~ n^1,24 (T=10) đến n^1,34 (T=50) — số mũ trôi lên theo độ sâu, không phải hằng số (bảng: paper_table8_scaling.csv).
- **Bảng so găng chuẩn** (mục 3) trên instance và code của đối thủ, cùng máy, kèm kiểm chứng khớp
  giá trị 5,6·10⁻¹⁷.
- **Quy mô tính toán chưa ai công bố**: n=10⁵, T=100 trong 602 s trên CPU laptop — **chỉ là mốc
  chi phí tính, KHÔNG phải mốc độ chính xác** (xem mục 8: ở T sâu với đường đi lấy mẫu, giá trị bị
  chệch lên rất mạnh).
- **Độ bền**: 5 họ quá trình, Spearman 0,90–0,996 với nested distance chính xác.

Còn thiếu, theo thứ tự chặn đường:
1. **So găng với FVI (2306.12658)** — kỷ lục trục thời gian, có code công khai (`FVIOT`), cần torch.
   Đây là baseline **bắt buộc** còn lại; không có nó, reviewer sẽ hỏi ngay.
2. **Một ứng dụng** — đánh giá generative time series (khoảng trống hẹp đã xác minh) là rẻ nhất.
3. **Định lý hội tụ δ→0** và **chặn S theo lớp quá trình** — phần của advisor; paper vẫn đăng được
   dạng "thuật toán + thực nghiệm" nếu chưa có, nhưng có thì lên hạng venue.
4. **Đa chiều** — mới test 2-D/16 hướng.

## 7. Giới hạn của khảo sát (nhóm khảo sát tự khai)

Nhóm A/B đóng kín; **nhóm C (700 bài "nhanh nhưng không adapted") KHÔNG đóng kín** — chỉ là mẫu
sâu một bước, vì 15 hub OT tổng quát có 22.641 bài trích ngược nên bị chặn có chủ ý. Quy mô thí
nghiệm chỉ đọc full text cho **17/70** bài nhóm A; 53 bài còn lại chỉ dựa trên abstract, nên mọi
khẳng định "bài này không có thí nghiệm" là **tạm thời**. Khoảng 755 id (~13%) không fetch lại được
và không được phân loại. arXiv API bị 429 suốt phiên nên metadata đi qua OpenAlex.


## 8. Kết quả âm tính quyết định: hai chế độ thông tin (thí nghiệm 09/2026)

![Hai chế độ]({{artifact:a8770eb1-71fc-4d04-956a-c470045a1bfc}})

Chạy code gốc FVI (2306.12658, `FVIOT`) trên CPU tại chỗ: bài toán hai bước ngẫu nhiên Gauss
(σ=1,0 và 0,5, x₀=1, y₀=2, T=8, chi phí Σₜ|xₜ−yₜ|²). Với quá trình gia số độc lập, ghép gia số theo
từng bước cho **chân lý = 17,0**. FVI cho **17,484 ± 0,576 trong 14,2 s/instance** (3 instance) —
lệch **+2,9%**, khớp chân lý.

ATSW trên **đường đi lấy mẫu từ cùng quá trình** lệch **+42% đến +79%** (bảng 4), giảm rất chậm
theo n. Khớp log-log trên 3 điểm: chệch ≈ 348·n^(−0,19) → **để xuống 5% cần n ≈ 4·10⁹ đường đi**
(ngoại suy 3 điểm, chỉ nên đọc ở cấp bậc độ lớn).

Hai cách sửa đã thử và **đều thất bại**:
- **δ tăng theo độ sâu** (làm thô dần để nút đủ mẫu): tệ hơn hẳn, tới +460%. Nguyên nhân: ô thô thì
  tâm ô cách nhau 64–305 trong khi biên độ quá trình chỉ ~2,8 — sai số **chi phí** lấn hết lợi ích.
- **Ô thích nghi theo phân vị, đại diện = trung bình ô** (mô phỏng ý tưởng k-means của
  Eckstein–Pammer): cũng tệ hơn lưới cố định (+73…+128%). Với m ô mỗi tầng và T=8 tầng, số lịch sử
  khả dĩ là m⁸ nên vẫn cạn mẫu.

**Chẩn đoán, và đây là điểm phải nằm trong paper:** chệch **không** đến từ ghép quantile mà đến từ
**lượng thông tin đầu vào**. Đọc code FVI thấy nó lấy mẫu trạng thái kế tiếp từ **chính kernel thật**
(`MultivariateNormal(loc=x_t, cov=σ²I)`) — tức FVI là phương pháp **cần mô hình**. Cây kịch bản của
Eckstein–Pammer cũng là mô hình cho trước. ATSW chỉ dùng **đường đi**.

Nên đối chiếu đúng đắn là:

| Đầu vào | Phương pháp | Chệch |
|---|---|---|
| Cây/mô hình cho trước | ATSW (T=2, nb=50) | +9,7% |
| Chỉ đường đi lấy mẫu | ATSW (T=8, n=5·10⁴) | +42,4% |
| Mô hình (kernel lấy mẫu được) | FVI (T=8) | +2,9% |

**Hệ quả cho phát biểu của paper:** vùng hợp lệ của ATSW là **khi cây/mô hình cho trước**, hoặc
T vừa phải so với n. Ở chế độ chỉ-có-đường-đi với T sâu, mọi bộ ước lượng nested đều gánh chệch
adapted-empirical-measure — đây là giới hạn **thống kê của đại lượng**, không phải lỗi thuật toán;
và ATSW làm phần *tính* rẻ đi chứ không sửa được phần *thống kê*.

**Và đây là câu trả lời sâu nhất cho "vì sao ô này trống lâu":** không phải vì thiếu thuật toán
nhanh, mà vì bài toán **thống kê** khó. Cả hai nhóm cạnh tranh đều tránh chế độ đường-đi-lấy-mẫu ở
T sâu — README của FVIOT ghi thẳng rằng adapted empirical measure với k-means *cần rất nhiều mẫu*,
nên họ dùng cây nhị phân không tái hợp thay thế; bản không gom của Eckstein–Pammer thì *dừng ở n=2000*.

**Câu hỏi lý thuyết thứ 5, và có lẽ là câu giá trị nhất:** cần bao nhiêu đường đi để một bộ ước
lượng nested đạt sai số ε ở độ sâu T, và có thể **chính quy hóa cây** (gộp giữa các nút cùng cấp,
co về phân phối biên) để giảm chệch không? Câu này nối thẳng vào dòng *adapted empirical measures*
(2211.10162, 2401.14883) đang nóng — đúng phần một advisor lý thuyết có thể nhận.


## 9. Cải tiến thuật toán: k-Markov ATSW (thí nghiệm 09/2026)

![k-Markov]({{artifact:40c5e587-41ee-47b6-9e59-a8e987f01f36}})

**Ý tưởng.** Điều kiện hóa theo **cửa sổ k bước cuối** thay vì toàn bộ lịch sử. Số nút khi đó bị
chặn bởi (số ô)^k — **không tăng theo T** — nên hết cạn mẫu, mà giá trị ô vẫn giữ nguyên độ mịn
nên chi phí không bị sai như khi làm thô δ. Cấu trúc vẫn là nested DP vị nhân quả hai chiều;
điểm khác với Eckstein–Pammer vẫn nguyên: mỗi cặp nút dùng **ghép quantile O(b log b)** thay cho
LP O(b³)/Sinkhorn. Hậu thuẫn từ văn liệu: `get_meas_for_sinkhorn` của họ ghi *"Only implemented for
Markovian measures"* — cả dòng cạnh tranh đã giả định Markov.

**Kết quả 1 — bước ngẫu nhiên Gauss, T=8 (chân lý 17,0):**

| n | lịch sử đầy đủ | k=1 (m=40) | FVI (cần mô hình) |
|---|---|---|---|
| 2.000 | +78,8% | +11,3% | — |
| 10.000 | +62,3% | +7,8% | — |
| 50.000 | +42,4% (9,7 s) | **+1,7% (0,92 s)** | +2,9% (14,2 s) |

Ở n=50.000, k=1 vượt FVI ở cả hai cấu hình, mà **chỉ dùng đường đi — không cần mô hình**:
m=40 cho +1,73% trong 0,92 s (chính xác hơn FVI, nhanh hơn **15×**); m=80 cho +1,43% trong 3,4 s
(chính xác hơn nữa, nhanh hơn **4×**).

**Kết quả 2 — cây không Markov, T=4, b=3 (chân lý bằng DP chính xác = 5,7947):**

| | k=1 | k=2 | k=3 | lịch sử đầy đủ |
|---|---|---|---|---|
| n=5.000 | −1,02% | +0,69% | +0,69% | +2,27% |
| n=50.000 | −2,73% | +0,23% | +0,23% | +1,16% |

**Hai chiều lệch ngược nhau, và đó là điểm hay nhất:** k quá nhỏ → điều kiện hóa quá ít → chệch
**xuống**; lịch sử đầy đủ với mẫu hữu hạn → điều kiện hóa quá nhiều → chệch **lên**. Nên k là một
knob có nghĩa thống kê rõ ràng (bộ nhớ hiệu dụng của quá trình) với **cực trị trong** — khác hẳn δ,
vốn chỉ đánh đổi hai loại lỗi kỹ thuật.

**Hệ quả cho paper.** Đóng góp thuật toán được phát biểu lại thành: *k-Markov adapted tree-sliced
readout* — họ metric nội suy giữa Wasserstein tĩnh (k=0) và adapted đầy đủ (k=T), với ghép quantile
thay cho LP/Sinkhorn ở mỗi cặp trạng thái. Nó vừa sửa được giới hạn thống kê ở mục 8, vừa giữ
nguyên lợi thế tốc độ ở mục 3.

**Giới hạn của loạt thí nghiệm này (phải ghi trong paper).** Mới hai quá trình, một chiều;
k=2 và k=3 cho kết quả giống hệt trên cây T=4 vì cửa sổ đã bão hòa ở độ sâu đó, nên **loạt này
không tách được k=2 khỏi k=3**; chưa có quy tắc chọn k từ dữ liệu; chưa thử k>1 ở T sâu.

**Câu hỏi lý thuyết mới (thứ 6), sắc và có thể trả lời:** khoảng cách k-adapted hội tụ về adapted
đầy đủ nhanh thế nào theo k, và với tốc độ phụ thuộc đại lượng trộn (mixing) nào của quá trình?
Ghép với câu thứ 5 (cần bao nhiêu mẫu ở độ sâu T) thì có một **đánh đổi chệch–phương sai theo k**
— đây là dạng kết quả một advisor lý thuyết nhận trọn được, và nó cho quy tắc chọn k.


## 10. Đổi sang lưới cố định để định lý phủ được code (09/2026)

Mục 9 dùng ô chia theo **phân vị mẫu gộp** — biên ô ngẫu nhiên, nên chứng minh nhất quán (vốn giả
định phân hoạch cố định) **không phủ** được ước lượng đang chạy. Thay vì mở rộng định lý sang ô ước
lượng (khó hơn hẳn), tôi kiểm xem đổi sang lưới cố định thì mất gì.

**Toàn bộ cấu hình đã chạy, không cắt dòng nào:**

| Chuẩn | Cấu hình | Ô phân vị (cũ) | Lưới cố định | Bên nào tốt hơn |
|---|---|---|---|---|
| Gauss T=8, n=50k | k=1 | +1,73% / 0,92 s | **+1,24%** (δ=0,125) / 1,97 s | lưới cố định |
| Cây không Markov, n=5k | k=1 | **−1,02%** | −2,68% | ô phân vị |
| Cây không Markov, n=5k | k=2 | **+0,69%** | +1,05% | ô phân vị |
| Cây không Markov, n=50k | k=1 | **−2,73%** | −4,17% | ô phân vị |
| Cây không Markov, n=50k | k=2 | +0,23% | **+0,07%** | lưới cố định |

**Kết luận trung thực: lưới cố định tệ hơn ở 3/5 cấu hình.** Nó chỉ thắng ở chuẩn Gauss và ở điểm
vận hành tốt nhất của chuẩn cây (n lớn, k=2). Ở k=1 — vốn đã là chế độ điều kiện hóa quá ít — lưới
cố định làm chệch nặng thêm (−4,17% so với −2,73%), và đó là khoảng cách lớn nhất trong cả bảng.

Vậy đây **không phải** một cải tiến. Đây là một **đánh đổi có chủ đích**: nhận thêm chệch ở chế độ
k thấp để lấy về một estimator mà định lý phủ được. Lý do nhận đánh đổi: ở cấu hình sẽ dùng thật
(k tại cực trị trong, n lớn) hai bên tương đương — chênh 0,16 điểm phần trăm, đổi chiều tùy chuẩn.

Giá thứ hai: ở chuẩn Gauss cần δ mịn hơn nên chậm ~2×. Và δ có **cực trị trong** giống k —
δ=0,0625 tệ hơn δ=0,125 (+1,38% vs +1,24%), vì ô quá nhỏ thì lại cạn mẫu.

**Estimator của paper từ nay là bản lưới cố định** (`atsw_fixedgrid.py`): ô = ⌊(x−s)/δ⌋, đại diện =
tâm ô, cả hai tất định khi (δ, s) cho trước; trung bình trên s ~ U[0,δ) giữ phần "sliced". Kiểm đúng
đắn: ví dụ ε cho đúng 1,3000.

**Hệ quả:** giả thiết "phân hoạch cố định" giờ khớp code; cổng G3 chuyển từ FAIL sang khớp, cả bốn
cổng sạch. Việc hình thức hóa mệnh đề nhất quán không còn vướng khoảng cách này.

**Giới hạn:** δ tối ưu vẫn quét thủ công; chưa có quy tắc chọn δ từ dữ liệu; quan hệ δ↔k chưa khảo
sát; và chưa kiểm liệu lưới cố định có thu hẹp khoảng cách ở k=1 khi δ mịn hơn nữa hay không.
