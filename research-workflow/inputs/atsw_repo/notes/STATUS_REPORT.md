# ATSW — Báo cáo trạng thái toàn diện
### Adapted Tree-Sliced Wasserstein: từ chỗ bắt đầu đến chỗ đang đứng

*Tài liệu đứng một mình: đọc từ đầu đến cuối là có đủ ngữ cảnh, không cần tài liệu nào khác.
Mọi con số đến từ thí nghiệm chạy tại chỗ hoặc truy vấn thật; bảng nguồn ghi ở từng mục.
Cập nhật 09/2026.*

---

## 0. Tóm tắt một trang

**Xuất phát:** nhóm có hai bài về tree-sliced Wasserstein cho chuỗi thời gian (TTSW —
Pattern Anal. Appl. 2026; OTSW — IEEE Access 2026). Cảm nhận ban đầu của tác giả: hướng này
chỉ còn đi ngang. Kiểm chứng cho thấy cảm nhận đó đúng — nhưng đúng về *nước đi*, không đúng
về *hướng*.

**Phát hiện trung tâm:** cùng một cây phi-dự-đoán, **cách đọc cây** quyết định metric bắt được
topology nào. Đọc phẳng kiểu TTSW hội tụ về **sai giới hạn**; đọc một lượt theo thứ tự từ điển
sập về Wasserstein tĩnh; chỉ **đọc lồng** (điều kiện hóa theo lịch sử rồi mới ghép) mới bắt được
adapted Wasserstein. Cấu trúc cây thời-gian-trước là **cần nhưng không đủ** — đây là bước tiến
khái niệm so với bài cũ, có phản ví dụ đóng.

**Thuật toán:** ATSW = cây lượng tử hóa phi-dự-đoán trên **lưới cố định** + đọc lồng theo cửa sổ
**k bước** + trung bình trên dịch lưới ngẫu nhiên. Mỗi cặp nút dùng ghép quantile O(b log b) thay
LP O(b³)/Sinkhorn.

**Bốn kết quả có bằng chứng:**
1. Trên cây cho trước, rẻ hơn DPP chính xác tới 4 bậc (nb=100: 258,9 s → 8,2 ms), cùng máy, dùng
   **code gốc** của đối thủ, kèm kiểm chứng khớp giá trị 5,6·10⁻¹⁷.
2. Ở chế độ chỉ-có-đường-đi tại T sâu, bản đọc lịch sử đầy đủ **chệch +42…+79%** — giới hạn
   **thống kê**, không phải lỗi thuật toán. Đây là kết quả âm tính định vị được ranh giới thật.
3. Cửa sổ **k-Markov** sửa được: Gauss T=8, n=50k → **+1,24%**, trong khi phương pháp cần-mô-hình
   tốt nhất (FVI) cho +2,9%. ATSW **chỉ dùng đường đi**.
4. k là knob có nghĩa thống kê với **cực trị trong**: k nhỏ → chệch xuống, lịch sử đầy đủ → chệch lên.

**Chỗ đứng so với thế giới:** không bài công bố nào chạm cả T lớn và n lớn. Nhưng phát biểu phải
hẹp: ở T nhỏ, phương pháp công bố nhanh tương đương.

**Việc còn lại:** một định lý. Hiện có rất nhiều số đo và chưa định lý nào — mà trong lĩnh vực này
đó chính là thứ phân biệt tạp chí hạng cao với arXiv.

---

## 1. Xuất phát điểm và chẩn đoán

TTSW/OTSW là **cùng một nước đi dùng hai lần**: tree-sampling với một quy tắc phân hoạch khác.
Nước đi đó còn vài biến thể nữa rồi hết, và mỗi biến thể là một bài Q2.

Bản đồ văn liệu ban đầu (997 bài, 2018–2026, từ 82 tham chiếu của TTSW + harvest từ khóa + trích
dẫn xuôi + quét arXiv trực tiếp) cho thấy dòng tổ tiên trực tiếp chỉ có ~12 bài, một nửa còn là
preprint, và nhóm 2024–25 là **một nhóm tác giả** quanh ý tưởng *systems of lines*.

![Bản đồ văn liệu]({{artifact:c7ab24dd-471b-49d2-9582-3aab45269f4a}})

Kết luận: cần đổi **loại đóng góp**, không phải đổi tham số.

---

