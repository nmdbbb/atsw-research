# Phương pháp: cây chung cho các trạng thái điều kiện

Thuật toán hiện có dựng một biểu diễn chung cho nhiều mô hình quá trình, rồi dùng
biểu diễn đó để trả khoảng adapted OT và chứng nhận thứ tự khi hai khoảng tách
nhau. Nó thay bảng transport giữa mọi cặp trạng thái bằng một đồ thị cạnh ứng
viên thưa, các cây có trọng số và một tập hàm thăm dò điều kiện dùng lại được.
Mục tiêu nghiên cứu rộng hơn là đánh đổi **kích thước biểu diễn, độ sắc bảo đảm
và tổng chi phí quyết định**, theo [hợp đồng](../objective.json).

## Đối tượng và đầu ra

Mỗi bài toán so sánh cố định luật quá trình, filtration, horizon, chi phí và
chuẩn hóa. Đại lượng cần giữ thứ tự là

```text
D(P,Q) = inf_{π bicausal} Eπ[Σ_t c_t(X_t,Y_t)].
```

Candidate thực thi trên mô hình k-window hữu hạn với xác suất và giá trị hữu tỉ,
quan sát đầy đủ trạng thái cửa sổ, chi phí vô hướng `c_t(x,y)=|x-y|` tại
`t=1,…,T`. Trong chế độ này `D=AW₁` của mô hình đã khai. Nếu mô hình được dựng
từ paths, certificate vẫn nói về mô hình đó; cần cầu nối riêng để kết luận về
luật population. Những giới hạn thực thi này không giới hạn miền nghiên cứu.

Với query `q`, candidate trả `[L(q,a),U(q,a)]` cho mỗi đối tượng `a`. Quy tắc
`U(q,a)<L(q,b)` chứng nhận `D(q,a)<D(q,b)`. Khoảng chồng nhau để unresolved;
`L=0` không chứng minh hai luật bằng nhau. Top-K, thứ tự đầy đủ và fallback là
mở rộng tùy chọn. Giao diện hiện tại trả bounds; bên gọi áp dụng quy tắc thứ tự.

## Biểu diễn điều kiện

Ở mỗi thời điểm, gộp các trạng thái có nhãn `(model_id, full_window)` từ toàn
batch thành một lớp. Hai trạng thái cùng đầu ra số vẫn tách biệt nếu thuộc hai
mô hình hoặc hai lịch sử: kernel tương lai của chúng có thể khác nhau. Mỗi lớp
có một cây so sánh; các kernel của mô hình giữ riêng quan hệ chuyển thời gian.
Cạnh cây là đường so sánh trạng thái, không phải bước thời gian hoặc phép sửa path.

Đặt `P_s` là kernel từ trạng thái `s`, `g_t(s,r)=|x_s-x_r|` cho `t≥1` và
`g_0=0`. Pseudometric điều kiện thật thỏa Bellman recursion:

```text
d_T(s,r) = |x_s-x_r|
d_t(s,r) = g_t(s,r) + W_{d_{t+1}}(P_s,P_r)
D(A,B)   = W_{d_0}(initial_A,initial_B).
```

Đây là đối tượng dùng trong chứng minh; candidate không dựng bảng `d_t` bằng
exact OT. Cây và các feature chỉ đọc trạng thái, khối lượng, kernel và đầu ra.

## Chặn trên bằng cây có trọng số

Lớp cuối dùng chain sắp theo đầu ra số; độ dài cạnh bằng chênh lệch tuyệt đối,
nên metric đường đi đúng bằng `d_T`. Các lớp trước xây đồ thị ứng viên từ cây
chia median theo feature và cạnh nối các nút kề nhau khi sắp từng tọa độ feature.
Tọa độ gồm đầu ra hiện tại và kỳ vọng các probe ở lớp sau. Mỗi cạnh `(s,r)` có
trọng số

```text
w_t(s,r) = g_t(s,r) + W_{ρ_{t+1}}(P_s,P_r),
```

trong đó `ρ` là metric đường đi của cây. Chọn minimum spanning tree trên đồ thị
đã cân trọng số. Tính đơn điệu của OT cho `w_t(s,r)≥d_t(s,r)`; bất đẳng thức
tam giác cho `ρ_t≥d_t` trên mọi cặp. Vì vậy
`U(A,B)=W_{ρ_0}(initial_A,initial_B)≥D(A,B)`.
MST tối thiểu hóa tổng trọng số cây, chưa có bảo đảm độ méo từng cặp. Cạnh dài
bằng không được phép. Lập luận áp dụng transport từng bước Bellman, không đồng
nhất một coupling ordinary OT trên toàn paths với coupling bicausal.

## Chặn dưới bằng probe điều kiện

Giả sử mọi probe `f_j` ở lớp sau đều 1-Lipschitz đối với `d_{t+1}`. Đặt

