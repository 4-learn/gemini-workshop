"""
Workshop 解答：任務 2 - 使用 Gemini 分析圖片

執行方式：
python 02_image_analysis.py

預期輸出：
=== 圖片分析結果 ===

場景描述：
這是一個施工現場，可以看到多名工人正在進行作業...

觀察到的人員：
- 左側有一名工人，未配戴安全帽
- 中間有一名工人，穿著反光背心
...

安全評估：
可能存在的安全隱患包括...
"""

import google.generativeai as genai
from PIL import Image
from pathlib import Path

# 建立模型
model = genai.GenerativeModel("gemini-1.5-flash")

# 載入圖片（請替換成實際圖片路徑）
image_path = "test_image.jpg"

# 檢查圖片是否存在
if Path(image_path).exists():
    image = Image.open(image_path)

    # 分析圖片
    prompt = """
    請分析這張工地照片，回答：
    1. 場景描述
    2. 觀察到的人員及其裝備
    3. 可能的安全隱患
    """

    response = model.generate_content([prompt, image])
    print("=== 圖片分析結果 ===\n")
    print(response.text)
else:
    # 沒有圖片時，使用純文字模式測試
    prompt = """
    假設你正在分析一張工地照片，照片中：
    - 有 3 名工人在施工區
    - 1 人沒戴安全帽
    - 1 人沒穿反光背心

    請提供安全評估。
    """

    response = model.generate_content(prompt)
    print("=== 模擬圖片分析結果 ===\n")
    print(response.text)