## 2. Định vị: khoảng trống đã kiểm chứng

Hai vòng khảo sát bằng **từ khóa** liên tục để lọt bài mới. Vòng ba đi bằng **bao đóng trích dẫn**
(OpenAlex, 4 vòng, 20 hạt giống) → **6.059 bản ghi**; nhóm adapted đóng kín.

Và lý do cấu trúc của việc "vẫn còn bài mới" nằm ở đây: **bao đóng trích dẫn mù với biên mới** —
bài chưa ai trích thì không có đường trích dẫn dẫn tới. Phải bổ sung một lượt rà cụm từ + giới hạn
ngày, chạy **theo lịch**. Đó là quy tắc, không phải sơ suất một lần.

Khoảng trống đã xác minh: trong 57 bài causal/adapted OT — **0 bài dùng tree metric, 0 sliced,
0 nhắc linear-time**. Trong 41 bài OT-cho-imitation-learning — **0 dùng tree metric**.

---

## 3. Phát hiện khái niệm: cách đọc quyết định topology

Trên ví dụ chuẩn (nested distance = 1+ε):

| Cách đọc cùng một cây | Kết quả | Kết luận |
|---|---|---|
| Phẳng kiểu TTSW (L1 trên ô trụ) | δ→0 hội tụ về 4,0 ≠ 1,30 | **sai cả giới hạn** |
| Lex một lượt, O(n log n) | = ε | sập về Wasserstein tĩnh |
| **Đọc lồng** | **= 1+ε chính xác** | đúng adapted |

![Xây dựng ATSW]({{artifact:16b68961-eadb-4996-bb34-09fa75d91deb}})

Cơ chế của thất bại lex đã định vị được: nó ghép khối lượng **biên** trước khi điều kiện hóa, mà
điều kiện hóa với ghép **không giao hoán**.

---

## 4. Thuật toán và bằng chứng số

### 4.1 Trên cây cho trước — so găng bằng code gốc của đối thủ

Instance sinh bằng chính generator của Eckstein–Pammer, chạy cùng máy, hai nhánh code gốc của họ
(DPP-LP và DPP-Sinkhorn) so với ATSW. Support cây của họ là số nguyên nên δ=1 là **không mất mát** —
chênh lệch còn lại chỉ do ghép quantile thay LP.

![So găng]({{artifact:3155a746-4cba-41c5-9428-e5ce42594a90}})

Kiểm chứng chuyển đổi: DPP chính xác tôi cài lại **khớp code gốc của họ tới 5,6·10⁻¹⁷** trên 15
instance. Nguồn: `paper_table1_headtohead.csv`, `paper_table2_delta_sweep.csv`, `paper_table3_eps_sweep.csv`.

Một dữ kiện phải nói kèm: nhánh DPP-Sinkhorn của họ **không** hội tụ về giá trị đúng khi giảm ε —
nó vỡ số học dưới ε=0,01, đúng như docstring của họ cảnh báo.

### 4.2 Giới hạn thống kê ở chế độ chỉ-có-đường-đi

![Hai chế độ]({{artifact:a8770eb1-71fc-4d04-956a-c470045a1bfc}})

Chuẩn FVI (hai bước ngẫu nhiên Gauss, T=8, chân lý giải tích 17,0): FVI cho 17,484 (+2,9%) trong
14,2 s. ATSW đọc lịch sử đầy đủ trên đường đi lấy mẫu: **+42…+79%**, giảm như n^(−0,19) → cần
~4·10⁹ đường đi để xuống 5%.

Chẩn đoán, và đây là phần quan trọng nhất của mục này: **FVI lấy mẫu trạng thái kế tiếp từ chính
kernel thật** — nó **cần mô hình**. Cây kịch bản của Eckstein–Pammer cũng là mô hình cho trước.
ATSW chỉ dùng **đường đi**. Chệch đến từ **lượng thông tin đầu vào**, không từ ghép quantile.

Hai cách sửa đã thử và **đều thất bại**: δ thô dần theo độ sâu (+460%, vì sai số chi phí lấn hết);
ô thích nghi theo phân vị (+73…+128%, vì số lịch sử khả dĩ vẫn là m^T). Nguồn: `paper_table4_regime.csv`.

### 4.3 Cửa sổ k-Markov — cách sửa hiệu quả

