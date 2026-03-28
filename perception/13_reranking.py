"""
Workshop 解答：Reranking（語意重排序）

對 RAG 搜尋結果做二次排序，提升精準度。

執行方式：
  python 13_reranking.py
  python 13_reranking.py --mock
"""

import json
import os
import sys
import numpy as np
from dotenv import load_dotenv

load_dotenv()

# 法規資料（跟 12_rag.py 一樣）
CHUNKS = [
    {"id": "reg_001", "title": "安全帽規定",
     "content": "依據職業安全衛生設施規則第 281 條，雇主對於在高度 2 公尺以上之工作場所，應使勞工確實使用安全帽。"},
    {"id": "reg_002", "title": "反光背心規定",
     "content": "依據職業安全衛生設施規則第 21 條，雇主應提供適當之反光標示或背心。"},
    {"id": "reg_003", "title": "護目鏡規定",
     "content": "依據職業安全衛生設施規則第 287 條，從事焊接、切割或研磨作業時，應配戴護目鏡或面罩。"},
    {"id": "reg_004", "title": "安全出口規定",
     "content": "依據建築技術規則第 97 條，安全出口寬度不得小於 1.2 公尺，不得堆放物品阻礙通行。"},
    {"id": "reg_005", "title": "高空作業安全帶",
     "content": "依據職業安全衛生設施規則第 281 條之 1，從事高度 2 公尺以上之高空作業，應使用安全帶或安全母索。"},
    {"id": "reg_006", "title": "化學品標示",
     "content": "依據危害性化學品標示及通識規則第 5 條，雇主應於化學品容器上標示名稱、危害圖式、警示語。"},
    {"id": "reg_007", "title": "噪音防護",
     "content": "依據職業安全衛生設施規則第 300 條，工作場所噪音超過 85 分貝時，雇主應提供耳塞或耳罩。"},
    {"id": "reg_008", "title": "消防設備",
     "content": "依據消防法第 6 條，各類場所應設置滅火器、室內消防栓等消防安全設備。"},
]


def get_embeddings(texts, mock=False):
    if mock:
        keywords = ["安全帽", "反光", "護目鏡", "出口", "高空", "化學", "噪音", "消防", "帽", "背心", "焊接", "作業"]
        vectors = []
        for text in texts:
            vec = [1.0 if kw in text else 0.0 for kw in keywords]
            np.random.seed(hash(text) % 2**31)
            vec = np.array(vec) + np.random.normal(0, 0.1, len(keywords))
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            vectors.append(vec.tolist())
        return vectors

    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    result = genai.embed_content(model="models/text-embedding-004", content=texts)
    return result["embedding"]


def cosine_similarity(a, b):
    a, b = np.array(a), np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8))


def main():
    use_mock = "--mock" in sys.argv

    print("=== Reranking Workshop ===\n")

    # 建立 embedding
    chunk_texts = [c["content"] for c in CHUNKS]
    chunk_embeddings = get_embeddings(chunk_texts, mock=use_mock)

    question = "在高處工作需要什麼安全裝備？"
    print(f"問題：{question}\n")

    # === 題目 1：向量搜尋（粗搜 top 5） ===

    print("1. 向量搜尋（粗搜 top 5）")
    print("-" * 50)

    query_emb = get_embeddings([question], mock=use_mock)[0]
    scores = []
    for i, emb in enumerate(chunk_embeddings):
        score = cosine_similarity(query_emb, emb)
        scores.append((score, i))
    scores.sort(reverse=True)
    top5 = [(CHUNKS[idx], round(sc, 4)) for sc, idx in scores[:5]]

    for i, (chunk, score) in enumerate(top5):
        print(f"   {i+1}. [{score}] {chunk['title']}")

    # === 題目 2：用 Gemini 做 Reranking ===

    print(f"\n2. Reranking（語意精排）")
    print("-" * 50)

    if use_mock:
        # 模擬 reranking：包含「高空」或「安全帽」的排前面
        def relevance(chunk):
            kw_score = 0
            for kw in ["高空", "安全帶", "安全帽", "高度"]:
                if kw in chunk["content"]:
                    kw_score += 1
            return kw_score

        reranked = sorted(top5, key=lambda x: -relevance(x[0]))
    else:
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        model = genai.GenerativeModel("gemini-2.5-flash")

        candidate_text = ""
        for i, (chunk, _) in enumerate(top5):
            candidate_text += f"\n段落 {i+1}（{chunk['title']}）：\n{chunk['content']}\n"

        prompt = f"""以下有 5 段法規文字。
請根據問題的相關性排序，最相關在前。
只輸出編號，用逗號分隔。

問題：{question}
{candidate_text}
排序："""

        response = model.generate_content(prompt)
        try:
            order = [int(x.strip()) - 1 for x in response.text.strip().split(",")]
            reranked = [(top5[i][0], round(1.0 - j * 0.15, 2)) for j, i in enumerate(order) if i < len(top5)]
        except (ValueError, IndexError):
            reranked = top5

    for i, (chunk, score) in enumerate(reranked):
        if use_mock:
            score = round(1.0 - i * 0.15, 2)
        print(f"   {i+1}. [{score}] {chunk['title']}")

    # === 題目 3：比較 ===

    print(f"\n3. 比較結果")
    print("-" * 50)

    old_top3 = [c["title"] for c, _ in top5[:3]]
    new_top3 = [c["title"] for c, _ in reranked[:3]]

    print(f"   向量搜尋 top 3: {old_top3}")
    print(f"   Reranking top 3: {new_top3}")

    if old_top3 != new_top3:
        print(f"\n   Reranking 改變了排序，更相關的結果排到前面")
    else:
        print(f"\n   排序沒變，Reranking 確認了搜尋結果合理")

    print("\n=== 完成 ===")


if __name__ == "__main__":
    main()
