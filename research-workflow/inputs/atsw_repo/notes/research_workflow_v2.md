# Workflow nghiên cứu có kiểm chứng

> **Tài liệu này là bản chi tiết của một phần. Bức tranh đầy đủ và hiện hành: `STATUS_REPORT.md`.**

*Cách vận hành một chương trình nghiên cứu khi phần lớn lao động do agent làm và phần quyết định
vẫn thuộc về người. Thiết kế xoay quanh một đơn vị duy nhất — **tuyên bố** — và một câu hỏi duy
nhất đặt cho mọi tuyên bố: **cái gì kiểm được nó?***

---

## 1. Nguyên lý

Khối lượng tính toán chuyển hóa thành hiểu biết ở đúng những nơi tồn tại một **bộ kiểm** rẻ và đáng
tin. Ở nơi không có bộ kiểm, thêm khối lượng chỉ nhân bản độ bất định: N lời giải không kiểm được
tệ hơn một, vì bây giờ phải *chọn*, mà chọn chính là năng lực ta đang muốn thay thế.

Hệ quả thiết kế, và là quy tắc chi phối toàn bộ tài liệu này:

> **Không tăng số lần thử ở đỉnh. Làm bộ kiểm mịn hơn ở từng nút.**

Đây cũng là kiến trúc mà các harness hình thức hóa hiện đại dùng: phân rã thành DAG rồi đặt cổng
kiểm ở từng vòng, thay vì một lần chạy dài dễ vỡ.

---

## 2. Đơn vị công việc: tuyên bố

Mọi thứ chương trình sản xuất ra đều quy về **tuyên bố**. Một tuyên bố hợp lệ có đủ năm trường:

| Trường | Nội dung |
|---|---|
| `phát biểu` | Một câu, đủ chính xác để sai được |
| `nguồn` | Định danh thật (arXiv id / bảng số / artifact), resolve được |
| `bộ kiểm` | Thứ có thể bác bỏ nó |
| `độ mạnh bộ kiểm` | mạnh (xác nhận được) / một phần (chỉ bác bỏ được) / yếu (không kiểm được) |
| `trạng thái` | đề xuất → đã kiểm → **đứng** / **hẹp** / **rút** |

Hai quy tắc theo sau, và chúng là toàn bộ kỷ luật của workflow:

1. **Không bộ kiểm thì không nâng trạng thái.** Một tuyên bố "đề xuất" ở lại đó bao lâu cũng được;
   nó chỉ không được xuất hiện trong tài liệu như thể đã đứng.
2. **Trạng thái chỉ đi một chiều trong tài liệu.** Khi một tuyên bố bị hẹp lại hoặc rút, mọi nơi
   còn chứa nó phải mang nhãn — kể cả tài liệu cũ, kể cả hình.

Sổ: `claim_ledger.csv`. Đây là **nguồn sự thật duy nhất** về trạng thái; tài liệu văn xuôi là dẫn xuất.

---

## 3. Ba làn sinh tuyên bố

### Làn A — Văn liệu

Mục tiêu: biết chắc ô mình định đứng có trống không, và trống **vì sao**.

1. **Bao đóng trích dẫn** trên OpenAlex, 3–4 vòng hai chiều từ tập hạt giống. Cho ra phần cộng đồng
   đã liên kết với nhau — đóng kín được.
2. **Rà biên theo cụm từ + giới hạn ngày.** Bắt buộc và định kỳ, vì bao đóng trích dẫn **mù với bài
   mới chưa ai trích**. Đây là lý do cấu trúc khiến "vẫn còn bài mới" xuất hiện, không phải sơ suất.
3. Với mỗi đối thủ: đọc **full text**, lấy **nguyên văn** phát biểu độ phức tạp và quy mô thí nghiệm
   lớn nhất. Nếu chỉ đọc được abstract thì ghi rõ điều đó cùng tuyên bố.
4. Phân loại đối thủ theo **đại lượng họ tính**, không theo tốc độ họ khoe. "Nhanh" mà tính đại
   lượng khác thì không phải đối thủ, và cần một câu giải thích vì sao.

Tuyên bố từ làn này hợp lệ khi mọi định danh resolve được. **Không id thì không có tuyên bố.**

### Làn B — Thực nghiệm

Mục tiêu: một phán quyết, không phải một quan sát.

1. Thẻ giả thuyết mở bằng **tiêu chí giết**: con số nào thì bỏ hướng này. Viết trước khi chạy.
2. Chạy **thí nghiệm rẻ nhất phân biệt được** trước. Kết thúc bằng ĐẬU / SỬA / GIẾT; không để
   trạng thái "nghi vấn" tồn tại qua đêm.
3. **So găng dùng code gốc của đối thủ, trên instance của họ, cùng máy.** Bản tự cài lại chỉ để hiểu
   cơ chế; nó **không** được dùng để tuyên bố tỷ lệ. Tỷ lệ đối với một bản cài không phải của họ là
   tỷ lệ với chính mình.
4. Khi chuyển đổi định dạng dữ liệu giữa hai hệ: **kiểm chứng khớp giá trị** trước, tin thời gian sau.
5. Kết quả âm tính là kết quả. Ghi kèm **cơ chế** — "hỏng ở đâu và vì sao" đáng giá hơn "chạy được".

### Làn C — Lý thuyết

Mục tiêu: biến số đo thành bảo đảm — ở đúng những chỗ làm được.

