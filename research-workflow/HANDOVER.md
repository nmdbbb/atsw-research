# Bàn giao — cuối chu kỳ 1

Ngày 2026-09-09. Ledger 11 event, chuỗi hash liền, `verify_contract` khớp `tree-adapted-ot-sota-v1`.
`scientific_objective_achieved: false`, `sota_frontier_reproduced: false` — **không** có tuyên bố nào
về tốc độ hay SOTA trong chu kỳ này.

Kiểm nhanh trước khi tin file nào:

    python -c "import sys,pathlib;sys.path.append('.');import workflow as W;print(W.verify_ledger(pathlib.Path('.'))[:16]);print(W.verify_contract(pathlib.Path('.'))['objective_id'])"
    python -m unittest discover -s tests -q

## Đã đóng trong chu kỳ 1

**Target đúng.** Builder `k=2` trong archive tính sai gốc: bỏ bước chuyển đầu và điều kiện vào cửa sổ
modal — giá trị đúng 4/3, archive trả 0 (`research/sota/imported_root_counterexample.json`, đã tự tái
lập). `adapters/common_model.py` là mô hình đúng và **mọi việc mới phải dùng nó**. Đường archive giữ
lại **chỉ** làm bằng chứng lịch sử.

**Thiết kế đã đóng băng trước mọi phép đo candidate** — `frozen_design.json` (`b322420cc9142f0a…`) +
`frozen_design_amendment_1.json` (`c150f7025359ea2b…`), cả hai commit vào ledger.
Họ quá trình thứ hai, luật khai trước khi đo:

    X_{t+1} = 0.55 X_t + 0.95 sin(1.7 X_t) - 0.45 (X_t - X_{t-1}) + 0.7 eps_t

Hai tính chất `objective.breadth` đòi, **kiểm bằng số** (20 000 đường, T=60):

| | AR(1) đối chứng | họ thứ hai |
|---|---|---|
| số lần kỳ vọng có điều kiện giảm | 0 / 13 | **4 / 13** (sâu nhất −0,499) |
| độ lớn hiệu ứng lag-2 | 0,056 | **1,496** (gấp 26,6×) |

Đại lượng phân xử là **độ lớn** hiệu ứng, không phải z: AR(1) cũng cho z=8,3 vì n lớn và trong bin
hữu hạn của X_t thì X_{t-1} còn tương quan với X_t — artifact của bin.

**Khả thi 24 ô, đo chứ không suy đoán.** Bảng chuyển dày đặc lớn nhất 0,44 GB → biểu diễn không phải
nút thắt; **số LP mới là**. Tham chiếu exact ở `k=2, δ=0.18` cần ~3,8 h cho MỘT seed/shift.
Cách giải **không thu hẹp miền vận hành**: candidate và comparator vẫn chạy đủ 24 task × 5 seed ×
3 shift; chỉ **tham chiếu exact** bị giới hạn (đủ ở 8 ô, twin thu nhỏ T=12/1500 đường ở 4 ô, chỉ
audit tính đúng, **không** báo tốc độ). Chính sách khai trước, trong `frozen_design.json`.

**Định tuyến model sang hệ Claude.** `claude_router.py` + `CLAUDE_ROUTING.md`; `MODEL_ROUTING.md`
giữ nguyên làm lịch sử. Thang thật ba bậc `haiku-4-5 < sonnet-5 < opus-5`, giữ chính sách cộng một
bậc, không hạ bậc âm thầm. Ba thứ **không** chuyển được nguyên trạng: không có `reasoning_effort`,
không có `fork_turns` (tương đương là bắt buộc `context_summary`), và `claude-fable-5*` **không** vào
thang năng lực — chúng là lane sinh biến thể code, không có phép đo nào xếp chúng so với opus.

## Ba comparator / giả thuyết: trạng thái hiện tại

| | Kết luận | Vai được phép |
|---|---|---|
| **PNOT** (C++ gốc, pinned) | không phủ `k=2` (`utils.cpp:103-109`, không có tham số k), không phủ root ngẫu nhiên (`solver.cpp:238` trả `V[0][0][0]`), **không có chứng nhận nào** (trả `double` trơn) | chỉ comparator exact `k=1` root tiền định |
| **nested Sinkhorn có chứng nhận** | chứng nhận hai phía tại gốc **hợp lệ**: `L ≤ exact_dp ≤ U` trên 20/20 instance tiny (120 phép kiểm; vi phạm khả thi đối ngẫu lớn nhất 3,25e-16). Không đạt khớp 1e-9 trên fixture không suy biến, và chướng ngại là **định luật chi phí đo được**: độ rộng Θ(ε), số vòng lặp Θ(1/ε), tức công cho độ rộng w là Θ(1/w) | chỉ track **certified-quality**, bị loại khỏi track exact/1e-9 |
| **H-B block bounds** | `revise`. L1/L2/L3 hợp lệ; bao hàm kiểm ở mọi cặp trạng thái mọi tầng trên 48 ô; truyền cận tới gốc **đúng** (đơn điệu + quy nạp từ V_T=0). Nhưng envelope **lỏng 190–196×** ở tầng 1, `L_root = 0` trên 48/48 ô | chưa phân loại; chờ Probe C1 |

