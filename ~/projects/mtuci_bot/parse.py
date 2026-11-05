import os
import sys
from tqdm import tqdm
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict

os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

def parse_pdfs(pdf_dir: str, output_file: str):
    """Parse all PDFs in directory to markdown."""
    # Создаем словарь с моделями (это обязательно для PdfConverter)
    converter = PdfConverter(
        artifact_dict=create_model_dict(),
    )

    total_files = len([f for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf')])
    processed = 0

    print(f"Parsing {total_files} PDFs...")
    for pdf_file in tqdm(os.listdir(pdf_dir), desc="Parsing PDF", total=total_files):
        if not pdf_file.lower().endswith('.pdf'):
            continue

        try:
            # Конвертер вызывается как функция, а не через .convert()
            rendered = converter(pdf_file)
            
            # Извлекаем текст из результата
            text = rendered.markdown

            # Write to output
            with open(f'{output_file}.md', 'a', encoding='utf-8') as f:
                f.write(f'=== {pdf_file}\n')
                f.write(text)

            processed += 1
            print(f"{pdf_file}: {len(text)} tokens")

        except Exception as e:
            print(f"{pdf_file}: Error — {e}, skipping")
            continue

    print(f"\nProcessed {processed}/{total_files} PDFs")

if __name__ == "__main__":
    parse_pdfs('pdfs/', 'output/combined')