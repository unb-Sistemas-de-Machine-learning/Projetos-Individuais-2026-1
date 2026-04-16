import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import mlflow
from tqdm import tqdm
from torch.amp import autocast, GradScaler
from torch.optim.lr_scheduler import StepLR


def select_device():
    """
    Seleciona o dispositivo (GPU/MPS/CPU) disponível.
    
    Returns:
        torch.device: Dispositivo selecionado
    """
    if torch.backends.mps.is_available():
        device = torch.device("mps")
    elif torch.cuda.is_available():
        device = torch.device("cuda")
    else:
        device = torch.device("cpu")
    
    print(f"Usando dispositivo: {device}")
    return device


def setup_training(model, device, learning_rate=1e-4):
    """
    Configura o modelo, otimizador, criterion e scheduler para treinamento.
    
    Args:
        model: Modelo a ser treinado
        device: Dispositivo (CPU/GPU/MPS)
        learning_rate: Taxa de aprendizagem
        
    Returns:
        Tupla (optimizer, criterion, scheduler, scaler)
    """
    model = model.to(device)
    
    # Otimizador e loss
    optimizer = optim.Adam(
        filter(lambda p: p.requires_grad, model.parameters()), 
        lr=learning_rate
    )
    criterion = nn.CrossEntropyLoss()
    scheduler = StepLR(optimizer, step_size=3, gamma=0.1)
    
    # GradScaler para mixed precision (apenas para CUDA)
    scaler = GradScaler() if device.type == 'cuda' else None
    
    return optimizer, criterion, scheduler, scaler


def train_epoch(model, train_loader, optimizer, criterion, scaler, device):
    """
    Treina um epoch.
    
    Args:
        model: Modelo a ser treinado
        train_loader: DataLoader de treino
        optimizer: Otimizador
        criterion: Função de loss
        scaler: GradScaler para mixed precision
        device: Dispositivo
        
    Returns:
        Perda média do epoch
    """
    model.train()
    running_loss = 0.0
    progress_bar = tqdm(train_loader, desc="Training", unit="batch")
    
    for imgs, lbls in progress_bar:
        imgs, lbls = imgs.to(device), lbls.to(device)
        optimizer.zero_grad()
        
        # Mixed precision
        with autocast(device_type=device.type):
            outputs = model(imgs)
            loss = criterion(outputs, lbls)
        
        if scaler:
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
        else:
            loss.backward()
            optimizer.step()
        
        running_loss += loss.item()
        progress_bar.set_postfix(loss=f"{loss.item():.4f}")
    
    avg_loss = running_loss / len(train_loader)
    return avg_loss


def train_model(model, train_loader, epochs=2, learning_rate=1e-4):
    """
    Realiza fine-tuning do modelo com transfer learning.
    
    Args:
        model: Modelo pré-treinado
        train_loader: DataLoader de treino
        epochs: Número de epochs
        learning_rate: Taxa de aprendizagem
        
    Returns:
        Tupla (modelo treinado, dispositivo usado)
    """
    print("Iniciando fine-tuning...")
    
    # Selecionar dispositivo e preparar treinamento
    device = select_device()
    optimizer, criterion, scheduler, scaler = setup_training(model, device, learning_rate)
    
    # Treinamento
    for epoch in range(epochs):
        avg_loss = train_epoch(model, train_loader, optimizer, criterion, scaler, device)
        scheduler.step()
        
        mlflow.log_metric(f"train_loss_epoch_{epoch+1}", avg_loss)
        print(f"Epoch {epoch+1}/{epochs}, Loss: {avg_loss:.4f}")
    
    print("Fine-tuning concluído.")
    return model, device
