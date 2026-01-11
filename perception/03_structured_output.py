"""
Workshop 解答：任務 3 - 使用 Gemini 輸出結構化 JSON

執行方式：
python 03_structured_output.py

預期輸出：
=== 結構化分析結果 ===

原始回應:
{
    "scene": "施工現場",
    "person_count": 3,
    "safety_score": 65,
    "violations": [
        {
            "type": "no_helmet",
            "severity": "high",
            "description": "左側工人未配戴安全帽"
        }
    ]
}

解析結果:
  場景: 施工現場
  人數: 3
  安全評分: 65/100
  違規數: 1
"""

import google.generativeai as genai
import json

# 建立模型
model = genai.GenerativeModel("gemini-1.5-flash")

# 要求結構化輸出的 Prompt
prompt = """
分析以下工安事件，以 JSON 格式回答：

事件描述：施工現場有 3 名工人，其中 1 人沒戴安全帽，1 人沒穿反光背心。

請用以下格式回答（只輸出 JSON，不要其他文字）：
{
    "scene": "場景描述",
    "person_count": 數字,
    "safety_score": 0-100 的安全評分,
    "violations": [
        {
            "type": "違規類型代碼",
            "severity": "high/medium/low",
            "description": "違規描述"
        }
    ]
}
"""

response = model.generate_content(prompt)

print("=== 結構化分析結果 ===\n")
print("原始回應:")
print(response.text)

# 嘗試解析 JSON
try:
    # 清理回應（移除可能的 markdown 標記）
    text = response.text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]

    data = json.loads(text.strip())

    print("\n解析結果:")
    print(f"  場景: {data['scene']}")
    print(f"  人數: {data['person_count']}")
    print(f"  安全評分: {data['safety_score']}/100")
    print(f"  違規數: {len(data['violations'])}")

except json.JSONDecodeError as e:
    print(f"\nJSON 解析失敗: {e}")