![k-Markov]({{artifact:40c5e587-41ee-47b6-9e59-a8e987f01f36}})

Điều kiện hóa theo **k bước cuối** thay vì toàn bộ lịch sử: số nút bị chặn bởi (số ô)^k, **không
tăng theo T**, mà giá trị ô vẫn mịn. Hậu thuẫn văn liệu: hàm chuẩn bị dữ liệu của Eckstein–Pammer
ghi *"Only implemented for Markovian measures"* — cả dòng cạnh tranh đã giả định Markov.

| Chuẩn | Lịch sử đầy đủ | k-Markov | Đối chiếu |
|---|---|---|---|
| Gauss T=8, n=50k | +42,4% (9,7 s) | **+1,24%** (1,97 s) | FVI +2,9% (14,2 s), **cần mô hình** |
| Cây không Markov T=4, n=50k | +1,16% | **+0,07%** (k=2) | chân lý = DP chính xác |

k là knob hai chiều: k nhỏ → chệch **xuống** (điều kiện hóa quá ít); lịch sử đầy đủ → chệch **lên**
(mẫu cạn). Cực trị trong, có nghĩa thống kê (bộ nhớ hiệu dụng của quá trình).
Nguồn: `paper_table5_kmarkov.csv`.

### 4.4 Lưới cố định — một đánh đổi, không phải cải tiến

Để chứng minh nhất quán (giả định phân hoạch cố định) phủ được code, đã đổi từ ô-theo-phân-vị sang
lưới cố định. Toàn bộ 5 cấu hình đã chạy:

| Chuẩn | k | Ô phân vị | Lưới cố định | Tốt hơn |
|---|---|---|---|---|
| Gauss T=8, n=50k | 1 | +1,73% | **+1,24%** | lưới cố định |
| Cây, n=5k | 1 | **−1,02%** | −2,68% | ô phân vị |
| Cây, n=5k | 2 | **+0,69%** | +1,05% | ô phân vị |
| Cây, n=50k | 1 | **−2,73%** | −4,17% | ô phân vị |
| Cây, n=50k | 2 | +0,23% | **+0,07%** | lưới cố định |

**Lưới cố định tệ hơn ở 3/5 cấu hình**, nặng nhất ở k=1. Nhận đánh đổi này vì ở điểm vận hành thật
(k tại cực trị trong, n lớn) hai bên tương đương, và đổi lại định lý phủ được estimator.
Nguồn: `paper_table6_fixedgrid.csv`.

---

## 5. Chỗ đứng so với thế giới

![Bản đồ định vị]({{artifact:12526eb5-7007-4248-9a63-0dc80165fc1e}})

Hai trục, chưa ai chiếm cả hai. Trục số mẫu: Eckstein–Pammer, n=10⁴ trong **14,38 s** — nhưng
**T=3**, và tốc độ đến từ gom ~√n điểm mỗi mốc (bản không gom *"stopped after n = 2000"*). Trục
thời gian: fitted value iteration (2306.12658), **T=40, N=4.000 trong 257,7 s**, có code công khai.

Vì sao các bài "nhanh" khác không phải đối thủ, một dòng: sliced và tree-sliced đạt O(Ln log n)
**chính vì** OT 1-D và OT trên cây có nghiệm đóng — không có filtration nào phải tôn trọng.

**Tuyên bố đứng được:** lần đầu báo cáo tính adapted distance ở vùng T lớn **và** n lớn.
**Không** tuyên bố "nhanh hơn ×N" — đại lượng khác nhau, phần cứng khác nhau, và ở T nhỏ họ nhanh
tương đương.

---

## 6. Trạng thái lý thuyết

