import os
import sys
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from tqdm import tqdm

os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"


def parse_pdfs(pdf_dir: str, output_file: str):
    """Парсит все PDF из директории в Markdown через marker-pdf."""


    converter = PdfConverter(
        artifact_dict=create_model_dict(),
    )
    total_files = len([f for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf')])
    
    print(f"Конвертирую {total_files} PDF файлов...")
    processed = 0
    
    with open(output_file, 'a', encoding='utf-8') as output:
        for pdf_file in tqdm(os.listdir(pdf_dir), desc="PDF файлы", total=total_files):
            if not pdf_file.lower().endswith('.pdf'):
                continue
            
            full_path = os.path.join(pdf_dir, pdf_file)
            
            try:
                rendered = converter(full_path)
                # marker-pdf возвращает объект DocumentWithImages, текст — в .markdown
                md_content = getattr(rendered, 'markdown', str(rendered))
                
                output.write(f'=== {pdf_file}\n\n')
                output.write(md_content[:3000])
                output.write('\n\n')
                
                processed += 1
                print(f"  ✓ {pdf_file}")
                
            except Exception as e:
                print(f"  ✗ {pdf_file}: {e}")
                continue
    
    print(f"\nГотово! Обработано {processed}/{total_files} файлов")


if __name__ == "__main__":
    parse_pdfs('pdfs/', 'output/combined.md')