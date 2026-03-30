"""
Workshop 解答：多模型工安系統 Client

用 A2A 協定串起 3 個 FastAPI Agent。

執行方式：
  1. 開 3 個 terminal，分別啟動：
     uvicorn detection_server:app --port 8000
     uvicorn regulation_server:app --port 8001
     uvicorn report_server:app --port 8002

  2. 執行 client：
     python client.py
"""

import requests
import uuid


def create_task(action, input_data):
    return {
        "task_id": f"t-{uuid.uuid4().hex[:8]}",
        "action": action,
        "input": input_data,
    }


def main():
    print("=" * 60)
    print("  多模型工安系統 — A2A 協作（FastAPI 版）")
    print("=" * 60)

    # 1. 發現 Agent
    print(f"\n{'─' * 60}")
    print(f"  發現 Agent")
    print(f"{'─' * 60}")

    agents = {
        "detection": "http://localhost:8000",
        "regulation": "http://localhost:8001",
        "report": "http://localhost:8002",
    }

    for name, url in agents.items():
        try:
            card = requests.get(f"{url}/.well-known/agent.json").json()
            print(f"  {card['name']}")
            print(f"    URL: {card['url']}")
            print(f"    模型: {card['model']}")
            print(f"    能力: {card['capabilities']}")
        except Exception as e:
            print(f"  ❌ {name} ({url}) 無法連線：{e}")
            print(f"\n  請先啟動 3 個 server（見 docstring）")
            return

    # 2. 偵測（Gemini）
    print(f"\n{'─' * 60}")
    print(f"  Step 1: 偵測 Agent (Gemini)")
    print(f"{'─' * 60}")

    detection = requests.post(
        "http://localhost:8000/detect",
        json={"description": "A區工人沒戴安全帽"},
    ).json()
    print(f"  違規: {detection['violations']}")

    # 3. 查法規（Qwen）
    print(f"\n{'─' * 60}")
    print(f"  Step 2: 法規 Agent (Qwen)")
    print(f"{'─' * 60}")

    violation = detection["violations"][0]
    task = create_task("regulation_search", {"violation_type": violation["type"]})
    regulation = requests.post("http://localhost:8001/task", json=task).json()
    print(f"  法規: {regulation['output']['regulation'][:50]}...")
    print(f"  罰則: {regulation['output']['penalty']}")

    # 4. 報告（Claude）
    print(f"\n{'─' * 60}")
    print(f"  Step 3: 報告 Agent (Claude)")
    print(f"{'─' * 60}")

    task = create_task("generate_report", {
        "violation": violation,
        "regulation": regulation["output"],
    })
    report = requests.post("http://localhost:8002/task", json=task).json()
    print(f"\n{report['output']['report']}")

    # 5. 總結
    print(f"\n{'=' * 60}")
    print(f"  完成：3 個 FastAPI Agent 透過 A2A 協作")
    print(f"{'=' * 60}")

    print(f"\n  Agent 分工：")
    print(f"  {'任務':>8} {'模型':>15} {'Port':>8}")
    print(f"  {'─' * 35}")
    print(f"  {'偵測':>8} {'Gemini':>15} {'8000':>8}")
    print(f"  {'法規':>8} {'Qwen':>15} {'8001':>8}")
    print(f"  {'報告':>8} {'Claude':>15} {'8002':>8}")


if __name__ == "__main__":
    main()
