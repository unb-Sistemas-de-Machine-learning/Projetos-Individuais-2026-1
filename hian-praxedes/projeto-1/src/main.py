from dotenv import load_dotenv
load_dotenv()

from pipeline import run_pipeline
from pdf_reader import extract_text_from_pdf

def main():
    print("=== Agente de Resumo de Materiais Didáticos ===")
    print("Informe o caminho de um arquivo PDF para resumir.\n")

    pdf_path = input("Caminho do PDF: ").strip()

    try:
        pdf_text = extract_text_from_pdf(pdf_path)
        result = run_pipeline(pdf_text)

        print("\n=== Resultado ===\n")
        print(result)

    except Exception as e:
        print(f"\nErro: {e}")

if __name__ == "__main__":
    main()