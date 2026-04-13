import os


class SkinCancerDataset:
    def __init__(self, data_dir="data/raw"):
        self.data_dir = data_dir
        self.images = os.listdir(data_dir)

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        image_path = os.path.join(self.data_dir, self.images[idx])
        return image_path