Lane C còn góp một kết quả mới: **frontier accumulation lemma** —
`R − L_root ≥ Σ_frontier w*(node)·(V − E_lo)(node)` với `w*` là occupation của coupling tối ưu;
chứng minh và kiểm 64/64 cut.

## Giới hạn phải đọc trước khi dùng bất kỳ số nào ở trên

Cả ba lane **tự khai deviation**, và chúng đi kèm số:

* **Lane C**: mọi số ở **T=4**, không phải T=50. **Toàn bộ ô `k=2` bị bỏ** (exact DP cần 11 440–637 446
  cặp trạng thái ngay ở T=4). Luật sinh **tự dựng lại** vì thiết kế bị đóng băng giữa lúc review. Bổ đề
  frontier kiểm 16/48 ô. → **provisional, chưa phải evidence đã đăng ký.**
* **Lane D**: ε dừng ở 1e-4; con số 2,5e10 vòng lặp cho ε=1e-9 là **ngoại suy**, không phải đã chạy.
  Định luật chi phí đo trên **một** bài con. Chỉ 20 instance tiny, **không** có T=50 / lưới δ / họ quá
  trình. Timing chạy **1 lần** → **không có tuyên bố tốc độ nào.**
* **Lane B**: **không tự đo lại** — mọi số lấy từ artifact đã ghi và từ đọc mã. Fixture T∈{1..5},
  2–4 đường, so với `required_T=50`.

Một dự đoán của root **đã bị số bác**: "hai phía cùng luật ⇒ V*≈0 ⇒ chứng nhận tương đối vô nghĩa".
Đo thật: V* cùng luật = 1,016 (ar1) và 2,067 (son) — chặn xa khỏi 0, vì đó là hai mô hình **thực
nghiệm** độc lập của cùng một luật, khác nhau đúng bằng nhiễu lấy mẫu. Hệ quả **nặng hơn** phát hiện
ra: tín hiệu đối lập chỉ cao hơn sàn nhiễu **1,51×** (ar1) và **1,31×** (son) ở T=8/2000 đường. Bổ
chính 1 buộc: mọi tuyên bố speed/quality phải báo kèm giá trị task đối chứng cùng ô, và tỉ lệ này
**phải đo lại** ở T=50 với số đường đã đóng băng — **cấm ngoại suy**.

## Việc còn mở, theo thứ tự

1. Đăng ký **Probe C1** (envelope headroom audit, ~31 s một core, không cần cài hierarchy) rồi chạy
   trên luật đã đóng băng — đây là thứ phân xử H-B. Lane C ghi rõ: **chưa** được cài hierarchy, chưa
   được chạy màn 48 ô, chưa được chạy T=50 trước khi Probe C1 qua.
2. Đóng `TIMING_BOUNDARY`: đồng hồ hiện bắt đầu **sau** khi dựng biểu diễn, nên mọi tỉ lệ cũ là
   solver-only. Cần đồng hồ **từ paths** và báo tách solver-only / end-to-end / cold-start.
3. Đo lại tỉ lệ tín hiệu/sàn nhiễu ở T=50.
4. Chạy lưới **development** (seed 1000–1004) trên 24 task. Chỉ khi sạch mới chạy **confirmation**
   (seed 2000–2004) với 5 lần lặp timing.

## Quy tắc vận hành nếu chạy hai phiên song song

`CONCURRENCY.md`, đã kiểm bằng ba phép thử: `write_new` (mode `x`) **an toàn**; chuỗi hash ledger
**vỡ vĩnh viễn** nếu hai phiên cùng append (và vỡ cho **cả hai**, vì `register`/`check-report` đều gọi
`verify_ledger` trước); ghi truncate vào file chung **mất dữ liệu im lặng**. Một chủ ghi mỗi file;
**một** phiên commit ledger, phiên khác bỏ đề xuất vào `ledger/inbox/<lane>/`.

Sub-agent **thừa hưởng cả quyền đọc và ghi** vào `/home/nmd/workflow` — đã xác nhận bằng probe và
bằng việc ba lane đều ghi được file của mình.
