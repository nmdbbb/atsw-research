# Bộ công cụ đối chiếu v4 — thu thập source, chưa chạy thực nghiệm

Ngày kiểm: 2026-09-11. Phạm vi là chuẩn bị công cụ cho biểu diễn adapted OT dùng lại
được và quyết định thứ tự có bảo đảm tất định. Đây là inventory nguồn và kế hoạch
đối chiếu; không sửa objective, không chứng nhận thuật toán và không báo kết quả
khoa học. Scope hiện hành là [revision v4](../../SCOPE_REVISION_4.md);
manifest gắn objective ID và SHA256 sau khi PO tích hợp amendment đã review.

Đã tải **4 checkout upstream**, kiểm trạng thái Git sạch, đọc source chọn lọc;
đã tải thêm archive NestedOT đúng pin để so byte với bản vendor. Không import,
build, chạy notebook, cài package hay benchmark bất cứ nguồn tải xuống nào.
Các môi trường/thử nghiệm cũ của dự án không được kiểm lại trong lượt này.
Manifest máy đọc được ở [comparison_toolkit_v4.json](comparison_toolkit_v4.json).
Cache chỉ nằm local, bị Git ignore và không đi theo push; manifest và lệnh phục
hồi bên dưới mới là đầu ra bền vững.
Tổng file tracked của bốn checkout là 154.232.803 byte (không tính `.git`);
riêng TreeWasserstein là 143.926.261 byte do dữ liệu `.mat`, archive và MEX đi kèm.
Đây không phải dung lượng dependency đã cài; không giải nén/chạy các binary đó.

## Nguồn đã có thật trên đĩa

Mọi đường dẫn cache dưới đây tương đối với `research-workflow/.cache/comparison_sources/`.
Full commit, tree Git, file count, số byte, SHA256 những file đã chọn và provenance
khôi phục được ghi trong JSON; HEAD chỉ là HEAD quan sát lúc tải, không phải cam kết
phiên bản mới nhất trong tương lai.

