# Sheet2Sound Jupyter Notebook Pipeline

This directory contains individual Jupyter Notebooks for each stage of the **Sheet2Sound** OMR-to-Audio pipeline:

1. **[`01_pdf_page_rendering.ipynb`](file:///c:/Users/hamza/Desktop/S2S/jupyter/01_pdf_page_rendering.ipynb)**
   - Renders 300 DPI PNG images from PDF scores (`empty-core-3.pdf`) using PyMuPDF (`fitz`).
2. **[`02_omr_recognition.ipynb`](file:///c:/Users/hamza/Desktop/S2S/jupyter/02_omr_recognition.ipynb)**
   - Runs Optical Music Recognition (OMR) using `oemer` or backend fallback to produce MusicXML (`empty_core_omr.musicxml`).
3. **[`03_score_inspection.ipynb`](file:///c:/Users/hamza/Desktop/S2S/jupyter/03_score_inspection.ipynb)**
   - Parses MusicXML with `music21` to inspect notes, pitches, frequencies, and staves.
4. **[`04_midi_export.ipynb`](file:///c:/Users/hamza/Desktop/S2S/jupyter/04_midi_export.ipynb)**
   - Handles note ties, measure quantization, and exports score to standard MIDI (`empty_core_output.mid`).
5. **[`05_audio_synthesis.ipynb`](file:///c:/Users/hamza/Desktop/S2S/jupyter/05_audio_synthesis.ipynb)**
   - Synthesizes MIDI frequencies into 44.1kHz WAV piano audio (`empty_core_output.wav`) with attack/decay envelopes.
6. **[`06_waveform_and_playback.ipynb`](file:///c:/Users/hamza/Desktop/S2S/jupyter/06_waveform_and_playback.ipynb)**
   - Plots the audio waveform with `matplotlib` and provides interactive inline playback in Jupyter.

> **Full Pipeline Notebook**: [`omr_to_audio_pipeline.ipynb`](file:///c:/Users/hamza/Desktop/S2S/jupyter/omr_to_audio_pipeline.ipynb) contains all steps combined in a single notebook.
