import torch
import torch.nn as nn
import torchvision.models as models


def load_resnet18():
    """
    Carrega o modelo ResNet18 pré-treinado do ImageNet.
    
    Returns:
        Modelo ResNet18 em modo de avaliação
    """
    model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
    model.eval()  # Modo de avaliação
    return model


def adapt_model_for_task(model, num_classes=6):
    """
    Adapta o modelo ResNet18 para a tarefa específica (classificação de 6 classes de animais).
    
    Args:
        model: Modelo pré-treinado
        num_classes: Número de classes da tarefa
        
    Returns:
        Modelo adaptado
    """
    # Substituir a última camada fully connected
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    return model


def freeze_layers(model, freeze_until_layer='layer4'):
    """
    Congela as camadas do modelo até a camada especificada para transfer learning.
    
    Args:
        model: Modelo a ser congelado
        freeze_until_layer: Nome da última camada a congelar (ex: 'layer4')
        
    Returns:
        Modelo com camadas congeladas
    """
    for name, param in model.named_parameters():
        if freeze_until_layer in name or 'fc' in name:
            param.requires_grad = True
        else:
            param.requires_grad = False
    
    return model


def get_trainable_parameters(model):
    """
    Retorna apenas os parâmetros treináveis do modelo.
    
    Args:
        model: Modelo
        
    Returns:
        Gerador de parâmetros treináveis
    """
    return filter(lambda p: p.requires_grad, model.parameters())


def get_model_size_info(model):
    """
    Calcula informações sobre tamanho e memória do modelo.
    
    Args:
        model: Modelo
        
    Returns:
        Dicionário com total_params, trainable_params e model_size_mb
    """
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    
    # Memória estimada (assumindo float32 = 4 bytes)
    param_size_bytes = total_params * 4
    param_size_mb = param_size_bytes / (1024 ** 2)
    
    return {
        'total_params': total_params,
        'trainable_params': trainable_params,
        'model_size_mb': param_size_mb
    }


if __name__ == "__main__":
    model = load_resnet18()
    model = adapt_model_for_task(model, num_classes=6)
    model = freeze_layers(model)
    
    info = get_model_size_info(model)
    print(f"Total de parâmetros: {info['total_params']:,}")
    print(f"Parâmetros treináveis: {info['trainable_params']:,}")
    print(f"Tamanho estimado: {info['model_size_mb']:.2f} MB")