| # | Mệnh đề | Trạng thái | Bộ kiểm |
|---|---|---|---|
| 1 | Nhất quán của ước lượng k-Markov (m,k,T hữu hạn, lưới cố định) | **ĐÃ MÁY KIỂM — nhưng đích là SURROGATE, không phải AW** — `Vdp_consistent_ae`: Vdp(K̂)→Vdp(K) h.c.c. từ ước lượng đếm; hai vế cùng là Vdp (đã có ghép comonotone), KHÔNG có infimum trên tập ghép nối ⇒ không chứng minh hội tụ về AW. Chệch surrogate→AW: đo 10–20%, chưa có chặn. Lean 4.33 + mathlib, 35 kết quả, 613 dòng, 0 `sorry` | Lean — mạnh nhất |
| 2 | Phân phối tiệm cận; giới hạn **phi Gauss** tại tie | **đã kiểm số hai ca**, khớp hằng số | mô phỏng — mạnh |
| 3 | Chặn gap ghép quantile trên cây đa nhánh | mở | chỉ bác bỏ được |
| 4 | Chặn kích thước giá coupling S theo lớp quá trình | mở | **yếu** — cần người |
| 5 | Cần bao nhiêu mẫu ở độ sâu T; chính quy hóa cây có giảm chệch không | mở, sinh từ mục 4.2 | — |
| 6 | k-adapted → adapted khi k tăng, tốc độ theo mixing | mở, sinh từ mục 4.3 | — |

Mệnh đề 2 là kết quả tinh tế nhất đã có: toán tử ghép comonotone chỉ **khả vi theo hướng**, nên tại
chỗ hai CDF trùng nhau, delta method thường sai và giới hạn là ảnh phi tuyến của một Gauss. Kiểm số
xác nhận đến hằng số (half-normal; kỳ vọng 0,4514 dẫn tay vs 0,4535 mô phỏng).

---

## 7. Venue

Quartile là thuộc tính **tạp chí**; hội nghị ML **không có quartile** — nếu yêu cầu Q1/Q2 đến từ
học bổng hay quy chế thì đường tạp chí là đường duy nhất.

Đếm trên corpus: 21 bài adapted ở tạp chí hạng cao — hầu hết là **định lý**. 10 bài ở tạp chí
ứng dụng/OR — thuật toán + thực nghiệm. **42/100 bài nhóm tính toán không lọt tạp chí nào.**
Bài mẫu cần nhìn: *Computational methods for adapted optimal transport* nằm ở **Annals of Applied
Probability 2024** — một bài **tính toán** vào được tạp chí xác suất hạng cao, vì mang theo lý
thuyết hội tụ.

Kết luận: thứ nâng hạng ở đây không phải quy mô hay tốc độ, mà là **có chứng minh được gì không**.

---

## 8. Quy trình

Vận hành theo `claim-gated-research`: mọi tuyên bố phải có bộ kiểm; sổ `claim_ledger.csv` là nguồn
sự thật duy nhất về trạng thái; bốn cổng tự động (`wf_check.py`) canh bốn bất biến — tuyên bố đã
rút không sót, số trong tài liệu khớp CSV nguồn, giả thiết định lý khớp code, mệnh đề đã kiểm số
không hồi quy. Hiện: **0 FAIL**.

---

## 9. Mọi tuyên bố đã rút — để không ai dùng lại

| Đã rút | Bản đúng |
|---|---|
| "Nhanh hơn EP ×1 700" | So với bản EP tự cài, không phải runtime công bố (14,38 s @ n=10⁴, T=3) |
| "Duy nhất còn sống ở n≥10⁴" | Đúng là DPP *chính xác* không chạy nổi ở đó trên cây cho trước |
| "Không còn yếu tố nào đủ giết" | Sau đó tìm ra giới hạn thống kê (mục 4.2) |
| "Không hội nghị ML nào trong nhóm adapted" | Có 5/133 bài — bên lề, không vắng |
| "Chỉ 4 bài cạnh tranh về tốc độ" | 11 − 6 = **5** |
| "Quét đủ 14 bài cite TemporalOT" | **13** bài duy nhất; một bài đếm trùng hai nguồn |
| "Lưới cố định không mất mát" | Tệ hơn ở **3/5** cấu hình; là đánh đổi có chủ đích |
| "Metric adapted đầu tiên ở n≥10⁵" | Đúng về **chi phí tính**, không phải độ chính xác |

---

## 10. Việc tiếp theo

1. **Ứng dụng minh chứng** — phần lý thuyết đã đóng. Mệnh đề nhất quán nay là định lý máy
   bảo chứng (`Atsw.lean`, `LEAN_README.md`), nên việc còn thiếu để thành paper là một ứng
   dụng ngoài benchmark nội bộ.
2. Quy tắc chọn k và δ từ dữ liệu (reviewer chắc chắn hỏi).
3. Ứng dụng minh chứng: metric đánh giá generative time series, hoặc OT-reward cho imitation
   learning — hai khoảng trống đã xác minh, cùng dùng đúng estimator này.
