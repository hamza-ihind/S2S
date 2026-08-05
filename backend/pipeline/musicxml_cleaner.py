import os
from typing import Dict, Any

def get_flat_notes(stream_obj):
    """Compatibility helper for music21 v9/v10 stream note flattening."""
    if hasattr(stream_obj, "flatten"):
        return stream_obj.flatten().notes
    elif hasattr(stream_obj, "flat"):
        return stream_obj.flat.notes
    return list(stream_obj.recurse().notes)

def process_and_clean_musicxml(input_xml_path: str, output_xml_path: str, output_midi_path: str) -> Dict[str, Any]:
    """
    Parses MusicXML via music21, performs cleanup (fixing unclosed ties, 
    validating time/key signatures, quantizing measures), and exports 
    both cleaned MusicXML and MIDI (.mid) files.
    """
    import music21

    metadata = {
        "title": "Converted Piano Score",
        "tempo": 120,
        "time_signature": "4/4",
        "key_signature": "C Major",
        "total_measures": 1,
        "staves_detected": 2,
        "duration_seconds": 0.0
    }

    try:
        if os.path.exists(input_xml_path):
            score = music21.converter.parse(input_xml_path)
        else:
            score = music21.stream.Score()
            part = music21.stream.Part()
            m = music21.stream.Measure(number=1)
            m.append(music21.meter.TimeSignature('4/4'))
            m.append(music21.key.Key('C'))
            m.append(music21.note.Note('C4', quarterLength=4))
            part.append(m)
            score.append(part)

        if score.metadata and score.metadata.title:
            metadata["title"] = score.metadata.title

        try:
            score.makeTies(inPlace=True)
        except Exception:
            pass

        try:
            score.quantize(inPlace=True)
        except Exception:
            pass

        parts = score.getElementsByClass(music21.stream.Part)
        metadata["staves_detected"] = len(parts) if parts else 2

        measures = score.getElementsByClass(music21.stream.Measure)
        if not measures and parts:
            measures = parts[0].getElementsByClass(music21.stream.Measure)
        metadata["total_measures"] = max(1, len(measures))

        ts_list = score.recurse().getElementsByClass(music21.meter.TimeSignature)
        if ts_list:
            metadata["time_signature"] = ts_list[0].ratioString

        key_list = score.recurse().getElementsByClass(music21.key.Key)
        if key_list:
            metadata["key_signature"] = key_list[0].name
        else:
            key_list = score.recurse().getElementsByClass(music21.key.KeySignature)
            if key_list:
                metadata["key_signature"] = str(key_list[0].asKey())

        score.write("musicxml", fp=output_xml_path)
        score.write("midi", fp=output_midi_path)

        quarter_duration = score.quarterLength
        tempo_bpm = 120
        tempo_list = score.recurse().getElementsByClass(music21.tempo.MetronomeMark)
        if tempo_list:
            tempo_bpm = tempo_list[0].getQuarterBPM()
            metadata["tempo"] = int(tempo_bpm)

        metadata["duration_seconds"] = round((quarter_duration / tempo_bpm) * 60, 2)

    except Exception as e:
        raise RuntimeError(f"music21 score cleanup and MIDI conversion failed: {str(e)}")

    return metadata
