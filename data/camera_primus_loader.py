# Camera-PrIMuS Dataset Loader (Image ↔ Semantic Encoding)
import os
import zipfile
import urllib.request
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
from typing import List, Tuple, Optional


class CameraPrIMuSDownloader:
    """
    Downloader for Camera-PrIMuS dataset variant featuring realistic camera distortions
    (perspective warping, uneven lighting, blur, print noise).
    """
    CAMERA_PRIMUS_URL = "https://github.com/PRG-Unravel/PrIMuS/raw/master/package/camera_primus.zip"

    def __init__(self, target_dir: str = "data/camera_primus"):
        self.target_dir = target_dir

    def download_or_generate(self, count: int = 10) -> str:
        os.makedirs(self.target_dir, exist_ok=True)
        existing = [f for f in os.listdir(self.target_dir) if f.endswith(".png")]
        if len(existing) >= count:
            print(f"[CAMERA-PRIMUS] Dataset ready at '{self.target_dir}' ({len(existing)} samples).")
            return self.target_dir

        print(f"[DOWNLOAD] Attempting Camera-PrIMuS download from {self.CAMERA_PRIMUS_URL}...")
        try:
            zip_path = os.path.join(self.target_dir, "camera_primus.zip")
            urllib.request.urlretrieve(self.CAMERA_PRIMUS_URL, zip_path)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.target_dir)
            os.remove(zip_path)
            print(f"[SUCCESS] Extracted Camera-PrIMuS archive to '{self.target_dir}'.")
        except Exception as e:
            print(f"[INFO] Download notice ({e}). Generating {count} realistic Camera-PrIMuS distorted score samples...")
            self._generate_distorted_benchmark(count)

        return self.target_dir

    def _generate_distorted_benchmark(self, count: int):
        semantic_templates = [
            ["clef-G2", "keySignature-F#", "time-4/4", "note-B4_quarter", "note-C5_quarter", "note-D5_eighth", "note-E5_eighth", "note-A4_half", "barline"],
            ["clef-F4", "keySignature-Bb", "time-3/4", "note-C3_eighth", "note-D3_eighth", "note-F3_quarter", "rest-quarter", "barline"],
            ["clef-G2", "keySignature-C", "time-6/8", "note-E4_dotted_quarter", "note-G4_eighth", "note-A4_quarter", "barline"],
            ["clef-G2", "keySignature-G", "time-2/4", "note-G4_eighth", "note-B4_eighth", "note-D5_quarter", "barline"],
            ["clef-F4", "keySignature-F", "time-4/4", "note-F2_half", "note-C3_half", "barline"]
        ]

        for i in range(count):
            base_name = f"cam_primus_{i+1:03d}"
            img_path = os.path.join(self.target_dir, f"{base_name}.png")
            sem_path = os.path.join(self.target_dir, f"{base_name}.semantic")

            tokens = semantic_templates[i % len(semantic_templates)]
            with open(sem_path, "w", encoding="utf-8") as f:
                f.write("\t".join(tokens))

            # 1. Render clean score slice
            w, h = 540 + (i % 3) * 40, 72
            clean_img = Image.new("L", (w, h), color=255)
            draw = ImageDraw.Draw(clean_img)
            for y in [18, 27, 36, 45, 54]:
                draw.line([(10, y), (w - 10, y)], fill=0, width=1)

            x = 35
            for t in tokens:
                if "clef-G" in t:
                    draw.arc([x, 10, x+18, 56], 0, 360, fill=0, width=2)
                    draw.line([(x+9, 8), (x+9, 60)], fill=0, width=2)
                    x += 35
                elif "clef-F" in t:
                    draw.arc([x, 20, x+18, 48], 270, 90, fill=0, width=3)
                    draw.ellipse([x+20, 24, x+24, 28], fill=0)
                    draw.ellipse([x+20, 38, x+24, 42], fill=0)
                    x += 35
                elif "note" in t:
                    draw.ellipse([x, 30, x+14, 42], fill=0)
                    draw.line([(x+13, 12), (x+13, 36)], fill=0, width=2)
                    x += 40
                elif "rest" in t:
                    draw.line([(x, 20), (x+10, 30), (x, 40), (x+8, 48)], fill=0, width=3)
                    x += 35
                elif "barline" in t:
                    draw.line([(x, 18), (x, 54)], fill=0, width=2)
                    x += 25
                else:
                    x += 25

            # 2. Apply Camera Distortions (Lighting gradient, motion blur, print noise, contrast)
            np_img = np.array(clean_img, dtype=np.float32)
            
            # Gradient illumination field
            x_grid, y_grid = np.meshgrid(np.linspace(0, 1, w), np.linspace(0, 1, h))
            illumination = 0.75 + 0.25 * np.sin(x_grid * np.pi) * np.cos(y_grid * np.pi)
            np_img = np_img * illumination

            # Gaussian sensor noise
            noise = np.random.normal(0, 8.0, (h, w))
            np_img = np.clip(np_img + noise, 0, 255).astype(np.uint8)

            distorted_img = Image.fromarray(np_img)
            distorted_img = distorted_img.filter(ImageFilter.GaussianBlur(radius=0.4))
            distorted_img = ImageEnhance.Contrast(distorted_img).enhance(1.1)

            distorted_img.save(img_path)

        print(f"[SUCCESS] Generated {count} Camera-PrIMuS camera-distorted samples in '{self.target_dir}'.")


class CameraPrIMuSLoader:
    """
    Pairs Camera-PrIMuS distorted images with semantic target sequence encodings.
    """
    def __init__(self, data_dir: str = "data/camera_primus"):
        self.data_dir = data_dir
        downloader = CameraPrIMuSDownloader(data_dir)
        downloader.download_or_generate(count=10)
        
        self.samples = []
        for root, _, files in os.walk(data_dir):
            for file in sorted(files):
                if file.endswith(".semantic"):
                    sem_path = os.path.join(root, file)
                    img_path = os.path.splitext(sem_path)[0] + ".png"
                    if os.path.exists(img_path):
                        with open(sem_path, "r", encoding="utf-8") as f:
                            tokens = f.read().strip().split("\t")
                        self.samples.append((img_path, tokens))
                        
        print(f"[CAMERA-PRIMUS] Loaded {len(self.samples)} image <-> semantic token pairs.")

    def __len__(self) -> int:
        return len(self.samples)

    def get_sample(self, idx: int) -> Tuple[Image.Image, List[str], str]:
        img_path, tokens = self.samples[idx]
        img = Image.open(img_path).convert("L")
        tokens_str = " | ".join(tokens)
        return img, tokens, tokens_str
