# Cycle 3 reading — đặc tả cài được cho inner solver OT (n=m=20..60, chung một M, hàng nghìn biên)

Bối cảnh: mỗi tầng của vòng quy nạp lùi phải giải `B = n*m` bài toán vận chuyển Kantorovich
rời rạc, **tất cả dùng chung một ma trận chi phí `M` (n×m)**, chỉ khác cặp biên `(a, b)`.
`M` gần Monge (submodular) nhưng không thoả hẳn. Yêu cầu: **chính xác** (không Sinkhorn),
nhanh hơn champion hiện tại (đơn hình vận tải warm-start từ đỉnh tây-bắc, 0.66x `ot.emd2`).

Sáu đặc tả dưới đây xếp theo mức độ "khai thác được M dùng chung" giảm dần.
Mọi nguồn đều có DOI/arXiv đã kiểm qua Crossref. Chỗ nào tôi suy ra (không phải trích
dẫn) đều được đánh dấu **[suy ra tại đây, chưa có nguồn]**.

---

## SPEC 1 — Monge sequence: tiền xử lý MỘT LẦN trên M, mỗi biên chỉ còn greedy tuyến tính

**fits_shared_M: CÓ (đây là đúng cái bạn hỏi ở mục 1).**

### Ý tưởng cốt lõi
Hoffman (1963) chứng minh: nếu `M` thoả điều kiện Monge thì quy tắc góc tây-bắc là tối ưu
**cho mọi cặp biên**, và quy tắc đó thậm chí không đọc giá trị của `M`. Tổng quát hoá của
Hoffman: một hoán vị `σ` của `n*m` ô được gọi là **Monge sequence** của `M` nếu thuật toán
greedy chạy theo thứ tự `σ` (lấy `t = min(a_i, b_j)` tại mỗi ô, trừ đi, đi tiếp) cho nghiệm
tối ưu **với mọi vector cung và cầu**. Alon–Cosares–Hochbaum–Shamir (1989) đưa ra thuật toán
đa thức đầu tiên vừa *kiểm tra* điều kiện Hoffman vừa *xây* Monge sequence khi nó tồn tại;
tác giả nói rõ mục đích: sau khi có `σ`, "mọi bài toán vận chuyển tiếp theo với ma trận chi
phí đó giải được trong thời gian tuyến tính".

Đây là cấu trúc khớp chính xác với bài toán của bạn: `σ` phụ thuộc **chỉ vào M**, chi phí
xây `σ` khấu hao trên `n*m` bài toán của tầng.

Điều kiện tiền tố Hoffman: `σ` là Monge sequence ⟺ với mọi cặp ô `(i,j)` đứng trước `(k,l)`
trong `σ` mà `k≠i, l≠j`:  `M[i,j] + M[k,l] ≤ M[i,l] + M[k,j]`.

### Cấu trúc được khai thác
Tính submodular *cục bộ* (bất đẳng thức tứ giác trên từng cặp ô), không cần Monge toàn cục.
`M` "gần Monge" của bạn có khả năng cao vẫn có Monge sequence, hoặc có **tiền tố Monge dài**
(xem phần dự phòng). Quan trọng: tính admissible là **đơn điệu** — khi tập ô còn lại co lại,
một ô đã admissible thì mãi admissible ⟹ xây `σ` theo vòng "bóc lớp", mỗi lớp xuất ra theo
thứ tự tuỳ ý.

### Độ phức tạp tuyên bố
- Xây `σ`: Alon et al. tuyên bố đa thức và "nhanh hơn thuật toán tốt nhất đã biết cho bài
  toán vận chuyển" (con số chính xác nằm trong bài, **tôi chưa xác minh**). Bản numpy bóc
  lớp dưới đây: `O(rounds · (nm)²)` với `rounds` thực nghiệm nhỏ; `nm ≤ 3600` ⟹ mỗi vòng là
  một reduce trên ma trận 3600×3600 (~0.1 s), bộ nhớ ~100 MB/tạm.
- Giải mỗi biên: `O(n + m + |σ|)`, **không pivot, không LP**. Bản batch: `|σ|` phép toán
  vector trên mảng độ dài `B` ⟹ `O(nm · B)` cho cả tầng, thuần numpy, không vòng lặp Python
  theo bài toán.

### Pseudocode
```python
# ============ MỘT LẦN cho mỗi tầng ============
def monge_sequence(M, tol=1e-12):
    n, m = M.shape
    I, J = [x.ravel() for x in np.meshgrid(np.arange(n), np.arange(m), indexing='ij')]
    alive = np.ones(n*m, bool); seq = []
    while alive.any():
        i, j = I[alive], J[alive]; v = M[i, j]
        # V[c,c'] = M[i,j] + M[i',j'] - M[i,j'] - M[i',j]  (test tiền tố Hoffman)
        V = v[:, None] + v[None, :] - M[i[:, None], j[None, :]] - M[i[None, :], j[:, None]]
        mask = (i[:, None] != i[None, :]) & (j[:, None] != j[None, :])
        adm = ((V <= tol) | ~mask).all(axis=1)     # ô c được phép đứng trước MỌI ô còn lại
        if not adm.any():
            return seq, (i, j)                     # KHÔNG có Monge sequence -> khối dư
        idx = np.flatnonzero(alive)[adm]
        seq.extend(zip(I[idx], J[idx])); alive[idx] = False   # đồng hạng: thứ tự nào cũng đúng
    return seq, None

# ============ MỖI TẦNG, TẤT CẢ B BIÊN CÙNG LÚC ============
def greedy_batch(seq, M, A, Bm):        # A:(B,n)  Bm:(B,m)
    a, b = A.copy(), Bm.copy(); cost = np.zeros(len(A))
    for (i, j) in seq:                  # |seq| <= n*m vòng, mỗi vòng là op vector độ dài B
        t = np.minimum(a[:, i], b[:, j])
        cost += t * M[i, j]; a[:, i] -= t; b[:, j] -= t
    return cost                          # CHÍNH XÁC nếu seq là Monge sequence
```

