"""
Workshop 解答：圖像輸入與描述

題目：
1. 準備 3 張工地照片（可用網路圖片）
2. 設計 prompt 來檢查 PPE 配戴情況
3. 分析結果並輸出結構化報告

執行方式：
python 06_image_input.py
"""

import google.generativeai as genai
import os
from pathlib import Path


def main():
    print("=== 圖像輸入與 PPE 檢測 ===\n")

    # === 1. 準備圖片 ===

    print("1. 準備測試圖片")
    print("-" * 50)

    # 實際應用中，這裡會是真實的圖片路徑
    test_images = [
        {"id": "site_001", "path": "construction_site_1.jpg", "description": "施工區域照片"},
        {"id": "site_002", "path": "construction_site_2.jpg", "description": "倉庫區域照片"},
        {"id": "site_003", "path": "construction_site_3.jpg", "description": "機房區域照片"},
    ]

    print("   測試圖片列表：")
    for img in test_images:
        print(f"   - {img['id']}: {img['description']}")

    # === 2. PPE 檢測 Prompt 設計 ===

    print("\n2. PPE 檢測 Prompt 設計")
    print("-" * 50)

    ppe_detection_prompt = """
請分析這張工地照片中的人員安全裝備配戴情況。

## 檢查項目
請檢查以下 PPE（個人防護裝備）：
1. 安全帽（硬帽）
2. 反光背心
3. 安全鞋
4. 護目鏡（如適用）
5. 手套（如適用）

## 輸出格式
請用以下 JSON 格式回答：

```json
{
    "image_analysis": {
        "scene_description": "場景描述",
        "total_persons": 數字,
        "persons": [
            {
                "person_id": 1,
                "location": "位置描述",
                "ppe_status": {
                    "helmet": true/false,
                    "vest": true/false,
                    "safety_shoes": "visible/not_visible/missing",
                    "goggles": "wearing/not_wearing/not_applicable",
                    "gloves": "wearing/not_wearing/not_applicable"
                },
                "violations": ["違規項目列表"],
                "risk_level": "high/medium/low"
            }
        ],
        "overall_compliance": "compliant/non_compliant",
        "recommendations": ["建議事項"]
    }
}
```

## 注意事項
- 如果無法清楚看到某項裝備，請標註為 "not_visible"
- 如果某項裝備在該場景不適用，請標註為 "not_applicable"
- risk_level 判斷標準：
  - high: 缺少安全帽或在危險區域缺少必要防護
  - medium: 缺少反光背心或部分防護裝備
  - low: 僅有輕微不合規

請仔細分析圖片並提供詳細報告。
"""

    print("   Prompt 設計完成")
    print(f"   Prompt 長度：{len(ppe_detection_prompt)} 字元")

    # === 3. 分析函數實作 ===

    print("\n3. 圖像分析函數實作")
    print("-" * 50)

    def analyze_image_for_ppe(image_path: str, prompt: str = ppe_detection_prompt) -> dict:
        """
        分析圖片中的 PPE 配戴情況

        Args:
            image_path: 圖片路徑
            prompt: 分析 prompt

        Returns:
            dict: 分析結果
        """
        # 實際應用中的 Gemini API 呼叫
        # api_key = os.environ.get("GOOGLE_API_KEY")
        # genai.configure(api_key=api_key)
        # model = genai.GenerativeModel("gemini-1.5-flash")
        #
        # image = PIL.Image.open(image_path)
        # response = model.generate_content([prompt, image])
        # return json.loads(response.text)

        # 模擬回應
        return {
            "image_analysis": {
                "scene_description": "施工現場，可見 3 名工人正在進行作業",
                "total_persons": 3,
                "persons": [
                    {
                        "person_id": 1,
                        "location": "畫面左側，靠近鷹架",
                        "ppe_status": {
                            "helmet": True,
                            "vest": True,
                            "safety_shoes": "visible",
                            "goggles": "not_applicable",
                            "gloves": "wearing"
                        },
                        "violations": [],
                        "risk_level": "low"
                    },
                    {
                        "person_id": 2,
                        "location": "畫面中央，操作機具",
                        "ppe_status": {
                            "helmet": False,
                            "vest": True,
                            "safety_shoes": "visible",
                            "goggles": "not_wearing",
                            "gloves": "not_wearing"
                        },
                        "violations": ["未配戴安全帽", "操作機具未戴護目鏡"],
                        "risk_level": "high"
                    },
                    {
                        "person_id": 3,
                        "location": "畫面右側，搬運材料",
                        "ppe_status": {
                            "helmet": True,
                            "vest": False,
                            "safety_shoes": "not_visible",
                            "goggles": "not_applicable",
                            "gloves": "wearing"
                        },
                        "violations": ["未穿著反光背心"],
                        "risk_level": "medium"
                    }
                ],
                "overall_compliance": "non_compliant",
                "recommendations": [
                    "要求人員 2 立即配戴安全帽",
                    "提供護目鏡給操作機具人員",
                    "要求人員 3 穿上反光背心",
                    "進行現場安全教育訓練"
                ]
            }
        }

    # 測試分析
    print("\n   模擬分析結果：")
    result = analyze_image_for_ppe("test_image.jpg")

    print(f"\n   場景描述：{result['image_analysis']['scene_description']}")
    print(f"   偵測人數：{result['image_analysis']['total_persons']}")
    print(f"   整體合規：{result['image_analysis']['overall_compliance']}")

    print("\n   各人員狀態：")
    for person in result['image_analysis']['persons']:
        status = "✓ 合規" if not person['violations'] else f"✗ 違規: {', '.join(person['violations'])}"
        print(f"   - 人員 {person['person_id']} ({person['location']}): {status}")

    print("\n   建議事項：")
    for rec in result['image_analysis']['recommendations']:
        print(f"   • {rec}")

    # === 完整報告格式 ===

    report_template = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
完整分析報告範本
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

照片 1 分析結果：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

場景：施工區域
時間：2024-01-15 10:30:00
攝影機：CAM-001

人員數量：3 人

PPE 配戴情況：
┌──────────┬────────┬────────┬────────┬────────┬────────┐
│ 人員      │ 安全帽 │ 反光背心│ 安全鞋 │ 護目鏡 │ 手套   │
├──────────┼────────┼────────┼────────┼────────┼────────┤
│ 人員 1    │ ✓      │ ✓      │ ✓      │ N/A    │ ✓      │
│ 人員 2    │ ✗      │ ✓      │ ✓      │ ✗      │ ✗      │
│ 人員 3    │ ✓      │ ✗      │ ?      │ N/A    │ ✓      │
└──────────┴────────┴────────┴────────┴────────┴────────┘

圖例：✓ 配戴  ✗ 未配戴  ? 無法確認  N/A 不適用

違規摘要：
- 人員 2：【高風險】未配戴安全帽、操作機具未戴護目鏡
- 人員 3：【中風險】未穿著反光背心

建議處置：
1. 立即要求人員 2 配戴安全帽（最高優先）
2. 提供並要求人員 2 配戴護目鏡
3. 要求人員 3 穿著反光背心
4. 安排安全教育訓練

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    print(report_template)

    print("=== 完成 ===")


if __name__ == "__main__":
    main()
