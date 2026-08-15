# Custom End-to-End Optical Music Recognition (OMR) System

A custom-trained, end-to-end Optical Music Recognition (OMR) pipeline built to convert scanned sheet music into MusicXML, MIDI, and playable audio without relying on black-box OMR wrappers.

---

## 🏗️ Project Layout

```
S2S/
├── omr-core/           # Custom OMR model architectures (CRNN/CTC seq2seq & YOLOv8 detector)
├── backend/            # API service wrapping the OMR pipeline
├── frontend/           # Web application (planned)
├── data/               # Dataset loaders (PrIMuS, DeepScores, MUSCIMA++)
│   ├── primus_loader.py       # PrIMuS dataset loader & vocabulary encoder
│   ├── deepscores_loader.py   # DeepScores bounding box scaffolding
│   ├── muscima_loader.py      # MUSCIMA++ node graph scaffolding
│   └── demo_pipeline.py       # Data verification script
├── notebooks/          # Jupyter experimentation notebooks
│   └── 01_primus_data_pipeline.ipynb
├── docs/               # Architectural evaluations & paper references
│   └── omr_architecture_evaluation.md
└── README.md
```

---

## 📖 Phase 1 — Foundations

- **Architecture Evaluation**: Evaluates End-to-End Seq2Seq (Calvo-Zaragoza et al., PrIMuS CRNN/CTC) vs. Two-Stage Detection + Graph Reconstruction (YOLOv8 + DeepScores/MUSCIMA++). See [`docs/omr_architecture_evaluation.md`](file:///c:/Users/hamza/Desktop/S2S/docs/omr_architecture_evaluation.md).
- **PrIMuS Loader**: Supports loading score images (`.png`), agnostic sequence annotations (`.agnostic`), and semantic sequence annotations (`.semantic`). See [`data/primus_loader.py`](file:///c:/Users/hamza/Desktop/S2S/data/primus_loader.py).
- **Interactive Verification**: Try [`notebooks/01_primus_data_pipeline.ipynb`](file:///c:/Users/hamza/Desktop/S2S/notebooks/01_primus_data_pipeline.ipynb) to visualize score slices and token alignments.
