"""
Workshop 解答：Gemini 感知層

題目要求：
1. 實作工安圖像分析器
2. 結構化輸出（JSON）
3. 與系統整合（產生事件）
4. 錯誤處理與 fallback

預期輸出：
=== 工安感知系統 ===

分析圖像: test_image.jpg

分析結果:
  場景: 施工現場，多名工人正在作業
  人數: 3
  安全評分: 65/100

違規事項:
  1. [HIGH] no_helmet - 左側工人未配戴安全帽
  2. [MEDIUM] no_vest - 中間工人未穿反光背心

建議:
  - 加強入口處 PPE 檢查
  - 設置自動提醒系統

已轉換為 2 個系統事件
"""

import os
import json
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Optional
from abc import ABC, abstractmethod

# 嘗試載入 Gemini（可選）
try:
    import google.generativeai as genai
    from dotenv import load_dotenv
    load_dotenv()
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


# === 資料結構 ===

@dataclass
class Violation:
    """違規項目"""
    type: str
    description: str
    location: str
    severity: str  # high, medium, low
    regulation: Optional[str] = None


@dataclass
class PerceptionResult:
    """感知結果"""
    timestamp: datetime
    source: str
    scene_description: str
    people_count: int
    violations: list[Violation]
    safety_score: int
    recommendations: list[str]
    confidence: float = 1.0
    metadata: dict = field(default_factory=dict)


@dataclass
class DetectionEvent:
    """偵測事件（與系統整合用）"""
    event_id: str
    timestamp: datetime
    object: str
    confidence: float
    source: str
    metadata: dict


# === 感知器介面 ===

class PerceptionProvider(ABC):
    """感知器抽象介面"""

    @abstractmethod
    def analyze(self, image, source: str) -> PerceptionResult:
        """分析圖像"""
        pass


# === Gemini 感知器 ===

class GeminiPerception(PerceptionProvider):
    """使用 Gemini 的感知器"""

    SYSTEM_PROMPT = """你是工安監控系統的 AI 視覺分析員。
分析工地照片，找出安全違規和風險。

重點檢查：
1. PPE：安全帽、反光背心、安全鞋、護目鏡
2. 高空作業：安全帶、護欄
3. 環境：通道、照明、雜物

請客觀、專業地分析。"""

    ANALYSIS_PROMPT = """分析這張工地照片。

以 JSON 格式輸出：
```json
{
    "scene_description": "場景描述",
    "people_count": 人數,
    "violations": [
        {
            "type": "違規類型代碼",
            "description": "描述",
            "location": "圖片中位置",
            "severity": "high/medium/low",
            "regulation": "相關法規"
        }
    ],
    "safety_score": 0-100,
    "recommendations": ["建議"]
}
```

違規類型代碼：no_helmet, no_vest, no_safety_belt, blocked_exit, other

只輸出 JSON。"""

    def __init__(self):
        if not GEMINI_AVAILABLE:
            raise RuntimeError("Gemini 未安裝，請執行: pip install google-generativeai")

        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("請設定 GOOGLE_API_KEY")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            "gemini-1.5-flash",
            system_instruction=self.SYSTEM_PROMPT
        )

    def analyze(self, image, source: str = "unknown") -> PerceptionResult:
        """分析圖像"""
        response = self.model.generate_content([self.ANALYSIS_PROMPT, image])
        data = self._parse_json(response.text)

        violations = [
            Violation(
                type=v.get("type", "unknown"),
                description=v.get("description", ""),
                location=v.get("location", ""),
                severity=v.get("severity", "medium"),
                regulation=v.get("regulation")
            )
            for v in data.get("violations", [])
        ]

        return PerceptionResult(
            timestamp=datetime.now(timezone.utc),
            source=source,
            scene_description=data.get("scene_description", ""),
            people_count=data.get("people_count", 0),
            violations=violations,
            safety_score=data.get("safety_score", 0),
            recommendations=data.get("recommendations", []),
            metadata={"provider": "gemini", "raw": response.text}
        )

    def _parse_json(self, text: str) -> dict:
        """解析 JSON"""
        text = text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            return {"error": "parse_failed", "raw": text}


# === 模擬感知器（不需 API）===

class MockPerception(PerceptionProvider):
    """模擬感知器（用於測試）"""

    def __init__(self, violation_rate: float = 0.3):
        self.violation_rate = violation_rate
        import random
        self.random = random

    def analyze(self, image, source: str = "unknown") -> PerceptionResult:
        """模擬分析"""
        import random

        # 模擬人數
        people_count = random.randint(1, 5)

        # 模擬違規
        violations = []
        violation_types = [
            ("no_helmet", "未配戴安全帽", "職安法第281條"),
            ("no_vest", "未穿反光背心", "職安法第277條"),
            ("no_safety_belt", "未繫安全帶", "職安法第225條"),
        ]

        for vtype, desc, reg in violation_types:
            if random.random() < self.violation_rate:
                violations.append(Violation(
                    type=vtype,
                    description=f"偵測到人員{desc}",
                    location=random.choice(["左側", "中間", "右側"]),
                    severity=random.choice(["high", "medium", "low"]),
                    regulation=reg
                ))

        # 計算安全分數
        base_score = 100
        for v in violations:
            penalty = {"high": 20, "medium": 10, "low": 5}.get(v.severity, 10)
            base_score -= penalty

        return PerceptionResult(
            timestamp=datetime.now(timezone.utc),
            source=source,
            scene_description="施工現場，多名工人正在作業",
            people_count=people_count,
            violations=violations,
            safety_score=max(0, base_score),
            recommendations=["加強 PPE 檢查", "設置提醒系統"],
            confidence=0.85,
            metadata={"provider": "mock"}
        )


