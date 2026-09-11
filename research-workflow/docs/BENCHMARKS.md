# Thí nghiệm và công cụ so sánh

## Target và đầu ra

Mỗi protocol cố định law/filtration, horizon, cost, p, root, units, chuẩn hóa và
quyền truy cập dữ liệu. Mọi comparator nhận cùng target. Một implementation có
terminal cost, discount hoặc regularization cần cầu nối trước khi vào cùng bảng
giá trị finite additive adapted OT.

Đầu ra chính: các quan hệ strict được chứng nhận, ties được xác định, unresolved
và fallback nếu dùng. Numerical solver speed và certified decision cost là hai
track riêng. Solver thiếu certificate trong API vẫn là đối thủ tiềm năng; kiểm
khả năng xây adapter và tính đủ công adapter.

## Panel đối chiếu

| Phương pháp | Vai trò | Điều kiện tham gia |
|---|---|---|
| Exact/strong adapted DP, PNOT khi đúng miền | Đối thủ cùng target và reference nhỏ | Đúng filtration, root, cost; được early-stop khi bounds đủ quyết định; kiểm backend thật. |
| Nested Sinkhorn | Đối thủ xấp xỉ có thể chứng nhận | Interval cho target unregularized, feasibility/duality và sai số truyền tới root hợp lệ. |
| Marginal OT lower + feasible-policy upper | Baseline chặn rẻ | Additive cost; policy bicausal và số học có kiểm chứng. |
| Ordinary tree-Wasserstein | Control cho phần biểu diễn cây | Score ordinary OT; claim adapted cần theorem riêng. |
| Candidate bỏ conditional information | Ablation thông tin | Giữ protocol và báo phần thông tin bị loại. |
| Candidate bỏ sharing | Ablation cơ chế tiết kiệm | Giữ kernel/bounds và tính cả phần dựng lại representation. |

WL/OTM/bisimulation và learned methods là đối chiếu prior art quan trọng. Chỉ
thêm adapter thực nghiệm khi tương thích target và có khả năng đổi kết luận.
Thiếu đối thủ đủ điều kiện phải được nêu trong phạm vi claim so sánh.

## Dữ liệu, reference và phép đo

- Split theo đối tượng/quá trình; các cặp sinh từ cùng đối tượng kế thừa nhóm.
  Tách development, calibration và held-out confirmation. Khai training-only,
  database-built hay transductive representation và công chèn query. Nhãn
  reference held-out không được dùng để thiết kế cây hoặc chọn biểu diễn.
- Có controls về timing thông tin, cùng giá trị hiện tại nhưng khác conditional
  future, higher-order dependence khi có claim tương ứng, ties và near ties.
- Chọn analytic hoặc independent exact references cho trường hợp quản lý được.
  Float agreement không chứng nhận strict order; reference intervals chồng nhau
  được ghi chưa phân biệt. Trường hợp lớn dựa trên guarantee đã review, không
  bắt buộc trả phí exact toàn bảng chỉ để có nhãn.
- Đo correctness của quyết định khẳng định, certified coverage trước fallback,
  unresolved/fallback/final coverage và tổng chi phí ở cùng guarantee/coverage.
  Giữ toàn bộ trường hợp thuộc miền đã đăng ký trong mẫu số; phân tầng theo margin.
- Báo time/work/memory, số OT solves và continuation entries, quy mô representation,
  horizon, số object/query phù hợp claim. Kendall/Spearman/recall là số đo phụ.
- Tính model/representation/index build, training labels, calibration, warm-up,
  query insertion, certification/refinement, update và fallback. Báo cold-start,
  query-only, amortized và điểm hòa vốn; phân biệt operation count với wall-clock.

Trước khi đo prediction, đóng băng hypothesis, comparator eligibility, arithmetic,
margin/tie rules, ngưỡng coverage và lợi ích chi phí, số mẫu, repeats, timeout và
ngân sách. Quy trình tại [WORKFLOW.md](../WORKFLOW.md).

## Mã nguồn đã thu thập

Pin đầy đủ, dependency, license evidence và file hashes ở
[source manifest](../research/sota/comparison_toolkit_v4.json). Các checkout dưới
`.cache/comparison_sources/` là nguồn local bị Git ignore; chưa cài hoặc thực thi
trong đợt thu thập. Mức sẵn sàng cần kiểm lại khi chọn adapter.

| Nguồn | Pin rút gọn | Tình trạng cần xử lý |
|---|---|---|
| [NestedOT](https://github.com/justinhou95/NestedOT) | `9f85f18` | Có vendor; 434 file đối chiếu upstream khớp. Eligibility đã audit giới hạn k=1/root khai trước. Boolean Markov/full-history chưa là arbitrary k; wrapper có Python fallback. |
| [ot_markov_distances](https://github.com/YusuLab/ot_markov_distances) | `6f5e349` | Python/Torch; WL terminal hoặc discounted, có stationary defaults. Metadata khai Cecill-B, checkout thiếu license text. |
| [TreeWasserstein](https://github.com/lttam/TreeWasserstein) | `540f84e` | MATLAB/FIGTree; MEX Linux/macOS, chưa xác nhận Windows. Checkout thiếu license file; dùng làm nguồn đọc, giải quyết quyền reuse trước khi phát hành adapter từ source. |
| [END](https://github.com/BenoitTran/END) | `359691f` | Julia notebook MIT, thiếu environment lock. Default path cost cần audit để khớp additive target; nhánh epsilon khác 0 ghi WIP. |
| [Nested_tree_reduction](https://github.com/dan-mim/Nested_tree_reduction) | `03d792d` | Workload/reduction source; imports MPI, dependency khai chưa đầy đủ; requirements là conda export. Routine distance cần audit cost/normalization/fallback trước khi làm oracle. |

POT/common-model, Gaussian oracle và các adapter nội bộ là thành phần sẵn có
trong repository. Source availability, installation, correctness testing và
certificate eligibility là các mức khác nhau; mỗi probe ghi rõ mức đã đạt.

## Khôi phục source

Từ repo root bằng PowerShell, khi các thư mục đích chưa tồn tại:

```powershell
$manifest = Get-Content -Raw -Encoding utf8 research-workflow/research/sota/comparison_toolkit_v4.json | ConvertFrom-Json
foreach ($source in $manifest.downloaded_checkouts) {
    $dest = $source.path
    if (Test-Path -LiteralPath $dest) { throw "Inspect existing destination: $dest" }
    New-Item -ItemType Directory -Force -Path $dest | Out-Null
    git -c core.autocrlf=false init $dest
    if ($LASTEXITCODE -ne 0) { throw 'git init failed' }
    git -C $dest remote add origin $source.url
    if ($LASTEXITCODE -ne 0) { throw 'git remote failed' }
    git -C $dest fetch --depth 1 origin $source.commit
    if ($LASTEXITCODE -ne 0) { throw 'git fetch failed' }
    git -C $dest -c core.autocrlf=false checkout --detach FETCH_HEAD
    if ($LASTEXITCODE -ne 0) { throw 'git checkout failed' }
    if ((git -C $dest rev-parse HEAD) -ne $source.commit) { throw 'Commit mismatch' }
}
```

Nếu đích đã có, đối chiếu HEAD/status/hash trước khi dùng. Commit pin phụ thuộc
upstream còn cung cấp object; manifest là provenance, không phải remote backup.
