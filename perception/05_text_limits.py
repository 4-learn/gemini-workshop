"""
Workshop 解答：文字輸入的限制

題目：
1. 計算一份法規文件的 token 數量
2. 實作分段處理功能
3. 測試處理結果

執行方式：
python 05_text_limits.py
"""

import tiktoken  # OpenAI 的 tokenizer，可用於估算


def main():
    print("=== 文字輸入限制與分段處理 ===\n")

    # === 1. 計算 Token 數量 ===

    print("1. Token 數量計算")
    print("-" * 50)

    # 模擬法規文件內容
    sample_regulation = """
    職業安全衛生法

    第一章 總則

    第1條 為防止職業災害，保障工作者安全及健康，特制定本法。

    第2條 本法所稱工作者，指下列人員：
    一、勞工：指受僱從事工作獲致工資者。
    二、自營作業者：指獨立從事勞動或技藝工作，獲致報酬，且未僱用有酬人員幫同工作者。
    """ * 100  # 重複 100 次模擬長文件

    print(f"   文件長度：{len(sample_regulation)} 字元")

    # 使用 tiktoken 估算 token 數量
    # 注意：Gemini 的 tokenizer 與 OpenAI 不同，這只是估算
    try:
        encoding = tiktoken.encoding_for_model("gpt-4")
        token_count = len(encoding.encode(sample_regulation))
        print(f"   估算 Token 數量：約 {token_count} tokens")
    except:
        # 簡單估算：中文約 1.5 字 = 1 token
        estimated_tokens = int(len(sample_regulation) / 1.5)
        print(f"   估算 Token 數量：約 {estimated_tokens} tokens")

    # === Token 限制說明 ===

    limits_info = """

各模型 Token 限制：
┌─────────────────────┬──────────────────┬──────────────────┐
│ 模型                │ 輸入限制          │ 輸出限制          │
├─────────────────────┼──────────────────┼──────────────────┤
│ Gemini 1.5 Pro      │ 1,000,000 tokens │ 8,192 tokens     │
│ Gemini 1.5 Flash    │ 1,000,000 tokens │ 8,192 tokens     │
│ GPT-4 Turbo         │ 128,000 tokens   │ 4,096 tokens     │
│ Claude 3            │ 200,000 tokens   │ 4,096 tokens     │
└─────────────────────┴──────────────────┴──────────────────┘
"""
    print(limits_info)

    # === 2. 分段處理功能 ===

    print("\n2. 分段處理功能實作")
    print("-" * 50)

    def split_into_chunks(text: str, max_tokens: int = 10000) -> list:
        """
        將長文本分割成多個段落

        Args:
            text: 原始文本
            max_tokens: 每段最大 token 數

        Returns:
            list: 分割後的文本列表
        """
        # 估算每段最大字元數（中文約 1.5 字 = 1 token）
        max_chars = int(max_tokens * 1.5)

        chunks = []
        current_pos = 0

        while current_pos < len(text):
            # 取得一段文本
            end_pos = min(current_pos + max_chars, len(text))

            # 嘗試在句號或換行處斷開
            if end_pos < len(text):
                # 往回找最近的斷句點
                for sep in ["。\n", "。", "\n\n", "\n"]:
                    last_sep = text.rfind(sep, current_pos, end_pos)
                    if last_sep > current_pos:
                        end_pos = last_sep + len(sep)
                        break

            chunk = text[current_pos:end_pos].strip()
            if chunk:
                chunks.append(chunk)

            current_pos = end_pos

        return chunks

    # 測試分段
    chunks = split_into_chunks(sample_regulation, max_tokens=8000)

    print(f"   原始文件長度：{len(sample_regulation)} 字元")
    print(f"   分段數量：{len(chunks)} 段")
    print(f"\n   各段長度：")
    for i, chunk in enumerate(chunks):
        print(f"   - 第 {i+1} 段：{len(chunk)} 字元")

    # === 3. 分段處理測試 ===

    print("\n3. 分段處理測試")
    print("-" * 50)

    def process_chunks_with_summary(chunks: list) -> dict:
        """
        分段處理並合併結果

        在實際應用中，這裡會呼叫 Gemini API
        """
        results = {
            "total_chunks": len(chunks),
            "summaries": [],
            "final_summary": ""
        }

        # 模擬處理每一段
        for i, chunk in enumerate(chunks):
            # 實際應用：summary = gemini.generate(f"摘要以下內容：{chunk}")
            summary = f"[第 {i+1} 段摘要] 本段包含 {len(chunk)} 字元的法規內容..."
            results["summaries"].append(summary)
            print(f"   處理第 {i+1}/{len(chunks)} 段...")

        # 合併所有摘要
        all_summaries = "\n".join(results["summaries"])
        # 實際應用：final = gemini.generate(f"整合以下摘要：{all_summaries}")
        results["final_summary"] = f"[最終摘要] 共處理 {len(chunks)} 段法規文件..."

        return results

    results = process_chunks_with_summary(chunks)

    print(f"\n   處理結果：")
    print(f"   - 總段數：{results['total_chunks']}")
    print(f"   - 最終摘要：{results['final_summary']}")

    # === 最佳實踐 ===

    best_practices = """
分段處理最佳實踐
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【策略選擇】

1. Map-Reduce 策略
   ┌─────┐  ┌─────┐  ┌─────┐
   │段落1│  │段落2│  │段落3│
   └──┬──┘  └──┬──┘  └──┬──┘
      │        │        │
      ▼        ▼        ▼
   ┌─────┐  ┌─────┐  ┌─────┐
   │摘要1│  │摘要2│  │摘要3│
   └──┬──┘  └──┬──┘  └──┬──┘
      └────────┼────────┘
               ▼
         ┌──────────┐
         │ 最終摘要 │
         └──────────┘

2. Refine 策略
   段落1 → 初步摘要 → 加入段落2 → 更新摘要 → 加入段落3 → 最終摘要

【注意事項】

1. 保持上下文：在每段開頭加入前段摘要
2. 重疊處理：相鄰段落保留部分重疊，避免資訊遺失
3. 並行處理：獨立段落可以並行呼叫 API
4. 錯誤處理：單段失敗不應影響其他段落
"""
    print(best_practices)

    print("\n=== 完成 ===")


if __name__ == "__main__":
    main()
