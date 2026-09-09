# ATSW — note tham chiếu

*Sinh tự động từ `content/model.yaml` + `content/screens.yaml`. Đừng sửa file này.*

## Người đọc được giả định

**Advisor lý thuyết (xác suất / OT) và thành viên lab. Người trình có background RL, ML, OT cơ bản.**

**Đã biết:**
- xác suất cơ bản: biến ngẫu nhiên, kỳ vọng, phân phối, xác suất điều kiện
- optimal transport và Wasserstein cổ điển ở mức định nghĩa
- ML/RL cơ bản: loss, reward, mô hình sinh

**Chưa biết (nên deck phải định nghĩa):**
- adapted / nested optimal transport
- nested distance của Pflug–Pichler
- tree-sliced Wasserstein (kể cả hai bài TTSW/OTSW của nhóm)
- ghép kiểu Knothe–Rosenblatt
- nested Sinkhorn của Eckstein–Pammer
- mọi quy ước và tên riêng nội bộ của nhóm

## Từ điển đầy đủ

*(Note được phép có từ điển; deck thì không — mọi thuật ngữ đã định nghĩa tại chỗ dùng đầu tiên.)*

| Thuật ngữ | Định nghĩa ở màn | Nghĩa |
|---|---|---|
| **cây kịch bản** | S1 | Cách vẽ một quá trình ngẫu nhiên theo thời gian: từ hiện tại toả ra các khả năng, mỗi khả năng lại toả tiếp. Cả deck này chỉ nói về khoảng cách giữa hai cây kịch bản. |
| **nút** | S1 | Một trạng thái tại một thời điểm, cộng với toàn bộ lịch sử dẫn tới nó. Đứng ở một nút, bạn biết đúng những gì đã xảy ra tới lúc đó — không hơn. |
| **nhánh** | S1 | Một khả năng xảy ra tiếp theo, kèm xác suất. Trong deck này mọi nhánh đều có xác suất 1/2 cho gọn. |
| **đường đi** | S1 | Một tương lai có thể, từ gốc tới lá. Cả cây = phân phối trên các đường đi. |
| **lá / kết cục cuối** | S1 | Giá trị ở thời điểm cuối — thứ mà mọi metric “chỉ nhìn kết quả” quan sát được. Toàn bộ vấn đề của deck: hai cây có thể có cùng tập lá, cùng xác suất lá mà vẫn khác nhau về bản chất. |
| **n và T** | S1 | n = số đường đi mẫu (kích thước dữ liệu). T = số thời điểm (độ dài chuỗi). |
| **quy ước chi phí** | S1 | Chi phí ghép hai đường đi = tổng theo từng thời điểm của |xt − yt|. Khoảng cách giữa hai cây = chi phí ghép trung bình nhỏ nhất. Mọi con số trong deck phụ thuộc quy ước này. |
| **Wasserstein cổ điển** | S2 | Khoảng cách giữa hai phân phối đường đi, trong đó phép ghép được phép nhìn trọn cả tương lai trước khi quyết định ghép đường nào với đường nào. Chính chỗ “được phép” này là nguồn của vấn đề. |
| **adapted (= nested = causal = bicausal)** | S2 | Bốn tên cho cùng một ý: phép ghép chỉ được dùng thông tin đã biết đến thời điểm đó, không được nhìn trước. “Nested distance” là tên của Pflug–Pichler cho phiên bản trên cây. |
| **cách đọc (readout)** | S4 | Có cây rồi vẫn chưa có số. Phải chọn quy tắc ai-ghép-với-ai: đường đi nào của cây này ghép với đường nào của cây kia, theo thứ tự nào, và được dùng thông tin gì khi ghép. Quy tắc đó gọi là cách đọc. Cùng một cây, khác cách đọc là khác đáp số. |
| **điều kiện hóa theo lịch sử** | S4 | Chỉ so sánh các nút có cùng quá khứ với nhau: chia các nút thành từng nhóm theo lịch sử rồi làm việc trong từng nhóm, không ghép chéo giữa các nhóm. |
| **ghép quantile** | S4 | Sắp hai nhóm số theo thứ tự tăng dần rồi ghép số thứ k với số thứ k. Trong một chiều đó là cách ghép tối ưu, và sau khi sắp xếp thì chi phí tuyến tính. |
| **lượng tử hóa phi-dự-đoán** | S5 | Gom n đường đi mẫu thành một cây: cắt theo thời gian trước, rồi mới theo giá trị. Thứ tự này là điều kiện để cây không “nhìn trước tương lai”. Đây là cấu trúc lấy từ TTSW. |
| **δ** | S5 | Bước lưới khi cắt theo giá trị. δ càng mịn thì cây càng gần quá trình thật và sai lệch càng nhỏ, nhưng chi phí càng tăng. Đây là biến điều khiển chính của độ chính xác ở màn 7. |
| **DP lá → gốc** | S5 | Quy hoạch động: tính ở lát thời gian cuối trước, rồi dùng kết quả đó để tính lát trước nó, cứ thế lùi về gốc. Nhờ vậy mỗi lát chỉ phải làm một lần. |
| **lát (slice)** | S5 | Một lần đọc cây với một lưới cụ thể. Mỗi lát cho một con số; kết quả cuối là trung bình nhiều lát. |
| **hướng chiếu** | S5 | Khi giá trị nhiều chiều, mỗi lát chiếu dữ liệu xuống một đường thẳng ngẫu nhiên rồi mới đọc. Trung bình trên nhiều hướng chiếu là ý “sliced”. |
| **TTSW / OTSW** | S5 | Hai bài đã có của nhóm về tree-sliced Wasserstein: chúng đóng góp cấu trúc cây và kỹ thuật slicing. ATSW dùng lại đúng hai thứ đó và thay cách đọc. |
| **topology mà một metric sinh ra** | S5 | Nói gọn: metric quyết định “dãy nào coi là hội tụ về đâu”. Hai cách đọc cho hai topology khác nhau nghĩa là chúng không đo cùng một khái niệm gần nhau, chứ không phải chỉ lệch hằng số. |
| **phân phối biên** | S3 | Phân phối của giá trị tại từng thời điểm xét riêng lẻ, bỏ đi quan hệ giữa các thời điểm. Khớp phân phối biên là điều kiện rất yếu: hai cây A/B ở màn 2 khớp nhau ở mọi biên. |
| **Sinkhorn / entropic regularization** | S6 | Cách giải OT bằng cách thêm một lượng “làm mượt” (entropic regularization) rồi lặp, đổi một chút chính xác lấy tốc độ và tính khả vi. Nhanh và chính xác trên bài nhỏ. |
| **cặp nút** | S6 | Mỗi nút của cây này ghép với mỗi nút của cây kia. Baseline phải giải một bài OT nhỏ cho từng cặp, nên số cặp nút — không phải n — mới là thứ quyết định chi phí của nó. |
| **nested distance chính xác** | S6 | Giá trị adapted đúng, tính bằng định nghĩa không xấp xỉ. Chỉ tính được ở n nhỏ — đó là lý do vừa cần nó làm mốc, vừa cần ATSW cho quy mô lớn (ở n = 100.000 thì không có mốc nào). |
| **tương quan Spearman** | S7 | Tương quan thứ hạng: hỏi hai cách chấm điểm có xếp cùng thứ tự hay không, không hỏi giá trị có bằng nhau hay không. 1.0 = thứ tự trùng khớp hoàn toàn. |
| **năm họ quá trình** | S7 | Gauss (chuẩn) · Student-t(3) (đuôi nặng) · Lognormal (lệch phải, đuôi nặng) · Lattice (giá trị rời rạc trên lưới) · Trend (có xu thế theo thời gian). |
| **KR (Knothe–Rosenblatt)** | S9 | Cách ghép hai phân phối bằng cách xử lý từng toạ độ theo quantile, có điều kiện hóa theo các toạ độ trước. “Giá trị nested (KR)” = mốc đúng mà phép đọc lồng đang xấp xỉ. |
| **gap KR** | S9 | Khoảng chênh giữa giá trị ATSW và mốc KR-nested. Phần do δ chưa mịn gọi là phần dư lượng tử hóa. |
| **tính Monge** | S9 | Một phép ghép là Monge nếu mỗi điểm bên này đi về đúng một điểm bên kia (không xẻ khối lượng). Toán tử DP của chúng tôi giữ được tính chất này trên cây nhị phân; trên cây đa nhánh thì không hẳn. |
| **chặn bi-Lipschitz** | S9 | Chặn hai chiều dạng c₁·d ≤ ATSW ≤ c₂·d với d là adapted Wasserstein thật. Có chặn này thì ATSW không chỉ “xếp hạng giống” mà còn kiểm soát được sai lệch. |
| **tách điểm và bất đẳng thức tam giác** | S9 | Hai điều kiện để một hàm khoảng cách xứng đáng gọi là metric: khác nhau thì khoảng cách phải dương (tách điểm), và đi đường vòng không được rẻ hơn đi thẳng (bất đẳng thức tam giác). |
| **adapted empirical measures** | S9 | Dòng kết quả về việc lấy n mẫu từ một quá trình rồi hỏi cây thực nghiệm hội tụ về quá trình thật nhanh cỡ nào — theo nghĩa adapted, không phải nghĩa cổ điển. |
| **shifted-grid quantization** | S9 | Lượng tử hóa bằng lưới có gốc lệch ngẫu nhiên — đúng cái ATSW đang dùng ở chữ S. |
| **phản ví dụ số** | S9 | Một cặp cây cụ thể, dựng bằng số, trên đó tính chất mong muốn không đúng — dùng để chặn hướng chứng minh sai. |
| **TemporalOT** | S10 | Một phương pháp imitation learning dùng OT có mặt nạ thời gian, giải bằng Sinkhorn. Đây là chỗ ATSW có thể thay vào. |
| **COT-GAN** | S10 | Mô hình sinh chuỗi thời gian dùng causal OT làm loss. Dòng loss đã có người làm; dòng đánh giá thì chưa. |

