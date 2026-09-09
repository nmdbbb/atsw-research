"""Kiem MOI tham chieu sha256 tro toi tep trong repo, va bao ket thuc dong co phai nguyen nhan.

digest() cua workflow.py bam BYTE THO, nen moi tep bi ghim hash phai byte-exact tren
moi nen tang. Script nay tim tat ca cac cap (truong *sha256, tep duoc tro toi) trong
ledger/events.jsonl, ledger/preregistered/*.json, runs/**/*.json, roi bao:
  KHOP        - byte tren dia dung bang hash da ghi
  CAN_CRLF    - lech, nhung khop lai sau LF->CRLF  => nguyen nhan la ket thuc dong
  CAN_LF      - lech, nhung khop lai sau CRLF->LF
  LECH        - lech that su, khong phai ket thuc dong
  KHONG_THAY  - khong tim duoc tep tuong ung
"""
import hashlib, json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CRLF, LF = b"\r\n", b"\n"
# ten truong -> cach suy ra duong dan tep
PATH_KEYS = {
    "objective_sha256": lambda p, e: "objective.json",
    "design_sha256": lambda p, e: "frozen_design.json",
    "design_amendment_sha256": lambda p, e: "frozen_design_amendment_1.json",
    "generators_sha256": lambda p, e: "generators.py",
    "record_sha256": lambda p, e: "ledger/preregistered/%s.json" % e.get("id", ""),
    "registered_record_sha256": lambda p, e: "ledger/preregistered/%s.json" % e.get("hypothesis", ""),
    "source_sha256": lambda p, e: e.get("source"),
    "evidence_sha256": lambda p, e: e.get("evidence"),
    "result_sha256": lambda p, e: e.get("result_path"),
    "probe_sha256": lambda p, e: e.get("probe"),
    "code_sha256": lambda p, e: e.get("code") or e.get("code_path"),
    "sha256": lambda p, e: e.get("file") or e.get("path") or e.get("source"),
}


def classify(path, want):
    # Ledger co ban ghi duoc tao tren Windows nen chua duong dan dau \ (vi du
    # 'runs\\cycle_1\\H_A01_future_classes.json'). Chuan hoa khi PHAN GIAI duong dan;
    # khong sua ban ghi, vi sua la ghi lai chuoi hash.
    p = ROOT / str(path).replace("\\", "/")
    if not p.is_file():
        return "KHONG_THAY", 0
    b = p.read_bytes()
    if hashlib.sha256(b).hexdigest() == want:
        return "KHOP", len(b)
    if hashlib.sha256(b.replace(LF, CRLF)).hexdigest() == want:
        return "CAN_CRLF", len(b)
    if hashlib.sha256(b.replace(CRLF, LF)).hexdigest() == want:
        return "CAN_LF", len(b)
    return "LECH", len(b)


def pins():
    seen = set()
    srcs = [ROOT / "ledger/events.jsonl"]
    srcs += sorted((ROOT / "ledger/preregistered").glob("*.json"))
    srcs += sorted(ROOT.glob("runs/**/*.json"))
    for src in srcs:
        if not src.is_file():
            continue
        if src.suffix == ".jsonl":
            objs = [json.loads(l) for l in src.read_text(encoding="utf-8").splitlines()]
        else:
            try:
                objs = [json.loads(src.read_text(encoding="utf-8"))]
            except json.JSONDecodeError:
                continue
        stack = list(objs)
        while stack:
            o = stack.pop()
            if isinstance(o, list):
                stack.extend(o); continue
            if not isinstance(o, dict):
                continue
            stack.extend(v for v in o.values() if isinstance(v, (dict, list)))
            for key, resolve in PATH_KEYS.items():
                val = o.get(key)
                if not isinstance(val, str) or not re.fullmatch(r"[0-9a-f]{64}", val):
                    continue
                target = resolve(src, o)
                if not target:
                    continue
                item = (str(target), val, str(src.relative_to(ROOT)), key)
                if item[:2] not in seen:
                    seen.add(item[:2]); yield item


def superseded_objective_pins():
    """Hash objective da bi thay the boi mot ban revision -> pin cu la LICH SU, dung."""
    out = set()
    for rec in sorted((ROOT / "ledger").glob("contract_revision_*.json")):
        d = json.loads(rec.read_text(encoding="utf-8"))
        for k in ("previous_objective_sha256", "old_objective_sha256", "superseded_sha256"):
            if isinstance(d.get(k), str):
                out.add(d[k])
    events = ROOT / "ledger/events.jsonl"
    if events.is_file() and (ROOT / "ledger/contract.json").is_file():
        cur = json.loads((ROOT / "ledger/contract.json").read_text(encoding="utf-8"))["objective_sha256"]
        lines = events.read_text(encoding="utf-8").splitlines()
        frozen = [json.loads(l)["payload"].get("objective_sha256") for l in lines
                  if json.loads(l)["kind"] == "contract_frozen"]
        if len(frozen) >= 1 and out or cur not in frozen:
            out |= {h for h in frozen if h and h != cur}
    return out


def report():
    rows = sorted(pins())
    historical = superseded_objective_pins()
    counts, bad = {}, []
    for target, want, src, key in rows:
        verdict, size = classify(target, want)
        if verdict != "KHOP" and key == "objective_sha256" and want in historical:
            verdict = "LICH_SU"
        counts[verdict] = counts.get(verdict, 0) + 1
        if verdict not in ("KHOP", "LICH_SU"):
            bad.append((verdict, target, size, src))
    return rows, counts, bad


if __name__ == "__main__":
    rows, counts, bad = report()
    for verdict, target, size, src in bad:
        print("  %-11s %-52s %6dB  (ghim trong %s)" % (verdict, target, size, src))
    print("tong ghim:", len(rows), "|", ", ".join("%s=%d" % kv for kv in sorted(counts.items())))
    sys.exit(1 if bad else 0)
