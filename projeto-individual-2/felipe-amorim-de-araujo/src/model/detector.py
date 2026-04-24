# src/model/detector.py
from pathlib import Path

import torch
from PIL import Image
from torchvision.ops import nms
from transformers import YolosForObjectDetection, YolosImageProcessor

MODEL_NAME = "hustvl/yolos-small"


class SpaceDetector:
    """
    Wraps YOLOS-small for object detection on astronomical images.

    Base (COCO-pretrained) model: labels are stripped, used as a generic blob detector.
    Fine-tuned model: includes "label" key (star / galaxy / quasar) in each detection.
    """

    def __init__(self, model_name: str = MODEL_NAME):
        self.model_name = str(model_name)
        self.processor = YolosImageProcessor.from_pretrained(model_name)
        self.model = YolosForObjectDetection.from_pretrained(model_name)
        self.model.eval()

        id2label = getattr(self.model.config, "id2label", {})
        self._include_labels = bool(id2label) and 0 in id2label and id2label[0] in ("star", "galaxy", "quasar")

    @classmethod
    def from_finetuned(cls, checkpoint_dir: str | Path) -> "SpaceDetector":
        """Load from a local fine-tuned checkpoint directory."""
        return cls(model_name=str(checkpoint_dir))

    def detect(
        self,
        img: Image.Image,
        confidence_threshold: float = 0.6,
        nms_iou_threshold: float = 0.5,
    ) -> list[dict]:
        """Run inference on a PIL RGB image. Returns list of {"box", "score"[, "label"]} dicts."""
        inputs = self.processor(images=img, return_tensors="pt")

        with torch.no_grad():
            outputs = self.model(**inputs)

        target_sizes = torch.tensor([img.size[::-1]])
        results = self.processor.post_process_object_detection(
            outputs,
            threshold=confidence_threshold,
            target_sizes=target_sizes,
        )[0]

        scores = results["scores"]
        labels = results["labels"]
        boxes = results["boxes"]

        if len(scores) > 0:
            kept = nms(boxes, scores, iou_threshold=nms_iou_threshold)
            scores, labels, boxes = scores[kept], labels[kept], boxes[kept]

        id2label = self.model.config.id2label
        detections = []
        for score, label, box in zip(scores, labels, boxes):
            det: dict = {
                "box": [round(v, 2) for v in box.tolist()],
                "score": round(score.item(), 4),
            }
            if self._include_labels:
                det["label"] = id2label[label.item()]
            detections.append(det)

        return detections
