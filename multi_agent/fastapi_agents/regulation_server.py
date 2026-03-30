"""
法規 Agent（模擬 Qwen）

啟動：uvicorn regulation_server:app --port 8001
"""

from fastapi import FastAPI

app = FastAPI()

REGULATIONS = {
    "no_helmet": {
        "regulation": "職業安全衛生設施規則第 281 條：雇主對於在高度 2 公尺以上之工作場所，應使勞工確實使用安全帽。",
        "source": "安全帽規定",
        "penalty": "罰鍰 3~30 萬元",
    },
    "no_safety_belt": {
        "regulation": "職業安全衛生設施規則第 225 條：高空作業應使用安全帶。",
        "source": "安全帶規定",
        "penalty": "罰鍰 3~30 萬元",
    },
}

@app.get("/.well-known/agent.json")
async def agent_card():
    return {
        "name": "法規查詢 Agent (Qwen)",
        "description": "用 RAG 搜尋台灣工安法規",
        "url": "http://localhost:8001",
        "capabilities": ["regulation_search"],
        "model": "qwen-2.5",
    }

@app.post("/task")
async def handle_task(task: dict):
    violation_type = task["input"]["violation_type"]
    reg = REGULATIONS.get(violation_type, {
        "regulation": f"查無 {violation_type} 相關法規",
        "source": "N/A",
        "penalty": "N/A",
    })
    reg["model_used"] = "qwen-2.5"
    return {
        "task_id": task.get("task_id", ""),
        "status": "completed",
        "output": reg,
    }
