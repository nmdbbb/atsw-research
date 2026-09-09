# Khối lượng + workflow thay được giới hạn nào của agent — phân tích có đo

*Trả lời phản biện: "giới hạn của agent hoàn toàn có thể dùng khối lượng và workflow để thay thế".
Kết luận ngắn: **phần lớn đúng**, nhưng có một điều kiện chặn cứng, và tôi đo được nó.*

![Khối lượng và bộ kiểm]({{artifact:dbe92f5e-4364-48d0-a4db-0018a48f1501}})

## 1. Bốn giới hạn tôi nêu trước — cái nào là giới hạn LƯỢNG

| Giới hạn | Là lượng hay loại? | Cơ chế thay thế |
|---|---|---|
| Bảo chứng đúng/sai | **Lượng** — bạn đúng | Sinh N lời giải, giữ lại cái **qua được bộ kiểm** (Lean type-check hoặc phản chứng bằng số). Đúng là generate-and-test, và nó co giãn theo compute |
| Đối chiếu định lý với code | **Lượng** — bạn đúng | Cơ giới hóa được: mỗi mệnh đề sinh một bảng "giả thiết ↔ dòng code", mismatch báo tự động. Chính chỗ tôi bắt được lỗi phân hoạch-cố-định là một quy trình, không phải trực giác |
| Chọn mệnh đề đáng chứng minh | **Một nửa** | Sinh nhiều ứng viên rồi **học tiêu chí từ dữ liệu**: phiên này đã làm — corpus cho thấy bài có định lý → tạp chí hạng cao, bài thuật toán+thực nghiệm → OR, 42/100 bài tính toán mắc kẹt arXiv. Đó là tiêu chí **đo được**, không phải taste. Phần còn lại không cơ giới hóa được: khi lớp tham chiếu quá mỏng (mệnh đề chưa ai phát biểu) thì không có tín hiệu để học |
| Đứng tên, chịu trách nhiệm, quan hệ reviewer | **Loại** — nhưng là rào **thể chế**, không phải kỹ thuật | Không compute nào đổi được quy định "tác giả phải là người". Tuy nhiên bạn **đã có** advisor cho vai này — nên với dự án của bạn nó không phải ràng buộc |

Vậy 3 trên 4 là giới hạn lượng, và cái thứ tư không phải giới hạn kỹ thuật. **Phản biện của bạn đứng.**

## 2. Điều kiện chặn cứng: khối lượng chỉ đổi thành đúng đắn KHI CÓ BỘ KIỂM

Đây là chỗ tôi đo thay vì phán. Hai ca, cùng một câu hỏi dạng "tính phân phối giới hạn", đều có
chân lý (tôi dẫn tay **và** mô phỏng độc lập):

| Ca | Chân lý | 1 lần thử | 8 lần + đa số |
|---|---|---|---|
| Khả vi (không tie) | σ² = 1,1000 (mô phỏng 1,1035) | **8/8 đúng** | 8/8 |
| Chỉ khả vi hướng (có tie) | không chuẩn, kỳ vọng 0,4514 (mô phỏng 0,4535) | **7/8 đúng** | **8/8 sau khi phân xử** |

Hai điều quan trọng trong bảng này:

1. **Sai số KHÔNG tương quan hoàn toàn.** Ca khó: 7 agent bắt được tính không-chuẩn và cho kỳ vọng
   đúng đến 4 chữ số; 1 agent trả lời "chuẩn, kỳ vọng 0" — đúng cái sai kinh điển của delta method.
   Vì các lần thử **phân kỳ**, đa số và bộ kiểm đều phân xử được. Đây là bằng chứng thuận cho bạn.
2. **Bộ kiểm phải là thống kê, không phải mắt.** Panel (a): mật độ thật và Gauss khớp-tốt-nhất gần
   như trùng nhau — KS bác bỏ ở p≈10⁻⁵ nhưng nhìn không ra. Cái phân xử được là **kỳ vọng 0,45 vs 0**.
   Tức phải thiết kế đúng đại lượng để kiểm, và việc đó cần hiểu bài toán.

## 3. Chỗ khối lượng thất bại — và nó cụ thể, không trừu tượng

Xếp bốn mệnh đề của dự án theo **độ mạnh của bộ kiểm**:

