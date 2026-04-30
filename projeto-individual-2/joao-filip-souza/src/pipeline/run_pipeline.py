import mlflow
import mlflow.pytorch

# Importações do pipeline (em ordem numérica de execução)
from src.data.ingestion import download_cifar10
from src.data.preprocessing import preprocess_cifar10, split_train_val, create_data_loaders
from src.model.model_loading import load_resnet18, adapt_model_for_task, freeze_layers, get_model_size_info
from src.model.training import train_model
from src.model.evaluation import evaluate_model, calculate_metrics, log_evaluation_metrics, print_evaluation_results
from src.model.model_registry import (
    register_model_to_registry,
    compare_and_promote_model,
    print_registry_summary
)
from src.guardrails.validation import validar_imagem, validar_confianca

def run_pipeline():
    """
    Executa o pipeline completo: ingestão, preprocessamento, carregamento do modelo, 
    treinamento, avaliação e logging com MLflow.
    
    A pipeline segue a seguinte ordem:
    1. Ingestão: Baixa o dataset CIFAR-10
    2. Preprocessamento: Filtra classes de animais e divide em treino/validação
    3. Carregamento do Modelo: Carrega ResNet18 pré-treinado
    4. Treinamento: Fine-tuning do modelo
    5. Avaliação: Avalia o modelo nos dados de validação
    """
    # Caminhos
    DATA_RAW = "../data/raw/"
    DATA_PROCESSED = "../data/processed/"

    # Configurar MLflow
    mlflow.set_experiment("CIFAR-10 Animal Classification")

    with mlflow.start_run():
        # Log de parâmetros iniciais
        mlflow.log_param("dataset", "CIFAR-10")
        mlflow.log_param("model", "ResNet18")
        mlflow.log_param("classes", "bird, cat, deer, dog, frog, horse")
        mlflow.log_param("train_val_split", "0.7/0.3")
        mlflow.log_param("seed", 42)
        mlflow.set_tag("tipo", "treino")

      
        print("\n[1/5] Iniciando ingestão de dados...")
        download_cifar10(DATA_RAW)
        print("✓ Ingestão concluída.")

   
        print("\n[2/5] Iniciando preprocessamento...")
        filtered_data = preprocess_cifar10(DATA_RAW, DATA_PROCESSED)
        mlflow.log_param("filtered_classes", 6)
        mlflow.log_param("filtered_samples", len(filtered_data))
        print(f"✓ Preprocessamento concluído. {len(filtered_data)} imagens filtradas.")

        # Divisão 70/30 (agora no preprocessing)
        print("\n[2.1/5] Dividindo dataset em treino (70%) e validação (30%)...")
        train_dataset, val_dataset = split_train_val(filtered_data, train_ratio=0.7, seed=42)
        mlflow.log_param("train_samples", len(train_dataset))
        mlflow.log_param("val_samples", len(val_dataset))
        print(f"✓ Divisão concluída. Treino: {len(train_dataset)}, Validação: {len(val_dataset)}")

        # Criar DataLoaders
        print("\n[2.2/5] Criando DataLoaders...")
        train_loader, val_loader = create_data_loaders(train_dataset, val_dataset)
        print(f"✓ DataLoaders criados.")

        print("\n[3/5] Carregando modelo...")
        model = load_resnet18()
        model = adapt_model_for_task(model, num_classes=6)
        model = freeze_layers(model)
        print("✓ Modelo carregado e adaptado.")

        print("\n[3.1/5] Coletando informações do modelo...")
        model_info = get_model_size_info(model)
        print(f"Total de parâmetros: {model_info['total_params']:,}")
        print(f"Parâmetros treináveis: {model_info['trainable_params']:,}")
        print(f"Tamanho estimado: {model_info['model_size_mb']:.2f} MB")
        mlflow.log_metric("total_params", model_info['total_params'])
        mlflow.log_metric("trainable_params", model_info['trainable_params'])
        mlflow.log_metric("model_size_mb", model_info['model_size_mb'])

        print("\n[4/5] Iniciando treinamento...")
        model, device = train_model(model, train_loader, epochs=5)
        mlflow.log_param("device", str(device))
        print("Treinamento concluído.")

        print("\n[5/5] Avaliando modelo...")
        eval_results = evaluate_model(model, val_loader, device)
        metrics = calculate_metrics(
            eval_results['y_true'], 
            eval_results['y_pred'], 
            eval_results['confidences']
        )
        
        log_evaluation_metrics(metrics)
        print_evaluation_results(metrics)
        print("Avaliação concluída.")

        
        print("\n[6/5] Registrando modelo no MLflow Model Registry...")
        
        # Salvar o modelo como artifact
        model_info = mlflow.pytorch.log_model(
            model, 
            name="model"
        )
        
        # Construir URI do modelo
        run_id = mlflow.active_run().info.run_id
        model_uri = f"runs:/{run_id}/model"
        
        # Registrar no Model Registry
        MODEL_NAME = "CIFAR10-AnimalClassifier"
        new_version = register_model_to_registry(
            model_name=MODEL_NAME,
            model_uri=model_uri,
            metrics=metrics
        )
        
        # Comparar com versão anterior e promover se for melhor
        was_promoted, promotion_message = compare_and_promote_model(
            model_name=MODEL_NAME,
            new_version=new_version,
            new_metrics=metrics,
            promotion_metric='accuracy'
        )
        
        if was_promoted:
            print(f"\n{promotion_message}")
            mlflow.set_tag("model_status", "promoted")
        else:
            print(f"\n{promotion_message}")
            mlflow.set_tag("model_status", "archived")
        
        # Imprimir resumo do registry
        print_registry_summary(MODEL_NAME)
        print("Modelo registrado e comparado no MLflow Model Registry.")
        
   
        print("\nPIPELINE EXECUTADO COM SUCESSO!")
      

if __name__ == "__main__":
    run_pipeline()
