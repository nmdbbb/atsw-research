# Agent có thay được advisor lý thuyết không — thử nghiệm thật (09/2026)

*Không phải bài luận. Tôi lấy đúng mệnh đề (1) của dự án — nhất quán của ước lượng k-Markov —
giao cho agent chứng minh, rồi tự kiểm bằng máy. Đây là kết quả.*

## 1. Hiện trạng công cụ (từ văn liệu, 09/2026)

- **Autoformalization đã đến mức paper nghiên cứu.** LeanMarathon (arXiv 2606.05400) hình thức hóa
  trọn hai bài 2026 về bốn bài toán Erdős vào Lean 4, chứng minh 258 bổ đề/định lý, không còn `sorry`,
  trong khi một agent thương mại đơn lẻ thất bại sau hàng chục giờ.
- **Có ca vượt người rõ rệt.** Hệ Gauss hoàn tất hình thức hóa Prime Number Theorem trong Lean —
  việc đã đình trệ hơn 18 tháng công sức chuyên gia — trong **ba tuần**.
- **Prover chuyên dụng đã thành một dòng riêng**: DeepSeek-Prover-V2, Goedel-Prover-V2, Kimina-Prover,
  cùng hạ tầng LeanDojo / Lean Copilot / Pantograph.
- Có cả hướng dẫn thực hành cho đúng câu hỏi này: *The Agentic Researcher* (arXiv 2603.15914).

Điểm mấu chốt của cả dòng này: **giá trị đến từ việc chứng minh được KIỂM MÁY**, không phải từ việc
model tự tin. Lean là bên vouching, không phải agent.

## 2. Thử nghiệm: agent chứng minh mệnh đề của chính dự án

**Phần (a) — nhất quán h.c.c.** Agent trả về chứng minh đúng cấu trúc: tham số hóa hữu hạn chiều
(vì m, k, T cố định), giả thiết **khả đạt** (nút không có khối lượng thì kernel là 0/0), công thức
Fréchet–Hoeffding cho ghép comonotone, bổ đề "ô khối lượng 0 không đóng góp", SLLN + tính Lipschitz
của toán tử ghép, rồi quy nạp lùi. Nó **tự liệt kê** chỗ có thể hỏng, trong đó có quy ước 0/0.

**Phần (b) — phân phối tiệm cận.** Đây là phép thử thật, và agent tìm đúng điểm tinh tế mà một
người mới vào nghề gần như chắc chắn bỏ qua:

> Toán tử ghép comonotone dựng từ min/max/(·)₊ nên chỉ **khả vi theo hướng (Hadamard)**, không
> Fréchet, tại chỗ hai CDF tích lũy **trùng nhau**. Ở đó delta method thường sai; phải dùng bản mở
> rộng (Shapiro / Dümbgen / Fang–Santos) và giới hạn là **ảnh phi tuyến của một Gauss**, không còn Gauss.

Và nó đưa ra **ví dụ nhỏ nhất kiểm được**: T=1, m=2, chi phí 0/1 → V₀ = |p − q|; đặt p₀=q₀=½ thì
√n·V̂₀ ⇒ half-normal scale 1/√2.

## 3. Kiểm chứng bằng máy (dùng chính hàm ghép trong `atsw_kmarkov.py`)

| Kiểm | Kết quả |
|---|---|
| QC((p,1−p),(q,1−q);M) = \|p−q\| trên 361 điểm | sai số tối đa **0,0** |
| Ca tie (p₀=q₀=½), n=20.000, 6.000 lần lặp | KS vs half-normal **p=0,32** (khớp); KS vs Gauss khớp-tốt-nhất **p≈10⁻⁴⁷** (bác bỏ); độ lệch đo **+1,01** vs lý thuyết half-normal **0,995** |
| Ca lành (p₀=0,3, q₀=0,7), n=20.000 | KS vs N(0; 0,42) **p=0,63**; phương sai đo 0,403 vs lý thuyết 0,42 |
| n=200 (cả hai ca) | KS bác bỏ — do rời rạc nhị thức ở n nhỏ, không mâu thuẫn với giới hạn |

