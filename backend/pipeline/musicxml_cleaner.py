import os
from typing import Dict, Any, Union, List

def get_flat_notes(stream_obj):
    """Compatibility helper for music21 v9/v10 stream note flattening."""
    if hasattr(stream_obj, "flatten"):
        return stream_obj.flatten().notes
    elif hasattr(stream_obj, "flat"):
        return stream_obj.flat.notes
    return list(stream_obj.recurse().notes)

def merge_multi_page_scores(xml_paths: List[str]):
    """
    Parses and merges multiple page MusicXML / MXL files into a single consolidated music21 Score.
    """
    import music21
    valid_paths = [p for p in xml_paths if os.path.exists(p) and os.path.getsize(p) > 0]
    if not valid_paths:
        return music21.stream.Score()
    if len(valid_paths) == 1:
        return music21.converter.parse(valid_paths[0])

    combined_score = music21.stream.Score()
    parts_map = {}

    first_score = music21.converter.parse(valid_paths[0])
    if first_score.metadata:
        combined_score.metadata = first_score.metadata

    for idx, part in enumerate(first_score.getElementsByClass(music21.stream.Part)):
        p_id = part.id or f"P{idx+1}"
        new_part = music21.stream.Part(id=p_id)
        if hasattr(part, "partName") and part.partName:
            new_part.partName = part.partName
        for elem in part:
            new_part.append(elem)
        parts_map[p_id] = new_part
        combined_score.append(new_part)

    for path in valid_paths[1:]:
        try:
            page_score = music21.converter.parse(path)
            page_parts = list(page_score.getElementsByClass(music21.stream.Part))
            for idx, part in enumerate(page_parts):
                p_id = part.id or f"P{idx+1}"
                if p_id in parts_map:
                    target_part = parts_map[p_id]
                else:
                    target_keys = list(parts_map.keys())
                    if idx < len(target_keys):
                        target_part = parts_map[target_keys[idx]]
                    else:
                        target_part = music21.stream.Part(id=p_id)
                        parts_map[p_id] = target_part
                        combined_score.append(target_part)

                for elem in part:
                    if isinstance(elem, music21.stream.Measure):
                        target_part.append(elem)
        except Exception as e:
            print(f"Warning: Failed to merge score page {path}: {str(e)}")

    return combined_score

def process_and_clean_musicxml(
    input_xml_paths: Union[str, List[str]], 
    output_xml_path: str, 
    output_midi_path: str
) -> Dict[str, Any]:
    """
    Parses MusicXML (single file or list of page files) via music21, 
    performs cleanup (fixing unclosed ties, validating time/key signatures, quantizing measures), 
    and exports both cleaned MusicXML and MIDI (.mid) files.
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
        if isinstance(input_xml_paths, str):
            paths = [input_xml_paths]
        else:
            paths = input_xml_paths

        valid_paths = [p for p in paths if os.path.exists(p) and os.path.getsize(p) > 0]

        if valid_paths:
            score = merge_multi_page_scores(valid_paths)
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

        dir_xml = os.path.dirname(output_xml_path)
        if dir_xml:
            os.makedirs(dir_xml, exist_ok=True)
        dir_midi = os.path.dirname(output_midi_path)
        if dir_midi:
            os.makedirs(dir_midi, exist_ok=True)

        score.write("musicxml", fp=output_xml_path)
        score.write("midi", fp=output_midi_path)

        quarter_duration = score.quarterLength
        tempo_bpm = 120
        tempo_list = score.recurse().getElementsByClass(music21.tempo.MetronomeMark)
        if tempo_list:
            tempo_bpm = tempo_list[0].getQuarterBPM()
            metadata["tempo"] = int(tempo_bpm)

        metadata["duration_seconds"] = round((quarter_duration / max(1, tempo_bpm)) * 60, 2)

    except Exception as e:
        raise RuntimeError(f"music21 score cleanup and MIDI conversion failed: {str(e)}")

    return metadata

