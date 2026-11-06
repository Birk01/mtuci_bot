import os
from sentence_transformers import SentenceTransformer
import faiss


def chunk_markdown(text: str, chunk_size: int = 500, overlap: int = 50) -> list:
    """Разбивает текст на чанки по заголовкам Markdown."""
    lines = text.split('\n')
    chunks = []
    current_chunk = ""
    
    for line in lines:
        if line.strip().startswith('#'):
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            current_chunk = line + '\n'
        elif len(current_chunk) + len(line) < chunk_size:
            current_chunk += line
        else:
            chunks.append(current_chunk.strip())
            current_chunk = line
    
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return chunks


class IndexBuilder:
    def __init__(self, embedding_model: str = "intfloat/multilingual-e5-base"):
        self.embedding_model = embedding_model
        print(f"Загружаю модель эмбеддингов: {embedding_model}")
        
    def build_index(self, corpus_path: str, index_path: str = "output/index.faiss", 
                    chunks_path: str = "output/chunks.json"):
        """Строит FAISS индекс из markdown файла."""
        
        encoder = SentenceTransformer(self.embedding_model)
        
        with open(corpus_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Разбиваем корпус по маркерам файлов ('=== '), беря ВСЕ части, а не первую
        parts = text.split('=== ')
        raw_text = '\n'.join(parts[1:]) if len(parts) > 1 else text
        chunks = chunk_markdown(raw_text)
        print(f"Найдено чанков: {len(chunks)}")
        
        embeddings = encoder.encode(chunks, batch_size=32, show_progress_bar=True)
        
        dim = embeddings.shape[1]
        index = faiss.IndexFlatL2(dim)
        index.add(embeddings)
        
        os.makedirs(os.path.dirname(index_path), exist_ok=True)
        faiss.write_index(index, index_path)
        
        import json
        with open(chunks_path, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, ensure_ascii=False)  # Сохраняем ВСЕ чанки (иначе индексы в FAISS будут ссылаться на несуществующие чанки)
        
        print(f"✓ Индекс сохранён в {index_path}")
        print(f"✓ Чанки ({len(chunks)} штук) сохранены в {chunks_path}")


if __name__ == "__main__":
    builder = IndexBuilder()
    builder.build_index("output/combined.md")