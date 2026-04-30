import torch
import torch.nn.functional as F

def predict(model, image_tensor):
    """
    Faz inferência com o modelo em uma imagem tensor.
    Retorna a classe prevista e a probabilidade.
    """
    # Obter o dispositivo do modelo
    device = next(model.parameters()).device
    # Mover tensor para o mesmo dispositivo
    image_tensor = image_tensor.to(device)
    
    with torch.no_grad():
        outputs = model(image_tensor)
        probabilities = F.softmax(outputs, dim=1)
        confidence, predicted_class = torch.max(probabilities, 1)
        return predicted_class.item(), confidence.item()

if __name__ == "__main__":
    from load_model import load_resnet18
    model = load_resnet18()
    dummy_input = torch.randn(1, 3, 224, 224)
    pred_class, conf = predict(model, dummy_input)
    print(f"Classe prevista: {pred_class}, Confiança: {conf}")
