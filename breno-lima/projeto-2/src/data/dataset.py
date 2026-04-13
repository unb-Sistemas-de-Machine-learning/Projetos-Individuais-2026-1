import os
import random


class SkinCancerDataset:
    def __init__(self, data_dir="data/raw", seed=42):
        self.data_dir = data_dir
        all_images = [
            f for f in os.listdir(data_dir)
            if f.lower().endswith((".jpg", ".jpeg", ".png"))
        ]

        random.seed(seed)
        random.shuffle(all_images)

        n = len(all_images)
        train_end = int(n * 0.70)
        val_end = int(n * 0.85)

        self.train = all_images[:train_end]
        self.val = all_images[train_end:val_end]
        self.test = all_images[val_end:]

    def _full_paths(self, subset):
        return [os.path.join(self.data_dir, f) for f in subset]

    def get_split(self, split: str):
        splits = {"train": self.train, "val": self.val, "test": self.test}
        if split not in splits:
            raise ValueError(f"Split inválido: '{split}'. Use 'train', 'val' ou 'test'.")
        return self._full_paths(splits[split])

    def split_sizes(self):
        return {"train": len(self.train), "val": len(self.val), "test": len(self.test)}

    def __len__(self):
        return len(self.train) + len(self.val) + len(self.test)

    def __getitem__(self, idx):
        all_images = self.train + self.val + self.test
        return os.path.join(self.data_dir, all_images[idx])