1. Phân rã mệnh đề thành **DAG bổ đề**.
2. Mỗi nút phải mang **một trong hai**: một phép kiểm số **phản chứng được**, hoặc một phát biểu
   hình thức hóa. Nút không có cả hai mang nhãn `UNVERIFIED`.
3. **Fan-out N=8 chỉ ở nút có bộ kiểm.** Ở nút `UNVERIFIED`, fan-out bị cấm: nó tạo ra nhiều văn bản
   hợp lý không phân xử được. Đó là nơi duy nhất cần người.
4. Bộ kiểm phải là **thống kê, không phải thị giác**. Hai phân phối có thể trùng nhau khi nhìn mà
   khác nhau ở một đại lượng quyết định. Chọn đại lượng phân xử trước khi chạy.
5. Mỗi mệnh đề đã kiểm số trở thành **test hồi quy** trong bộ cổng.

---

## 4. Duy trì: bốn bất biến

Bốn cổng trong `wf_check.py`, mỗi cổng giữ một bất biến. Chạy sau mỗi chu kỳ; mã trả về khác 0 chặn
việc công bố tiếp.

| Cổng | Bất biến được giữ | Cách kiểm |
|---|---|---|
| **G1** | Tuyên bố đã rút không xuất hiện ở đâu mà không có nhãn | Quét mẫu tuyên bố đã rút trên mọi tài liệu; tài liệu loại *sổ* được miễn trừ |
| **G2** | Mọi số trong tài liệu bằng số trong nguồn sinh ra nó | Mỗi số khai một dòng: tài liệu, CSV nguồn, cách chọn ô |
| **G3** | Giả thiết của định lý đúng là thứ code hiện thực | Mỗi giả thiết ghép một vị từ trên mã nguồn |
| **G4** | Mệnh đề đã kiểm số không bị hồi quy | Chạy lại oracle, so với mục tiêu và dung sai |

Nguyên tắc chung của cả bốn: **số không được gõ tay vào văn xuôi.** Hoặc sinh từ nguồn, hoặc khai
vào G2 để máy canh.

Và về phiên bản: sửa artifact thì lưu **bản mới**, rồi kiểm con trỏ *bản mới nhất* thực sự trỏ vào
nội dung vừa sửa — trong môi trường nhiều luồng cùng ghi, điều đó không hiển nhiên.

---

## 5. Chu kỳ

1. Chọn thẻ có `khả thi × khớp tài sản` cao nhất trong backlog.
2. Chạy làn B (thí nghiệm rẻ nhất) hoặc làn C (phân rã DAG), tùy thẻ.
3. Ra phán quyết; cập nhật `claim_ledger.csv`.
4. `python wf_check.py` — phải sạch, hoặc mọi FAIL phải nằm trong danh sách đã biết và có tên.
5. Rà biên văn liệu (làn A, bước 2) theo lịch.
6. Báo cho người **chỉ khi có phán quyết rõ**.

---

## 6. Phân vai

| Việc | Ai |
|---|---|
| Bao đóng văn liệu, đọc full text, tổng hợp | Agent |
| Thí nghiệm, so găng, kiểm chứng số | Agent |
| Dựng chứng minh ở nút **có** bộ kiểm | Agent, fan-out N=8 |
| Vận hành bốn cổng, giữ sổ tuyên bố | Agent |
| Nút `UNVERIFIED` | **Người** |
| Chọn mệnh đề nào đáng chứng minh | **Người**, có tiêu chí chấm từ corpus |
| Đứng tên, chịu trách nhiệm | **Người** |

Phân vai này không phải nhượng bộ về năng lực mà là hệ quả trực tiếp của nguyên lý mục 1: agent
nhận mọi việc có bộ kiểm, người giữ đúng phần không có.

---

## 7. Ranh giới đã biết

- **Cổng chỉ mạnh bằng bảng khai của nó.** G2 và G3 kiểm được đúng những dòng đã khai; khai thiếu
  thì cổng im lặng. Mở rộng bảng khai là việc thường xuyên, không phải việc một lần.
- **Chưa có cổng hình thức hóa.** Bộ kiểm mạnh nhất — máy kiểm chứng minh — chưa nằm trong workflow.
  Đây là khoảng trống lớn nhất còn lại.
- **N=8 đo trên một model.** Fan-out chỉ phân xử được khi các lần thử sai **khác nhau**; điều đó đã
  kiểm ở bài dễ và một bài khó, chưa kiểm ở mệnh đề nhiều bước.
- **Tiêu chí chọn hướng học từ corpus chỉ tốt khi lớp tham chiếu đủ dày.** Với mệnh đề chưa ai phát
  biểu, không có tín hiệu để học, và quyết định quay về cho người.

---

## Phụ lục — vì sao bốn cổng này, không phải bốn cổng khác

Mỗi cổng sinh ra từ một lỗi đã thực sự xảy ra và đã lọt qua mọi lớp kiểm khác:

- **G1**: một tỷ lệ tốc độ bị rút vẫn nằm trong bản pitch và bản trình chiếu nhiều ngày sau đó.
- **G2**: ba lần liên tiếp, số gõ tay trong tài liệu lệch với bảng số sinh ra nó.
- **G3**: một định lý được chứng minh cho ước lượng dùng lưới cố định, trong khi code dùng ô chia
  theo phân vị dữ liệu — hai ước lượng khác nhau, không ai phát hiện nếu không đối chiếu từng dòng.
- **G4**: phòng ngừa; hai oracle số hiện có sẽ im lặng hỏng nếu thuật toán đổi.
