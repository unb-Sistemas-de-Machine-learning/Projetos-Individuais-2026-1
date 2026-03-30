from pathlib import Path
from dotenv import load_dotenv
from pipeline import run_pipeline
from pdf_reader import extract_text_from_pdf

def run_tests():
    load_dotenv()

    pdf_folder = Path("data/pdfs")
    output_file = Path("resultados/resultados-testes.md")

    if not pdf_folder.exists():
        raise FileNotFoundError("A pasta data/pdfs não foi encontrada.")

    pdf_files = list(pdf_folder.glob("*.pdf"))

    if not pdf_files:
        raise ValueError("Nenhum PDF encontrado em data/pdfs.")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# Resultados dos Testes com PDFs\n\n")

        for i, pdf_file in enumerate(pdf_files, start=1):
            try:
                pdf_text = extract_text_from_pdf(str(pdf_file))
                result = run_pipeline(pdf_text)

                f.write(f"## Teste {i} - {pdf_file.name}\n\n")
                f.write("### Arquivo\n")
                f.write(f"{pdf_file}\n\n")
                f.write("### Saída do agente\n")
                f.write(result + "\n\n")
                f.write("---\n\n")

            except Exception as e:
                f.write(f"## Teste {i} - {pdf_file.name}\n\n")
                f.write(f"Erro ao processar o arquivo: {e}\n\n")
                f.write("---\n\n")

    print("Testes finalizados. Resultado salvo em resultados/resultados-testes.md")

if __name__ == "__main__":
    run_tests()