| Source / paper gốc đã mở | Checkout và pin | Vai trò, điều kiện dùng |
|---|---|---|
| [YusuLab/ot_markov_distances](https://github.com/YusuLab/ot_markov_distances), [Distances for Markov Chains, and Their Differentiation](https://arxiv.org/abs/2302.08621v2) | `YusuLab__ot_markov_distances`, `6f5e34958c795e32b27f452f5f8e30d9cbdb0d4e` | Nguồn thuật toán WL/discounted WL, sparse/batched transport và novelty threat. Chưa là comparator cùng finite additive target. |
| [lttam/TreeWasserstein](https://github.com/lttam/TreeWasserstein), [Tree-Sliced Variants of Wasserstein Distances](https://arxiv.org/abs/1902.00342v3) | `lttam__TreeWasserstein`, `540f84e1ff55dda0e91f778496d10bdc0abfcd2f` | Ordinary tree-Wasserstein ablation: biểu diễn dùng chung và truy vấn L1; không tự giữ filtration hay thứ tự adapted OT. |
| [BenoitTran/END](https://github.com/BenoitTran/END), [Entropic Regularization of the Nested Distance](https://arxiv.org/abs/2107.09864v1) | `BenoitTran__END`, `359691f8db4b105098f1b2223b8adf14edbcde55` | Nguồn nested Sinkhorn và DP Julia; cần chuẩn hóa cost/root và certificate adapter trước track quyết định có chứng nhận. |
| [dan-mim/Nested_tree_reduction](https://github.com/dan-mim/Nested_tree_reduction), [Scenario Tree Reduction via Wasserstein Barycenters](https://dan-mim.github.io/files/reduction_tree.pdf) | `dan-mim__Nested_tree_reduction`, `03d792d0d7b4ce00bf85cf29cc16401d00c45910` | Công cụ sinh/giảm scenario tree, novelty threat cho compression; có routine nested distance cần audit riêng nếu dùng làm oracle. |
| [NestedOT tại pin vendor](https://github.com/justinhou95/NestedOT/tree/9f85f18fb32b67f9ba1112cf38a97f4f98c57d8a), [Nested Optimal Transport Distances](https://arxiv.org/abs/2509.06702) | Vendor `research-workflow/third_party/nestedot`; pin `9f85f18fb32b67f9ba1112cf38a97f4f98c57d8a` | Nguồn DP C++/Python mạnh, hiện chỉ giữ eligibility lịch sử k=1/root đã khai; mở rộng k hoặc certificate cần adapter có kiểm chứng. |

Các paper được xác minh nhận dạng/link qua nguồn chính; không phải full theorem
review trong lượt này. Nhận xét về implementation dựa trên các file và hash ghi
trong JSON. Không nhận các tuyên bố tốc độ/production-ready của README làm kết quả
của dự án.

## Những điểm ảnh hưởng trực tiếp tới adapter

**ot_markov_distances.** `wl.py:wl_k` nhận transition matrices, label/cost matrix,
`k`, initial distributions tùy chọn và `reg`; nếu bỏ initial distributions nó tính
stationary measures. Recursion thay cost bằng OT của continuation, không cộng
stage cost mỗi bước: đây là terminal-style WL. `discounted_wl.py` có bước
`delta * distance_matrix + (1-delta) * sinkhorn_result`. Không thay `k` bằng horizon
rồi gọi là finite additive bicausal AW; cần viết và kiểm cầu nối riêng. Có thể dùng
kernel OT/sparsity như thành phần implementation, nhưng đó là adapter mới và phải
tính công của nó. `pyproject.toml` khai Python ^3.10, Torch ^2.0.0, NetworkX ^3.1,
Poetry build; POT là test dependency. Metadata khai `Cecill-B`, nhưng checkout
không có file LICENSE: ghi là license declared, chưa coi license text đã xác minh.

**TreeWasserstein.** `BuildTreeMetric_HighDim_V2.m` dựng tree metric bằng farthest
point clustering; `TreeMapping.m` ánh xạ measure sang vector cạnh và dùng
`knnsearch`; khoảng cách tree lấy L1 giữa vector. Cần MATLAB, chức năng nearest
neighbor tương ứng và FIGTree clustering; repository có MEX Linux/macOS, không
thấy binary Windows hay C++ nguồn của MEX. `figtreeKCenterClustering.m` là interface
stub, không chứng minh chạy được trên Windows. Không tìm thấy license file cả ở
checkout và inventory zip bundled; quyền reuse/redistribution chưa xác định.
Source đã sưu tập để đọc; trước dùng source vào adapter phát hành cần giải quyết
license hoặc triển khai độc lập từ paper. Ablation ordinary tree vẫn có giá trị
để đo phần lợi ích của tree dùng lại; không gán bound adapted OT cho score này.

**END.** MIT; một notebook Julia (metadata Julia 1.5.2), không có Project/Manifest
pin dependency. Cell import `JuMP`, `ScenTrees`, `LinearAlgebra`, `OptimalTransport`,
`Tulip`, sau đó `Statistics`. Hai hàm là `nested_distance` và
`entropic_nested_distance`. Source dựng tổng bình phương trên path rồi lấy căn
trước nested recursion có tham số `r`. Với `r=1`, đó không phải tổng stage L1 của
AW1 hiện tại. Phải thay/kiểm cost theo target đã khai, root stochastic/deterministic
và units. Nhánh `epsilon=0` chọn gamma theo maximum cost; nhánh epsilon khác 0 được
ghi WIP và truyền `-gamma` vào `sinkhorn2`: chưa coi là adapter certificate chạy
được. Cần implementation ổn định, kiểm feasibility/duality, accounting bias và
sai số số học; không dùng một nhánh WIP để kết luận nested Sinkhorn không cạnh tranh.

**Nested_tree_reduction.** LICENSE là MIT; setup classifier lại ghi Other/Proprietary
License (metadata không nhất quán). README mô tả `core.py/metrics.py` nhưng source
thật dùng `tree_reduction_MPI.py`, `NestedDistance.py`, `MAM.py`, `barycenter_IBP.py`
và `create_homogenous_filtrations_and_trees.py`. API thực có `KP_reduction`,
`generate_uniform_tree`, `nested_distance`. Setup khai NumPy, SciPy, CasADi,
pyopticontrol, pystocoptim; imports còn dùng mpi4py/MPI, NetworkX, Numba, Matplotlib.
`__init__.py` import reduction MPI nên MPI có thể cần ngay cả khi chỉ muốn dùng
helper; chưa chạy để xác minh. `requirements.txt` là conda win-64 export (Python
3.13.5), không phải pip requirements như README hướng dẫn. Cần môi trường riêng và
adapter minimal, không cài mù file này. Routine distance khởi tạo squared L2 toàn
path (additive AW2 squared khi semantics thích hợp), normalize cost qua maximum,
có fallback làm tròn; trường hợp zero maximum và chuyển p/q trong fallback cần
kiểm. Chưa đủ làm exact certified oracle. Reduction thay support/probabilities;
khi dùng nó làm representation, phải tính conversion error về law gốc cùng phí
build/calibration. Khi chỉ dùng sinh workload, mọi comparator nhận cùng law hữu hạn
đã đóng băng, không thay target theo output của từng phương pháp.

**NestedOT.** Apache-2.0 ở license cấp dự án; dependency bundled còn có license riêng.
`setup.py` yêu cầu pybind11/setuptools, C++/OpenMP và NumPy/tqdm/POT. Wrapper
`pnot/solver.py:nested_ot` nhận paths, grid, boolean `markovian`, power, threads;
bare `except` có thể chuyển sang Python. Phải ghi backend thật, không ghi mọi call
là C++. Boolean Markov/full-history không phải arbitrary k; cần audit embedding
k-window bảo toàn filtration và current-stage cost. Giữ hạn chế audit cũ tại
[baselines.json](baselines.json), không cấp eligibility mới từ lượt đọc này.
Archive pin SHA256 `d226523bed07cc0483497c4fe61f4284f590970ce5a053bbdd5439b240a54b7f`
đã tải lại; **434/434 file upstream khớp byte vendor**, không missing/different.
File provenance thêm của dự án được phân biệt khỏi upstream.

## Panel tối thiểu cho thực nghiệm sau gate

| Hàng đối chiếu | Đầu vào/đầu ra cần có | Readiness hiện tại |
|---|---|---|
| Exact/strong DP, có early stop theo bound | Cùng law hữu hạn, additive cost, filtration, root và units; lower/upper có kiểm chứng để dừng khi quyết định đã tách | Tái dùng common-model/POT hoặc NestedOT khi đúng miền; strength, early stop và certificate phải được triển khai/kiểm riêng. POT là baseline/oracle, không tự là SOTA. |
| Certified nested Sinkhorn | Interval của **unregularized** target, feasible coupling/dual, kiểm sai số regularization và propagation tới root | Dùng nguồn END, [nested Sinkhorn paper](https://link.springer.com/article/10.1007/s10287-021-00415-7) và adapter dự án có sẵn làm đầu mối; chỉ vào track certified khi adapter cho miền mới đã sẵn sàng. |
| Cheap valid marginal lower + feasible upper | Tổng marginal OT lower theo additive cost; một bicausal policy khả thi như product conditional coupling cho upper, kiểm số học | Baseline bắt buộc để xem cơ chế mới vượt phép chặn rẻ; không cần framework ngoài. Tính đầy đủ công marginals/coupling/propagation. |
| Ordinary tree ablation | Tree representation dùng lại, score L1 hoặc tree-sliced rõ cost | Heuristic track, kèm công build/query và order agreement thực nghiệm; chỉ có guarantee nếu có theorem/adapter riêng. |
| Candidate với sharing bị tắt | Cùng thuật toán/certificate và input; không chia sẻ representation/cache giữa đối tượng/truy vấn theo định nghĩa đã khai | Ablation bắt buộc để tách lợi ích reuse khỏi kernel, bound hay phần cứng; phải tính cả phần build lặp. |

Đây là panel phương pháp tối thiểu, không bắt buộc viết adapter cho từng repository
được thu thập. Các framework khác, gồm [AOTNumerics / Computational methods for
adapted optimal transport](https://arxiv.org/abs/2203.05005), fitted value iteration,
occupancy/policy-gradient và representations khác, được giữ làm novelty threat
hoặc ứng viên có điều kiện nếu có thể thay quyết định. Không kéo tất cả thành
completion requirement. AOTNumerics/POT không được tải thêm hay kiểm môi trường
trong lượt này; thông tin lịch sử nằm trong baseline register.

Quyết định thứ tự chỉ được công bố khi interval/certificate hợp lệ chứng minh
quan hệ đã khai (ví dụ `U(a,b) < L(a,c)` cho thứ tự strict). Interval chồng nhau là
abstention, không tự biến thành sai thứ tự hay tự ép fallback; ties theo contract.
So sánh numerical speed và certified decision cost/coverage riêng, cùng quyền truy
cập dữ liệu và ngân sách. Tính build, conversion, applicability, calibration,
query, update, feasibility repair, error checks và fallback nếu sử dụng; ghi
amortization theo số object/query thật. Package không expose certificate chỉ có
nghĩa **adapter chưa sẵn sàng**, không chứng minh certificate bất khả thi.

## Phục hồi sau fresh clone

Chạy từ repo root bằng PowerShell. Đây là lệnh fetch/source checkout, không cài
hay thực thi code tải về. Chỉ chạy khi đường dẫn đích chưa tồn tại; nếu tồn tại,
kiểm HEAD/status và đối chiếu manifest, không ghi đè. Full pin có thể fetch từ
upstream chừng nào upstream còn cung cấp object; không hứa cache remote vĩnh viễn.

```powershell
$manifest = Get-Content -Raw -Encoding utf8 research-workflow/research/sota/comparison_toolkit_v4.json | ConvertFrom-Json
foreach ($source in $manifest.downloaded_checkouts) {
    $dest = $source.path
    if (Test-Path -LiteralPath $dest) { throw "Inspect existing destination first: $dest" }
    New-Item -ItemType Directory -Force -Path $dest | Out-Null
    git -c core.autocrlf=false init $dest
    if ($LASTEXITCODE -ne 0) { throw 'git init failed' }
    git -C $dest remote add origin $source.url
    git -C $dest fetch --depth 1 origin $source.commit
    if ($LASTEXITCODE -ne 0) { throw 'git fetch failed' }
    git -C $dest -c core.autocrlf=false checkout --detach FETCH_HEAD
    if ($LASTEXITCODE -ne 0) { throw 'git checkout failed' }
    $actual = git -C $dest rev-parse HEAD
    if ($actual -ne $source.commit) { throw 'Commit mismatch' }
    git -C $dest status --porcelain
}
```

NestedOT đã theo repo ở `third_party/nestedot`. Muốn so với upstream lại, tải
`vendor_validation.archive_url` vào `archive_path` trong JSON, kiểm SHA256 trước
khi so file trong zip với vendor; không chạy archive. `nestedot_vendor_comparison.json`
là log local tái tạo được, còn aggregate và archive pin được giữ trong manifest.

Quyết định tiếp theo thuộc PO: chọn một comparator adapter cùng target đủ mạnh cho
probe đã được cấp gate, sau đó mới cài môi trường tối thiểu và kiểm correctness.
Lượt này đã hoàn thành collection; chưa có kết quả tốc độ, coverage hay order guarantee mới.
