"""
Workshop 解答：多模型工安系統

用 A2A 協定串起 3 個 Agent（模擬不同模型），
建立完整的偵測 → 法規 → 報告流程。

執行方式：
  python 16_multi_model_system.py

不需要 API Key（全部用模擬）
"""

import json
import uuid
from datetime import datetime


# === A2A 基礎 ===

class AgentCard:
    def __init__(self, name, description, url, capabilities, model):
        self.name = name
        self.description = description
        self.url = url
        self.capabilities = capabilities
        self.model = model

    def to_dict(self):
        return {
            "name": self.name,
            "url": self.url,
            "capabilities": self.capabilities,
            "model": self.model,
        }


class Task:
    def __init__(self, action, input_data):
        self.task_id = f"t-{uuid.uuid4().hex[:8]}"
        self.action = action
        self.input = input_data
        self.status = "pending"
        self.output = None
        self.duration_ms = 0

    def complete(self, output, duration_ms=0):
        self.status = "completed"
        self.output = output
        self.duration_ms = duration_ms


# === 偵測 Agent（模擬 Gemini：多模態看圖） ===

class DetectionAgent:
    card = AgentCard(
        name="偵測 Agent",
        description="分析工地照片，用 Structured Output 輸出違規 JSON",
        url="http://localhost:8000",
        capabilities=["detect_violations"],
        model="Gemini（多模態、免費額度高）",
    )

    REGULATIONS_KEYWORDS = {
        "安全帽": {"type": "no_helmet", "severity": "high"},
        "反光背心": {"type": "no_vest", "severity": "medium"},
        "護目鏡": {"type": "no_goggles", "severity": "medium"},
    }

    def handle_task(self, task):
        description = task.input.get("description", "")
        violations = []
        for keyword, violation in self.REGULATIONS_KEYWORDS.items():
            if keyword in description or violation["type"].replace("no_", "沒") in description:
                violations.append(violation)

        if not violations:
            violations = [{"type": "no_helmet", "severity": "high"}]

        task.complete({
            "violations": violations,
            "person_count": 3,
            "model_used": "gemini-2.5-flash",
        })
        return task


# === 法規 Agent（模擬 Qwen：中文 RAG） ===

class RegulationAgent:
    card = AgentCard(
        name="法規查詢 Agent",
        description="用 RAG 搜尋台灣工安法規",
        url="http://localhost:8001",
        capabilities=["regulation_search"],
        model="Qwen（中文理解好、成本低）",
    )

    REGULATIONS = {
        "no_helmet": {
            "regulation": "職業安全衛生設施規則第 281 條：雇主對於在高度 2 公尺以上之工作場所，應使勞工確實使用安全帽。安全帽應符合 CNS 國家標準。",
            "source": "安全帽規定",
            "penalty": "罰鍰 3~30 萬元",
        },
        "no_vest": {
            "regulation": "職業安全衛生設施規則第 21 條：雇主應提供適當之反光標示或背心。",
            "source": "反光背心規定",
            "penalty": "罰鍰 3~15 萬元",
        },
        "no_goggles": {
            "regulation": "職業安全衛生設施規則第 287 條：從事焊接作業應配戴護目鏡。",
            "source": "護目鏡規定",
            "penalty": "罰鍰 3~15 萬元",
        },
    }

    def handle_task(self, task):
        vtype = task.input.get("violation_type", "unknown")
        reg = self.REGULATIONS.get(vtype, {
            "regulation": f"找不到 {vtype} 的相關法規",
            "source": "N/A",
            "penalty": "N/A",
        })
        reg["model_used"] = "qwen-2.5"
        task.complete(reg)
        return task


# === 報告 Agent（模擬 Claude：文筆好） ===

class ReportAgent:
    card = AgentCard(
        name="報告 Agent",
        description="根據違規和法規生成專業告警報告",
        url="http://localhost:8002",
        capabilities=["generate_report"],
        model="Claude（文筆好、精準）",
    )

    def handle_task(self, task):
        violation = task.input.get("violation", {})
        regulation = task.input.get("regulation", {})
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

        task.complete({
            "report": report,
            "severity": severity,
            "model_used": "claude-sonnet",
        })
        return task


