import argparse
import json
import sys
import time

import torch
import torch.nn.functional as F
import torchvision.transforms as transforms
from PIL import Image

import mlflow
import mlflow.pytorch


from src.model.predict import predict
from src.guardrails.validation import (
    validar_imagem,
    validar_confianca,
    validar_dominio
)

def load_model_from_registry(model_name: str, stage: str = "Production"):
    """
    Carrega modelo do MLflow Model Registry.
    
    Args:
        model_name: Nome do modelo no registry (ex: "CIFAR10-AnimalClassifier")
        stage: Stage do modelo (Production, Staging, Archived)
        
    Returns:
        Modelo carregado e em modo de avaliação
    """
    model_uri = f"models:/{model_name}/{stage}"
    
    print(f"Carregando modelo do Model Registry...")
    print(f"  Nome: {model_name}")
    print(f"  Stage: {stage}")
    print(f"  URI: {model_uri}")
    
    try:
        model = mlflow.pytorch.load_model(model_uri)
        model.eval()
        print(f"Modelo carregado com sucesso!")
        return model
    except Exception as e:
        raise ValueError(f"Erro ao carregar modelo: {e}")


def get_available_stages(model_name: str):
    """
    Lista as versões e stages disponíveis do modelo.
    
    Args:
        model_name: Nome do modelo
        
    Returns:
        Dicionário com informações das versões
    """
    try:
        client = mlflow.tracking.MlflowClient()
        versions = client.search_model_versions(f"name = '{model_name}'")
        
        print(f"\nVersões disponíveis do modelo '{model_name}':")
        
        versions_info = {}
        for version in sorted(versions, key=lambda v: int(v.version), reverse=True):
            stage = version.current_stage
            run = client.get_run(version.run_id)
            accuracy = run.data.metrics.get('accuracy', 'N/A')
            
    
            
            print(f" v{version.version} [{stage}]")
            print(f"   Acurácia: {accuracy if isinstance(accuracy, str) else f'{accuracy:.4f}'}")
            
            versions_info[stage] = {
                'version': version.version,
                'accuracy': accuracy
            }
        
        return versions_info
        
    except Exception as e:
        print(f"Erro ao buscar versões: {e}")
        return {}

def main():
    parser = argparse.ArgumentParser(description="Inferência com MLflow Model Registry + Tracing")
    parser.add_argument(
        "--model_name",
        type=str,
        default="CIFAR10-AnimalClassifier",
        help="Nome do modelo no Model Registry"
    )
    parser.add_argument(
        "--stage",
        type=str,
        default="Production",
        choices=["Production", "Staging", "Archived"],
        help="Stage do modelo a usar"
    )
    parser.add_argument(
        "--list_versions",
        action="store_true",
        help="Listar versões disponíveis e sair"
    )
    parser.add_argument(
        "--input_tensor",
        type=str,
        required=not "--list_versions" in sys.argv,
        help="Caminho para tensor salvo ou 'random'"
    )
    args = parser.parse_args()

    if args.list_versions:
        get_available_stages(args.model_name)
        return

    mlflow.set_experiment("CIFAR-10 Animal Classification")

    with mlflow.start_run():

        mlflow.set_tag("tipo", "inferencia")
        mlflow.log_param("model_name", args.model_name)
        mlflow.log_param("model_stage", args.stage)

        with mlflow.start_span("pipeline"):

            with mlflow.start_span("load_model") as span:
                print("Carregando modelo do MLflow Model Registry...")
                model = load_model_from_registry(args.model_name, args.stage)
                
                device = next(model.parameters()).device
                mlflow.log_param("device", str(device))
                span.set_attribute("device", str(device))

            with mlflow.start_span("preprocessamento") as span:

                if args.input_tensor == "random":
                    print("Gerando tensor aleatório...")
                    img = torch.randn(1, 3, 224, 224) * 0.1 + 0.5
                    span.set_attribute("input_type", "random")

                elif args.input_tensor.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                    print(f"Carregando imagem: {args.input_tensor}")
                    image = Image.open(args.input_tensor).convert('RGB')

                    transform = transforms.Compose([
                        transforms.Resize((224, 224)),
                        transforms.ToTensor(),
                        transforms.Normalize(
                            mean=[0.485, 0.456, 0.406],
                            std=[0.229, 0.224, 0.225]
                        )
                    ])

                    img = transform(image).unsqueeze(0)
                    span.set_attribute("input_type", "image_file")

                else:
                    print(f"Carregando tensor salvo: {args.input_tensor}")
                    img = torch.load(args.input_tensor)
                    span.set_attribute("input_type", "tensor_file")

                span.set_attribute("batch_size", int(img.shape[0]))

            with mlflow.start_span("validacao"):
                try:
                    validar_imagem(img)
                    print("Imagem válida.")
                except ValueError as e:
                    print(f"Erro de validação: {e}")
                    raise

            with mlflow.start_span("inferencia") as span:

                start = time.time()

                pred_class, conf = predict(model, img)

                latency = time.time() - start

                mlflow.log_metric("latency_ms", latency * 1000)
                span.set_attribute("confidence", float(conf))
                span.set_attribute("predicted_class", int(pred_class))
                span.set_attribute("latency_ms", float(latency * 1000))


            with mlflow.start_span("debug_probabilidades"):
                classes = ['bird', 'cat', 'deer', 'dog', 'frog', 'horse']

                with torch.no_grad():
                    outputs = model(img.to(next(model.parameters()).device))
                    probabilities = F.softmax(outputs, dim=1)
                    probs_list = probabilities[0].cpu().numpy()

                    print("\nProbabilidades por classe:")
                    for cls, prob in zip(classes, probs_list):
                        print(f"  {cls:8s}: {prob:.4f}")
                    print()
                    
                    # Log das probabilidades
                    for cls, prob in zip(classes, probs_list):
                        mlflow.log_metric(f"prob_{cls}", float(prob))
                    

            with mlflow.start_span("posprocessamento") as span:

                status_conf = validar_confianca(conf)
                status_dom = validar_dominio(pred_class)

                if status_conf == "incerto":
                    resultado = {
                        "classe": "desconhecida",
                        "warning": "Baixa confiança",
                        "confidence": float(conf)
                    }
                elif status_dom == "fora_do_dominio":
                    resultado = {
                        "classe": classes[pred_class],
                        "warning": "Classe fora do domínio esperado",
                        "confidence": float(conf)
                    }
                else:
                    resultado = {
                        "classe": classes[pred_class],
                        "confidence": float(conf)
                    }

                mlflow.log_param("resultado_classe", resultado.get("classe", "desconhecida"))
                mlflow.log_metric("resultado_confidence", float(conf))
                
                span.set_attribute("quality.score", float(conf))
                span.set_attribute("quality.label", "alta" if conf > 0.8 else "baixa")
                span.set_attribute("quality.status", status_conf)
                span.set_attribute("quality.domain", status_dom)

            print("RESULTADO DA INFERÊNCIA")
            print(json.dumps(resultado, indent=2))


if __name__ == "__main__":
    main()