## Sổ số liệu — mỗi con số kèm toàn bộ field

### f_classic — ε
- **kind**: closed_form
- **what**: Wasserstein cổ điển giữa cặp cây A/B
- **convention**: quy ước chi phí

### f_adapted — 1 + ε
- **kind**: closed_form
- **what**: khoảng cách adapted giữa cặp cây A/B
- **convention**: quy ước chi phí

### f_lex — ε
- **kind**: closed_form
- **what**: giá trị của cách đọc một lượt (lex) — trùng đúng Wasserstein cổ điển
- **convention**: quy ước chi phí

### f_flat — 4.00
- **kind**: open
- **what**: giá trị của cách đọc phẳng trên cặp cây A/B
- **known**: Không phản ứng với ε — tức là hội tụ về một giới hạn sai.
- **CÒN THIẾU**: đo trên thang nào: 4.00 không cùng thang với 1 + ε, nên hiện chỉ so được HƯỚNG chứ không so được độ lớn; công thức / đoạn code sinh ra con số này

### f_truth_pair — 1.25 hay 1.30
- **kind**: open
- **what**: mốc đúng của cặp cây A/B
- **known**: Công thức đóng cho 1 + ε = 1.25 tại ε = 0.25; ghi chú nội bộ (pitch_unified.md §2) ghi 1.30.
- **CÒN THIẾU**: chốt từ code: nếu là 1.30 thì quy ước chi phí khác với quy ước đang khai báo ở màn 1