### Dự phòng khi không tồn tại Monge sequence đầy đủ (trường hợp "gần Monge" của bạn)
`monge_sequence` trả về tiền tố hợp lệ + khối ô dư. Chạy greedy theo tiền tố, rồi giải bài
toán vận chuyển **thặng dư** (chỉ trên các hàng/cột chưa cạn) bằng champion hiện tại. Kích
thước bài toán thặng dư là tiêu chí giết khai tự nhiên: nếu nó không nhỏ hơn hẳn n×m thì
hướng này chết. Có kết quả liên quan: greedy theo một chuỗi khởi đầu vẫn tối ưu ngay cả khi
không có Monge sequence, với điều kiện không phát sinh thiếu/thừa (Allocation under a general
substitution structure, EJOR 2019) — điều kiện này kiểm được sau khi chạy.

**[suy ra tại đây, chưa có nguồn]** Điều kiện tiền tố Hoffman chỉ là bất đẳng thức trên các
cặp ô, nên **hạn chế của một Monge sequence xuống một ma trận con bất kỳ vẫn là Monge
sequence của ma trận con đó**. Trong cây kịch bản (SPEC 6), mỗi cặp nút dùng một *ma trận
con* của ma trận khoảng cách tầng sau; vậy một `σ` xây trên ma trận tầng đầy đủ dùng lại
được cho mọi cặp nút. Đây là đòn bẩy lớn nhất trong toàn bộ danh sách.

### Nguồn
- A. J. Hoffman, "On simple linear programming problems", in V. Klee (ed.), *Convexity*,
  Proc. Symposia in Pure Mathematics vol. 7, AMS, 1963, pp. 317–327.
- N. Alon, S. Cosares, D. S. Hochbaum, R. Shamir, "An algorithm for the detection and
  construction of Monge sequences", *Linear Algebra Appl.* 114/115 (1989) 669–680.
  DOI 10.1016/0024-3795(89)90487-4
- U. Derigs, O. Goecke, R. Schrader, "Monge sequences and a simple assignment algorithm",
  *Discrete Appl. Math.* 15 (1986) 241–248. DOI 10.1016/0166-218X(86)90045-4
- R. Shamir, "A fast algorithm for constructing Monge sequences in transportation problems
  with forbidden arcs", *Discrete Math.* 114 (1993) 435–444. DOI 10.1016/0012-365X(93)90382-4
  (bản có ô cấm; dùng nếu bạn ép `M[i,j]=+inf` ở đâu đó)
- B. L. Dietrich, "Monge sequences, antimatroids, and the transportation problem with
  forbidden arcs", *Linear Algebra Appl.* 139 (1990) 133–145. DOI 10.1016/0024-3795(90)90393-Q
  (cấu trúc antimatroid của tập Monge sequence — giải thích vì sao "bóc lớp" trong pseudocode
  là đúng: tập ô admissible tại mỗi bước là tập khả thi của một antimatroid).
- "Allocation under a general substitution structure", *EJOR* 277 (2019) 492–506.
  DOI 10.1016/j.ejor.2019.02.049 — dùng cho phần "greedy vẫn tối ưu khi không có Monge
  sequence, nếu không phát sinh thiếu/thừa".

---

## SPEC 2 — Góc tây-bắc Hoffman + chứng chỉ vi phạm Monge; họ SMAWK/AKMSW cho chi phí thoả bất đẳng thức tứ giác

**fits_shared_M: CÓ (chứng chỉ Monge tính một lần trên M).**

### Ý tưởng cốt lõi
Hai phần.

(a) **Chứng chỉ.** Monge toàn cục tương đương điều kiện 2×2 kề nhau. Tính
`δ = max(0, max_{i,j} (M[i,j] + M[i+1,j+1] - M[i,j+1] - M[i+1,j]))` một lần: `δ = 0` ⟺ `M`
Monge ⟺ NW-corner **đã là tối ưu chính xác** cho mọi biên, và bạn có thể xoá hẳn pha đơn hình.
Đây là phép thử rẻ nhất trong cả tài liệu này (một phép trừ ma trận) và nó *kết thúc* chu kỳ
nếu `δ = 0`. Với `δ > 0`: **[suy ra tại đây]** nếu `M = M̃ + E` với `M̃` Monge, thì
`cost_M(NW) - opt_M ≤ 2‖E‖_∞ · mass`; tìm `M̃` gần nhất theo sup-norm là một LP (biến `M̃`,
ràng buộc 2×2 kề nhau) giải một lần cho cả tầng, cho **cận sai số tiên nghiệm** — nhưng đó là
cận, không phải nghiệm chính xác, nên chỉ dùng để quyết định có đáng chạy pha sửa hay không.

