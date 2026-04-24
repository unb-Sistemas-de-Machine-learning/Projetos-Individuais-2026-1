import os
from torchvision import datasets


def download_cifar10(data_path: str):
    """
    Baixa o dataset CIFAR-10 para o caminho especificado.
    
    Args:
        data_path: Caminho onde o dataset será armazenado
        
    Returns:
        Dataset CIFAR-10 baixado
    """
    if not os.path.exists(data_path):
        os.makedirs(data_path)
    dataset = datasets.CIFAR10(root=data_path, download=True)
    return dataset


if __name__ == "__main__":
    DATA_PATH = "../../data/raw/"
    download_cifar10(DATA_PATH)
    print("Dataset CIFAR-10 baixado com sucesso!")
