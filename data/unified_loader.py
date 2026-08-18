# Unified OMR Dataset Loader & Automated Data Downloader
import os
import sys
import zipfile
import urllib.request
import torch
import numpy as np
from PIL import Image, ImageDraw
from torch.utils.data import Dataset, DataLoader
from typing import List, Tuple, Dict, Any, Optional

from data.primus_loader import PrIMuSVocabulary


class OMRDataDownloader:
    """
    Automated dataset fetcher for OMR datasets (PrIMuS, GrandStaff, synthetic benchmarks).
    Downloads archive zip files if remote URL provided or generates local dataset splits.
    """
    PRIMUS_SAMPLE_URL = "https://github.com/PRG-Unravel/PrIMuS/raw/master/package/primus_calvo_oneset.zip"

    def __init__(self, target_dir: str = "data/primus"):
        self.target_dir = target_dir

    def download_or_generate(self, sample_count: int = 20) -> str:
        os.makedirs(self.target_dir, exist_ok=True)
        
        # Check if dataset already populated with images and annotations
        existing_files = os.listdir(self.target_dir)
        if len(existing_files) > 5:
            print(f"[DATASET] Dataset directory '{self.target_dir}' already populated with {len(existing_files)} files.")
            return self.target_dir

        print(f"[DOWNLOAD] Preparing OMR dataset in '{self.target_dir}'...")
        try:
            zip_path = os.path.join(self.target_dir, "primus_sample.zip")
            print(f"[DOWNLOAD] Downloading PrIMuS sample dataset from {self.PRIMUS_SAMPLE_URL}...")
            urllib.request.urlretrieve(self.PRIMUS_SAMPLE_URL, zip_path)
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.target_dir)
            os.remove(zip_path)
            print(f"[SUCCESS] Successfully extracted PrIMuS dataset to '{self.target_dir}'.")
        except Exception as e:
            print(f"[INFO] Remote download notice: {e}. Generating local verification dataset ({sample_count} samples)...")
            self._create_local_benchmark_samples(sample_count)

        return self.target_dir

    def _create_local_benchmark_samples(self, count: int):
        agnostic_vocab = [
            ["clef.G-L2", "keySignature.F#", "timeSignature.4/4", "note.quarter-L4", "note.quarter-S3", "note.half-L3", "barline"],
            ["clef.F-L4", "keySignature.Bb", "timeSignature.3/4", "note.eighth-S2", "note.eighth-L3", "note.quarter-S3", "rest.quarter-L3", "barline"],
            ["clef.G-L2", "timeSignature.6/8", "note.dottedQuarter-L4", "note.eighth-S3", "note.quarter-L3", "barline"]
        ]
        
        semantic_vocab = [
            ["clef-G2", "keySignature-F#", "time-4/4", "note-B4_quarter", "note-C5_quarter", "note-A4_half", "barline"],
            ["clef-F4", "keySignature-Bb", "time-3/4", "note-C3_eighth", "note-D3_eighth", "note-F3_quarter", "rest-quarter", "barline"],
            ["clef-G2", "time-6/8", "note-B4_dotted_quarter", "note-C5_eighth", "note-A4_quarter", "barline"]
        ]

        for i in range(count):
            base_name = f"score_slice_{i+1:03d}"
            img_path = os.path.join(self.target_dir, f"{base_name}.png")
            agnostic_path = os.path.join(self.target_dir, f"{base_name}.agnostic")
            semantic_path = os.path.join(self.target_dir, f"{base_name}.semantic")

            agn_tokens = agnostic_vocab[i % len(agnostic_vocab)]
            sem_tokens = semantic_vocab[i % len(semantic_vocab)]

            # Save agnostic annotation
            with open(agnostic_path, "w", encoding="utf-8") as f:
                f.write("\t".join(agn_tokens))

            # Save semantic annotation
            with open(semantic_path, "w", encoding="utf-8") as f:
                f.write("\t".join(sem_tokens))

            # Draw score image slice
            w, h = 480 + (i % 3) * 60, 64
            img = Image.new("L", (w, h), color=255)
            draw = ImageDraw.Draw(img)
            for y in [16, 24, 32, 40, 48]:
                draw.line([(10, y), (w - 10, y)], fill=0, width=1)
            
            x = 30
            for t in agn_tokens:
                draw.ellipse([x, 28, x+12, 38], fill=0)
                draw.line([(x+11, 10), (x+11, 33)], fill=0, width=2)
                x += 35
            img.save(img_path)

        print(f"[SUCCESS] Local OMR benchmark created in '{self.target_dir}' ({count} score slices).")


