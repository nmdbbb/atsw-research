# Finding ĐÃ XỬ LÝ: tính toàn vẹn của ledger phụ thuộc nền tảng

> **Trạng thái: đã sửa.** `verify_ledger` pass trên Linux, 25/25 ghim hash hợp lệ
> (24 KHỚP + 1 lịch sử), 65/65 test pass. Bản sửa **không** ghi lại ledger — mọi
> hash đã commit còn nguyên hiệu lực. Chi tiết ở mục "Bản sửa đã áp" cuối file.


Phát hiện khi clone repo đã push xuống Linux (WSL, ext4) và chạy `verify_ledger`.

## Triệu chứng

    python -c "import sys,pathlib;sys.path.append('.');import workflow as W;W.verify_ledger(pathlib.Path('.'))"
    ValueError: Preregistration integrity failure: H_A01_future_classes

Trên Windows lệnh này **pass**. Trên Linux nó **fail**. Cùng một commit.

## Nguyên nhân, đã xác định bằng số

`digest()` băm **byte thô**: `hashlib.sha256(Path(path).read_bytes())`.

Ba bản ghi preregistered được ghi trên Windows với kết thúc dòng **CRLF**, và
`record_sha256` trong ledger là hash của byte CRLF. Không có `.gitattributes`,
nên với `core.autocrlf=true` phía Windows, git lưu blob dạng LF và trả CRLF khi
checkout trên Windows, LF khi checkout trên Linux.

| bản ghi | trên đĩa Linux | hash khớp? | khớp lại sau LF→CRLF |
|---|---|---|---|
| `H_A01_future_classes` | LF, 5556 B | lệch | có |
| `H_B01_temporal_block_bounds` | LF, 5839 B | lệch | có |
| `H_B01C1_envelope_headroom` | LF, 5666 B | lệch | có |

Cả ba khớp lại **chính xác** sau khi chuyển LF→CRLF. Đó là bằng chứng đóng:
nguyên nhân là kết thúc dòng, không phải nội dung bị sửa.

## Phần KHÔNG bị ảnh hưởng

- **Chuỗi hash sự kiện: 30/30 dòng hợp lệ.** `events.jsonl` được đọc bằng
  `splitlines()` và băm qua `canonical()` (chuỗi Python, không phải byte tệp),
  nên nó miễn nhiễm với kết thúc dòng.
- `objective_sha256` khớp `contract.json`.
- 61/61 test pass.

Nên chỗ vỡ **chỉ** ở các digest băm-byte-tệp, và mọi digest kiểu đó đều có cùng
rủi ro: `source_sha256`, `design_sha256`, `probe_code_sha256`, `evidence_sha256`,
`generators_sha256`, và mọi `*_sha256` khác trỏ tới tệp text.

## Hai cách sửa — cần phiên chủ ledger quyết

**A. Khai CRLF là dạng chuẩn.** Thêm `.gitattributes` ở gốc repo:

    ledger/preregistered/*.json text eol=crlf

Không sửa ledger, hash hiện tại hợp lệ trên cả hai nền tảng. Nhược: chuẩn hoá
theo một dạng do lịch sử công cụ quyết định, và mọi tệp mới phải nhớ quy ước.

**B. Chuyển sang LF và di trú hash.** Thêm `* text=auto eol=lf`, tính lại toàn bộ
`*_sha256` cho byte LF, dựng lại chuỗi, giữ `events.jsonl` cũ làm bằng chứng bất
biến (`events.jsonl.pre-lf-migration`) kèm bảng ánh xạ hash cũ→mới.
Đúng hơn về lâu dài, nhưng là **ghi lại ledger** — thao tác xâm lấn nhất có thể.

**Khuyến nghị kèm theo, độc lập với A hay B:** sửa `digest()` chuẩn hoá kết thúc
dòng trước khi băm, để cổng không còn phụ thuộc cấu hình git của từng máy:

    def digest(path):
        return hashlib.sha256(Path(path).read_bytes().replace(b"\r\n", b"\n")).hexdigest()

Nếu chọn A thì phải làm ngược lại (chuẩn hoá về CRLF) cho hash cũ còn hiệu lực.

## Bản sửa đã áp — phương án A, không ghi lại ledger

Chọn A vì nó giữ **mọi** hash đã commit hợp lệ; B phải dựng lại chuỗi, là thao tác
xâm lấn nhất có thể trên ledger.

**1. `.gitattributes` ở gốc repo: `* -text`.** Tắt hoàn toàn chuẩn hoá kết thúc
dòng, nên checkout là verbatim trên mọi nền tảng. Đây là quy ước đúng cho một repo
mà tệp bị ghim hash: git không được phép đổi một byte nào.

**2. Sáu tệp chuyển về CRLF** để byte trên đĩa đúng bằng byte lúc ghi hash:

    ledger/preregistered/H_A01_future_classes.json
    ledger/preregistered/H_B01_temporal_block_bounds.json
    ledger/preregistered/H_B01C1_envelope_headroom.json
    runs/cycle_1/H_A01_future_classes.json
    runs/cycle_2/H_B01C1_envelope_headroom.json
    runs/cycle_2/policy_pool_common_smoke.json

**3. `digest()` giữ nguyên byte-exact.** *Không* thêm chuẩn hoá — nếu chuẩn hoá thì
hash CRLF đã commit sẽ vỡ. `tests/test_hash_pins.py` có một test khoá đúng điểm này
để phiên sau không "sửa" nó rồi làm vỡ ledger.

**4. `tools/verify_hash_pins.py`** — quét **mọi** trường `*sha256` trỏ tới tệp trong
`ledger/events.jsonl`, `ledger/preregistered/*.json` và `runs/**/*.json`, không chỉ
ba bản ghi đã biết. Nó phát hiện ra hai thứ mà kiểm tay đã bỏ sót: ba tệp evidence
nữa cũng lệch, và một đường dẫn kiểu Windows trong ledger.

**5. `tests/test_hash_pins.py`** — cổng CI bốn test: contract xác nhận được, mọi ghim
byte-exact, `.gitattributes` còn `* -text`, và `digest()` vẫn phân biệt CRLF với LF.

## Hai điều CHƯA sửa, có chủ ý

**Đường dẫn kiểu Windows trong ledger.** Dòng 3 của `events.jsonl` ghi
`result_path = 'runs\\cycle_1\\H_A01_future_classes.json'`. Sửa chuỗi này là ghi lại
chuỗi hash, nên `verify_hash_pins.py` **chuẩn hoá khi phân giải** thay vì sửa bản ghi.
Quy ước cho event mới: **luôn dùng dấu `/`**.

**Pin `objective_sha256` ở dòng 1** trỏ tới bản objective v1 (`c09ae45b…`), còn hiện
tại là v2 (`72f92ab1…`). Đây là **lịch sử đúng**, không phải lỗi: `contract_revision_2.json`
là bản cấp phép sửa. Checker phân loại nó là `LICH_SU`, không tính là fail.

## Kiểm nhanh trước khi tin repo

    cd research-workflow
    python tools/verify_hash_pins.py        # exit 0, "KHOP=24, LICH_SU=1"
    python -m unittest discover -s tests -q # 65 test
    python workflow.py status