```text
z_s,j      = E_{P_s} f_j
ell_t(s,r) = g_t(s,r) + max_j |z_s,j-z_r,j| ≤ d_t(s,r).
```

Ở lớp cuối, `ell_T` là khoảng cách tuyệt đối. Mỗi `ell_t` là pseudometric;
`f_a(s)=ell_t(s,a)` là 1-Lipschitz đối với `d_t` nhờ bất đẳng thức tam giác đảo.
Candidate chọn tối đa bốn anchor: bắt đầu ở root cây, rồi farthest-first theo
`ell_t`. Tập probe giữ các hàm anchor và thêm mọi minimum của hai hàm anchor,
tối đa mười probe. Minimum hữu hạn giữ tính 1-Lipschitz. Cuối cùng,

```text
L(A,B) = max_j |E_initial_A f_j - E_initial_B f_j| ≤ D(A,B).
```

Probe nonlinear truyền thông tin kernel ngược thời gian. Pair-min phân biệt
được mẫu hỗ trợ mà khoảng cách tới từng anchor có thể bỏ sót; chưa có định lý
phân biệt mọi luật cho một tập probe hữu hạn. Dựng lại cây/anchor có thể làm
bounds xấu đi; code không cung cấp tính đơn điệu qua các batch khác nhau.

## Transport trên cây và chi phí phải tính

Với hai phân bố `a,b` trên cùng cây, công thức chính xác là
`W_ρ(a,b)=Σ_e length(e)·|a(subtree_e)-b(subtree_e)|`.
Candidate dùng virtual tree: lập Euler ancestry và bảng lowest common ancestor
(LCA), giữ các nút có signed mass khác không cùng LCA, nén các đoạn đường có
imbalance không đổi rồi cộng đóng góp. Ancestry dùng Euler intervals để xử lý
đúng cạnh độ dài không. Dense traversal dành cho kiểm tra độc lập của evaluator.

| Thành phần | Chi phí đã xác định và điều kiện |
|---|---|
| Index một cây `N` nút | `O(N log N)` phép toán và bộ nhớ. |
| Một tree-OT query | `O(m+s log s+s log N)`, với `m` entries đầu vào phải đọc, `s` signed-support sau triệt tiêu. |
| Cân cạnh ứng viên ở lớp `t` | Với `F` tọa độ feature, degree ≤`3+2F`; tổng support đọc `O(F E_t)` và transport `O(F E_t log(2+N_{t+1}))`. `E_t` là số entries chuyển tiếp toàn batch. |
| Chọn topology | Median recursion hiện có upper bound `O(F N log N+N log²N)`; thêm dựng graph và sắp cạnh cho MST. Cây nhỏ có thể dùng đồ thị đầy đủ. |
| Probe, quyết định và lưu trữ | Tính mọi kỳ vọng, khoảng cách anchor, pair-min, root bounds; lưu mô hình, cây, index, feature và graph tạm. Counter chưa là mô hình chi phí đầy đủ. |

Các mức trên coi phép toán hữu tỉ là đơn vị; độ dài bit vẫn là chi phí thêm.
Phải tính dựng mô hình, sorting, build/index, root queries, cập nhật và fallback
nếu dùng. Thuật toán dựng chung bao gồm cả queries trong batch; query mới có
thể cần rebuild. Chưa có online insertion rẻ, runtime advantage hoặc điểm hòa vốn.

## Giao diện và phạm vi xác nhận

[Module](../adapters/shared_conditional_tree.py) cung cấp
`SharedTrees(models, anchor_count=4, bank='pair_min', topology='feature_mst', engine='virtual', audit_dense=False)`
và `bounds(left_id,right_id) -> (lower,upper)`. `models[id]` chứa cặp
`(state_masses_by_time, transition_kernels_by_time)` của cùng horizon; trạng thái
cửa sổ phải có thứ tự xác định và giá trị cuối cửa sổ là đầu ra hiện tại.
Tính hợp lệ, chuẩn hóa và nhất quán của mô hình là tiền điều kiện; đây chưa là
adapter tiếp nhận mọi mảng float hoặc dictionary tùy ý. Thuộc tính `work` và
`graph_sizes` cho biết bộ đếm thao tác và mật độ đồ thị đã dựng.

[Thiết kế gốc](../research/theory/shared_tree_design_01.md),
[review](../research/theory/shared_tree_design_01_review.md) và
[verdict có hash](../research/theory/shared_tree_design_01_verdict.json) là nguồn
của các lập luận trên. Review xác nhận construction và implementation tại
artifact được ghi nhận; tài liệu tổng hợp này không tạo sign-off toán học mới.
[Bằng chứng](EVIDENCE.md) phân biệt certificate hữu hạn đã có với các kết quả
định lượng, độ mới và lợi thế chi phí còn thiếu.
