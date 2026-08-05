import os
import time
import traceback
from typing import Dict, Any

from pipeline.pdf_processor import convert_pdf_to_images
from pipeline.omr_engine import run_omr_on_images
from pipeline.musicxml_cleaner import process_and_clean_musicxml
from pipeline.synth_engine import synthesize_midi_to_wav

def execute_pipeline(job: Dict[str, Any], pdf_path: str, output_base_dir: str):
    """
    Executes full Sheet2Sound conversion pipeline asynchronously.
    Updates job dictionary status, stage, progress %, and error details in real-time.
    """
    job_id = job["job_id"]
    job_dir = os.path.join(output_base_dir, job_id)
    os.makedirs(job_dir, exist_ok=True)

    job["start_time"] = time.time()
    job["status"] = "processing"
    job["progress"] = 5
    job["stage"] = "Rendering PDF pages to high-resolution images..."

    try:
        # Check for simulated error flag
        fail_stage = job.get("fail_stage")

        # STEP 1: PDF to Image conversion
        time.sleep(0.5)
        image_dir = os.path.join(job_dir, "images")
        image_paths = convert_pdf_to_images(pdf_path, image_dir, dpi=300)
        job["progress"] = 25
        job["stage"] = f"Rendered {len(image_paths)} page(s). Running OMR (oemer)..."

        if fail_stage == "omr":
            raise RuntimeError("OMR Engine (oemer) failed: staff lines could not be reliably detected in score scan.")

        # STEP 2: OMR Recognition
        time.sleep(0.8)
        raw_xml_path = os.path.join(job_dir, "raw_omr.musicxml")
        run_omr_on_images(image_paths, raw_xml_path)
        job["progress"] = 60
        job["stage"] = "Cleaning MusicXML & converting to MIDI..."

        if fail_stage == "synthesis":
            raise RuntimeError("FluidSynth synthesis error: SoundFont render engine crashed on measure 14.")

        # STEP 3: MusicXML cleanup and MIDI export
        time.sleep(0.5)
        clean_xml_path = os.path.join(job_dir, "output.musicxml")
        midi_path = os.path.join(job_dir, "output.mid")
        score_metadata = process_and_clean_musicxml(raw_xml_path, clean_xml_path, midi_path)
        
        job["progress"] = 85
        job["stage"] = "Synthesizing WAV audio via FluidSynth..."

        # STEP 4: MIDI to WAV Synthesis
        time.sleep(0.5)
        wav_path = os.path.join(job_dir, "output.wav")
        synthesize_midi_to_wav(midi_path, wav_path)

        # Store generated paths and metadata in job record
        job["audio_url"] = f"/static/{job_id}/output.wav"
        job["midi_url"] = f"/static/{job_id}/output.mid"
        job["musicxml_url"] = f"/static/{job_id}/output.musicxml"
        job["metadata"] = score_metadata

        job["progress"] = 100
        job["status"] = "done"
        job["stage"] = "Conversion Complete!"

    except Exception as e:
        print(f"Pipeline error for job {job_id}:\n{traceback.format_exc()}")
        job["status"] = "error"
        job["stage"] = "Pipeline Execution Error"
        job["error"] = str(e)
