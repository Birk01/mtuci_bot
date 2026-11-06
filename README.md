# 🤖 MTUCI RAG-бот

Проект по ML - создание чат-бота для документов МТУСИ на основе RAG (Retrieval-Augmented Generation).

## Что реализовано за 3 недели практики:

### Неделя 1: Парсинг документов
- ✅ `parse.py` — сборка Markdown-корпуса: тексты получены через чат DeepSeek (скидывал PDF → получал текст), затем склеены в `output/combined.md`. Маркер-парсер (`marker-pdf`) оставлен как запасной вариант, так как парсит слишком медленно
- ✅ Обработка ~60 официальных документов университета

### Неделя 2: Векторный индекс
- ✅ `build_index.py` — разделение текста на чанки по заголовкам
- ✅ Эмбеддинги через multilingual-e5-base (поддержка русскоязычных документов)
- ✅ FAISS индекс для быстрого поиска

### Неделя 3: RAG и интерфейс
- ✅ `rag.py` — класс с поиском по контексту и генерацией ответов
- ✅ `app.py` — Streamlit веб-интерфейс
- ✅ Кэширование через `@st.cache_resource`

## 🚀 Как запустить (пошагово)

### Шаг 0. Окружение (один раз)

⚠️ ВАЖНО: в проекте есть папки `venv/` и `.venv/` — обе занесены в `.gitignore`,
то есть после клона репозитория их НЕТ, виртуальное окружение нужно создать заново:

```bash
python -m venv .venv

# активация:
source .venv/bin/activate        # Linux / macOS
.venv\Scripts\activate           # Windows (cmd)
.venv\Scripts\Activate.ps1       # Windows (PowerShell)
```

Установка зависимостей:

```bash
pip install -r requirements.txt
```

Если нужен CUDA (ускорение эмбеддингов на видеокарте NVIDIA), сначала поставьте torch с нужной сборкой, например для CUDA 12.1:

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt   # остальное; torch уже будет установлен
```

`marker-pdf` из requirements нужен только для автоматического парсинга PDF (запасной вариант). Если тексты уже готовы (DeepSeek), его можно не ставить.

### Шаг 1. Подготовка текстов документов

Рабочий процесс: PDF скидывались в чат DeepSeek → получался текст → каждый документ сохранялся как отдельный файл в `parsed/`.

Формат: один файл = один документ, имя файла = имя документа (например `Reglament-o-rezhime-obuchayushchikhsya-po-OP.md`). Поддерживаются `.md` и `.txt`.

⚠️ Сейчас папка `parsed/` пустая — тексты из DeepSeek нужно заново разложить туда по файлам (в текущем `output/combined.md` только заголовки без текста). Если хотите пропустить ручной перенос, можно склеить все полученные тексты в один `output/combined.md` вручную — формат секций: `=== ИмяДокумента.pdf`, пустая строка, текст.

Сборка единого корпуса:

```bash
python parse.py
```

Результат: `output/combined.md` (секции вида `=== ИмяДокумента.pdf` + текст). Перезапускается начисто — дублей не будет.

### Шаг 2. Построение векторного индекса

```bash
python build_index.py
```

При первом запуске скачается модель эмбеддингов `intfloat/multilingual-e5-base` (~1 ГБ, нужен интернет). Результат: `output/index.faiss` и `output/chunks.json`.

### Шаг 3. Запуск бота

Веб-интерфейс (Streamlit):

```bash
streamlit run app.py
```

Откроется в браузере по адресу `http://localhost:8501`.

Или проверка поиска прямо в консоли:

```bash
python rag.py    # загрузит индекс и покажет пример запроса bot.ask('...')
```

### Частые проблемы

| Симптом | Решение |
|---|---|
| `ModuleNotFoundError: No module named 'faiss'` (или streamlit и т.п.) | Не активировано окружение: выполните `source .venv/bin/activate`, затем `pip install -r requirements.txt` |
| `FileNotFoundError: Сначала создайте индекс через build_index.py` | Не выполнен Шаг 2 (или нет `output/index.faiss`) |
| Бот запускается, но отвечает пусто / не находит источники | `output/combined.md` пуст или без текста — проверьте файлы в `parsed/` и перегоните Шаги 1–2 |
| Долгое скачивание модели при `build_index.py` | Это нормально при первом запуске (~1 ГБ); дальше берётся из кэша `~/.cache/huggingface` |
| Нет интернета / модель не качается | Скачайте `intfloat/multilingual-e5-base` заранее и укажите локальный путь в аргументе `embedding_model` класса `IndexBuilder` (build_index.py) и `RAGBot` (rag.py) |

## Архитектура:

```
pdfs/                          — исходные PDF документы
parsed/                        — готовые markdown-тексты (из DeepSeek), по файлу на документ
output/combined.md            — объединённый Markdown-корпус
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
