# 🤖 MTUCI RAG-бот

Проект по ML - создание чат-бота для документов МТУСИ на основе RAG (Retrieval-Augmented Generation).

## Что реализовано за 3 недели практики:

### Неделя 1: Парсинг документов
- ✅ `parse.py` — конвертация PDF в Markdown через marker-pdf
- ✅ Обработка ~60 официальных документов университета
- ✅ Следила работа на Mac M5 с Apple Silicon

### Неделя 2: Векторный индекс
- ✅ `build_index.py` — разделение текста на чанки по заголовкам
- ✅ Эмбеддинги через multilingual-e5-base (поддержка русскоязычных документов)
- ✅ FAISS индекс для быстрого поиска

### Неделя 3: RAG и интерфейс
- ✅ `rag.py` — класс с поиском по контексту и генерацией ответов
- ✅ `app.py` — Streamlit веб-интерфейс
- ✅ Кэширование через `@st.cache_resource`

## Как запустить:

```bash
# 1. Активировать окружение
source .venv/bin/activate

# 2. Установить зависимости
pip install torch sentence-transformers faiss-cpu streamlit marker-pdf tqdm unstructured[pdf]

# 3. Парсить PDF в Markdown
python parse.py

# 4. Создать векторный индекс
python build_index.py

# 5. Запустить интерфейс
streamlit run app.py
```

## Архитектура:

```
pdfs/                          — исходные PDF документы
output/combined.md            — объединённый Markdown после парсинга
output/index.faiss            — FAISS векторный индекс
output/chunks.json            — сохранённые чанки
rag.py                        — класс RAGBot (search + generate)
app.py                        — Streamlit фронтенд
```

## Технологический стек:

- **marker-pdf** — парсинг PDF в Markdown (native Python)
- **sentence-transformers** — эмбеддинги (intfloat/multilingual-e5-base)
- **FAISS** — поиск по векторам (IndexFlatL2)
- **Streamlit** — веб-интерфейс

## Примечания:

- Для Mac M5 обязательно: `PYTORCH_ENABLE_MPS_FALLBACK=1`
- FAISS использует CPU версию (faiss-cpu), GPU на Apple Silicon пока экспериментальный
