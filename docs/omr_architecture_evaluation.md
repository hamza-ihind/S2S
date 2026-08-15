# Optical Music Recognition (OMR) Architecture Evaluation & Justification

## Overview

This document evaluates the two primary architectural paradigms for building a custom Optical Music Recognition (OMR) system:

1. **End-to-End Sequence-to-Sequence (PrIMuS-style CRNN/CTC & Encoder-Decoder)** (Calvo-Zaragoza et al., 2017–2020)
2. **Two-Stage Detection + Semantic Reconstruction (YOLOv8 + Graph Heuristics)** (DeepScores / MUSCIMA++ style)

---

## 1. Paradigm Evaluation

### Option A: End-to-End Sequence-to-Sequence (PrIMuS Style)

In this approach, a Convolutional Recurrent Neural Network (CRNN) with Connectionist Temporal Classification (CTC) or an Attention-based Encoder-Decoder maps a sheet music image slice directly to a sequence of musical tokens (Agnostic or Semantic).

```
[ Sheet Music Image Slice ] ────► [ CNN Feature Extractor ] ────► [ RNN / Transformer Encoder ] ────► [ CTC / Attention Decoder ] ────► [ Agnostic / Semantic Tokens ]
```

#### Advantages:
- **No Manual Bounding Box Annotations Required**: Does not require pixel-level or bounding-box annotations for every symbol. Only requires line-level image slices paired with text-like token sequences (`.agnostic` or `.semantic`).
- **Unified End-to-End Optimization**: The network learns visual features, spatial alignment, and token ordering simultaneously under a single loss function.
- **Fast Iteration Speed**: Easily trainable on the benchmark **PrIMuS** (Printed Images of Music Scores) dataset containing 87,678 single-line music score snippets.
- **Direct Target Mapping**: Agnostic tokens encode physical symbol position relative to stafflines (e.g., `clef.G-L2`, `note.quarter-L4`), while Semantic tokens map directly to musical primitives (`clef-G2`, `note-C4_quarter`).

#### Disadvantages:
- **Limited to Line Slices / Systems**: Works best on single staff lines or isolated systems. Full-page polyphonic scores must first be segmented into individual staff lines.
- **Strict Left-to-Right Ordering**: Standard CTC assumes strict 1D temporal ordering, which requires careful handling for vertical polyphonic chords or multi-voice staves.

---

### Option B: Two-Stage Detection + Semantic Reconstruction (YOLOv8 + Heuristics)

In this approach, Stage 1 runs a object detector (e.g., YOLOv8 or Faster R-CNN) trained on datasets like DeepScores or MUSCIMA++ to predict 2D bounding boxes for every notehead, stem, accidental, rest, and clef. Stage 2 uses geometric heuristics and staff-line interpolation to reconstruct pitch, duration, and measure grouping.

```
[ Full Page / System Image ] ────► [ YOLOv8 Object Detector ] ────► [ 2D Bounding Boxes ] ────► [ Geometric Graph Reconstruction ] ────► [ MusicXML ]
```

#### Advantages:
- **Full Page / 2D Layout Robustness**: Can handle complex multi-system 2D layouts and polyphonic voices without slicing into single staff lines.
- **Explicit Geometry**: Direct access to notehead coordinates relative to staff lines ($y$-axis pitch interpolation).

#### Disadvantages:
- **Error Propagation**: Detection errors in Stage 1 (e.g., missed accidental or misclassified notehead) break downstream graph reconstruction in Stage 2.
- **Heavy Annotation Burden**: Requires thousands of manually labeled 2D bounding boxes across hundreds of symbol classes.
- **Complex Heuristic Stage**: Rule-based graph construction for ties, beams, and voices can become brittle and difficult to maintain.

---

## 2. Comparative Matrix

| Criterion | End-to-End Seq2Seq (PrIMuS) | Two-Stage Detection (YOLOv8 + Graph) |
| :--- | :--- | :--- |
| **Primary Dataset** | PrIMuS / Camera-PrIMuS (87k samples) | DeepScores v2 / MUSCIMA++ |
| **Annotation Complexity** | Low (Text token sequences) | High (2D Bounding boxes / Nodes) |
| **Pipeline Simplicity** | High (Single neural model) | Medium-Low (Detector + Heuristic Engine) |
| **Initial Pipeline Velocity** | **Very Fast** (Hours to working pipeline) | Moderate (Requires object detector + graph rules) |
| **Polyphonic Handling** | Staff-line level segmentation required | Handled via 2D bounding boxes |
| **Core Metric** | Symbol Error Rate (SER) | mAP @ IoU (Stage 1) + SER (Stage 2) |

---

## 3. Justified Choice & System Architecture

### Selected Strategy: **Hybrid PrIMuS-First End-to-End Pipeline**

For our custom OMR system, we select **PrIMuS-style End-to-End Sequence-to-Sequence** as our **Phase 1 & Phase 3 Core Baseline**, with an optional **YOLOv8 Staff/Symbol Detector (Phase 2)**:

1. **Phase 1 Foundations**: Implement PrIMuS data loading and token representation (`.agnostic` and `.semantic`).
2. **Phase 2 Detection**: Build a YOLOv8 / CNN staff-line segmenter and symbol detector for robust system slicing on full scanned pages.
3. **Phase 3 & 4 Recognition & Output**: Feed segmented staff slices into an end-to-end CRNN/CTC sequence model to produce semantic token streams, followed by MusicXML assembly, MIDI conversion, and audio synthesis.

This approach gives us a **working end-to-end pipeline early** while retaining the capability to handle multi-system full-page scans.
