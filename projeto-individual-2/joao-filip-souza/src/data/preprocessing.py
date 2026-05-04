import os
import torchvision.transforms as transforms
from torchvision import datasets
from torch.utils.data import Dataset, DataLoader
import torch


class FilteredCIFAR10(Dataset):
    """Dataset customizado que filtra apenas as classes de animais do CIFAR-10."""
    
    def __init__(self, root, transform=None, download=True, train=True):
        self.dataset = datasets.CIFAR10(root=root, download=download, train=train)
        self.transform = transform
        self.classes_animais = [2, 3, 4, 5, 6, 7]  # índices das classes
        self.label_map = {2: 0, 3: 1, 4: 2, 5: 3, 6: 4, 7: 5}
        # Filter indices
        self.indices = [i for i, (_, label) in enumerate(self.dataset) if label in self.classes_animais]

    def __len__(self):
        return len(self.indices)

    def __getitem__(self, idx):
        img, label = self.dataset[self.indices[idx]]
        if self.transform:
            img = self.transform(img)
        label = self.label_map[label]
        return img, label


def get_train_transform():
    """Retorna transformações para dados de treino."""
    return transforms.Compose([
        transforms.RandomResizedCrop(224, scale=(0.8, 1.0)),
        transforms.RandomHorizontalFlip(),
        transforms.ColorJitter(brightness=0.1, contrast=0.1, saturation=0.1, hue=0.1),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])


def get_val_transform():
    """Retorna transformações para dados de validação."""
    return transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])


def preprocess_cifar10(input_path: str, output_path: str, train=True):
    """
    Preprocessa o dataset CIFAR-10, filtrando apenas as classes de animais.
    
    Args:
        input_path: Caminho para dados brutos
        output_path: Caminho para salvar dados processados
        train: Se True, usa dados de treino; senão usa dados de validação
        
    Returns:
        Dataset filtrado com transformações aplicadas
    """
    transform = get_train_transform() if train else get_val_transform()
    filtered_dataset = FilteredCIFAR10(root=input_path, transform=transform, download=True, train=train)

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    return filtered_dataset


def split_train_val(dataset, train_ratio=0.7, seed=42):
    """
    Divide o dataset em conjuntos de treino e validação.
    
    Args:
        dataset: Dataset para ser dividido
        train_ratio: Proporção de dados para treino (padrão: 0.7)
        seed: Seed para reprodutibilidade
        
    Returns:
        Tupla (train_dataset, val_dataset)
    """
    train_size = int(train_ratio * len(dataset))
    val_size = len(dataset) - train_size
    
    train_dataset, val_dataset = torch.utils.data.random_split(
        dataset, 
        [train_size, val_size], 
        generator=torch.Generator().manual_seed(seed)
    )
    
    return train_dataset, val_dataset


def create_data_loaders(train_dataset, val_dataset, train_batch_size=128, val_batch_size=32, num_workers=4):
    """
    Cria DataLoaders para treino e validação.
    
    Args:
        train_dataset: Dataset de treino
        val_dataset: Dataset de validação
        train_batch_size: Tamanho do batch para treino
        val_batch_size: Tamanho do batch para validação
        num_workers: Número de workers para carregamento de dados
        
    Returns:
        Tupla (train_loader, val_loader)
    """
    train_loader = DataLoader(
        train_dataset, 
        batch_size=train_batch_size, 
        shuffle=True, 
        num_workers=num_workers, 
        persistent_workers=True, 
        prefetch_factor=2
    )
    
    val_loader = DataLoader(
        val_dataset, 
        batch_size=val_batch_size, 
        shuffle=False, 
        num_workers=num_workers // 2
    )
    
    return train_loader, val_loader


if __name__ == "__main__":
    INPUT_PATH = "../../data/raw/"
    OUTPUT_PATH = "../../data/processed/"
    filtered_data = preprocess_cifar10(INPUT_PATH, OUTPUT_PATH)
    print(f"Total de imagens filtradas: {len(filtered_data)}")
