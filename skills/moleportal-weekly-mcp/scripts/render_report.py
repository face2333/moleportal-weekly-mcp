#!/usr/bin/env python3
"""把 CLI 输出的结构化周报数据 + 模型产出的复盘分析，渲染成 HTML 看板。

数据来源：cli-anything-moleportal openapi weekly full-report --data-only
复盘分析：由 Agent（模型）按 SKILL.md 的约定生成，结构见 EMPTY_ANALYSIS

用法：
  python3 render_report.py \
      --data /tmp/weekly_data.json \
      --analysis /tmp/analysis.json \
      --output ~/Desktop/运营周报_2026-09-06.html

仅依赖标准库，模板随本 skill 分发，不依赖服务器端文件。
"""

from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path

DEFAULT_TEMPLATE = Path(__file__).resolve().parent.parent / "templates" / "weekly_report_template.html"

# 复盘分析区块的空结构：模型未产出时用它兜底，页面显示"暂无"
EMPTY_ANALYSIS = {
    "highlights": [],
    "risks": [],
    "activityRows": [],
    "groupRows": [],
    "wxmpRows": [],
    "globalItems": [],
    "plans": [],
}


def _gt(this: float, last: float) -> str:
    if last == 0:
        return "新增" if this > 0 else "持平"
    diff = this - last
    pct = abs(diff / last * 100)
    return f"{'↑' if diff > 0 else ('↓' if diff < 0 else '—')} {abs(diff):.0f} ({pct:.0f}%)"


def _fmt_date(yyyymmdd: str) -> str:
    try:
        return datetime.datetime.strptime(str(yyyymmdd), "%Y%m%d").strftime("%Y-%m-%d")
    except Exception:
        return str(yyyymmdd)


def render(data: dict, analysis: dict, template_path: Path, output_path: Path) -> None:
    p1 = data.get("p1") or {}
    p2 = data.get("p2") or {}
    p3 = data.get("p3") or {}

    this_week = data.get("thisWeek") or ""
    last_week = data.get("lastWeek") or ""
    this_start = this_week.split("~")[0].strip() if this_week else ""
    this_end = this_week.split("~")[-1].strip() if this_week else ""

    t_rec = (p1.get("thisWeek") or {}).get("totalRecords", 0)
    l_rec = (p1.get("lastWeek") or {}).get("totalRecords") or 0
    t_msg = (p2.get("thisWeek") or {}).get("totalMessages", 0)
    l_msg = (p2.get("lastWeek") or {}).get("totalMessages") or 0
    t_spk = (p2.get("thisWeek") or {}).get("speakerCount", 0)
    l_spk = (p2.get("lastWeek") or {}).get("speakerCount") or 0
    cur_total = (p3.get("summary") or {}).get("visitTotal", 0)
    cur_sess = (p3.get("trend") or {}).get("sessionCnt", 0)

    try:
        next_week = (f"{(datetime.date.fromisoformat(this_start) + datetime.timedelta(days=7)):%Y-%m-%d} 至 "
                     f"{(datetime.date.fromisoformat(this_end) + datetime.timedelta(days=7)):%Y-%m-%d}")
    except Exception:
        next_week = "—"

    replacements = {
        "{{REPORT_DATE}}": this_end or datetime.date.today().isoformat(),
        "{{THIS_WEEK}}": this_week.replace("~", "至") if this_week else "—",
        "{{LAST_WEEK}}": last_week.replace("~", "至") if last_week else "—",
        "{{GENERATED_AT}}": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "{{PART1_DATA}}": json.dumps(p1, ensure_ascii=False),
        "{{PART2_DATA}}": json.dumps(p2, ensure_ascii=False),
        "{{PART3_DATA}}": json.dumps(p3, ensure_ascii=False),
        "{{ANALYSIS_DATA}}": json.dumps(analysis, ensure_ascii=False),
        "{{m-participants}}": str(t_rec),
        "{{m-participants-last}}": str(l_rec),
        "{{m-participants-delta}}": _gt(t_rec, l_rec),
        "{{m-campaigns}}": str(p1.get("thisCampaigns", len((p1.get("thisWeek") or {}).get("activities", [])))),
        "{{m-campaigns-last}}": str(p1.get("lastCampaigns", len((p1.get("lastWeek") or {}).get("activities", [])))),
        "{{m-campaigns-delta}}": "新增" if l_rec == 0 and t_rec > 0 else _gt(t_rec, l_rec),
        "{{m-messages}}": str(t_msg),
        "{{m-messages-last}}": str(l_msg),
        "{{m-messages-delta}}": _gt(t_msg, l_msg),
        "{{m-speakers}}": str(t_spk),
        "{{m-speakers-last}}": str(l_spk),
        "{{m-speakers-delta}}": _gt(t_spk, l_spk),
        "{{m-total-users}}": str(cur_total),
        "{{m-sessions}}": str(cur_sess),
        "{{NEXT_WEEK}}": next_week,
        "{{WXMP_DATE}}": _fmt_date(p3.get("targetDate", "")),
    }

    if not template_path.is_file():
        raise SystemExit(f"模板不存在: {template_path}")

    tmpl = template_path.read_text(encoding="utf-8")
    for key, val in replacements.items():
        tmpl = tmpl.replace(key, str(val))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(tmpl, encoding="utf-8")
    print(f"✅ 看板已生成: {output_path}")


def main() -> None:
    ap = argparse.ArgumentParser(description="渲染运营周报 HTML 看板（skill 侧）")
    ap.add_argument("--data", required=True, help="full-report --data-only 输出的 JSON 文件")
    ap.add_argument("--analysis", default=None, help="模型产出的复盘分析 JSON（可选，缺省则用空结构）")
    ap.add_argument("--output", required=True, help="输出 HTML 路径")
    ap.add_argument("--template", default=str(DEFAULT_TEMPLATE), help="HTML 模板路径")
    args = ap.parse_args()

    data = json.loads(Path(args.data).read_text(encoding="utf-8"))
    if args.analysis:
        analysis = json.loads(Path(args.analysis).read_text(encoding="utf-8"))
    else:
        analysis = dict(EMPTY_ANALYSIS)
        print("⚠️ 未传 --analysis，复盘分析区块将为空", file=sys.stderr)

    render(data, analysis, Path(args.template), Path(args.output).expanduser())


if __name__ == "__main__":
    main()
