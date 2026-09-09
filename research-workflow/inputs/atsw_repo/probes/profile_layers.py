import os, sys, time, cProfile, pstats, io, importlib.util
sys.path.append(os.getcwd())
import numpy as np, ot
import kmarkov_driver as KD
sp = importlib.util.spec_from_file_location("v2", "variants_v2.py")
m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
f25 = m.v2_5_inner_solve

rg = np.random.default_rng(32_000_777)
Xa = KD.gen_paths(50, 4000, rg, a=0.7); Xb = KD.gen_paths(50, 4000, rg, a=0.55, sigma=1.15)
_sa, ra, Ka = KD.build(Xa, 0.5, 0.25); _sb, rb, Kb = KD.build(Xb, 0.5, 0.25)

# tái tạo các tầng (M dùng chung mỗi tầng)
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
def run_emd():
    for WA, WB, M in SUB:
        for i in range(WA.shape[0]):
            wa = np.ascontiguousarray(WA[i])
            for j in range(WB.shape[0]):
                ot.emd2(wa, np.ascontiguousarray(WB[j]), M)
def run_v25():
    for WA, WB, M in SUB:
        for i in range(WA.shape[0]):
            wa = np.ascontiguousarray(WA[i])
            for j in range(WB.shape[0]):
                f25(wa, np.ascontiguousarray(WB[j]), M)
npairs = sum(WA.shape[0]*WB.shape[0] for WA,WB,_ in SUB)
for nm, fn in (("ot.emd2", run_emd), ("v2_5", run_v25)):
    pr = cProfile.Profile(); pr.enable(); fn(); pr.disable()
    s = io.StringIO(); ps = pstats.Stats(pr, stream=s).sort_stats("tottime"); ps.print_stats(9)
    tot = ps.total_tt
    print(f"\n########## {nm}: {npairs} cặp, tổng {tot:.3f}s, {1e6*tot/npairs:.1f} us/cặp")
    for line in s.getvalue().split("\n"):
        if line.strip() and ("{" in line or "(" in line) and "ncalls" not in line:
            print("   ", line.strip()[:150])