### f_ep_time — (dãy)
- **kind**: measured
- **what**: thời gian chạy của baseline nested Sinkhorn theo n
- **against**: đồng hồ treo tường, cùng dữ liệu đầu vào với ATSW
- **instances**: cặp cây sinh từ cùng một quá trình, n = 100…800
- **code**: bản cài lại của nhóm theo thuật toán Eckstein–Pammer 2022 — KHÔNG phải code của tác giả
- **series**: n=100 → 1.01s, n=200 → 3.41s, n=400 → 13.28s, n=800 → 50.33s
- **CÒN THIẾU**: ε của Sinkhorn và số vòng lặp; cấu hình máy cụ thể (chỉ biết: CPU laptop); chưa ghi dùng quy ước chi phí nào

### f_atsw_time — (dãy)
- **kind**: measured
- **what**: thời gian chạy của ATSW theo n
- **against**: đồng hồ treo tường, cùng dữ liệu đầu vào với baseline
- **instances**: cặp cây sinh từ cùng một quá trình, n = 100…800
- **code**: bản cài của nhóm
- **series**: n=100 → 0.0031s, n=200 → 0.006s, n=400 → 0.0113s, n=800 → 0.0299s
- **CÒN THIẾU**: δ dùng cho từng điểm đo; số lát (slice) trung bình trên; chưa ghi dùng quy ước chi phí nào

### f_speedup — ×1.683
- **kind**: derived
- **what**: tỉ lệ nhanh hơn tại n = 800
- **formula**: f_ep_time[-1] / f_atsw_time[-1]

### f_node_pairs — (dãy)
- **kind**: measured
- **what**: số cặp nút baseline phải xử lý
- **against**: đếm trực tiếp trong lúc chạy
- **instances**: cùng các cặp cây ở f_ep_time
- **code**: bản cài lại của nhóm
- **series**: n=100 → 79720cặp, n=800 → 4446582cặp
- **CÒN THIẾU**: chưa ghi dùng quy ước chi phí nào

