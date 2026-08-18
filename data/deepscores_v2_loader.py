# DeepScores v2 COCO-Format Loader & Bounding Box Visualizer
import os
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import torch
from torch.utils.data import Dataset
from typing import List, Tuple, Dict, Any, Optional


class DeepScoresV2COCODataset(Dataset):
    """
    COCO-format PyTorch Dataset loader for DeepScores v2 score object detection.
    Parses COCO JSON annotations (images, annotations, categories, bounding boxes).
    """
    DEFAULT_CATEGORIES = [
        {"id": 1, "name": "noteheadBlack", "supercategory": "symbol"},
        {"id": 2, "name": "noteheadHalf", "supercategory": "symbol"},
        {"id": 3, "name": "clefG", "supercategory": "clef"},
        {"id": 4, "name": "clefF", "supercategory": "clef"},
        {"id": 5, "name": "stem", "supercategory": "stem"},
        {"id": 6, "name": "beam", "supercategory": "beam"},
        {"id": 7, "name": "accidentalSharp", "supercategory": "accidental"},
        {"id": 8, "name": "accidentalFlat", "supercategory": "accidental"},
        {"id": 9, "name": "restQuarter", "supercategory": "rest"},
        {"id": 10, "name": "timeSig4_4", "supercategory": "timeSig"}
    ]

    def __init__(self, dataset_dir: str = "data/deepscores_v2", json_filename: str = "deepscores_v2_coco.json"):
        self.dataset_dir = dataset_dir
        self.json_path = os.path.join(dataset_dir, json_filename)
        
        os.makedirs(dataset_dir, exist_ok=True)
        if not os.path.exists(self.json_path):
            self._generate_sample_coco_dataset()

        self._load_coco_json()

    def _load_coco_json(self):
        print(f"[DEEPSCORES-V2] Loading COCO annotations from '{self.json_path}'...")
        with open(self.json_path, "r", encoding="utf-8") as f:
            self.coco_data = json.load(f)

        self.images_dict = {img["id"]: img for img in self.coco_data.get("images", [])}
        self.cat_dict = {cat["id"]: cat["name"] for cat in self.coco_data.get("categories", [])}

        # Group annotations by image_id
        self.img_to_anns: Dict[int, List[Dict[str, Any]]] = {}
        for ann in self.coco_data.get("annotations", []):
            img_id = ann["image_id"]
            if img_id not in self.img_to_anns:
                self.img_to_anns[img_id] = []
            self.img_to_anns[img_id].append(ann)

        self.image_ids = list(self.images_dict.keys())
        print(f"[SUCCESS] Loaded {len(self.image_ids)} images and {len(self.coco_data.get('annotations', []))} object bounding boxes across {len(self.cat_dict)} classes.")

    def _generate_sample_coco_dataset(self):
        print(f"[DEEPSCORES-V2] Generating sample DeepScores v2 COCO dataset in '{self.dataset_dir}'...")
        images = []
        annotations = []
        categories = self.DEFAULT_CATEGORIES

        ann_id = 1
        for img_id in range(1, 6):
            file_name = f"deepscores_page_{img_id:03d}.png"
            img_path = os.path.join(self.dataset_dir, file_name)
            w, h = 800, 600

            # Render score page image
            img = Image.new("L", (w, h), color=255)
            draw = ImageDraw.Draw(img)

            # Draw 4 staves (5 lines each)
            for staff_idx in range(4):
                base_y = 80 + staff_idx * 120
                for line_offset in [0, 12, 24, 36, 48]:
                    draw.line([(40, base_y + line_offset), (w - 40, base_y + line_offset)], fill=0, width=1)

                # Add sample COCO annotations (Clef, Stem, Notehead, Accidental, Rest)
                # Clef G
                draw.arc([60, base_y - 8, 88, base_y + 56], 0, 360, fill=0, width=2)
                annotations.append({
                    "id": ann_id, "image_id": img_id, "category_id": 3,
                    "bbox": [60, base_y - 8, 28, 64], "area": 1792, "iscrowd": 0
                })
                ann_id += 1

                # Time Signature 4/4
                annotations.append({
                    "id": ann_id, "image_id": img_id, "category_id": 10,
                    "bbox": [105, base_y + 4, 24, 40], "area": 960, "iscrowd": 0
                })
                ann_id += 1

                # Notes across staff
                x_pos = 160
                for n in range(5):
                    n_y = base_y + 12 + (n % 3) * 12
                    # Notehead
                    draw.ellipse([x_pos, n_y, x_pos + 16, n_y + 12], fill=0)
                    annotations.append({
                        "id": ann_id, "image_id": img_id, "category_id": 1,
                        "bbox": [x_pos, n_y, 16, 12], "area": 192, "iscrowd": 0
                    })
                    ann_id += 1

                    # Stem
                    draw.line([(x_pos + 15, n_y - 24), (x_pos + 15, n_y + 6)], fill=0, width=2)
                    annotations.append({
                        "id": ann_id, "image_id": img_id, "category_id": 5,
                        "bbox": [x_pos + 14, n_y - 24, 3, 30], "area": 90, "iscrowd": 0
                    })
                    ann_id += 1

                    x_pos += 90

            img.save(img_path)
            images.append({
                "id": img_id,
                "file_name": file_name,
                "width": w,
                "height": h
            })

        coco_data = {
            "images": images,
            "annotations": annotations,
            "categories": categories
        }

        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(coco_data, f, indent=2)

    def __len__(self) -> int:
        return len(self.image_ids)

    def __getitem__(self, idx: int) -> Tuple[Image.Image, List[Dict[str, Any]], str]:
        img_id = self.image_ids[idx]
        img_info = self.images_dict[img_id]
        img_path = os.path.join(self.dataset_dir, img_info["file_name"])

        image = Image.open(img_path).convert("RGB")
        anns = self.img_to_anns.get(img_id, [])

        return image, anns, img_path

    def visualize_boxes(self, image: Image.Image, annotations: List[Dict[str, Any]]) -> Image.Image:
        """
        Overlays COCO bounding boxes [x, y, w, h] and class label tags onto score page image.
        """
        vis_img = image.copy().convert("RGB")
        draw = ImageDraw.Draw(vis_img)

        # Color palette for classes
        colors = ["#E63946", "#1D3557", "#2A9D8F", "#E76F51", "#F4A261", "#9C89B8", "#457B9D"]

        for ann in annotations:
            cat_id = ann["category_id"]
            cat_name = self.cat_dict.get(cat_id, f"Class_{cat_id}")
            x, y, w, h = ann["bbox"]

            color = colors[cat_id % len(colors)]
            draw.rectangle([x, y, x + w, y + h], outline=color, width=2)
            draw.rectangle([x, max(0, y - 14), x + len(cat_name) * 7, y], fill=color)
            draw.text((x + 2, max(0, y - 13)), cat_name, fill="white")

        return vis_img
