"""
報告 Agent（模擬 Gemini）

啟動：uvicorn report_server:app --port 8002
"""

from fastapi import FastAPI
from datetime import datetime

app = FastAPI()

@app.get("/.well-known/agent.json")
async def agent_card():
    return {
        "name": "報告 Agent (Gemini)",
        "description": "根據違規和法規生成專業告警報告",
        "url": "http://localhost:8002",
        "capabilities": ["generate_report"],
        "model": "gemini-2.5-flash",
    }

@app.post("/task")
async def handle_task(task: dict):
    violation = task["input"].get("violation", {})
    regulation = task["input"].get("regulation", {})
    severity = violation.get("severity", "medium")

    severity_label = {"high": "緊急", "medium": "注意", "low": "提醒"}.get(severity, "注意")

    report = f"""【{severity_label}告警】工安違規通報
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
時間：{datetime.now().strftime("%Y-%m-%d %H:%M")}
違規類型：{violation.get("type", "unknown")}
嚴重程度：{severity}

法規依據：
  {regulation.get("regulation", "N/A")}

罰則：{regulation.get("penalty", "N/A")}

建議措施：
  1. 立即要求現場人員改善
  2. 通知現場主管進行確認
  3. 記錄違規事件供後續追蹤
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

    return {
        "task_id": task.get("task_id", ""),
        "status": "completed",
        "output": {"report": report, "severity": severity, "model_used": "gemini-2.5-flash"},
    }
