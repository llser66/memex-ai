"""
Tool 节点（工具执行者）
----------------------
根据用户问题，判断并调用相应的工具函数。
目前只集成了“生成周报”工具，未来可扩展更多工具（邮件、日历等）。
"""

from pathlib import Path

from app.tools.report_tool import generate_weekly_report

def tool_node(state: dict) -> dict:
    question = state.get("question", "")

    # 如果问题包含周报相关词，调用周报生成工具
    if "周报" in question or "周总结" in question or "本周工作" in question:
        report_path = generate_weekly_report()
        report_file = Path(report_path).name
        result_msg = f"✅ 周报已生成：{report_file}"
    else:
        report_file = None
        result_msg = "暂不支持的工具类型，请换一种说法。"

    return {
        "tool_results": [result_msg],
        "report_file": report_file,
        "next_node": "generate"
    }
