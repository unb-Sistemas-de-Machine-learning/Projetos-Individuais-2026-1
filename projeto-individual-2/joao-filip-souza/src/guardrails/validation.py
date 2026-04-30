import torch
import numpy as np

def validar_imagem(img):
    """
    Valida se a imagem é válida para o modelo.
    """
    if img is None or not isinstance(img, torch.Tensor) or img.shape[0] != 1 or img.shape[1] != 3:
        raise ValueError("Imagem inválida: deve ser um tensor de shape (1, 3, H, W)")
    
    # Verificar se os valores estão no range esperado [0, 1] ou normalizados
    if img.min() < -3.0 or img.max() > 3.0:  # Aproximado para normalização ImageNet
        raise ValueError("Imagem com valores fora do range esperado. Use normalização adequada.")
    
    return True

def validar_confianca(prob):
    """
    Valida a confiança da predição.
    """
    if prob < 0.5:  # Threshold mais baixo para demonstração
        return "incerto"
    return "ok"

def validar_dominio(pred_class, classes_permitidas=[0, 1, 2, 3, 4, 5]):
    """
    Valida se a predição está dentro do domínio esperado (animais).
    Agora usa índices 0-5 para as classes de animais mapeadas.
    """
    if pred_class not in classes_permitidas:
        return "fora_do_dominio"
    return "ok"

def validar_entrada_usuario(entrada):
    """
    Valida entrada do usuário para evitar uso indevido.
    """
    if not isinstance(entrada, dict) or 'imagem' not in entrada:
        raise ValueError("Entrada deve ser um dicionário com chave 'imagem'")
    
    # Verificar se há tentativas de injeção ou dados maliciosos
    if len(str(entrada)) > 10000:  # Limite de tamanho
        raise ValueError("Entrada muito grande")
    
    return True
