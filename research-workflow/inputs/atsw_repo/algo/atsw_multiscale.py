"""ATSW với độ phân giải delta THAY ĐỔI THEO TẦNG.
Động cơ: ở T lớn, cây phi-dự-đoán bị thiếu mẫu ở tầng sâu (mỗi nút chỉ còn vài đường),
nên phân phối có điều kiện ước lượng tệ -> chệch lớn. Làm thô dần theo độ sâu giữ cho
mỗi nút còn đủ khối lượng."""
import numpy as np


def _ranges(sizes):
    if len(sizes) == 0:
        return np.zeros(0, np.int64)
    c = np.cumsum(sizes)
    out = np.ones(int(c[-1]), np.int64)
    out[0] = 0
    out[c[:-1]] -= sizes[:-1]
    return np.cumsum(out)


def atsw_ms(P1, w1, P2, w2, deltas, shifts, gcost=lambda dx: dx ** 2, tol=1e-14):
    """deltas, shifts: mảng độ dài T (một giá trị mỗi bước thời gian)."""
    T = P1.shape[1] - 1
    d = np.asarray(deltas, float); s = np.asarray(shifts, float)
    assert len(d) == T and len(s) == T
    C1 = np.floor((P1[:, 1:] - s[None, :]) / d[None, :]).astype(np.int64)
    C2 = np.floor((P2[:, 1:] - s[None, :]) / d[None, :]).astype(np.int64)
    pA = np.zeros(len(w1), np.int64); iA = np.arange(len(w1)); mA = (w1 / w1.sum()).astype(float)
    pB = np.zeros(len(w2), np.int64); iB = np.arange(len(w2)); mB = (w2 / w2.sum()).astype(float)
    total = 0.0; nseg = 0
    for t in range(T):
        ctr = lambda k: (k + 0.5) * d[t] + s[t]
        cA = C1[iA, t]; cB = C2[iB, t]
        oA = np.lexsort((cA, pA)); pA, iA, mA, cA = pA[oA], iA[oA], mA[oA], cA[oA]
        oB = np.lexsort((cB, pB)); pB, iB, mB, cB = pB[oB], iB[oB], mB[oB], cB[oB]
        newgA = np.empty(len(pA), bool); newgA[0] = True
        newgA[1:] = (pA[1:] != pA[:-1]) | (cA[1:] != cA[:-1])
        gidA = np.cumsum(newgA) - 1; ngA = gidA[-1] + 1
        gmA = np.bincount(gidA, weights=mA, minlength=ngA)
        gsA = np.flatnonzero(newgA); geA = np.append(gsA[1:], len(pA)); gpA = pA[gsA]; gcA = cA[gsA]
        newgB = np.empty(len(pB), bool); newgB[0] = True
        newgB[1:] = (pB[1:] != pB[:-1]) | (cB[1:] != cB[:-1])
        gidB = np.cumsum(newgB) - 1; ngB = gidB[-1] + 1
        gmB = np.bincount(gidB, weights=mB, minlength=ngB)
        gsB = np.flatnonzero(newgB); geB = np.append(gsB[1:], len(pB)); gpB = pB[gsB]; gcB = cB[gsB]
        npieces = int(max(gpA.max(), gpB.max())) + 1
        pmA = np.bincount(gpA, weights=gmA, minlength=npieces)
        pmB = np.bincount(gpB, weights=gmB, minlength=npieces)
        gmB = gmB * np.where(pmB > 0, pmA / np.maximum(pmB, 1e-300), 1.0)[gpB]
        cumA = np.cumsum(gmA); cumB = np.cumsum(gmB)
        startA = np.flatnonzero(np.concatenate([[True], gpA[1:] != gpA[:-1]]))
        baseA = np.zeros(ngA); baseA[startA[1:]] = cumA[startA[1:] - 1]
        baseA = np.maximum.accumulate(baseA); endA = cumA - baseA
        startB = np.flatnonzero(np.concatenate([[True], gpB[1:] != gpB[:-1]]))
        baseB = np.zeros(ngB); baseB[startB[1:]] = cumB[startB[1:] - 1]
        baseB = np.maximum.accumulate(baseB); endB = cumB - baseB
        Pm = np.concatenate([gpA, gpB]); Vm = np.concatenate([endA, endB])
        Sm = np.concatenate([np.zeros(ngA, np.int8), np.ones(ngB, np.int8)])
        om = np.lexsort((Sm, Vm, Pm)); Pm, Vm, Sm = Pm[om], Vm[om], Sm[om]
        firstm = np.concatenate([[True], Pm[1:] != Pm[:-1]])
        prevV = np.concatenate([[0.], Vm[:-1]]); prevV[firstm] = 0.
        seglen = Vm - prevV
        cntA = np.cumsum(Sm == 0) - (Sm == 0); cntB = np.cumsum(Sm == 1) - (Sm == 1)
        pf = np.flatnonzero(firstm)
        bA = np.zeros(len(Pm), np.int64); bA[pf] = cntA[pf]; bA = np.maximum.accumulate(bA)
        bB = np.zeros(len(Pm), np.int64); bB[pf] = cntB[pf]; bB = np.maximum.accumulate(bB)
        relA = cntA - bA; relB = cntB - bB
        cPA = np.bincount(gpA, minlength=npieces); cPB = np.bincount(gpB, minlength=npieces)
        oA2 = np.concatenate([[0], np.cumsum(cPA)[:-1]]); oB2 = np.concatenate([[0], np.cumsum(cPB)[:-1]])
        aI = oA2[Pm] + np.minimum(relA, np.maximum(cPA[Pm] - 1, 0))
        bI = oB2[Pm] + np.minimum(relB, np.maximum(cPB[Pm] - 1, 0))
        keep = seglen > tol
        aI = aI[keep]; bI = bI[keep]; sl = seglen[keep]; nseg += int(keep.sum())
        total += float(np.sum(sl * gcost(ctr(gcA[aI]) - ctr(gcB[bI]))))
        if t == T - 1:
            break
        szA = (geA - gsA)[aI]; szB = (geB - gsB)[bI]
        srcA = gsA[aI].repeat(szA) + _ranges(szA)
        mA2 = mA[srcA] * (sl / np.maximum(gmA[aI], 1e-300)).repeat(szA)
        pA2 = np.repeat(np.arange(len(aI)), szA); iA2 = iA[srcA]
        srcB = gsB[bI].repeat(szB) + _ranges(szB)
        mB2 = mB[srcB] * (sl / np.maximum(gmB[bI], 1e-300)).repeat(szB)
        pB2 = np.repeat(np.arange(len(bI)), szB); iB2 = iB[srcB]
        kA = mA2 > tol; kB = mB2 > tol
        pA, iA, mA = pA2[kA], iA2[kA], mA2[kA]
        pB, iB, mB = pB2[kB], iB2[kB], mB2[kB]
    return total, nseg


