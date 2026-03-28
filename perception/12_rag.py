"""
Workshop 解答：RAG（Retrieval-Augmented Generation）

法規搜尋 + Gemini 回答。

執行方式：
  python 12_rag.py
  python 12_rag.py --mock
"""

import json
import os
import sys
import numpy as np
from dotenv import load_dotenv

load_dotenv()

# 法規資料
CHUNKS = [
    {"id": "reg_001", "title": "安全帽規定",
     "content": "依據職業安全衛生設施規則第 281 條，雇主對於在高度 2 公尺以上之工作場所，應使勞工確實使用安全帽。安全帽應符合 CNS 國家標準。"},
    {"id": "reg_002", "title": "反光背心規定",
     "content": "依據職業安全衛生設施規則第 21 條，雇主應提供適當之反光標示或背心。於夜間或光線不足之場所作業，應提供高可見度服裝。"},
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

    print("=== RAG Workshop ===\n")

    # === 題目 1：建立 embedding ===

    print("1. 建立法規 embedding")
    print("-" * 50)

    chunk_texts = [c["content"] for c in CHUNKS]
    chunk_embeddings = get_embeddings(chunk_texts, mock=use_mock)
    print(f"   {len(CHUNKS)} 段法規，向量維度: {len(chunk_embeddings[0])}")

    # === 題目 2：實作向量搜尋 ===

    print("\n2. 實作向量搜尋")
    print("-" * 50)

    def search(query, top_k=3):
        query_emb = get_embeddings([query], mock=use_mock)[0]
        scores = []
        for i, emb in enumerate(chunk_embeddings):
            score = cosine_similarity(query_emb, emb)
            scores.append((score, i))
        scores.sort(reverse=True)
        return [(CHUNKS[idx], round(sc, 4)) for sc, idx in scores[:top_k]]

    test = search("安全帽有什麼規定？")
    for chunk, score in test:
        print(f"   [{score}] {chunk['title']}")

    # === 題目 3：組合 RAG pipeline ===

    print("\n3. RAG Pipeline")
    print("-" * 50)

    def rag_answer(question):
        # 搜尋
        results = search(question, top_k=3)
        print(f"\n   問題：{question}")
        print(f"   搜尋結果：")
        for chunk, score in results:
            print(f"     [{score}] {chunk['title']}")

        # 組 context
        context = "\n\n".join([f"【{c['title']}】\n{c['content']}" for c, _ in results])

        # 生成
        if use_mock:
            answer = f"根據{results[0][0]['title']}，{results[0][0]['content'][:60]}..."
        else:
            import google.generativeai as genai
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
            model = genai.GenerativeModel("gemini-2.5-flash")
            prompt = f"根據以下法規回答問題，只用提供的內容回答。\n\n法規：\n{context}\n\n問題：{question}"
            response = model.generate_content(prompt)
            answer = response.text

        print(f"   回答：{answer}")
        return answer

    # === 題目 4：測試 3 個問題 ===

    print("\n4. 測試")
    print("-" * 50)

    questions = [
        "安全帽有什麼規定？",
        "高空作業需要什麼防護？",
        "噪音太大怎麼辦？",
    ]

    for q in questions:
        rag_answer(q)

    print("\n=== 完成 ===")


if __name__ == "__main__":
    main()
