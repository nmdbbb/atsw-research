import os, sys, time, cProfile, pstats, io, importlib.util
sys.path.append(os.getcwd())
import numpy as np, ot
import kmarkov_driver as KD
sp = importlib.util.spec_from_file_location("v2","variants_v2.py")
m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); f25 = m.v2_5_inner_solve

def layers(delta, shift, T, npaths, nlay):
    rg = np.random.default_rng(34_000_000 + int(delta*100))
    Xa = KD.gen_paths(T, npaths, rg, a=0.7); Xb = KD.gen_paths(T, npaths, rg, a=0.55, sigma=1.15)
    _a, ra, Ka = KD.build(Xa, delta, shift); _b, rb, Kb = KD.build(Xb, delta, shift)
    V = np.zeros((len(ra[T]), len(rb[T]))); out = []
    for t in range(T-1, -1, -1):
        M = np.ascontiguousarray((ra[t+1][:,None]-rb[t+1][None,:])**2 + V)
        out.append((np.ascontiguousarray(Ka[t]), np.ascontiguousarray(Kb[t]), M))
        Vn = np.empty((Ka[t].shape[0], Kb[t].shape[0]))
        for i in range(Ka[t].shape[0]):
            wa = np.ascontiguousarray(Ka[t][i])
            for j in range(Kb[t].shape[0]):
                Vn[i,j] = ot.emd2(wa, np.ascontiguousarray(Kb[t][j]), M)
        V = Vn
    return out[-nlay:]          # các tầng GẦN GỐC (V đã tích lũy sâu nhất)

for delta, shift, npaths in ((0.5, 0.25, 4000), (0.18, 0.07, 8000)):
    LAY = layers(delta, shift, 50, npaths, 6)
    npairs = sum(WA.shape[0]*WB.shape[0] for WA,WB,_ in LAY)
    def run():
        for WA, WB, M in LAY:
            for i in range(WA.shape[0]):
                wa = np.ascontiguousarray(WA[i])
                for j in range(WB.shape[0]):
                    f25(wa, np.ascontiguousarray(WB[j]), M)
    pr = cProfile.Profile(); pr.enable(); run(); pr.disable()
    s = io.StringIO(); ps = pstats.Stats(pr, stream=s).sort_stats("ncalls")
    argmin = 0
    for (fn, ln, nm), (cc, nc, tt, ct, cs) in ps.stats.items():
        if nm == "argmin": argmin += nc
    t0=time.perf_counter(); run(); dt=time.perf_counter()-t0
    print(f"δ={delta}: {LAY[0][2].shape} | {npairs} cặp | {argmin/npairs:.2f} pivot/lần giải | "
          f"{1e6*dt/npairs:.0f} us/cặp (v2_5)", flush=True)
