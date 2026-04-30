import os
import sys

# Importando as funções dos seus outros arquivos
# Nota: Certifique-se de que o nome dos arquivos esteja correto (sem .py)
from extração import baixar_amostras_isic
from pipeline import executar_pipeline

def main():
    print("==================================================")
    print("🚀 INICIANDO SISTEMA DE ML: CÂNCER DE PELE")
    print("==================================================")
    
    # PASSO 1: INGESTÃO DE DADOS
    print("\n[Etapa 1/2] Verificando/Baixando base de dados...")
    
    # Uma boa prática: só baixar se a pasta não existir ou estiver vazia
    pasta_melanoma = "dados/maligno"
    pasta_nevus = "dados/benigno"
    if (not os.path.exists(pasta_melanoma) or len(os.listdir(pasta_melanoma)) < 25) and (not os.path.exists(pasta_nevus) or len(os.listdir(pasta_nevus)) < 25):
        baixar_amostras_isic()
    else:
        print("✅ Dados já encontrados localmente. Pulando extração para economizar tempo e rede.")

    # PASSO 2: PIPELINE E MLFLOW
    print("\n[Etapa 2/2] Executando o Pipeline (Avaliação e Registro no MLflow)...")
    try:
        executar_pipeline()
    except Exception as e:
        print(f"❌ Erro ao executar o pipeline: {e}")
        sys.exit(1)

    print("\n==================================================")
    print("✅ EXECUÇÃO FINALIZADA COM SUCESSO!")
    print("==================================================")
    print("Próximos passos:")
    print("1. Abra um terminal e digite 'mlflow ui' para ver os resultados.")
    print("2. Teste o modelo rodando: python codigo/inferência.py dados/maligno/maligno_0.png")

if __name__ == "__main__":
    main()