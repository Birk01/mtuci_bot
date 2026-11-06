import os
from sentence_transformers import SentenceTransformer
import faiss


def chunk_markdown(text: str, chunk_size: int = 1500, overlap: int = 200) -> list:
    """Разбивает текст на чанки по абзацам (с учётом заголовков Markdown).

    Работает и с файлами без заголовков — например, когда текст просто
    вставлен из DeepSeek-чата: режет по пустым строкам, склеивая абзацы
    до chunk_size.
    """
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    chunks = []
    current_chunk = ""

    for para in paragraphs:
        # Если абзац сам больше лимита — режем его по границам предложений
        while len(para) > chunk_size:
            cut = para.rfind('. ', 0, chunk_size)
            if cut == -1 or cut < chunk_size // 2:
                cut = para.rfind(' ', 0, chunk_size)
            if cut == -1:
                cut = chunk_size - 1
            cut += 1
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
                current_chunk = ""
            chunks.append(para[:cut].strip())
            para = para[cut:].strip()

        candidate = (current_chunk + '\n\n' + para).strip() if current_chunk else para
        if len(candidate) <= chunk_size:
            current_chunk = candidate
        else:
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            current_chunk = para

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
        
        # Разбиваем корпус по маркерам файлов ('=== filename.pdf'),
        # беря ВСЕ части, а не только вторую. Заголовок файла превращаем
        # в markdown-заголовок, чтобы он попадал в чанки и помогал поиску.
        parts = text.split('=== ')
        if len(parts) > 1:
            sections = []
            for part in parts[1:]:
                lines = part.split('\n', 1)
                fname = lines[0].strip()
                body = lines[1] if len(lines) > 1 else ''
                sections.append(f"# {fname}\n{body}")
            raw_text = '\n\n'.join(sections)
        else:
            raw_text = text
        chunks = chunk_markdown(raw_text)
        print(f"Найдено чанков: {len(chunks)}")

        if not chunks:
            raise SystemExit(
                "⚠ combined.md пустой или содержит только заголовки без текста.\n"
                "Проверьте, что вы вставили тексты документов в output/combined.md."
            )
        
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