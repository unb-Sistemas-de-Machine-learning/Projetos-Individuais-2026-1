import torch
import torch.nn.functional as F
from torch.amp import autocast
from sklearn.metrics import accuracy_score, precision_score
import numpy as np
import mlflow


def evaluate_model(model, val_loader, device):
    """
    Avalia o modelo no conjunto de validação.
    
    Args:
        model: Modelo a ser avaliado
        val_loader: DataLoader de validação
        device: Dispositivo
        
    Returns:
        Dicionário com y_true, y_pred e confidences
    """
    model.eval()
    y_true = []
    y_pred = []
    confidences = []

    with torch.no_grad():
        for imgs, lbls in val_loader:
            imgs = imgs.to(device)
            
            with autocast(device_type=device.type):
                outputs = model(imgs)
            
            probabilities = F.softmax(outputs, dim=1)
            confs, preds = torch.max(probabilities, 1)
            
            y_true.extend(lbls.cpu().numpy())
            y_pred.extend(preds.cpu().numpy())
            confidences.extend(confs.cpu().numpy())

    return {
        'y_true': np.array(y_true),
        'y_pred': np.array(y_pred),
        'confidences': np.array(confidences)
    }


def calculate_metrics(y_true, y_pred, confidences):
    """
    Calcula métricas de avaliação.
    
    Args:
        y_true: Labels verdadeiros
        y_pred: Predições do modelo
        confidences: Confiança das predições
        
    Returns:
        Dicionário com métricas calculadas
    """
    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, average='macro')
    mean_confidence = np.mean(confidences)

    return {
        'accuracy': accuracy,
        'precision': precision,
        'mean_confidence': mean_confidence
    }


def log_evaluation_metrics(metrics):
    """
    Registra as métricas de avaliação no MLflow.
    
    Args:
        metrics: Dicionário com métricas
    """
    mlflow.log_metric("accuracy", metrics['accuracy'])
    mlflow.log_metric("precision", metrics['precision'])
    mlflow.log_metric("mean_confidence", metrics['mean_confidence'])


def print_evaluation_results(metrics):
    """
    Imprime os resultados da avaliação.
    
    Args:
        metrics: Dicionário com métricas
    """
    print(f"Avaliação concluída:")
    print(f"  Acurácia: {metrics['accuracy']:.4f}")
    print(f"  Precisão (macro): {metrics['precision']:.4f}")
    print(f"  Confiança média: {metrics['mean_confidence']:.4f}")


if __name__ == "__main__":
    print("Módulo de avaliação carregado com sucesso!")
