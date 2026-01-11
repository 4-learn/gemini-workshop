"""
Workshop 解答：多模態輸入轉結構化資料

題目：
1. 設計違規報告的 JSON Schema
2. 實作圖像分析功能
3. 驗證輸出的 JSON 格式

執行方式：
python 08_multimodal_structured.py
"""

import json
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator
from enum import Enum


def main():
    print("=== 多模態輸入轉結構化資料 ===\n")

    # === 1. 設計 JSON Schema ===

    print("1. 違規報告 JSON Schema 設計")
    print("-" * 50)

    # 使用 Pydantic 定義結構化資料模型

    class RiskLevel(str, Enum):
        HIGH = "high"
        MEDIUM = "medium"
        LOW = "low"

    class PPEStatus(BaseModel):
        helmet: bool = Field(description="是否配戴安全帽")
        vest: bool = Field(description="是否穿著反光背心")
        safety_shoes: Optional[str] = Field(description="安全鞋狀態: visible/not_visible/missing")
        goggles: Optional[str] = Field(description="護目鏡狀態")
        gloves: Optional[str] = Field(description="手套狀態")

    class PersonAnalysis(BaseModel):
        person_id: int = Field(description="人員編號")
        location: str = Field(description="在畫面中的位置")
        activity: str = Field(description="正在進行的活動")
        ppe_status: PPEStatus = Field(description="PPE 配戴狀態")
        violations: list[str] = Field(default=[], description="違規項目列表")
        risk_level: RiskLevel = Field(description="風險等級")

    class ViolationReport(BaseModel):
        timestamp: datetime = Field(description="分析時間")
        image_id: str = Field(description="圖片識別碼")
        camera_id: str = Field(description="攝影機編號")
        zone: str = Field(description="區域名稱")
        scene_description: str = Field(description="場景描述")
        total_persons: int = Field(description="偵測到的人數")
        persons: list[PersonAnalysis] = Field(description="各人員分析結果")
        total_violations: int = Field(description="違規總數")
        high_risk_count: int = Field(description="高風險違規數")
        overall_status: str = Field(description="整體狀態: compliant/non_compliant")
        recommendations: list[str] = Field(description="建議事項")

    # 輸出 Schema
    schema = ViolationReport.model_json_schema()
    print("   Schema 定義完成")
    print(f"   欄位數量：{len(schema['properties'])} 個")

    # === 2. 實作圖像分析功能 ===

    print("\n2. 圖像分析功能實作")
    print("-" * 50)

    def analyze_image_structured(image_path: str, camera_id: str, zone: str) -> ViolationReport:
        """
        分析圖像並返回結構化違規報告

        Args:
            image_path: 圖片路徑
            camera_id: 攝影機編號
            zone: 區域名稱

        Returns:
            ViolationReport: 結構化的違規報告
        """
        # 實際應用中，這裡會呼叫 Gemini API
        # 並使用 JSON mode 確保輸出格式

        prompt = f"""
請分析這張工地照片，並以嚴格的 JSON 格式輸出分析結果。

JSON Schema:
{json.dumps(schema, indent=2, ensure_ascii=False)}

請確保輸出符合上述 Schema，所有必填欄位都要填寫。
"""

        # 模擬 Gemini 回應
        # response = model.generate_content([prompt, image],
        #     generation_config={"response_mime_type": "application/json"})

        # 模擬分析結果
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "image_id": f"img_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "camera_id": camera_id,
            "zone": zone,
            "scene_description": "施工區域，3名工人正在進行混凝土澆注作業",
            "total_persons": 3,
            "persons": [
                {
                    "person_id": 1,
                    "location": "畫面左側",
                    "activity": "操作混凝土泵車",
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
                    "location": "畫面中央",
                    "activity": "整平混凝土",
                    "ppe_status": {
                        "helmet": False,
                        "vest": True,
                        "safety_shoes": "visible",
                        "goggles": "not_applicable",
                        "gloves": "not_wearing"
                    },
                    "violations": ["未配戴安全帽", "未配戴手套"],
                    "risk_level": "high"
                },
                {
                    "person_id": 3,
                    "location": "畫面右側",
                    "activity": "搬運工具",
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
            "total_violations": 3,
            "high_risk_count": 1,
            "overall_status": "non_compliant",
            "recommendations": [
                "立即要求人員2配戴安全帽",
                "提供防護手套給人員2",
                "要求人員3穿著反光背心",
                "加強現場PPE督導"
            ]
        }

        return ViolationReport(**report_data)

    # 執行分析
    report = analyze_image_structured(
        image_path="construction_site.jpg",
        camera_id="CAM-A01",
        zone="施工區A"
    )

    print("   分析完成")
    print(f"   偵測人數：{report.total_persons}")
    print(f"   違規數量：{report.total_violations}")
    print(f"   高風險數：{report.high_risk_count}")

    # === 3. 驗證 JSON 格式 ===

    print("\n3. JSON 格式驗證")
    print("-" * 50)

    def validate_and_export(report: ViolationReport) -> tuple[bool, str]:
        """
        驗證並匯出 JSON

        Returns:
            tuple: (驗證是否通過, JSON 字串)
        """
        try:
            # Pydantic 會自動驗證
            json_str = report.model_dump_json(indent=2, ensure_ascii=False)
            return True, json_str
        except Exception as e:
            return False, str(e)

    is_valid, json_output = validate_and_export(report)

    print(f"   驗證結果：{'✓ 通過' if is_valid else '✗ 失敗'}")

    if is_valid:
        print("\n   JSON 輸出：")
        print("-" * 50)
        # 只印出部分內容
        json_dict = json.loads(json_output)
        preview = {
            "timestamp": json_dict["timestamp"],
            "image_id": json_dict["image_id"],
            "total_persons": json_dict["total_persons"],
            "total_violations": json_dict["total_violations"],
            "overall_status": json_dict["overall_status"],
            "persons_count": len(json_dict["persons"]),
            "recommendations_count": len(json_dict["recommendations"])
        }
        print(json.dumps(preview, indent=2, ensure_ascii=False))

    # === Gemini JSON Mode 說明 ===

    gemini_json_mode = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Gemini JSON Mode 使用方式
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

```python
import google.generativeai as genai

model = genai.GenerativeModel("gemini-1.5-flash")

# 方法 1：指定 response_mime_type
response = model.generate_content(
    [prompt, image],
    generation_config={
        "response_mime_type": "application/json"
    }
)

# 方法 2：提供 JSON Schema
response = model.generate_content(
    [prompt, image],
    generation_config={
        "response_mime_type": "application/json",
        "response_schema": ViolationReport.model_json_schema()
    }
)

# 解析結果
result = json.loads(response.text)
report = ViolationReport(**result)
```

優點：
- 確保輸出為有效的 JSON
- 減少格式錯誤
- 便於後續處理
"""
    print(gemini_json_mode)

    print("\n=== 完成 ===")


if __name__ == "__main__":
    main()
