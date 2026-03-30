"""
偵測 Agent（模擬 Gemini）

啟動：uvicorn detection_server:app --port 8000
"""

from fastapi import FastAPI

app = FastAPI()

LABEL = "偵測 Agent (Gemini)"

@app.get("/.well-known/agent.json")
async def agent_card():
    return {
        "name": LABEL,
        "description": "分析工地狀況，找出違規",
        "url": "http://localhost:8000",
        "capabilities": ["detect_violations"],
        "model": "gemini-2.5-flash",
    }

@app.post("/detect")
async def detect(data: dict):
    description = data.get("description", "")
    # 模擬 Gemini 偵測
    return {
        "violations": [{"type": "no_helmet", "severity": "high"}],
        "person_count": 3,
        "model_used": "gemini-2.5-flash",
    }