(b) **Thuật toán chính xác chuyên cho chi phí tứ giác.** Aggarwal–Bar-Noy–Khuller–Kravets–
Schieber giải bài toán vận chuyển khi hàm chi phí thoả bất đẳng thức tứ giác; trường hợp các
điểm nằm trên một đường cong đồng phôi với đường thẳng/đường tròn và chi phí là khoảng cách
dọc đường cong, họ đạt `O((m+n) log(m+n))` cho bài toán vận chuyển và `O(n log m)` cho matching
với ma trận Monge bitonic. Công cụ nền là SMAWK (tìm cực tiểu hàng của ma trận toàn đơn điệu
trong thời gian tuyến tính).

**Đánh giá thẳng:** (b) chỉ áp dụng khi `M` sinh từ hình học 1 chiều. Nếu `M` của ATSW là
`|x_i - y_j|^p` trên lưới đã sắp thì (b) áp được; nếu `M` là ma trận khoảng cách quy nạp
tổng quát thì không. Kiểm điều kiện này trước khi cài.

### Cấu trúc được khai thác
Submodular (Monge) toàn cục; toàn đơn điệu (total monotonicity) của ma trận chi phí.

### Độ phức tạp tuyên bố
- Chứng chỉ `δ`: `O(nm)`, một lần.
- NW-corner batch: `O((n+m) · B)` op vector, chính xác khi `δ = 0`.
- AKMSW: `O((m+n) log(m+n))` cho vận chuyển trên đường cong; SMAWK `O(n+m)` cho cực tiểu hàng.

### Pseudocode
```python
def monge_gap(M):                                     # 0 <=> Monge <=> NW-corner tối ưu
    D = M[:-1, :-1] + M[1:, 1:] - M[:-1, 1:] - M[1:, :-1]
    return max(0.0, float(D.max()))

def nw_corner_batch(M, A, Bm):                        # A:(B,n)  Bm:(B,m)
    B = len(A); r = np.arange(B)
    a, b = A.copy(), Bm.copy()
    i = np.zeros(B, int); j = np.zeros(B, int); cost = np.zeros(B)
    for _ in range(n + m - 1):
        t = np.minimum(a[r, i], b[r, j])
        cost += t * M[i, j]
        a[r, i] -= t; b[r, j] -= t
        adv_j = b[r, j] <= 1e-15
        adv_i = (a[r, i] <= 1e-15) & ~adv_j
        j = np.minimum(j + adv_j, m - 1); i = np.minimum(i + adv_i, n - 1)
    return cost
# delta = monge_gap(M);  if delta == 0: XONG, nw_corner_batch là nghiệm chính xác.
# else: NW-corner là warm start (champion hiện tại) và cận 2*||E||_inf*mass là kill-criterion.
```

### Nguồn
- Hoffman 1963 (như trên).
- R. E. Burkard, B. Klinz, R. Rudolf, "Perspectives of Monge properties in optimization",
  *Discrete Appl. Math.* 70 (1996) 95–161. DOI 10.1016/0166-218X(95)00103-X (khảo sát chuẩn:
  Monge, Monge hoán vị, nhận dạng, ứng dụng).
- A. Aggarwal, A. Bar-Noy, S. Khuller, D. Kravets, B. Schieber, "Efficient minimum cost
  matching and transportation using the quadrangle inequality", *J. Algorithms* 19 (1995)
  116–143. DOI 10.1006/jagm.1995.1030 (bản hội nghị FOCS 1992, DOI 10.1109/SFCS.1992.267793).
- A. Aggarwal, M. Klawe, S. Moran, P. Shor, R. Wilber, "Geometric applications of a
  matrix-searching algorithm" (SMAWK), *Algorithmica* 2 (1987) 195–208. DOI 10.1007/BF01840359
- W. W. Bein, P. Brucker, J. K. Park, P. K. Pathak, "A Monge property for the d-dimensional
  transportation problem", *Discrete Appl. Math.* 58 (1995) 97–109.
  DOI 10.1016/0166-218X(93)E0121-E
- R. Rudolf, G. J. Woeginger, "The cone of Monge matrices: extremal rays and applications",
  *ZOR* 42 (1995) 161–168. DOI 10.1007/BF01415751 (dùng nếu bạn muốn *chiếu* M lên nón Monge).

---

## SPEC 3 — Cố định thế đối ngẫu khả thi cho cả tầng + đồ thị đẳng thức + đường tăng ngắn nhất khởi động ấm

**fits_shared_M: CÓ (đây chính xác là giả thuyết bạn nêu ở mục 1 — và nó đúng).**

### Ý tưởng cốt lõi
Ràng buộc đối ngẫu là `u_i + v_j ≤ M_ij`. **Không có `a`, `b` trong đó.** Vậy một `(u,v)`
khả thi đối ngẫu là khả thi cho *mọi* biên trong tầng. Hệ quả cài được:

1. Tính `(u,v)` một lần cho tầng (ví dụ: giải một bài đại diện với biên trung bình đến tối
   ưu, lấy thế từ cây cơ sở — hoặc lấy từ SPEC 1/2 nếu có).
