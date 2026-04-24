import requests
import os
from tqdm import tqdm

BASE_URL = "https://api.isic-archive.com/api/v2"


class ISICClient:
    def __init__(self, output_dir="data/raw"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def list_images(self, limit=10):
        url = f"{BASE_URL}/images?limit={limit}"

        params = {"limit": limit}

        response = requests.get(url, params=params)
        response.raise_for_status()

        return response.json()["results"]

    def download_image(self, image_id, url):
        file_path = os.path.join(self.output_dir, f"{image_id}.jpg")

        if os.path.exists(file_path):
            return file_path

        response = requests.get(url)
        response.raise_for_status()

        with open(file_path, "wb") as f:
            f.write(response.content)

        return file_path

    def download_batch(self, limit=10):
        images = self.list_images(limit=limit)

        paths = []

        for image in tqdm(images):
            image_id = image["isic_id"]
            path = self.download_image(image_id, image["files"]["full"]["url"])
            paths.append(path)

        return paths