def atsw_codes(C1, C2, reps, w1, w2, gcost=lambda dx: dx ** 2, tol=1e-14):
    """Ô cho trước bằng MÃ nguyên (C1, C2: [n, T]) và giá trị đại diện reps[t][k].
    Cho phép ô thích nghi theo dữ liệu (phân vị + trung bình ô) thay vì lưới cố định."""
    T = C1.shape[1]
    C1 = np.asarray(C1, np.int64); C2 = np.asarray(C2, np.int64)
    pA = np.zeros(len(w1), np.int64); iA = np.arange(len(w1)); mA = (w1 / w1.sum()).astype(float)
    pB = np.zeros(len(w2), np.int64); iB = np.arange(len(w2)); mB = (w2 / w2.sum()).astype(float)
    total = 0.0; nseg = 0
    for t in range(T):
        ctr = lambda k: reps[t][k]
        cA = C1[iA, t]; cB = C2[iB, t]
        oA = np.lexsort((cA, pA)); pA, iA, mA, cA = pA[oA], iA[oA], mA[oA], cA[oA]
        oB = np.lexsort((cB, pB)); pB, iB, mB, cB = pB[oB], iB[oB], mB[oB], cB[oB]
        newgA = np.empty(len(pA), bool); newgA[0] = True
        newgA[1:] = (pA[1:] != pA[:-1]) | (cA[1:] != cA[:-1])
        gidA = np.cumsum(newgA) - 1; ngA = gidA[-1] + 1
        gmA = np.bincount(gidA, weights=mA, minlength=ngA)
        gsA = np.flatnonzero(newgA); geA = np.append(gsA[1:], len(pA)); gpA = pA[gsA]; gcA = cA[gsA]
        newgB = np.empty(len(pB), bool); newgB[0] = True
        newgB[1:] = (pB[1:] != pB[:-1]) | (cB[1:] != cB[:-1])
        gidB = np.cumsum(newgB) - 1; ngB = gidB[-1] + 1
        gmB = np.bincount(gidB, weights=mB, minlength=ngB)
        gsB = np.flatnonzero(newgB); geB = np.append(gsB[1:], len(pB)); gpB = pB[gsB]; gcB = cB[gsB]
        npieces = int(max(gpA.max(), gpB.max())) + 1
        pmA = np.bincount(gpA, weights=gmA, minlength=npieces)
        pmB = np.bincount(gpB, weights=gmB, minlength=npieces)
        gmB = gmB * np.where(pmB > 0, pmA / np.maximum(pmB, 1e-300), 1.0)[gpB]
        cumA = np.cumsum(gmA); cumB = np.cumsum(gmB)
        startA = np.flatnonzero(np.concatenate([[True], gpA[1:] != gpA[:-1]]))
        baseA = np.zeros(ngA); baseA[startA[1:]] = cumA[startA[1:] - 1]
        baseA = np.maximum.accumulate(baseA); endA = cumA - baseA
        startB = np.flatnonzero(np.concatenate([[True], gpB[1:] != gpB[:-1]]))
        baseB = np.zeros(ngB); baseB[startB[1:]] = cumB[startB[1:] - 1]
        baseB = np.maximum.accumulate(baseB); endB = cumB - baseB
        Pm = np.concatenate([gpA, gpB]); Vm = np.concatenate([endA, endB])
        Sm = np.concatenate([np.zeros(ngA, np.int8), np.ones(ngB, np.int8)])
        om = np.lexsort((Sm, Vm, Pm)); Pm, Vm, Sm = Pm[om], Vm[om], Sm[om]
        firstm = np.concatenate([[True], Pm[1:] != Pm[:-1]])
        prevV = np.concatenate([[0.], Vm[:-1]]); prevV[firstm] = 0.
        seglen = Vm - prevV
        cntA = np.cumsum(Sm == 0) - (Sm == 0); cntB = np.cumsum(Sm == 1) - (Sm == 1)
        pf = np.flatnonzero(firstm)
        bA = np.zeros(len(Pm), np.int64); bA[pf] = cntA[pf]; bA = np.maximum.accumulate(bA)
        bB = np.zeros(len(Pm), np.int64); bB[pf] = cntB[pf]; bB = np.maximum.accumulate(bB)
        relA = cntA - bA; relB = cntB - bB
        cPA = np.bincount(gpA, minlength=npieces); cPB = np.bincount(gpB, minlength=npieces)
        oA2 = np.concatenate([[0], np.cumsum(cPA)[:-1]]); oB2 = np.concatenate([[0], np.cumsum(cPB)[:-1]])
        aI = oA2[Pm] + np.minimum(relA, np.maximum(cPA[Pm] - 1, 0))
        bI = oB2[Pm] + np.minimum(relB, np.maximum(cPB[Pm] - 1, 0))
        keep = seglen > tol
        aI = aI[keep]; bI = bI[keep]; sl = seglen[keep]; nseg += int(keep.sum())
        total += float(np.sum(sl * gcost(ctr(gcA[aI]) - ctr(gcB[bI]))))
        if t == T - 1:
            break
        szA = (geA - gsA)[aI]; szB = (geB - gsB)[bI]
        srcA = gsA[aI].repeat(szA) + _ranges(szA)
        mA2 = mA[srcA] * (sl / np.maximum(gmA[aI], 1e-300)).repeat(szA)
        pA2 = np.repeat(np.arange(len(aI)), szA); iA2 = iA[srcA]
        srcB = gsB[bI].repeat(szB) + _ranges(szB)
        mB2 = mB[srcB] * (sl / np.maximum(gmB[bI], 1e-300)).repeat(szB)
        pB2 = np.repeat(np.arange(len(bI)), szB); iB2 = iB[srcB]
        kA = mA2 > tol; kB = mB2 > tol
        pA, iA, mA = pA2[kA], iA2[kA], mA2[kA]
        pB, iB, mB = pB2[kB], iB2[kB], mB2[kB]
    return total, nseg
