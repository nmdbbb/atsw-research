# Định tuyến model: cộng một bậc

Theo yêu cầu user, chọn mức đủ phù hợp rồi nâng một bậc trong thang model được công cụ phiên này cung cấp. Đây là chính sách điều phối của dự án, không phải bảng xếp hạng thực nghiệm của mọi model.

| Công việc | Mức nền dự kiến | Mức thực dùng | Reasoning |
|---|---|---|---|
| Trích metadata, sinh bảng, việc cơ học | GPT-5.6 Luna | GPT-5.6 Terra | medium |
| Viết adapter, runner, tích hợp thông thường | GPT-5.6 Terra | GPT-5.6 Sol | high |
| Đọc thuật toán và giả thiết, thiết kế benchmark | GPT-5.6 Sol | GPT-6 Astra | high |
| Lemma, chứng nhận, tìm phản ví dụ | GPT-5.6 Sol | GPT-6 Astra | xhigh |
| Phán quyết khoa học cuối | GPT-6 Astra | GPT-6 Astra, đã chạm mức cao nhất | xhigh |

Code: `model_router.py`. Ví dụ: `python research-workflow/model_router.py theorem`. Hàm `spawn_arguments` trả tham số cho công cụ multiagent, với `fork_turns="none"` và task packet tự chứa thông tin cần thiết. Root giữ mục tiêu chung. Lập luận toán phát sinh trong việc tích hợp phải chuyển sang vai theorem/certificate, không giữ ở model thấp vì tên task là code.

Nguồn chính thức đã kiểm: [model guidance](https://developers.openai.com/api/docs/guides/latest-model), [subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents). Model IDs khả dụng và mức reasoning còn bị giới hạn bởi công cụ/phiên. Router không tự kiểm tài khoản, quota hoặc mở dịch vụ API.

Quy tắc khi thiếu tài nguyên: không hạ model âm thầm, không đổi chứng nhận thành empirical, không dùng lại khóa/API khác để né lỗi. Nếu không tạo thêm thread, root làm phần cơ học trong lúc các nhánh nghiên cứu chạy hoặc chờ slot; ghi trạng thái thực tế. Một agent báo rate/quota/error không có kết quả được coi là đã hoàn tất. Artefact đã ghi trước lỗi được đọc và kiểm độc lập.

Trong phiên triển khai, hai task đã được dispatch thực: `quotient_review_v1` → Astra xhigh, `pnot_adapter_audit` → Astra high. Task triển khai router dự kiến Sol high gặp giới hạn thread, nên root thực hiện cục bộ. Đây không phải worker Sol đã chạy. Không cần đọc file env hoặc gửi khóa API để định tuyến các công cụ agent có sẵn.

Tăng model không thay proof, oracle và verifier độc lập. Cho dù cả hai agent đều Astra, phải giữ nhiệm vụ/phản biện khác nhau và kiểm bằng chứng ngoài lời đồng thuận.