# === 通知 Agent（模擬 GPT-4o-mini：便宜快速） ===

class NotificationAgent:
    card = AgentCard(
        name="通知 Agent",
        description="判斷是否發送通知，生成摘要",
        url="http://localhost:8003",
        capabilities=["evaluate_notification", "send_summary"],
        model="GPT-4o-mini（便宜、量大）",
    )

    def handle_task(self, task):
        severity = task.input.get("severity", "medium")
        report = task.input.get("report", "")

        should_notify = severity in ["high", "critical"]
        summary = report.split("\n")[0] if report else "無摘要"

        task.complete({
            "should_notify": should_notify,
            "summary": summary,
            "channels": ["LINE", "Email"] if should_notify else [],
            "model_used": "gpt-4o-mini",
        })
        return task


# === 主程式：完整流程 ===

def main():
    print("=" * 60)
    print("  多模型工安系統 — A2A 協作")
    print("=" * 60)

    # 建立 Agent
    detection = DetectionAgent()
    regulation = RegulationAgent()
    report = ReportAgent()
    notification = NotificationAgent()

    agents = [detection, regulation, report, notification]

    # 1. 發現 Agent
    print(f"\n{'─' * 60}")
    print(f"  發現 Agent")
    print(f"{'─' * 60}")

    for agent in agents:
        card = agent.card.to_dict()
        print(f"  {card['name']}")
        print(f"    URL: {card['url']}")
        print(f"    模型: {card['model']}")
        print(f"    能力: {card['capabilities']}")

    # 2. 偵測（Gemini）
    print(f"\n{'─' * 60}")
    print(f"  Step 1: 偵測 Agent (Gemini)")
    print(f"{'─' * 60}")

    task1 = Task("detect_violations", {"description": "A區工人沒戴安全帽"})
    detection.handle_task(task1)
    print(f"  {task1.task_id}: {json.dumps(task1.output, ensure_ascii=False)}")

    # 3. 查法規（Qwen）
    print(f"\n{'─' * 60}")
    print(f"  Step 2: 法規 Agent (Qwen)")
    print(f"{'─' * 60}")

    for violation in task1.output["violations"]:
        task2 = Task("regulation_search", {"violation_type": violation["type"]})
        regulation.handle_task(task2)
        print(f"  {task2.task_id}: {task2.output['regulation'][:50]}...")
        print(f"    罰則: {task2.output['penalty']}")

    # 4. 生成報告（Claude）
    print(f"\n{'─' * 60}")
    print(f"  Step 3: 報告 Agent (Claude)")
    print(f"{'─' * 60}")

    task3 = Task("generate_report", {
        "violation": task1.output["violations"][0],
        "regulation": task2.output,
    })
    report.handle_task(task3)
    print(f"\n{task3.output['report']}")

    # 5. 通知判斷（GPT-4o-mini）
    print(f"\n{'─' * 60}")
    print(f"  Step 4: 通知 Agent (GPT-4o-mini)")
    print(f"{'─' * 60}")

    task4 = Task("evaluate_notification", {
        "severity": task3.output["severity"],
        "report": task3.output["report"],
    })
    notification.handle_task(task4)
    print(f"  是否通知: {task4.output['should_notify']}")
    print(f"  通知管道: {task4.output['channels']}")
    print(f"  摘要: {task4.output['summary']}")

    # 6. 成本分析
    print(f"\n{'=' * 60}")
    print(f"  系統總結")
    print(f"{'=' * 60}")

    print(f"\n  Agent 分工：")
    models = {
        "偵測": ("Gemini", "多模態看圖", "免費/低"),
        "法規": ("Qwen", "中文 RAG", "低"),
        "報告": ("Claude", "專業文筆", "中"),
        "通知": ("GPT-4o-mini", "快速判斷", "極低"),
    }

    print(f"  {'任務':>8} {'模型':>15} {'用途':>15} {'成本':>8}")
    print(f"  {'─' * 50}")
    for task_name, (model, usage, cost) in models.items():
        print(f"  {task_name:>8} {model:>15} {usage:>15} {cost:>8}")

    print(f"\n  每個 Agent 選最適合的模型 = 品質最好 + 成本最低")


if __name__ == "__main__":
    main()
