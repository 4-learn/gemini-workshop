"""
Workshop 解答：任務 1 - 確認 Gemini 環境可以運作

執行方式：
export GOOGLE_API_KEY="your-api-key"
python 01_check_environment.py

預期輸出：
Hello! How can I help you today?
（或其他 Gemini 的回應）
"""

import google.generativeai as genai

# 建立模型
model = genai.GenerativeModel("gemini-1.5-flash")

# 測試
response = model.generate_content("說 Hello")
print(response.text)