2. `Cbar = M - u ⊕ v ≥ 0` và **đồ thị đẳng thức** `E = {(i,j) : Cbar[i,j] = 0}` dùng chung.
3. Với mỗi biên: chạy **luồng cực đại chỉ trên `E`**. Nếu đẩy được toàn bộ khối lượng thì
   theo bù trừ lỏng nghiệm đó **tối ưu**, và giá trị là `⟨u,a⟩ + ⟨v,b⟩` — không một pivot nào.
4. Chỉ khi còn thặng dư mới cập nhật đối ngẫu, bằng đường tăng ngắn nhất (SSP) trên chi phí
   rút gọn, khởi động từ `(u,v)` chứ không từ 0.

Đây đúng là **phương pháp nguyên-đối ngẫu** cổ điển (bài toán hạn chế = restricted primal) và
SSP với thế nút; xem AMO chương 9. Điểm mới trong ngữ cảnh của bạn không phải thuật toán mà là
*khấu hao*: bước dựng `(u,v)` và `E`, vốn là phần đắt, chia đều cho `n*m` bài toán.

Chỉ báo giết khai: đo tỉ lệ biên được giải xong ở bước 3 (0 pivot). Nếu `E` quá thưa để chở
hết khối lượng cho phần lớn biên, hướng này chết — và điều đó đo được trước khi cài SSP đầy đủ:
chỉ cần chạy `maxflow(E, a, b)` cho một mẫu biên.

### Cấu trúc được khai thác
Khả thi đối ngẫu độc lập với vế phải; bù trừ lỏng; độ thưa của đồ thị đẳng thức.

### Độ phức tạp tuyên bố
- Pha 1 (chỉ trên `E`): ≤ `n+m-1` lần tăng luồng, mỗi lần `O(|E|)` ⟹ `O((n+m)|E|)`; nếu `E`
  thưa thì rẻ hơn hẳn `O(nm)`.
- Pha 2 (SSP dày): `O((n+m) · nm)` xấu nhất cho mỗi bài (Dijkstra dày `O(nm)` mỗi lần tăng,
  ≤ `n+m-1` lần tăng vì mỗi lần làm cạn một nút).
- Với `n=m=50`: pha 1 ~ `100·|E|`; pha 2 xấu nhất ~ `2.5·10^5` flop.

### Pseudocode
```python
# ---- MỘT LẦN cho mỗi tầng ----
u, v   = dual_from_one_representative_solve(M, a_bar, b_bar)   # ví dụ champion hiện tại
Cbar   = M - u[:, None] - v[None, :]                           # >= 0, dùng chung
E      = Cbar <= 1e-12                                         # đồ thị đẳng thức, dùng chung

# ---- MỖI BIÊN ----
def solve_shared_dual(a, b, u, v, Cbar, E, M):
    X, ra, rb = maxflow_bipartite(E, a, b)      # đường tăng, <= n+m-1 lần
    if ra.sum() <= 1e-12:
        return float(u @ a + v @ b), X          # TỐI ƯU, 0 lần cập nhật đối ngẫu
    p = np.zeros(len(a)); q = np.zeros(len(b))  # hiệu chỉnh thế, khởi từ (u,v)
    while ra.sum() > 1e-12:
        C = Cbar + p[:, None] - q[None, :]      # >= 0 bất biến
        dist, pred = dijkstra_dense_bipartite(C, sources=(ra > 1e-12), sinks=(rb > 1e-12))
        p += dist_rows; q += dist_cols          # cập nhật thế theo nhãn ngắn nhất
        s, t, path = argmin_sink(dist, pred)
        delta = min(ra[s], rb[t], residual_caps_along(path))
        push(X, path, delta); ra[s] -= delta; rb[t] -= delta
    return float((M * X).sum()), X
```

### Nguồn
- R. K. Ahuja, T. L. Magnanti, J. B. Orlin, *Network Flows: Theory, Algorithms, and
  Applications*, Prentice Hall, 1993 — **Chương 9, "Minimum Cost Flows: Basic Algorithms"**
  (đường tăng ngắn nhất kế tiếp, phương pháp nguyên-đối ngẫu, thế nút / chi phí rút gọn);
  Chương 11, "Minimum Cost Flows: Network Simplex Algorithms". ISBN 013617549X.
- L. R. Ford, D. R. Fulkerson, *Flows in Networks*, Princeton Univ. Press, 1962 (phương pháp
  nguyên-đối ngẫu gốc cho bài toán Hitchcock).
- P. Kovács, "Minimum-cost flow algorithms: an experimental evaluation",
  *Optim. Methods Softw.* 30 (2014) 94–127. DOI 10.1080/10556788.2014.895828 (chọn biến thể
  nào trong thực tế; đây là nguồn tốt nhất để đặt kỳ vọng thời gian chạy).

**Kết quả âm tính đi kèm:** tôi KHÔNG tìm được bài báo nào phát biểu tường minh chiến lược
"tính một thế đối ngẫu cho cả lớp bài toán rồi tái dùng trên hàng nghìn vế phải" như một
thuật toán có tên. Nó là hệ quả hiển nhiên của lý thuyết nguyên-đối ngẫu nhưng không được
đóng gói. Xem `not_found`.

---

## SPEC 4 — Thư viện nón cơ sở (basis cone) + tái tối ưu bằng đơn hình đối ngẫu / toán tử rim

**fits_shared_M: CÓ.**

