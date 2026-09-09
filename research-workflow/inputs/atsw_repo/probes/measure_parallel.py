import os, sys, time
sys.path.append(os.getcwd())
import numpy as np, ot
from concurrent.futures import ThreadPoolExecutor
import kmarkov_driver as KD

rg = np.random.default_rng(32_000_777)
Xa = KD.gen_paths(50, 4000, rg, a=0.7); Xb = KD.gen_paths(50, 4000, rg, a=0.55, sigma=1.15)
_sa, ra, Ka = KD.build(Xa, 0.5, 0.25); _sb, rb, Kb = KD.build(Xb, 0.5, 0.25)
V = np.zeros((len(ra[50]), len(rb[50]))); LAY = []
for t in range(49, -1, -1):
    M = np.ascontiguousarray((ra[t+1][:,None]-rb[t+1][None,:])**2 + V)
    LAY.append((np.ascontiguousarray(Ka[t]), np.ascontiguousarray(Kb[t]), M))
    Vn = np.empty((Ka[t].shape[0], Kb[t].shape[0]))
    for i in range(Ka[t].shape[0]):
        wa = np.ascontiguousarray(Ka[t][i])
        for j in range(Kb[t].shape[0]):
            Vn[i,j] = ot.emd2(wa, np.ascontiguousarray(Kb[t][j]), M)
    V = Vn
SUB = LAY[:12]
npairs = sum(WA.shape[0]*WB.shape[0] for WA,WB,_ in SUB)

def row(args):
    wa, WB, M = args
    return [ot.emd2(wa, np.ascontiguousarray(WB[j]), M) for j in range(WB.shape[0])]

def seq():
    for WA, WB, M in SUB:
        for i in range(WA.shape[0]):
            row((np.ascontiguousarray(WA[i]), WB, M))

def par(nw):
    with ThreadPoolExecutor(max_workers=nw) as ex:
        for WA, WB, M in SUB:
            list(ex.map(row, [(np.ascontiguousarray(WA[i]), WB, M) for i in range(WA.shape[0])]))

t0=time.perf_counter(); seq(); t1=time.perf_counter()-t0
print(f"tuần tự  : {t1:.3f}s  ({1e6*t1/npairs:.1f} us/cặp)  [{npairs} cặp, 12 tầng]")
for nw in (4, 10, 20):
    ts = []
    for _ in range(3):
        t0=time.perf_counter(); par(nw); ts.append(time.perf_counter()-t0)
    tm = sorted(ts)[1]
    print(f"{nw:2d} luồng : {tm:.3f}s  tăng tốc {t1/tm:.2f}x  (song song theo HÀNG trong mỗi tầng)")
print("cores:", os.cpu_count())