**Dự đoán của agent đứng vững.** Nó không chỉ đúng định tính mà đúng đến hằng số.

## 4. Chỗ agent trượt — và nó nói lên điều quan trọng nhất

Định lý được chứng minh với giả thiết **(G1) phân hoạch cố định, không ước lượng**.

Nhưng code thật của mình, `quantile_codes` trong `atsw_kmarkov.py`, dựng ô bằng **phân vị của mẫu
gộp** — tức biên ô là **ngẫu nhiên, ước lượng từ chính dữ liệu**. Vậy định lý vừa chứng minh
**không phủ được ước lượng mình đang chạy**. Đây không phải lỗi của agent: nó chứng minh đúng thứ
được hỏi. Không ai phát hiện được khoảng cách này nếu không **đọc code** và đối chiếu với danh sách
giả thiết.

Hệ quả trực tiếp cho dự án: hoặc (i) đổi code sang lưới cố định để định lý áp dụng được, hoặc
(ii) mở rộng định lý sang ô ước lượng — khó hơn hẳn, vì biên ô ngẫu nhiên đưa thêm một tầng nhiễu
và có thể tạo tie ngẫu nhiên. **Đây là một câu hỏi nghiên cứu mới, sinh ra từ chính việc kiểm.**

## 5. Kết luận: thay được phần nào

| Việc của advisor | Agent thay được? |
|---|---|
| Nhớ đúng công cụ (Hadamard directional derivative, Fang–Santos) | **Có** — và nhanh hơn tra cứu |
| Dựng chứng minh cho mệnh đề đã phát biểu rõ | **Phần lớn** — phần (a) dùng được gần như nguyên |
| Tìm điểm tinh tế / phản ví dụ | **Có** — phần (b) là bằng chứng |
| Kiểm chứng bằng số | **Có, và đây là điểm mạnh nhất** — vòng "agent đề xuất → máy kiểm" chạy trong vài phút |
| Hình thức hóa để máy vouching (Lean) | **Có về nguyên tắc** (LeanMarathon, Gauss) — chưa dựng ở đây |
| **Chọn mệnh đề nào đáng chứng minh** | **Không** — đây là taste, phụ thuộc hiểu biết venue và giá trị của bài |
| **Bảo chứng đúng sai bằng uy tín** | **Không** — không có Lean thì không ai vouching; agent tự tin ngang nhau ở câu đúng và câu sai |
| **Đối chiếu định lý với code thật** | **Không tự động** — phải có người biết cả hai (mục 4) |
| Đứng tên, quan hệ reviewer, bảo vệ bài khi bị phản biện | **Không** |

**Phát biểu trung thực:** agent thay được phần **lao động** của advisor lý thuyết — nhớ công cụ,
dựng chứng minh, sinh phản ví dụ, kiểm bằng số — nhưng không thay được phần **thẩm quyền**: chọn
bài toán, bảo chứng, và chịu trách nhiệm. Với dự án này, tỷ lệ hợp lý là **agent làm 70–80% lao
động, advisor giữ 100% quyết định**, và mọi mệnh đề quan trọng nên đi qua một trong hai cửa kiểm:
mô phỏng số (rẻ, làm ngay) hoặc Lean (đắt, chỉ cho định lý chính).

## 6. Việc tiếp theo nếu đi hướng này

1. **Sửa khoảng cách ở mục 4** trước mọi thứ khác — hoặc đổi code sang lưới cố định, hoặc nhận
   rằng cần định lý mạnh hơn.
2. Đặt **điều kiện không-tie** thành một giả thiết được kiểm bằng số trên dữ liệu thật (dễ kiểm:
   quét xem có cặp CDF nào trùng ở lớp nào không).
3. Nếu muốn Lean: chỉ hình thức hóa **một** mệnh đề — nhất quán, m,k,T hữu hạn, lưới cố định.
   Đó là mệnh đề hữu hạn chiều, không cần giải tích nặng, khả thi nhất trong bốn mệnh đề.
