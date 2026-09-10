# Quyết định PO: bảo toàn thứ tự dưới điều kiện toán học

2026-09-10. User đã chọn rõ **giữ thứ tự dưới điều kiện toán học**, rồi giao PO
tiếp tục ra quyết định. Tài liệu này ghi lựa chọn và quyết định đầu tư trong
scope v3; không tạo hợp đồng v4 hay sửa hash v3. Nó làm rõ các lựa chọn còn mở
trong vòng thử 01: không tự chuyển statistical ranking, không bắt top-K đầy đủ
và không buộc fallback. Ghi nhận này mới hơn phần đề xuất trong trial 01/v3.

## Mục tiêu được chọn

Tìm score trên biểu diễn dùng chung và điều kiện C kiểm được từ đầu vào/biểu
diễn, sao cho các strict order được khẳng định khớp adapted OT hữu hạn. Ngoài
điều kiện đó cho phép chưa kết luận. Quan hệ query-triplet là đơn vị thử tối
thiểu; chưa phải quyết định sản phẩm top-K. Một claim có thể áp dụng hai cặp
không chung query nếu giữ cùng target/cost/normalization.

Điều kiện phải không vòng tròn (không đòi biết D cần tránh tính), có miền hữu
ích và chi phí thấp. Thứ tự dưới giả thiết toán học mới là bảo đảm; tương quan
thực nghiệm hỗ trợ định lượng, không thay thế nó. Cổng sức nặng chặn đầu tư
implementation/grid đáng kể, không chặn diagnostic đại số nhỏ cần thiết.

## Vòng thực hiện và quyết định đã ra

1. **Trial 01 đã đóng diagnostic:** trie unit/depth-cost có thể đảo thứ tự;
   kết quả đúng và đã review độc lập. Không bác mọi cách đặt trọng số/cây.
2. **Trial 02 có công thức bicausal đúng trên prefix tree:** theo dõi matched
   prefix mass m_h=m_parent*min(p_h,q_h), thay min(prefix masses) của ordinary
   tree OT. Nó khớp maximal-agreement trong Beiglbock--Zona, Lemma 2.1;
   giữ làm baseline, không claim phát minh.
3. **Điều kiện ranking cụ thể đã được suy ra:** chặn geometry bằng range cho
   U_tree, chặn L_marg từ tổng OT biên một thời điểm; U_tree(Q,A)<L_marg(Q,B)
   suy ra đúng thứ tự. Đây là hệ quả sơ cấp, không đóng góp chính.
4. **Không triển khai solver/grid:** range bound quá thô trong fixture temporal
   đã biết. Rule có thể khẳng định thứ tự ở fixture tách support dễ, nhưng điều
   đó không thỏa cổng sức nặng hay chứng minh useful coverage trên dữ liệu.
5. **Không bắt full-trie expansion:** với trọng số theo thời gian/state, công
   thức agreement gom được trên k-window graph bằng min hai transition kernels.
   Đây là đường tính baseline có thể rẻ; arbitrary-prefix learned weights vẫn
   có rủi ro expansion, và chưa có đo hiệu năng/bit complexity thực tế.

## Review và giới hạn

Reviewer độc lập đã ghi file review và thông báo xác nhận công thức/overlap.
Lượt agent sau đó kết thúc vì usage limit. File được giữ là review đã ghi trước
gián đoạn, không là xác nhận rằng mọi bổ sung cuối của root đã được reviewer
duyệt. Range/marginal bridge và script trial 02 do root kiểm; chưa có final
independent sign-off trên toàn packet. Không gọi thêm agent để lặp review chỉ
để đủ thủ tục; chưa promotion nên không bị ép triển khai trước khi quota hồi.

## Việc quyết định tiếp theo

**Chỉ cấp một task lý thuyết hữu hạn về geometry-aware prefix weights/condition,
không cấp grid:** tìm điều kiện cấu trúc kiểm được từ kernels/nhãn giúp thay
range toàn cục bằng chặn đủ sắc để phân biệt những quá trình có tương lai quay
lại gần nhau sau khi đã khác prefix. Đây là trường hợp prefix disagreement
tiếp tục tính phạt dù numeric distance đã nhỏ.

Task phải trả đủ bốn đầu ra:

- Một construction/condition cụ thể trên miền hữu hạn được khai rõ, giữ target.
- Cách kiểm không xây bảng continuation đầy đủ hay enumerate mọi full path.
- Phản ví dụ hai quá trình phân kỳ rồi hội tụ lại; chứng minh thứ tự trong miền
  hoặc chỉ rõ vì sao construction không thể bao trường hợp đó.
- So trực tiếp với baseline agreement + marginal/range vừa có và nearest prior
  art về maximal coupling/geometry; nếu chỉ lặp known inequalities thì dừng.

Gate để đầu tư prototype: có một lemma không vòng tròn, ít nhất một fixture
conditional thực sự vượt baseline (không chỉ terminal-only/Gaussian closed form),
và bảng work chỉ ra phép tính tránh được sau mọi kiểm điều kiện. Đó là evidence
để mở probe, chưa là novelty hay SOTA. Nếu không qua, PO dừng construction và
giữ nguyên câu hỏi nghiên cứu, không chạy lưới để tìm số đẹp.

Không hẹn nghiên cứu chạy nền. V3 và mục tiêu solver cũ đều chưa hoàn thành.