### f_pieces — ~n^1.33
- **kind**: measured
- **what**: số mảnh ATSW phải xử lý, theo n
- **against**: đếm mảnh + benchmark
- **instances**: cùng họ quá trình với f_atsw_time
- **code**: bản cài của nhóm
- **CÒN THIẾU**: khoảng n dùng để fit số mũ 1.33; chưa ghi dùng quy ước chi phí nào

### f_bigrun — 10 phút @ n = 100.000, T = 100
- **kind**: measured
- **what**: lần chạy lớn nhất đã làm được
- **against**: đồng hồ treo tường
- **instances**: một cặp cây ở quy mô lớn
- **code**: bản cài của nhóm (Python, chưa biên dịch)
- **CÒN THIẾU**: cấu hình máy cụ thể; δ và số lát; chưa ghi dùng quy ước chi phí nào

### f_acc — baseline +0.1% · ATSW +5%
- **kind**: measured
- **what**: sai lệch tương đối so với nested distance chính xác
- **against**: nested distance chính xác (tính được vì n nhỏ)
- **instances**: cây nhỏ
- **CÒN THIẾU**: danh sách instance cụ thể và n của chúng; đây là trung bình hay trường hợp tệ nhất; chưa ghi code/đoạn nào sinh ra số này; chưa ghi dùng quy ước chi phí nào

### f_spearman — (dãy)
- **kind**: measured
- **what**: tương quan thứ hạng Spearman giữa ATSW và nested distance chính xác
- **against**: nested distance chính xác
- **instances**: 5 họ × 12 cặp cây
- **code**: bản cài của nhóm
- **rows**: Gauss=0.979, Student-t(3)=0.951, Lognormal=0.895, Lattice=0.944, Trend=0.958
- **CÒN THIẾU**: δ trước và sau khi tinh chỉnh, cho từng họ; chưa ghi dùng quy ước chi phí nào

### f_quant_residual — 0.004
- **kind**: measured
- **what**: phần dư lượng tử hóa còn lại khi làm δ mịn dần
- **against**: mốc KR-nested
- **instances**: chuỗi δ giảm dần trên cùng một cặp cây
- **CÒN THIẾU**: dãy δ đã thử; chưa ghi code/đoạn nào sinh ra số này; chưa ghi dùng quy ước chi phí nào

### f_monge_viol — 2.2%
- **kind**: measured
- **what**: mức vi phạm tính Monge của toán tử DP trên cây đa nhánh
- **against**: kiểm trực tiếp trên phép ghép thu được
- **instances**: cây đa nhánh; cây nhị phân gần như không vi phạm
- **note**: mức vi phạm tương quan với gap KR — đã có phản ví dụ số
- **CÒN THIẾU**: chưa ghi code/đoạn nào sinh ra số này; chưa ghi dùng quy ước chi phí nào

### f_triangle — 0/546
- **kind**: measured
- **what**: số lần vi phạm bất đẳng thức tam giác
- **against**: kiểm mọi tam giác trong hai bộ test
- **instances**: hai bộ test, tổng 546 tam giác
- **note**: là bằng chứng, KHÔNG phải chứng minh
- **CÒN THIẾU**: chưa ghi code/đoạn nào sinh ra số này; chưa ghi dùng quy ước chi phí nào

### f_multidim — 2-D, 16 hướng chiếu
- **kind**: measured
- **what**: phạm vi đã test cho trường hợp nhiều chiều
- **against**: —
- **instances**: chỉ 2 chiều
- **CÒN THIẾU**: hằng số slicing ở chiều cao — chưa làm; chưa ghi code/đoạn nào sinh ra số này; chưa ghi dùng quy ước chi phí nào

### f_litsearch — ~50 truy vấn, 0 hit
- **kind**: measured
- **what**: kết quả tìm xem đã có ai làm tree/sliced cho adapted OT
- **against**: arXiv, OpenAlex, Semantic Scholar
- **instances**: có kiểm bẫy đổi thuật ngữ: nested = adapted = causal = bicausal
- **note**: dòng entropic (Eckstein–Pammer) là baseline, không phải người chiếm chỗ
- **CÒN THIẾU**: chưa ghi code/đoạn nào sinh ra số này; chưa ghi dùng quy ước chi phí nào
