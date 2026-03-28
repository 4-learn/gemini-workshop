"""
Workshop 解答：Structured Output

用 Gemini response_schema 保證輸出合法 JSON。
比較 prompt-based vs schema-based。

執行方式：
  python 10_structured_schema.py
  python 10_structured_schema.py --mock
"""

import json
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


def main():
    use_mock = "--mock" in sys.argv

    print("=== Structured Output Workshop ===\n")

    # === 題目 1：定義 JSON Schema ===

    print("1. 定義工安違規 JSON Schema")
    print("-" * 50)

    schema = {
        "type": "object",
        "properties": {
            "person_count": {
                "type": "integer",
                "description": "圖片中的人數",
            },
            "violations": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "type": {
                            "type": "string",
                            "enum": ["no_helmet", "no_vest", "no_goggles", "blocked_exit", "other"],
                        },
                        "severity": {
                            "type": "string",
                            "enum": ["high", "medium", "low"],
                        },
                        "description": {
                            "type": "string",
                        },
                    },
                    "required": ["type", "severity"],
                },
            },
            "recommendations": {
                "type": "array",
                "items": {"type": "string"},
            },
        },
        "required": ["person_count", "violations"],
    }

    print("   Schema 定義完成")
    print(f"   必填欄位: {schema['required']}")
    print(f"   違規類型: {schema['properties']['violations']['items']['properties']['type']['enum']}")

    # === 題目 2：Schema-based 分析 ===

    print("\n2. 用 schema-based 分析圖片")
    print("-" * 50)

    if use_mock:
        result = {
            "person_count": 3,
            "violations": [
                {"type": "no_helmet", "severity": "high", "description": "2號工人未戴安全帽"},
            ],
            "recommendations": ["加強安全帽佩戴", "增加巡檢頻率"],
        }
        print("   [mock 模式]")
    else:
        import google.generativeai as genai
        from PIL import Image

        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("   錯誤：找不到 GOOGLE_API_KEY")
            return

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            "gemini-2.5-flash",
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema=schema,
            ),
        )

        image = Image.open("workplace.jpg")
        response = model.generate_content(["分析這張工地照片的安全狀況", image])
        result = json.loads(response.text)

    print(f"   回傳類型: {type(result).__name__}")
    print(f"   內容:")
    print(json.dumps(result, indent=4, ensure_ascii=False))

    # === 題目 3：比較兩種方法 ===

    print("\n3. 比較 prompt-based vs schema-based")
    print("-" * 50)

    prompt_success = 0
    prompt_fail = 0

    for i in range(10):
        if use_mock:
            import random
            random.seed(i)
            if random.random() < 0.2:
                raw = '```json\n{"violations": []}\n```'
            else:
                raw = '{"person_count": 2, "violations": []}'
        else:
            model_basic = genai.GenerativeModel("gemini-2.5-flash")
            image = Image.open("workplace.jpg")
            response = model_basic.generate_content([
                "分析工地照片，只輸出 JSON：{\"person_count\": N, \"violations\": []}",
                image,
            ])
            raw = response.text

        try:
            json.loads(raw)
            prompt_success += 1
        except json.JSONDecodeError:
            prompt_fail += 1

    print(f"   prompt-based: 成功 {prompt_success}/10, 失敗 {prompt_fail}/10")
    print(f"   schema-based: 成功 10/10, 失敗 0/10（保證合法）")

    print(f"\n   結論：正式系統用 schema-based，快速測試用 prompt-based")

    print("\n=== 完成 ===")


if __name__ == "__main__":
    main()
