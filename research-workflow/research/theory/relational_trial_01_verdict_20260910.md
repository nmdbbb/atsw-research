# Review vòng thử 01 trên scope v3

Ngày 2026-09-10. User yêu cầu thử một workflow và review, sau khi đã đính chính
việc chốt scope quá sớm. Vòng này dùng v3 như bản thử. Không sửa objective/lock,
không quyết định thay user về top-K, loại guarantee hoặc fallback.

## Kết quả

**Hoàn tất một vòng diagnostic: construction cụ thể → claim → phản ví dụ →
kiểm hữu tỉ → review độc lập → quyết định.** Không mở grid, huấn luyện mô hình,
đăng ký hypothesis hay đo hiệu năng/tương quan thống kê.

Construction là trie chung của union các chuỗi, cạnh thêm một ký tự có giá 1,
score bằng tổng chênh lệch mass dưới cạnh. Đây chỉ là một diễn giải cụ thể của
ý tưởng user, không đại diện cho mọi cách đặt edit cost hoặc học tree geometry.

Đặt Q gồm (0,0),(0,1/4); B gồm (0,0),(1/8,1/4); C_low gồm (0,0),(0,3/8);
C_high gồm (0,0),(0,3/4). Mỗi chuỗi có mass 1/2. Cùng một trie cho cả bốn tập:

| Cặp | Score cây | Adapted OT absolute |
|---|---:|---:|
| Q,B | 2 | 3/16 = 0.1875 |
| Q,C_low | 1 | 1/16 = 0.0625 |
| Q,C_high | 1 | 1/4 = 0.25 |

Score coi C_high gần Q hơn B, trong khi adapted OT cho thứ tự ngược. C_low
và C_high có cùng score nhưng nằm ở hai phía của B theo adapted OT. Hiệu chỉnh
đơn điệu chỉ từ scalar score không khôi phục được toàn bộ thứ tự; abstain vẫn
có thể hợp lệ. Full prefix vector và numeric labels không bị mất theo lập luận này.

Một fixture riêng dùng CHÍNH tree metric cho cả hai phép tối ưu cho ordinary
tree OT = 2, bicausal cost = 5/2. Như vậy, chỉ đổi ground cost thành tree cost
không tự loại bỏ ràng buộc thông tin. Fixture này không đổi reference của các
phép so absolute ở trên và tự nó không chứng minh ranking inversion.

Các giá trị được suy ra bằng đại số trước khi chạy, kiểm bằng Fraction trên
polytope 2x2, và reviewer độc lập tính lại từ điều kiện bicausal. Đối chiếu thêm
12 trường hợp với common_model hiện có: k=1/2, absolute/squared, ba cặp; sai
khác numerical so với giá trị hữu tỉ bằng 0. Đây không phải certificate float
tổng quát, cũng không phải bằng chứng trên T50 hoặc một phân phối dữ liệu thực.

## Quyết định về ý tưởng

- Bác claim bảo toàn strict order phổ quát cho trie unit-edge/depth-only đã thử.
- Không bác tree chung với edge geometry khác, learned trees, richer conditional
  features, một miền con khai rõ, hay bảo đảm ranking thống kê.
- Kết quả này quá sơ cấp để coi là đóng góp chính hoặc bài báo âm tính. Giá trị
  là ngăn một claim sai và đặt hai câu hỏi: giữ numeric geometry thế nào, và giữ
  conditional information thế nào? Không buộc phải có hai phát minh riêng.
- Không cấp budget grid hoặc learned variant chỉ vì đã hoàn thành diagnostic.

## Review workflow v3

**Điểm làm đúng:** bắt cụ thể hóa representation, buộc cùng target, tách score
khỏi guarantee, kiểm thông tin theo thời gian, tính chi phí fallback và có
review độc lập. Nó đã ngăn một claim sai mà không cần benchmark lớn.

**Điểm cần xem lại trước khi chốt scope:**

1. User cần quan hệ/tương quan có bảo đảm; điều đó chưa chọn deterministic
   top-K. Bản v3 khóa quá sớm một nhiệm vụ và một loại bảo đảm.
2. Nếu sau này đòi top-K đầy đủ ở ranh giới gần hòa, chi phí refinement có thể
   gần chi phí giải OT. Đây là nguy cơ, không phải chặn dưới đã chứng minh.
   V3 hiện cho phép unresolved và không buộc fallback mọi nơi; không diễn giải
   nó sai thành nghĩa vụ trả lời hoàn toàn mọi truy vấn.
3. Cổng sức nặng nên chặn đầu tư đáng kể vào một candidate mỏng, không chặn
   những sanity check nhỏ cần để biết candidate là gì. Vòng diagnostic này
   không cần novelty để hợp lý, nhưng hoàn thành nó không tạo novelty.
4. Phản ví dụ worst-case không trả lời tương quan có tốt trên lớp dữ liệu quan
   tâm hay không. Không được lấy nó làm kết luận thay cho một protocol thống kê.
5. Trie unit-cost dễ bị bác vì không mã hóa độ lớn numeric. Đó là baseline
   hữu ích, chưa là phép thử đủ mạnh cho toàn bộ đề xuất tree support của user.

## Đề xuất tiếp theo — chưa áp dụng vào hợp đồng

Giữ câu hỏi rộng: biểu diễn dùng chung nào giữ quan hệ gần–xa theo adapted OT
với sai lệch được kiểm soát và công thấp? Trước construction tiếp theo, viết rõ:

- Quan hệ cần giữ: thứ tự cặp/triplet, query ranking hay top-K?
- Lượng từ/bảo đảm: trên mọi instance thuộc lớp đã khai, hay xác suất sai dưới
  một mô hình lấy mẫu? Margin và unresolved được xử lý thế nào?
- Lớp quá trình, target hữu hạn và chi phí tham chiếu nào thực sự cần thiết?

Một protocol thống kê về lỗi đảo thứ tự triplet là một lựa chọn đáng phân tích,
không phải lựa chọn đã được trial này xác nhận. Nếu dùng, phải tách object groups,
calibration/confirmation, uncertainty của reference và coverage; không thay
guarantee bằng pooled Spearman hoặc học/đánh giá trên cùng các cặp.

Sau khi chọn câu hỏi, mới so một representation có geometry/conditional content
với nearest prior art, rồi quyết định có đủ sức nặng để đăng ký probe hay không.
Không tự đăng ký lại construction bị bác dưới tên mới.

## Hồ sơ tái lập

- Packet: `relational_trial_01_packet_20260910.md`.
- Reviewer độc lập: `relational_trial_01_independent_review_20260910.md`.
- Kết quả: `relational_trial_01_checks_20260910.json`.
- Chạy lại từ repo root: `python research-workflow/tools/check_relational_trial_01.py`.
- Quyết định điều phối: `ledger/inbox/codex_orchestrator/relational_trial_01_20260910.json`.

Không claim SOTA, scientific completion, universal impossibility hay scope mới.
