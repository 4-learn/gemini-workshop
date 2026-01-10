# Gemini Workshop

感知層（Perception）的 Workshop 解答 - 多模態輸入處理。

## 目錄

| 目錄 | 說明 |
|------|------|
| `perception/` | 感知層整合：圖像分析、事件轉換 |

## 安裝

```bash
pip install google-generativeai Pillow python-dotenv
```

## 設定

```bash
export GOOGLE_API_KEY="your-api-key"
```

## 執行

```bash
# 感知層 Workshop（可用模擬模式，不需 API）
python perception/solution.py
```

## 注意事項

- 不設定 API Key 也可執行（使用模擬模式）
- 模擬模式會隨機產生違規事件
- 設定 API Key 後可測試真實 Gemini 分析