### Ý tưởng cốt lõi
Một cơ sở của LP vận chuyển là một **cây khung** `T` của `K_{n,m}` với `n+m-1` ô. Với `T` cố
định:
- Nghiệm chính `x_T(a,b)` là hàm **tuyến tính** của `(a,b)`: giải cây bằng bóc lá, ma trận
  `L_T` tính trước một lần ⟹ `x_T = L_T · [a;b]`.
- Khả thi **đối ngẫu** của `T` phụ thuộc **chỉ vào M** (chi phí rút gọn `≥ 0`).
- Khả thi **chính** của `T` là `L_T·[a;b] ≥ 0` — đúng một **nón đa diện** trong không gian rim.

Vậy: *một cây khả thi đối ngẫu cho `M` là tối ưu cho MỌI biên nằm trong nón của nó.* Wallace
(1986) chứng minh các nón này lát kín không gian rim và đưa thuật toán sinh mọi cơ sở khả thi
đối ngẫu bằng pivot đối ngẫu trên mạng hai phía; EJOR 2002 chỉ ra với LP vận chuyển mọi đa diện
cơ sở đối ngẫu đều **đầy chiều và bị chặn**, và biểu diễn tối tiểu của nó lấy trực tiếp từ cây.

Cài đặt thực dụng: giữ một **thư viện nhỏ** các cây `(T, L_T, u_T, v_T)` đã gặp. Với mỗi biên
mới, thử lần lượt các cây trong thư viện: phép thử là một phép nhân ma trận-vector `O(nm)` và
một so sánh dấu. Trúng ⟹ **không pivot nào**. Trượt ⟹ tái tối ưu bằng **đơn hình đối ngẫu**
(cơ sở cũ vẫn khả thi đối ngẫu vì `M` không đổi; chỉ phải sửa khả thi chính), rồi nạp cây mới
vào thư viện. Đây chính là "rim operators" của Srinivasan–Thompson.

Chỉ báo giết khai: kích thước thư viện bão hoà ở đâu. Nếu sau 200 biên thư viện vẫn tăng tuyến
tính thì tỷ lệ trúng quá thấp và hướng này chết.

### Cấu trúc được khai thác
Chỉ vế phải thay đổi ⟹ cơ sở tối ưu cũ vẫn khả thi đối ngẫu (định lý cơ bản của phân tích độ
nhạy LP); phân hoạch không gian rim thành nón cơ sở; cấu trúc cây của cơ sở vận chuyển.

### Độ phức tạp tuyên bố
- Thử thành viên nón: `O(nm)` mỗi cây (vector hoá được trên cả thư viện *và* cả batch biên:
  một `tensordot` `(K, nm, n+m) × (B, n+m)`).
- Đơn hình đối ngẫu: một pivot = `O(n+m)` cho cắt cây + `O(nm)` cho ratio test. Số pivot tỉ lệ
  "khoảng cách" giữa các rim, không phụ thuộc cỡ bài toán.

### Pseudocode
```python
# L_T: (nm) x (n+m) — nghiệm cây là hàm tuyến tính của rim, tính bằng bóc lá
def tree_solution_matrix(T, n, m):
    L = np.zeros((len(T), n + m))
    for (i, j), row in peel_leaves(T):        # lá: ô duy nhất của một hàng/cột còn sống
        L[row] = accumulated_rim_coefficients(i, j)   # +e_i / +e_{n+j} trừ đi các nhánh con
    return L

library = []                                   # [(T, L_T, cost_T, u_T, v_T)]
def solve_layer(M, A, Bm):
    out = np.empty(len(A))
    for k, rim in enumerate(np.hstack([A, Bm])):
        for (T, L, cT, u, v) in library:
            x = L @ rim
            if (x >= -1e-12).all():            # rim nằm trong nón của T
                out[k] = cT @ x; break         # TỐI ƯU, 0 pivot
        else:
            T, x = dual_simplex(library[-1][0] if library else nw_tree(rim), M, rim)
            library.append(pack(T, M, n, m)); out[k] = (M[tuple(zip(*T))] * x).sum()
    return out

def dual_simplex(T, M, rim):                   # chỉ sửa khả thi CHÍNH
    while True:
        x = solve_tree(T, rim)
        neg = np.flatnonzero(x < -1e-12)
        if neg.size == 0: return T, x
        leave = T[neg[0]]                      # bỏ ô này -> cây tách thành (S, S^c)
        S = side_of_cut(T, leave)
        cand = cells_crossing_cut(S, direction_fixed_by_sign)
        u, v = tree_potentials(T, M)
        enter = cand[np.argmin(M[cand[:,0], cand[:,1]] - u[cand[:,0]] - v[cand[:,1]])]
        T = swap(T, leave, enter)
```

### Nguồn
- V. Srinivasan, G. L. Thompson, "An operator theory of parametric programming for the
  transportation problem — I", *Naval Res. Logist. Quart.* 19 (1972) 205–225.
  DOI 10.1002/nav.3800190202; **— II**, 19 (1972) 227–252. DOI 10.1002/nav.3800190203.
  (Rim operators: chính xác là "cùng M, đổi cung/cầu".)
- S. W. Wallace, "Decomposing the requirement space of a transportation problem into
  polyhedral cones", *Mathematical Programming Studies* (1986) 29–47. DOI 10.1007/BFb0121124
- "Multiparametric demand transportation problem", *EJOR* 139 (2002) 206–219.
  DOI 10.1016/S0377-2217(01)00357-5 (đa diện cơ sở đối ngẫu đầy chiều, bị chặn; biểu diễn
  tối tiểu lấy từ cây khung).
