# PrIMuS Dataset Loader & Token Vocabulary Pipeline
import os
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import torch
from torch.utils.data import Dataset, DataLoader

class PrIMuSVocabulary:
    """
    Manages mapping between OMR token strings (agnostic or semantic) and integer IDs.
    """
    def __init__(self, pad_token="<PAD>", unk_token="<UNK>", bos_token="<BOS>", eos_token="<EOS>"):
        self.pad_token = pad_token
        self.unk_token = unk_token
        self.bos_token = bos_token
        self.eos_token = eos_token
        
        self.token2id = {pad_token: 0, unk_token: 1, bos_token: 2, eos_token: 3}
        self.id2token = {0: pad_token, 1: unk_token, 2: bos_token, 3: eos_token}
        
    def add_token(self, token):
        if token not in self.token2id:
            new_id = len(self.token2id)
            self.token2id[token] = new_id
            self.id2token[new_id] = token
            return new_id
        return self.token2id[token]

    def encode(self, token_list, add_special_tokens=True):
        ids = []
        if add_special_tokens:
            ids.append(self.token2id[self.bos_token])
        for t in token_list:
            ids.append(self.token2id.get(t, self.token2id[self.unk_token]))
        if add_special_tokens:
            ids.append(self.token2id[self.eos_token])
        return ids

    def decode(self, id_list, skip_special_tokens=True):
        tokens = []
        special = {self.token2id[self.pad_token], self.token2id[self.unk_token], self.token2id[self.bos_token], self.token2id[self.eos_token]}
        for idx in id_list:
            if skip_special_tokens and idx in special:
                continue
            tokens.append(self.id2token.get(idx, self.unk_token))
        return tokens

    def __len__(self):
        return len(self.token2id)


class PrIMuSDataset(Dataset):
    """
    Dataset loader for the PrIMuS / Camera-PrIMuS dataset.
    Supports reading image slices (.png), agnostic sequences (.agnostic), and semantic sequences (.semantic).
    Includes a synthetic sample generator when no local PrIMuS data folder is present.
    """
    def __init__(self, data_dir=None, annotation_type="agnostic", transform=None, sample_count=50):
        self.data_dir = data_dir
        self.annotation_type = annotation_type
        self.transform = transform
        
        self.vocab = PrIMuSVocabulary()
        self.samples = [] # List of tuples: (image_path_or_PIL, token_list)
        
        if data_dir and os.path.exists(data_dir) and len(os.listdir(data_dir)) > 0:
            self._load_from_directory()
        else:
            self._generate_synthetic_samples(sample_count)
            
        self._build_vocabulary()

    def _load_from_directory(self):
        print(f"[DATASET] Loading PrIMuS dataset from '{self.data_dir}' (annotation type: {self.annotation_type})...")
        ext = ".agnostic" if self.annotation_type == "agnostic" else ".semantic"
        
        for root, _, files in os.walk(self.data_dir):
            for file in files:
                if file.endswith(ext):
                    anno_path = os.path.join(root, file)
                    img_path = os.path.splitext(anno_path)[0] + ".png"
                    
                    if os.path.exists(img_path):
                        with open(anno_path, "r", encoding="utf-8") as f:
                            tokens = f.read().strip().split("\t")
                        self.samples.append((img_path, tokens))
                        
        print(f"[SUCCESS] Loaded {len(self.samples)} PrIMuS samples from directory.")

    def _generate_synthetic_samples(self, count):
        print(f"[INFO] Local dataset directory '{self.data_dir}' not found or empty. Generating {count} synthetic PrIMuS samples for Phase 1 verification...")
        
        # Synthetic PrIMuS agnostic and semantic vocabularies
        agnostic_templates = [
            ["clef.G-L2", "keySignature.F#", "timeSignature.4/4", "note.quarter-L4", "note.quarter-S3", "note.half-L3", "barline"],
            ["clef.F-L4", "keySignature.Bb", "timeSignature.3/4", "note.eighth-S2", "note.eighth-L3", "note.quarter-S3", "rest.quarter-L3", "barline"],
            ["clef.G-L2", "timeSignature.6/8", "note.dottedQuarter-L4", "note.eighth-S3", "note.quarter-L3", "barline"]
        ]
        
        semantic_templates = [
            ["clef-G2", "keySignature-F#", "time-4/4", "note-B4_quarter", "note-C5_quarter", "note-A4_half", "barline"],
            ["clef-F4", "keySignature-Bb", "time-3/4", "note-C3_eighth", "note-D3_eighth", "note-F3_quarter", "rest-quarter", "barline"],
            ["clef-G2", "time-6/8", "note-B4_dotted_quarter", "note-C5_eighth", "note-A4_quarter", "barline"]
        ]
        
        templates = agnostic_templates if self.annotation_type == "agnostic" else semantic_templates
        
        for i in range(count):
            tokens = templates[i % len(templates)]
            img = self._render_synthetic_score_slice(tokens)
            self.samples.append((img, tokens))

    def _render_synthetic_score_slice(self, tokens):
        # Render a single-staff line snippet image (e.g. 512x64 px)
        width, height = 512, 64
        img = Image.new("L", (width, height), color=255)
        draw = ImageDraw.Draw(img)
        
        # Draw 5 stafflines
        for y_pos in [16, 24, 32, 40, 48]:
            draw.line([(10, y_pos), (width - 10, y_pos)], fill=0, width=1)
            
        # Draw symbols along horizontal axis
        x_cursor = 30
        for token in tokens:
            if "clef.G" in token or "clef-G" in token:
                draw.arc([x_cursor, 10, x_cursor+16, 50], 0, 360, fill=0, width=2)
                draw.line([(x_cursor+8, 8), (x_cursor+8, 54)], fill=0, width=2)
                x_cursor += 30
            elif "clef.F" in token or "clef-F" in token:
                draw.arc([x_cursor, 18, x_cursor+16, 42], 270, 90, fill=0, width=3)
                draw.ellipse([x_cursor+18, 22, x_cursor+22, 26], fill=0)
                draw.ellipse([x_cursor+18, 34, x_cursor+22, 38], fill=0)
                x_cursor += 30
            elif "note" in token:
                draw.ellipse([x_cursor, 28, x_cursor+14, 38], fill=0)
                draw.line([(x_cursor+13, 10), (x_cursor+13, 33)], fill=0, width=2)
                x_cursor += 35
            elif "rest" in token:
                pts = [(x_cursor, 18), (x_cursor+10, 26), (x_cursor, 34), (x_cursor+8, 42)]
                draw.line(pts, fill=0, width=3)
                x_cursor += 30
            elif "barline" in token:
                draw.line([(x_cursor, 16), (x_cursor, 48)], fill=0, width=2)
                x_cursor += 25
            else:
                x_cursor += 20
                
        return img

    def _build_vocabulary(self):
        for _, tokens in self.samples:
            for t in tokens:
                self.vocab.add_token(t)
        print(f"[VOCAB] PrIMuS Vocabulary constructed: {len(self.vocab)} unique tokens.")

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        img_item, tokens = self.samples[idx]
        
        if isinstance(img_item, str):
            image = Image.open(img_item).convert("L")
        else:
            image = img_item.convert("L")
            
        if self.transform:
            image = self.transform(image)
            
        encoded_tokens = torch.tensor(self.vocab.encode(tokens), dtype=torch.long)
        return image, encoded_tokens, tokens
