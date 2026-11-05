import os
import sys
import json
from tqdm import tqdm
from typing import List
import torch
from torch.utils.data import Dataset, DataLoader
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# --- 1. ИСПРАВЛЕНИЕ КЛАССА DATASET ---
class PDFChunkDataset(Dataset):
    def __init__(self, chunks: List[str]):
        super().__init__()
        # Сохраняем данные в атрибут self.data, как и положено классу Dataset
        self.data = chunks
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        return self.data[idx]

# --- 2. ИСПРАВЛЕНИЕ ЛОГИКИ НАРЕЗКИ ---
def chunk_markdown_by_headers(text: str, max_chunk_size: int = 5000, overlap: int = 500) -> List[str]:
    """Split markdown by headers into chunks of approximately max_chunk_size tokens."""
    import re
    # Ищем заголовки с их содержимым
    headers = re.findall(r'^#+\s.*$', text, re.MULTILINE)
    if not headers:
        return [text[i:i+max_chunk_size] for i in range(0, len(text), max_chunk_size - overlap)]
    
    chunks = []
    current_chunk = ""
    
    # Разбиваем текст по заголовкам
    parts = re.split(r'(^#+\s.*$)', text, flags=re.MULTILINE)
    
    for part in parts:
        if not part.strip():
            continue
            
        # Если добавление части превысит лимит, сохраняем текущий чанк
        if len(current_chunk) + len(part) > max_chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            current_chunk = part + "\n"
        else:
            current_chunk += part + "\n"
            
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return chunks

# --- 3. ИСПРАВЛЕНИЕ LOADER ---
class CombinedMDLoader:
    def __init__(self, file_path: str):
        self.file_path = file_path
        # Убрали pydub, используем стандартное чтение файла
        with open(self.file_path, 'r', encoding='utf-8') as f:
            self.text = f.read()
    
    def __getitem__(self, i):
        return self.text.split('\n')[i]
    
    def __len__(self):
        return len(self.text.split('\n'))

def load_corpus(output_dir: str):
    print("Loading combined markdown...")
    loader = CombinedMDLoader(f'{output_dir}/combined.md')
    print(f"Loaded {len(loader)} lines from corpus")
    
    chunks = chunk_markdown_by_headers(loader.text)
    print(f"Created {len(chunks)} chunks")
    
    for i, chunk in enumerate(tqdm(chunks, desc="Chunking", total=len(chunks))):
        # Trim chunk if too large (исправлено, так как chunk - это строка)
        if len(chunk.split()) > 500:
            chunk = " ".join(chunk.split()[:500])
        
        chunks[i] = chunk.strip()
    
    print(f"Total text tokens in chunks: {sum(len(c.split()) for c in chunks)}")
    return chunks

# --- 4. ИСПРАВЛЕНИЕ ПОСТРОЕНИЯ ИНДЕКСА ---
def build_faiss_index(chunks: List[str]):
    print("Initializing embedding model...")
    # Загружаем модель для создания векторов
    model = SentenceTransformer('intfloat/multilingual-e5-base')
    
    print("Encoding chunks to vectors...")
    # Кодируем тексты в векторы (эмбеддинги)
    embeddings = model.encode(chunks, show_progress_bar=True, convert_to_numpy=True)
    
    print("Building FAISS index...")
    dim = embeddings.shape[1] # Размерность вектора (для e5-base это 768)
    index = faiss.IndexFlatL2(dim)
    
    # Добавляем именно векторы, а не строки!
    index.add(embeddings.astype(np.float32))
    
    print(f"Indexed {index.ntotal} vectors")
    return index, embeddings

def build_index(output_dir: str):
    print("Building vector index...")
    
    # Загружаем и нарезаем
    chunks = load_corpus(output_dir)
    
    # Строим индекс
    index, embeddings = build_faiss_index(chunks)
    
    # Сохраняем выходные данные
    os.makedirs(output_dir, exist_ok=True)
    
    # ВАЖНО: Правильный метод сохранения FAISS — faiss.write_index
    faiss.write_index(index, f'{output_dir}/index.faiss')
    
    with open(f'{output_dir}/chunks.json', 'w', encoding='utf-8') as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
        
    # Сохраняем и сами эмбеддинги (пригодятся для RAG)
    np.save(f'{output_dir}/embeddings.npy', embeddings)
    
    print("Index saved to output/")

if __name__ == "__main__":
    build_index('output')