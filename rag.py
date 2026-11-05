import os
from sentence_transformers import SentenceTransformer
import faiss


class RAGBot:
    def __init__(self, chunks_path: str = "output/chunks.json", 
                 index_path: str = "output/index.faiss",
                 embedding_model: str = "intfloat/multilingual-e5-base"):
        self.embedding_model = embedding_model
        self.encoder = SentenceTransformer(embedding_model)
        
        self.chunks = None
        self.index = None
        
        if os.path.exists(index_path):
            dim = self.encoder.embeddings.embedding_dim
            self.index = faiss.read_index(index_path)
            
            import json
            with open(chunks_path, 'r', encoding='utf-8') as f:
                all_chunks = json.load(f)
            
            print(f"✓ Индекс загружен ({len(all_chunks)} чанков)")
        else:
            raise FileNotFoundError("Сначала создайте индекс через build_index.py")
    
    def search(self, query: str, top_k: int = 3, index_path: str = "output/index.faiss"):
        """Ищет релевантные чанки по запросу."""
        
        if not self.index:
            raise RuntimeError("Сначала загрузите индекс")
        
        query_emb = self.encoder.encode([query])
        
        D, I = self.index.search(query_emb, top_k)
        
        results = []
        for i in range(top_k):
            score = float(D[0][i])
            idx = int(I[0][i])
            if len(self.chunks) > idx:
                results.append({
                    'text': self.chunks[idx],
                    'score': score,
                    'distance': D[0][i]
                })
        
        return results
    
    def generate_answer(self, query: str, context_chunks: list):
        """Генерирует ответ (placeholder - просто возвращает контекст)."""
        # В реальном проекте здесь был бы LLM
        if not context_chunks:
            return "Из предоставленных документов не найден ответ на ваш вопрос."
        
        texts = []
        for item in context_chunks:
            text = item['text'][:300] + '...' if len(item['text']) > 300 else item['text']
            texts.append(f"[{item['distance']:.2f}]\n{text}")
        
        return "На основе найденных документов:\n\n" + "\n---\n".join(texts)
    
    def ask(self, query: str, top_k: int = 3) -> dict:
        """Полный RAG цикл."""
        results = self.search(query, top_k)
        
        context_chunks = [r for r in results if r['distance'] < 4.0]
        answer = self.generate_answer(query, context_chunks)
        
        return {
            'query': query,
            'answer': answer,
            'sources': context_chunks,
            'relevance_scores': [r['distance'] for r in context_chunks]
        }


if __name__ == "__main__":
    bot = RAGBot()
    print("Пример использования: bot.ask('Как зачисляют студентов?')")