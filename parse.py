import os


def parse_pdfs(pdf_dir: str, output_file: str):
    """Собирает combined.md из готовых Markdown-файлов (без парсинга PDF).

    Вариант 1 (рекомендуемый, так как marker-pdf не используется):
    положите тексты, полученные из DeepSeek, в директорию 'parsed/' — по одному
    .md-файлу на документ. Имена файлов должны совпадать с именами PDF
    (например, parsed/Reglament-o-rezhime-obuchayushchikhsya-po-OP.md).
    Скрипт склеит их в output/combined.md в формате '=== имя.pdf' + текст,
    который понимает build_index.py.

    Если в директории 'parsed/' нет файлов, а pdfs/ содержит PDF и установлен
    marker-pdf — скрипт попытается распарсить PDF автоматически.
    """

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    parsed_dir = "parsed/"

    md_files = []
    if os.path.isdir(parsed_dir):
        md_files = sorted(f for f in os.listdir(parsed_dir)
                          if f.lower().endswith(('.md', '.txt')))

    processed = 0
    with open(output_file, 'w', encoding='utf-8') as output:
        if md_files:
            print(f"Склеиваю {len(md_files)} готовых markdown-файлов из '{parsed_dir}'...")
            for md_file in md_files:
                full_path = os.path.join(parsed_dir, md_file)
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                if not content:
                    print(f"  ⚠ {md_file}: пустой файл, пропускаю")
                    continue
                # Имя документа: убираем расширение .md/.txt, добавляем .pdf,
                # чтобы источники в RAG выглядели как оригинальные PDF
                doc_name = os.path.splitext(md_file)[0]
                if not doc_name.lower().endswith('.pdf'):
                    doc_name += '.pdf'
                output.write(f'=== {doc_name}\n\n{content}\n\n')
                processed += 1
                print(f"  ✓ {md_file} ({len(content)} символов)")
        else:
            print(f"В директории '{parsed_dir}' нет .md/.txt файлов.")
            print("Попробую распарсить PDF через marker-pdf...")
            try:
                from marker.converters.pdf import PdfConverter
                from marker.models import create_model_dict
            except ImportError:
                print("✗ marker-pdf не установлен. Положите готовые markdown-файлы "
                      "в директорию 'parsed/' и запустите скрипт снова.")
                return

            converter = PdfConverter(artifact_dict=create_model_dict())
            pdf_files = [f for f in os.listdir(pdf_dir)
                         if f.lower().endswith('.pdf')]
            print(f"Конвертирую {len(pdf_files)} PDF файлов...")
            for pdf_file in pdf_files:
                full_path = os.path.join(pdf_dir, pdf_file)
                try:
                    rendered = converter(full_path)
                    # marker-pdf возвращает объект DocumentWithImages, текст — в .markdown
                    md_content = getattr(rendered, 'markdown', str(rendered))
                    output.write(f'=== {pdf_file}\n\n{md_content}\n\n')
                    processed += 1
                    print(f"  ✓ {pdf_file}")
                except Exception as e:
                    print(f"  ✗ {pdf_file}: {e}")
                    continue

    print(f"\nГотово! Обработано {processed} документов → {output_file}")


if __name__ == "__main__":
    parse_pdfs('pdfs/', 'output/combined.md')