- AMO 1993, Chương 11 (đơn hình mạng, cấu trúc cây cơ sở) — như trên.

---

## SPEC 5 — Đấu giá ε-scaling theo lô, giá khởi tạo dùng chung (numpy/GPU tensor)

**fits_shared_M: CÓ (vector giá là đối ngẫu của M, độc lập biên).**

### Ý tưởng cốt lõi
Bertsekas–Castañon tổng quát hoá thuật toán đấu giá sang bài toán vận chuyển tuyến tính bằng
cách chuyển nó thành bài toán gán rồi khai thác cấu trúc "người/vật giống nhau"; các pha đặt
giá và trao vật **song song hoá được hoàn toàn**. Với chi phí nguyên và ε-scaling xuống dưới
`1/min(n,m)`, nghiệm là **tối ưu chính xác** — không phải xấp xỉ entropic.

Ba điểm khiến nó khớp bài toán của bạn:
1. Biến đối ngẫu duy nhất là vector giá `q` trên đích; điều kiện ε-bù trừ lỏng chỉ dính `M`
   và `q`, **không dính biên** ⟹ một `q₀` tốt cho cả tầng.
2. Pha đặt giá là một phép reduce `argmax`/`top-2` trên tensor `(B, n, m)` — đúng khuôn numpy
   và GPU, không có cấu trúc dữ liệu cây, không nhánh rẽ theo bài toán.
3. Trong đúng dòng nested distance, Qu–Tran nêu rõ các bài OT con "giải được bằng thuật toán
   đấu giá với độ phức tạp `O(n³ log n)`" — tức đây là lựa chọn đã được dùng ở chính lĩnh vực
   của bạn.

Cảnh báo cài đặt: đấu giá cần **chi phí nguyên** để bảo đảm chính xác. Nhân `M` với `1/ε₀` rồi
làm tròn; sai số làm tròn phải nhỏ hơn khe tối ưu. Nếu biên của bạn là số thực (không phải bội
của một đơn vị chung) thì phải rời rạc hoá khối lượng nữa — đây là rủi ro chính xác lớn nhất
của SPEC này và là tiêu chí giết khai: **đo lại bằng `ot.emd2` trên toàn bộ tầng, phải khớp
đến 1e-12, không thì bỏ.**

### Cấu trúc được khai thác
Đối ngẫu độc lập biên (giá); song song hoá theo người đặt giá; ε-scaling.

### Độ phức tạp tuyên bố
`O(n³ log(nC))` mỗi bài với ε-scaling (con số Qu–Tran trích cho OT con của nested distance là
`O(n³ log n)`); theo lô, chi phí mỗi vòng quét là `B·n·m` phép toán tensor.

### Pseudocode
```python
Mi = np.rint(M / eps0).astype(np.int64)         # chi phí nguyên hoá (BẮT BUỘC cho tính đúng)

def auction_batch(Mi, A, Bm, q0, eps_list):     # A:(B,n) cung, Bm:(B,m) cầu
    B, n = A.shape; m = Bm.shape[1]
    q = np.tile(q0, (B, 1)).astype(float)       # giá khởi tạo DÙNG CHUNG cho cả tầng
    for eps in eps_list:                        # ε-scaling: eps giảm dần < 1/min(n,m)
        X  = np.zeros((B, n, m)); ra = A.copy(); rb = Bm.copy()
        while (ra > 1e-12).any():
            V  = -Mi[None] - q[:, None, :]                      # (B,n,m) giá trị đích j với i
            V  = np.where(rb[:, None, :] > 1e-12, V, -np.inf)   # chỉ đích còn chỗ
            V  = np.where((ra > 1e-12)[:, :, None], V, -np.inf) # chỉ nguồn còn hàng
            j1 = V.argmax(2); v1 = np.take_along_axis(V, j1[..., None], 2)[..., 0]
            v2 = np.partition(V, -2, axis=2)[:, :, -2]          # giá trị tốt nhì
            bid = np.take_along_axis(q, j1, 1) + (v1 - v2) + eps
            # trao mỗi đích cho người trả cao nhất; chuyển t = min(ra_i, rb_j)
            q, X, ra, rb = award_highest_bidder(q, X, ra, rb, j1, bid)
        q0 = q[0]                               # tái dùng cho vòng eps sau
    return (X * Mi).sum((1, 2)) * eps0
```

### Nguồn
- D. P. Bertsekas, D. A. Castañon, "The auction algorithm for transportation problems",
  *Annals of Operations Research* 20 (1989) 67–96. DOI 10.1007/BF02216923
- D. P. Bertsekas, D. A. Castañon, "A generic auction algorithm for the minimum cost network
  flow problem", *Comput. Optim. Appl.* 2 (1993) 229–260.
- Z. Qu, B. Tran, "Entropic regularization of the nested distance", arXiv:2107.09864 (nêu
  `O(n³ log n)` cho OT con bằng đấu giá trong ngữ cảnh nested distance).
