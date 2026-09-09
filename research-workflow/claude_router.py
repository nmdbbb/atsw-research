"""Định tuyến task sang thang model của phiên Claude: cộng một bậc trên mức nền.

Bản chuyển từ `model_router.py` (hệ OpenAI: Luna/Terra/Sol/Astra, reasoning_effort, fork_turns).
Đây là CHÍNH SÁCH ĐIỀU PHỐI cục bộ trên các model id mà phiên này thực sự phơi ra, không phải
tuyên bố về một thứ tự năng lực đã đo. Nó chỉ sinh tham số; không tự khởi động agent, không đọc
credential, không gọi API, không đổi model của root.

KHÁC BIỆT CƠ CHẾ so với bản OpenAI — ghi rõ để không phát ra field mà công cụ bỏ qua:
* Không có `reasoning_effort`. Nền tảng này không có núm effort. Mức effort dự kiến được giữ lại
  dưới tên `intended_effort` như GHI CHÚ cho người đọc, và KHÔNG nằm trong kwargs gửi đi.
* Không có `fork_turns`. Sub-agent ở đây có context mới hoàn toàn theo thiết kế: nó chỉ thấy
  `task` + `context_summary`, không thừa hưởng transcript. Nên tương đương của `fork_turns="none"`
  là BẮT BUỘC `context_summary` khác rỗng — thiếu nó thì đứa con không biết bối cảnh gì.
* Đường dẫn tương đối không tới được sub-agent (nó chạy ở thư mục làm việc riêng). File dùng chung
  phải đưa bằng đường dẫn TUYỆT ĐỐI trong host grant, hoặc bằng marker artifact.

THANG NĂNG LỰC: ba bậc. Không đưa `claude-fable-5*` vào thang — trong phiên này chúng được dùng để
SINH biến thể code, và không có phép đo nào đặt chúng trên hay dưới opus cho việc suy luận. Xếp
chúng thành một lane riêng (`GENERATION_LANE`) thay vì bịa ra một bậc.
"""
from __future__ import annotations

import argparse
import json

LADDER = ("claude-haiku-4-5-20251001", "claude-sonnet-5", "claude-opus-5")
GENERATION_LANE = ("claude-fable-5", "claude-fable-5-1")

TASKS = {
    "mechanical":       (LADDER[0], "thấp"),
    "implementation":   (LADDER[1], "cao"),
    "literature":       (LADDER[1], "cao"),
    "benchmark_design": (LADDER[1], "cao"),
    "theorem":          (LADDER[1], "rất cao"),
    "certificate":      (LADDER[1], "rất cao"),
    "skeptic":          (LADDER[1], "rất cao"),
    "scientific_audit": (LADDER[2], "rất cao"),
    "variant_synthesis": (GENERATION_LANE[0], "n/a"),
}


class RoutingUnavailable(RuntimeError):
    pass


def route(task_kind, available_models=None):
    if task_kind not in TASKS:
        raise ValueError(f"Unknown task kind: {task_kind}")
    baseline, effort = TASKS[task_kind]
    if task_kind == "variant_synthesis":            # lane riêng: không cộng bậc
        available = set(GENERATION_LANE if available_models is None else available_models)
        selected = next((m for m in GENERATION_LANE if m in available), None)
        if selected is None:
            raise RoutingUnavailable("Không có model nào của lane sinh biến thể; không thay bằng model thang chính")
        return {"task_kind": task_kind, "baseline": baseline, "requested_tier": baseline,
                "model": selected, "intended_effort": effort, "lane": "generation",
                "capped_at_highest_tier": False,
                "availability_verified": available_models is not None}
    index = min(LADDER.index(baseline) + 1, len(LADDER) - 1)
    available = set(LADDER if available_models is None else available_models)
    selected = next((m for m in LADDER[index:] if m in available), None)
    if selected is None:
        raise RoutingUnavailable(
            f"Không có model nào ở bậc {LADDER[index]} hoặc cao hơn; KHÔNG hạ bậc âm thầm")
    return {"task_kind": task_kind, "baseline": baseline, "requested_tier": LADDER[index],
            "model": selected, "intended_effort": effort, "lane": "capability",
            "capped_at_highest_tier": baseline == LADDER[-1],
            "availability_verified": available_models is not None}


def spawn_arguments(task_kind, task_name, task_text, context_summary, available_models=None,
                    output_schema=None):
    """Trả kwargs cho công cụ delegation của phiên. `intended_effort` KHÔNG được gửi đi."""
    choice = route(task_kind, available_models)
    for name, value in (("task_name", task_name), ("task_text", task_text),
                        ("context_summary", context_summary)):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} phải là chuỗi khác rỗng "
                             "(context_summary là bắt buộc: sub-agent không thừa hưởng transcript)")
    kwargs = {"name": task_name, "task": task_text, "context_summary": context_summary,
              "model": choice["model"]}
    if output_schema is not None:
        if not isinstance(output_schema, dict):
            raise ValueError("output_schema phải là dict JSON Schema")
        kwargs["output_schema"] = output_schema
    return kwargs


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Định tuyến task sang thang model của phiên Claude")
    p.add_argument("task_kind", choices=sorted(TASKS))
    p.add_argument("--available", nargs="*", default=None,
                   help="danh sách model thật của phiên (từ host.list_models())")
    a = p.parse_args()
    try:
        print(json.dumps(route(a.task_kind, a.available), indent=2, ensure_ascii=False))
    except RoutingUnavailable as exc:
        p.exit(2, str(exc) + "\n")