class UnifiedOMRDataset(Dataset):
    """
    Unified PyTorch Dataset supporting agnostic and semantic OMR representations.
    Seamlessly parses images, builds global vocabularies, and encodes target token sequences.
    """
    def __init__(
        self,
        data_dir: str,
        annotation_type: str = "agnostic",
        img_height: int = 64,
        max_samples: Optional[int] = None
    ):
        self.data_dir = data_dir
        self.annotation_type = annotation_type.lower()
        self.img_height = img_height
        
        self.vocab = PrIMuSVocabulary()
        self.samples: List[Tuple[str, List[str]]] = []
        
        # Load dataset files
        downloader = OMRDataDownloader(data_dir)
        downloader.download_or_generate(sample_count=20)
        self._load_dataset_files(max_samples)
        self._build_vocab()

    def _load_dataset_files(self, max_samples: Optional[int]):
        ext = ".agnostic" if self.annotation_type == "agnostic" else ".semantic"
        
        for root, _, files in os.walk(self.data_dir):
            for file in sorted(files):
                if file.endswith(ext):
                    anno_path = os.path.join(root, file)
                    img_path = os.path.splitext(anno_path)[0] + ".png"
                    
                    if os.path.exists(img_path):
                        with open(anno_path, "r", encoding="utf-8") as f:
                            tokens = f.read().strip().split("\t")
                        self.samples.append((img_path, tokens))
                        
                        if max_samples and len(self.samples) >= max_samples:
                            break
            if max_samples and len(self.samples) >= max_samples:
                break
                
        print(f"[UNIFIED] Loaded {len(self.samples)} '{self.annotation_type}' samples from '{self.data_dir}'.")

    def _build_vocab(self):
        for _, tokens in self.samples:
            for t in tokens:
                self.vocab.add_token(t)
        print(f"[VOCAB] Vocabulary size: {len(self.vocab)} unique tokens (including PAD, UNK, BOS, EOS).")

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor, List[str], str]:
        img_path, raw_tokens = self.samples[idx]
        
        # Load and scale image to target fixed height maintaining aspect ratio
        img = Image.open(img_path).convert("L")
        w, h = img.size
        aspect_ratio = w / float(h)
        new_w = max(16, int(self.img_height * aspect_ratio))
        img = img.resize((new_w, self.img_height), Image.Resampling.BILINEAR)
        
        # Convert image to Normalized PyTorch Float Tensor [1, H, W] in range [0, 1]
        img_np = np.array(img, dtype=np.float32) / 255.0
        img_tensor = torch.tensor(img_np, dtype=torch.float32).unsqueeze(0)
        
        # Encode tokens with BOS and EOS
        encoded_ids = torch.tensor(self.vocab.encode(raw_tokens, add_special_tokens=True), dtype=torch.long)
        
        return img_tensor, encoded_ids, raw_tokens, img_path


class UnifiedCollate:
    """
    Custom collation function for batching variable-width score images and variable-length token sequences.
    Pads images horizontally to max width in batch and pads token sequences with <PAD> ID (0).
    """
    def __init__(self, pad_id: int = 0):
        self.pad_id = pad_id

    def __call__(self, batch: List[Tuple[torch.Tensor, torch.Tensor, List[str], str]]) -> Dict[str, Any]:
        imgs, seqs, raw_seqs, paths = zip(*batch)
        
        # Find maximum image width and sequence length in current batch
        max_w = max(img.shape[2] for img in imgs)
        max_len = max(seq.shape[0] for seq in seqs)
        
        batch_size = len(batch)
        img_h = imgs[0].shape[1]
        
        # Padded Image Tensor [B, 1, H, Max_W] filled with white (1.0)
        padded_imgs = torch.ones((batch_size, 1, img_h, max_w), dtype=torch.float32)
        
        # Padded Sequence Tensor [B, Max_Len] filled with pad_id (0)
        padded_seqs = torch.full((batch_size, max_len), fill_value=self.pad_id, dtype=torch.long)
        
        # Padding masks [B, Max_Len] (1 for real tokens, 0 for PAD)
        pad_masks = torch.zeros((batch_size, max_len), dtype=torch.float32)
        
        img_widths = []
        seq_lengths = []
        
        for idx in range(batch_size):
            img_tensor = imgs[idx]
            seq_tensor = seqs[idx]
            
            w = img_tensor.shape[2]
            l = seq_tensor.shape[0]
            
            padded_imgs[idx, :, :, :w] = img_tensor
            padded_seqs[idx, :l] = seq_tensor
            pad_masks[idx, :l] = 1.0
            
            img_widths.append(w)
            seq_lengths.append(l)

        return {
            "images": padded_imgs,
            "sequences": padded_seqs,
            "padding_masks": pad_masks,
            "img_widths": img_widths,
            "seq_lengths": seq_lengths,
            "raw_sequences": raw_seqs,
            "file_paths": paths
        }


def get_omr_dataloader(
    data_dir: str,
    annotation_type: str = "agnostic",
    batch_size: int = 4,
    shuffle: bool = True,
    img_height: int = 64
) -> Tuple[DataLoader, UnifiedOMRDataset]:
    """
    Factory function to construct a unified PyTorch DataLoader for OMR training/evaluation.
    """
    dataset = UnifiedOMRDataset(data_dir=data_dir, annotation_type=annotation_type, img_height=img_height)
    collate_fn = UnifiedCollate(pad_id=dataset.vocab.token2id[dataset.vocab.pad_token])
    
    loader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        collate_fn=collate_fn
    )
    return loader, dataset