- Đối chứng phía GPU: "GPU-accelerated transportation simplex algorithm", *J. Parallel
  Distrib. Comput.* 184 (2024) 104790. DOI 10.1016/j.jpdc.2023.104790 — họ tăng tốc **một**
  bài lớn (1000×10000), KHÔNG phải hàng nghìn bài nhỏ; kết luận của tài liệu song song hoá
  đơn hình mạng cho bài nhỏ là tiêu cực (chi phí copy host↔device át phần tìm pivot). Với cỡ
  20..60 của bạn, song song hoá **giữa các bài** (đấu giá theo lô) là hướng đúng, không phải
  song song hoá *bên trong* một bài.

---

## SPEC 6 — Inner solver trong dòng nested distance / adapted Wasserstein: hiện trạng và khuôn quy nạp lùi

**fits_shared_M: MỘT PHẦN — cấu trúc có sẵn, nhưng chưa ai khai thác.**

### Ý tưởng cốt lõi
Khoảng cách lồng (nested distance) của Pflug–Pichler tính bằng quy nạp lùi trên hai cây kịch
bản: ở mỗi cặp nút `(i,j)` cùng tầng, giải một bài OT giữa hai phân phối con có điều kiện, với
ma trận chi phí là **ma trận khoảng cách của tầng sau đã tính xong**. Kovacevic–Pichler đưa
thuật toán tính/xấp xỉ trên cây; Pflug–Pichler (2014) trình bày hệ thống ở chương "The Nested
Distance".

Điểm mấu chốt cho bạn: `M_ij = d[t+1][children(i), children(j)]` là **ma trận con của một ma
trận duy nhất của tầng** `d[t+1]`. Nghĩa là cấu trúc "chung một M" mà bạn mô tả đã có sẵn
trong bài toán chuẩn — nhưng không tài liệu nào tôi tra được khai thác nó.

Ai đã làm gì cho inner solver:
- **LP tổng quát mỗi cặp nút**: Pflug–Pichler 2012; Kovacevic–Pichler 2015. Đây là mặc định.
- **Đấu giá `O(n³ log n)`**: Qu–Tran (arXiv:2107.09864) — lựa chọn *chính xác* duy nhất được
  nêu tên mà tôi tìm thấy.
- **Entropic**: Pichler–Weinhardt, "The nested Sinkhorn divergence to learn the nested
  distance" (DOI 10.1007/s10287-021-00415-7); Eckstein–Pammer (DOI 10.1214/23-AAP1975) chứng
  minh AOT ổn định theo nhiễu biên nên xấp xỉ được bằng dãy LP, và entropic hội tụ về bài gốc
  khi tham số → 0. Cả hai **không chính xác** theo tiêu chuẩn của bạn.
- **Quy hoạch động / value iteration**: Bayraktar–Han, "Fitted value iteration methods for
  bicausal optimal transport" (DOI 10.1007/s00245-025-10283-1); Moulos, "Bicausal optimal
  transport for Markov chains via dynamic programming" (DOI 10.1109/ISIT45174.2021.9517977).
  Đây là tối ưu hoá *ngoài*, vẫn cần inner solver.

**Kết luận thẳng: chưa có ai làm inner solver chuyên dụng khai thác M dùng chung cho nested
distance / adapted Wasserstein.** Cái gần nhất là chọn đấu giá thay LP. Đây là khoảng trống
thật, và nó là chỗ đóng góp của bạn.

### Độ phức tạp tuyên bố
Số bài OT con là hàm mũ theo chân trời `T` (Qu–Tran nói rõ điều này), mỗi bài cỡ `n` = số con
tối đa của một nút. Với inner solver `O(n³ log n)` (đấu giá), tổng chi phí tầng `t` là
`|nodes_t|² · O(n³ log n)`.

### Pseudocode
```python
# d[T] = ma trận khoảng cách trạng thái cuối (từ chi phí nền c)
for t in range(T - 1, -1, -1):
    Dnext = d[t + 1]                                    # MỘT ma trận dùng chung cho cả tầng
    seq, resid = monge_sequence(Dnext)                  # <-- SPEC 1, khấu hao trên cả tầng
    A = []; Bm = []; idx = []
    for i in nodes(t, tree1):
        for j in nodes(t, tree2):
            A.append(cond_prob(tree1, i)); Bm.append(cond_prob(tree2, j)); idx.append((i, j))
    # mọi cặp (i,j) dùng MA TRẬN CON của Dnext -> hạn chế của seq vẫn là Monge sequence
    # [suy ra tại đây]: điều kiện tiền tố Hoffman là bất đẳng thức theo cặp ô, kế thừa xuống
    # ma trận con, nên chỉ cần lọc seq theo (children(i) x children(j)).
    vals = greedy_batch_submatrix(seq, Dnext, A, Bm, idx)
    for (i, j), w in zip(idx, vals):
        d[t][i, j] = (c[i, j] ** r + w) ** (1.0 / r)
```

### Nguồn
- G. Ch. Pflug, A. Pichler, "A distance for multistage stochastic optimization models",
  *SIAM J. Optim.* 22(1) (2012) 1–23. DOI 10.1137/110825054
- G. Ch. Pflug, A. Pichler, *Multistage Stochastic Optimization*, Springer, 2014,
  **Chương 2 "The Nested Distance"**, pp. 41–93. DOI 10.1007/978-3-319-08843-3_2
- R. Kovacevic, A. Pichler, "Tree approximation for discrete time stochastic processes: a
  process distance approach", *Ann. Oper. Res.* 235 (2015) 395–421. DOI 10.1007/s10479-015-1994-2