| Mệnh đề | Bộ kiểm khả dụng | Khối lượng có ăn? |
|---|---|---|
| (1) Nhất quán, m,k,T hữu hạn, lưới cố định | **Mạnh** — hữu hạn chiều, hình thức hóa Lean được; kiểm số được | **Có** — generate-and-test là đủ |
| (2) Phân phối tiệm cận | **Mạnh** — mô phỏng phân xử, vừa chứng minh hai lần | **Có** |
| (3) Chặn gap ghép quantile | **Một phần** — tìm phản ví dụ thì **bác bỏ** được, nhưng không **xác nhận** được | Có, một chiều |
| (4) Chặn S theo lớp quá trình | **Yếu** — mô phỏng không bao giờ xác nhận được một chặn tiệm cận; hình thức hóa cần giải tích đo nặng | **KHÔNG** |

Ở mệnh đề (4), khối lượng **làm tệ hơn**: N lời giải trông hợp lý mà không kiểm được thì tệ hơn một
lời giải, vì bây giờ bạn phải **chọn**, và chọn chính là năng lực bạn đang muốn thay thế. Đây là
phát biểu chính xác của giới hạn, thay cho câu "agent không thay được advisor" tôi nói lúc trước:

> **Khối lượng thay được thẩm quyền ở đúng những nơi tồn tại một bộ kiểm rẻ và đáng tin. Ở nơi
> không có bộ kiểm, khối lượng chỉ nhân bản độ bất định.**

Điều này khớp với LeanMarathon, và lần này tôi dẫn nguyên văn abstract (đã tải trực tiếp từ arXiv
2606.05400) thay vì phát biểu từ trí nhớ. Bài mô tả bộ điều phối của họ là thứ *"discharges the proof
directed acyclic graph (DAG) from its dynamic leaves upward in parallel CI-gated rounds"*, và kết luận
rằng co-mathematics đáng tin *"requires not only stronger provers, but durable harnesses"*. Tức:
DAG chứng minh + cổng CI ở từng vòng, và giá trị nằm ở **harness bền**, không ở prover mạnh hơn.
Diễn giải "làm bộ kiểm mịn hơn thay vì thử nhiều hơn ở đỉnh" là **suy ra của tôi** từ hai câu đó,
không phải câu chữ của bài.

## 4. Workflow tôi đề xuất, theo đúng nguyên lý đó

1. **Phân rã mọi mệnh đề thành DAG bổ đề.** Mỗi nút phải có **một** trong hai: (a) một phép kiểm số
   phản chứng được, hoặc (b) một phát biểu Lean. Nút không có cả hai bị đánh dấu `UNVERIFIED`.
2. **Fan-out chỉ ở nút có bộ kiểm.** N=8 là đủ theo số đo trên (87,5% → 100%). Ở nút `UNVERIFIED`
   thì fan-out **không được phép** — đó là nơi duy nhất cần người.
3. **Cổng giả thiết ↔ code**, chạy tự động mỗi lần mệnh đề đổi: bảng đối chiếu từng giả thiết với
   dòng code hiện thực. Lỗi "phân hoạch cố định vs phân vị dữ liệu" mà tôi bắt được sẽ do cổng này bắt.
4. **Tiêu chí chọn mệnh đề học từ corpus**, không từ cảm nhận: đã có dữ liệu venue để chấm.
5. **Người giữ đúng hai việc**: xử lý nút `UNVERIFIED`, và đứng tên.

Ước lượng cho bộ bốn mệnh đề hiện tại: khoảng **ba phần tư** khối lượng chứng minh nằm ở nút có bộ
kiểm — tức workflow này gánh được phần lớn, và phần cần advisor thu về đúng mệnh đề (4) cộng với
quyết định chọn hướng.

## 5. Giới hạn của chính phân tích này

Hai ca kiểm đều là T=1, không gian trạng thái 2–3 ô — nhỏ nhất có thể để có chân lý dẫn tay. Chưa
đo trên mệnh đề nhiều bước. N=8 với một model duy nhất; chưa thử nhiều model khác nhau, nên chưa
biết sai số có tương quan mạnh hơn ở bài khó hơn không — và đó chính là câu hỏi quyết định cho
mệnh đề (4). Chưa dựng Lean ở đây, nên "hình thức hóa được" với mệnh đề (1) vẫn là suy luận từ
văn liệu, chưa phải điều tôi đã chạy.
