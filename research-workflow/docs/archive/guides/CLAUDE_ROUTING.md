# Định tuyến model — hệ sinh thái Claude

Bản chuyển của `MODEL_ROUTING.md` (hệ OpenAI). File cũ **giữ nguyên** làm lịch sử; theo
`CONCURRENCY.md` mỗi file có một chủ ghi, nên bản này là file mới chứ không sửa file cũ.
Code: `claude_router.py`, test: `tests/test_claude_router.py` (31 test toàn bộ suite pass).

## Thang năng lực thật của phiên này

`host.list_models()` trả về 11 id. Thang dùng ba bậc, và **không** đưa `claude-fable-5*` vào thang:
trong lịch sử dự án chúng được dùng để **sinh biến thể code**, và không có phép đo nào đặt chúng
trên hay dưới opus cho việc suy luận. Xếp riêng thành lane `generation` thay vì bịa một bậc.

    LADDER          = claude-haiku-4-5-20251001  <  claude-sonnet-5  <  claude-opus-5
    GENERATION_LANE = claude-fable-5, claude-fable-5-1        (không phải một bậc năng lực)

Chính sách giữ nguyên tinh thần bản cũ: **chọn mức nền rồi cộng một bậc**, không hạ bậc âm thầm
(`RoutingUnavailable` nếu không có model ở bậc yêu cầu hoặc cao hơn).

| Công việc | Mức nền | Thực dùng | Ghi chú |
|---|---|---|---|
| Trích metadata, việc cơ học | haiku-4-5 | **sonnet-5** | |
| Viết adapter, runner, tích hợp | sonnet-5 | **opus-5** | |
| Đọc thuật toán, thiết kế benchmark | sonnet-5 | **opus-5** | |
| Lemma, chứng nhận, phản biện | sonnet-5 | **opus-5** | |
| Phán quyết khoa học cuối | opus-5 | **opus-5** | đã chạm bậc cao nhất |
| Sinh biến thể solver | fable-5 | **fable-5** | lane riêng, không cộng bậc |

Ánh xạ từ bảng cũ: Luna→haiku, Terra→sonnet-5, Sol→sonnet-5/opus-5, Astra→opus-5. Bốn bậc gộp
thành ba vì thang thật chỉ có ba, chứ không phải vì hạ yêu cầu.

## Ba cơ chế KHÔNG chuyển được nguyên trạng

1. **Không có `reasoning_effort`.** Nền tảng này không có núm effort. Router giữ `intended_effort`
   như **ghi chú cho người đọc** và **không** đưa vào kwargs gửi đi — phát ra một field mà công cụ
   bỏ qua thì tệ hơn là không có.
2. **Không có `fork_turns`.** Sub-agent ở đây có context mới hoàn toàn *theo thiết kế*: nó chỉ thấy
   `task` + `context_summary`, không thừa hưởng transcript. Tương đương của `fork_turns="none"` là
   **bắt buộc `context_summary` khác rỗng** — `spawn_arguments` raise `ValueError` nếu thiếu.
3. **Đường dẫn.** Sub-agent chạy ở thư mục làm việc riêng, nên đường dẫn tương đối không tới được
   nó. Đã **kiểm bằng một probe thật**: sub-agent **đọc được** `/home/nmd/workflow` (thừa hưởng host
   grant của phiên cha). Quyền **ghi chưa được xác nhận** — probe chỉ chạy `ls`/`cat`, và đứa con tự
   khai đúng điều đó. Nên mọi task giao xuống phải dùng **đường dẫn tuyệt đối**, và nếu ghi bị chặn
   thì đứa con lưu artifact rồi báo, **không** tự gọi `request_host_access`.

## Điều không đổi khi lên model cao hơn

Nâng bậc **không** thay proof, oracle và verifier độc lập. Dù hai lane đều chạy opus-5, phải giữ
nhiệm vụ và phản biện khác nhau, và kiểm bằng bằng chứng chứ không bằng sự đồng thuận. Một agent
báo lỗi/quota mà không có kết quả **không** được tính là đã hoàn tất.