- A. Pichler, M. Weinhardt, "The nested Sinkhorn divergence to learn the nested distance",
  *Comput. Manag. Sci.* 19 (2021) 269–293. DOI 10.1007/s10287-021-00415-7
- S. Eckstein, G. Pammer, "Computational methods for adapted optimal transport",
  *Ann. Appl. Probab.* 34(1A) (2024) 675–713. DOI 10.1214/23-AAP1975 (arXiv:2203.05005)
- Z. Qu, B. Tran, "Entropic regularization of the nested distance", arXiv:2107.09864
- E. Bayraktar, B. Han, "Fitted value iteration methods for bicausal optimal transport",
  *Appl. Math. Optim.* 92 (2025). DOI 10.1007/s00245-025-10283-1
- V. Moulos, "Bicausal optimal transport for Markov chains via dynamic programming",
  ISIT 2021, pp. 1688–1693. DOI 10.1109/ISIT45174.2021.9517977

---

## not_found — kết quả âm tính (có giá trị)

1. **Không có thuật toán mang tên "same cost matrix, many right-hand sides" cho OT chính
   xác.** Giả thuyết của bạn (đối ngẫu khả thi không phụ thuộc biên ⟹ tái dùng `(u,v)` và đồ
   thị đẳng thức) **đúng về mặt lý thuyết** và là hệ quả trực tiếp của phương pháp nguyên-đối
   ngẫu (AMO Ch. 9), nhưng tôi không tìm được bài báo nào đóng gói nó thành thuật toán có tên,
   có phân tích khấu hao, cho chế độ "hàng nghìn vế phải, một ma trận". Dòng gần nhất là
   parametric transportation (Srinivasan–Thompson, Wallace) — nhưng họ giả định vế phải biến
   thiên theo **một tham số** dọc một đường thẳng, không phải một đám mây `n*m` điểm rời rạc.
   Monge sequence (SPEC 1) là thứ duy nhất trong tài liệu *thật sự* tiền xử lý M cho mọi biên.

2. **Không có phân tích cận sai số của NW-corner theo mức vi phạm Monge.** Tôi tìm nhưng
   không thấy kết quả kiểu "nếu `δ = max` vi phạm 2×2 thì `cost(NW) - opt ≤ f(δ)`" hoặc
   "số pivot đơn hình từ warm start NW-corner bị chặn bởi `g(δ)`". Cận `2‖E‖_∞·mass` trong
   SPEC 2 là tôi tự suy, tầm thường, và gần như chắc chắn lỏng. Đây là chỗ trống có thể tự
   chứng minh được — và nó *chính là* định lượng cho champion hiện tại của bạn.

3. **Không có solver OT chính xác (LP-exact) theo lô trên GPU.** POT 0.9.7+ có `ot.batch.
   solve_batch` giải "exact OT" theo lô khi `reg=0`, nhưng theo release notes nó dùng **proximal
   point solver** (lặp entropic), tức chính xác ở giới hạn chứ không phải đơn hình. Với tiêu
   chuẩn "đúng tuyệt đối" của bạn thì đây không đủ — **cần đo lại chứ đừng tin nhãn "exact"**.
   Phía đơn hình mạng, tài liệu nói song song hoá *bên trong* một bài nhỏ là thất bại (chi phí
   copy host↔device át phần tìm pivot). Kết luận: muốn GPU thì phải là thuật toán **thuần
   tensor** (đấu giá — SPEC 5, hoặc greedy Monge sequence — SPEC 1), không phải đơn hình.

4. **Không có inner solver chuyên dụng khai thác M dùng chung trong dòng nested distance /
   adapted Wasserstein.** Xem SPEC 6. Họ dùng LP tổng quát, hoặc đấu giá, hoặc entropic. Việc
   `M` của một tầng là **một ma trận duy nhất** mà mọi cặp nút chỉ lấy ma trận con — chưa ai
   khai thác.

5. **Không xác minh được độ phức tạp chính xác của thuật toán Alon et al.** Abstract chỉ nói
   "đa thức" và "nhanh hơn thuật toán tốt nhất đã biết cho bài toán vận chuyển"; tôi không truy
   cập được toàn văn để lấy con số. Bản numpy trong SPEC 1 có cận riêng, không phải cận của họ.

---

## Thứ tự thử đề xuất (theo tỉ lệ lợi ích / công cài)

1. `monge_gap(M)` — 3 dòng. Nếu `= 0` thì chu kỳ 3 kết thúc ngay tại đây với `≪ 0.5x`.
2. `monge_sequence(M)` + `greedy_batch` (SPEC 1). Nếu tồn tại `σ` đầy đủ: mất hẳn pha LP,
   toàn tầng thành `O(nm·B)` op vector. Đây là ứng viên `< 0.5x` mạnh nhất.
3. Nếu chỉ có tiền tố: đo kích thước khối dư. Tiêu chí giết khai: khối dư `≥ 0.5·n` hàng còn
   sống ⟹ bỏ.
4. SPEC 3 (thế dùng chung + đồ thị đẳng thức). Đo tỉ lệ biên xong ở pha 1 với 0 pivot.
5. SPEC 4 (thư viện nón). Đo độ bão hoà thư viện.
6. SPEC 5 (đấu giá theo lô) chỉ khi 2–5 đều chết và bạn chấp nhận rủi ro nguyên hoá chi phí.