# === 感知層整合 ===

class PerceptionLayer:
    """
    感知層

    負責：
    1. 圖像分析
    2. 結果轉換為系統事件
    3. 錯誤處理與 fallback
    """

    def __init__(self, provider: PerceptionProvider = None, fallback: PerceptionProvider = None):
        self.provider = provider or MockPerception()
        self.fallback = fallback
        self.event_counter = 0

    def process(self, image, source: str = "unknown") -> tuple[PerceptionResult, list[DetectionEvent]]:
        """
        處理圖像

        Returns:
            (感知結果, 事件列表)
        """
        # 嘗試主感知器
        try:
            result = self.provider.analyze(image, source)
        except Exception as e:
            print(f"主感知器失敗: {e}")
            if self.fallback:
                result = self.fallback.analyze(image, source)
            else:
                raise

        # 轉換為系統事件
        events = self._to_events(result)

        return result, events

    def _to_events(self, result: PerceptionResult) -> list[DetectionEvent]:
        """轉換為系統事件"""
        events = []

        for violation in result.violations:
            self.event_counter += 1
            event = DetectionEvent(
                event_id=f"evt_{self.event_counter:06d}",
                timestamp=result.timestamp,
                object=violation.type,
                confidence=self._severity_to_confidence(violation.severity),
                source=result.source,
                metadata={
                    "description": violation.description,
                    "location": violation.location,
                    "severity": violation.severity,
                    "regulation": violation.regulation,
                    "safety_score": result.safety_score,
                }
            )
            events.append(event)

        return events

    def _severity_to_confidence(self, severity: str) -> float:
        """嚴重度轉信心度"""
        return {"high": 0.95, "medium": 0.80, "low": 0.60}.get(severity, 0.70)


# === 顯示結果 ===

def display_result(result: PerceptionResult, events: list[DetectionEvent]):
    """顯示分析結果"""
    print("=" * 50)
    print("分析結果")
    print("=" * 50)

    print(f"\n場景: {result.scene_description}")
    print(f"人數: {result.people_count}")
    print(f"安全評分: {result.safety_score}/100")

    if result.violations:
        print(f"\n違規事項 ({len(result.violations)}):")
        for i, v in enumerate(result.violations, 1):
            sev = {"high": "HIGH", "medium": "MED", "low": "LOW"}.get(v.severity, "?")
            print(f"  {i}. [{sev}] {v.type} - {v.description}")
            if v.regulation:
                print(f"      法規: {v.regulation}")
    else:
        print("\n未發現違規")

    if result.recommendations:
        print(f"\n建議:")
        for r in result.recommendations:
            print(f"  - {r}")

    print(f"\n已轉換為 {len(events)} 個系統事件")


# === 主程式 ===

def main():
    print("=" * 50)
    print("Gemini Workshop: 感知層")
    print("=" * 50)
    print()

    # 使用模擬感知器（不需 API）
    print("使用模擬感知器進行測試...\n")

    mock_provider = MockPerception(violation_rate=0.5)
    layer = PerceptionLayer(provider=mock_provider)

    # 模擬處理 3 個「影像」
    for i in range(3):
        print(f"\n--- 分析影像 {i+1} ---")

        result, events = layer.process(
            image=f"frame_{i}.jpg",  # 模擬影像
            source=f"camera_0{i+1}"
        )

        display_result(result, events)

    print("\n" + "-" * 50)

    # 嘗試使用 Gemini（如果有設定 API Key）
    if GEMINI_AVAILABLE and os.getenv("GOOGLE_API_KEY"):
        print("\n偵測到 Gemini API Key，是否測試真實分析？")
        print("輸入 'yes' 測試（需要提供圖片路徑），其他跳過")
        user_input = input("> ").strip().lower()

        if user_input == "yes":
            print("請輸入圖片路徑:")
            img_path = input("> ").strip()

            try:
                from PIL import Image
                img = Image.open(img_path)

                gemini_provider = GeminiPerception()
                layer = PerceptionLayer(
                    provider=gemini_provider,
                    fallback=mock_provider
                )

                result, events = layer.process(img, source=img_path)
                display_result(result, events)

            except Exception as e:
                print(f"錯誤: {e}")
    else:
        print("\n提示：設定 GOOGLE_API_KEY 可測試 Gemini 真實分析")

    print("\nWorkshop 完成！")


if __name__ == "__main__":
    main()
