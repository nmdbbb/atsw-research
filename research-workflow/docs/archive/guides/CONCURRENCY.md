# Chạy hai phiên song song trên thư mục này

Trạng thái: **được, nhưng phải phân vùng quyền ghi.** Ba phép kiểm dưới đây chạy trên bản sao tạm
của `workflow.py` + `ledger/`, không chạm ledger thật.

## Cái gì an toàn, cái gì vỡ

| Cơ chế | Kết quả kiểm | Kết luận |
|---|---|---|
| `write_new()` — mở mode `"x"` | phiên thứ hai nhận `FileExistsError`, file của phiên đầu còn nguyên | **an toàn** cho ghi song song |
| `append_event()` / `verify_ledger()` — chuỗi hash | hai phiên đọc cùng `tail` rồi cùng append → `ValueError: Ledger integrity failure on line 3` | **vỡ, và vỡ vĩnh viễn**: `register` và `check-report` đều gọi `verify_ledger` trước, nên sau đó MỌI lệnh của CẢ HAI phiên đều fail |
| ghi truncate (`write_text`, `json.dump` mode `w`) vào file chung | A ghi 2025 byte, B ghi sau → còn 13 byte, không lỗi, không cảnh báo | **mất dữ liệu im lặng** |
| artifact store của project | đã xảy ra thật: một phiên khác ghi `claim_ledger.csv` v10 trong khi phiên này đang giữ v9 | phải **đọc lại rồi hợp nhất**, không ghi đè |

Kernel (python/bash/r) **không** chia sẻ giữa hai phiên — không cần điều phối gì ở đó. Chỉ có
filesystem và artifact store là chung.

## Quy tắc phân vùng

1. **Một chủ ghi cho mỗi file.** Không có ngoại lệ. File nào hai phiên đều cần sửa thì tách thành
   hai file theo phiên rồi hợp nhất bằng một bước riêng.
2. **Ledger có đúng MỘT phiên được commit.** Phiên đó là chủ (`ledger_owner`). Phiên còn lại
   **không gọi** `workflow.py register` / `check-report`; nó bỏ đề xuất vào
   `ledger/inbox/<session>/<ten>.json` bằng `write_new` (mode `x`, an toàn), chủ đọc và commit.
3. **`objective.json` là đóng băng.** `ledger/contract.json` giữ sha256 của nó, nên sửa từ bất kỳ
   phiên nào cũng làm `verify_contract` fail cho cả hai. Muốn đổi mục tiêu thì dừng cả hai phiên,
   sửa, rồi `init` lại.
4. **Thư mục theo phiên.** `runs/cycle_N/<session>/…`, `research/<lane>/notes.<session>.md`,
   `status.<session>.json`. `status.json` và `research/*/notes.md` chỉ chủ được ghi.
5. **Artifact store: tên file phải khác nhau giữa hai phiên** (hậu tố `_s1` / `_s2`), hoặc dùng
   `version_of` với id vừa đọc được. Không bao giờ ghi đè theo tên.
6. **Trước khi sửa bất kỳ file chung: đọc lại từ đĩa, hợp nhất, rồi ghi.** Không giữ bản đã đọc từ
   lượt trước — giữa hai lượt phiên kia có thể đã ghi.
7. **Đọc thì thoải mái.** Mọi file đọc song song không có rủi ro; chỉ ghi mới có.

## Phân lane đề nghị (hai phiên không tranh nhau)

| | Phiên A | Phiên B |
|---|---|---|
| vai | thực thi + đo | literature + lý thuyết + phản biện |
| được ghi | `adapters/`, `certify/`, `runs/cycle_N/A/`, `status.A.json` | `research/sota/notes.B.md`, `research/theory/notes.B.md`, `ledger/inbox/B/` |
| ledger | **chủ** (commit) | chỉ bỏ vào inbox |
| artifact | hậu tố `_A` | hậu tố `_B` |

Lý do chia thế: hai lane này cần đúng những file khác nhau, và lane đo là lane duy nhất sinh ra
evidence phải vào ledger — nên cho nó làm chủ ledger thì số lần cần điều phối gần bằng 0.
