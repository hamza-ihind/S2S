# MuNG XML (Music Notation Graph) Parser & Note Event Reconstructor
import os
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple, Optional


@dataclass
class NoteEvent:
    """
    Reconstructed musical note event representation (pitch + duration + onset).
    """
    id: int
    onset_beat: float
    pitch_name: str       # e.g., "C4", "F#4", "Bb3", "E5"
    duration_name: str    # e.g., "quarter", "eighth", "half", "whole"
    quarter_length: float # e.g., 1.0, 0.5, 2.0, 4.0
    clef_context: str     # e.g., "g-clef", "f-clef"


class MuNGGraphParser:
    """
    Parser for MuNG (Music Notation Graph) XML files.
    Parses graph nodes, spatial bounding boxes, outlinks/inlinks, and reconstructs
    musical pitch and duration note events from raw graph topology.
    """
    DIATONIC_PITCHES_G_CLEF = ["G5", "F5", "E5", "D5", "C5", "B4", "A4", "G4", "F4", "E4", "D4", "C4"]

    def __init__(self, mung_xml_dir: str = "data/mung_samples"):
        self.mung_dir = mung_xml_dir
        os.makedirs(mung_xml_dir, exist_ok=True)

    def generate_sample_mung_xml(self, xml_filename: str = "sample_score_001.mung.xml") -> str:
        xml_path = os.path.join(self.mung_dir, xml_filename)
        if os.path.exists(xml_path):
            return xml_path

        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<score-notation-graph page="1">
  <!-- Staff Line System Reference -->
  <staff id="staff_1" top="100" bottom="180">
    <staff-line y="100"/>
    <staff-line y="120"/>
    <staff-line y="140"/>
    <staff-line y="160"/>
    <staff-line y="180"/>
  </staff>

  <!-- Node 1: Treble Clef -->
  <node id="1" class="g-clef" top="90" left="20" bottom="190" right="60">
    <outlinks/>
  </node>

  <!-- Node 2: Accidental Sharp attached to Note 3 -->
  <node id="2" class="accidental-sharp" top="112" left="100" bottom="128" right="112">
    <outlinks>
      <link target="3" type="accidental-of"/>
    </outlinks>
  </node>

  <!-- Node 3: Quarter Notehead on F5 line (y_center=120) -->
  <node id="3" class="notehead-full" top="114" left="120" bottom="126" right="134">
    <outlinks>
      <link target="4" type="has-stem"/>
    </outlinks>
  </node>

  <!-- Node 4: Stem for Note 3 -->
  <node id="4" class="stem" top="80" left="133" bottom="120" right="135">
    <outlinks/>
  </node>

  <!-- Node 5: Eighth Notehead on C5 line (y_center=140) -->
  <node id="5" class="notehead-full" top="134" left="180" bottom="146" right="194">
    <outlinks>
      <link target="6" type="has-stem"/>
      <link target="7" type="has-beam"/>
    </outlinks>
  </node>

  <!-- Node 6: Stem for Note 5 -->
  <node id="6" class="stem" top="100" left="193" bottom="140" right="195">
    <outlinks/>
  </node>

  <!-- Node 7: Beam for Note 5 -->
  <node id="7" class="beam" top="98" left="193" bottom="104" right="240">
    <outlinks/>
  </node>

  <!-- Node 8: Half Notehead on G4 line (y_center=160) -->
  <node id="8" class="notehead-empty" top="154" left="250" bottom="166" right="266">
    <outlinks>
      <link target="9" type="has-stem"/>
    </outlinks>
  </node>

  <!-- Node 9: Stem for Note 8 -->
  <node id="9" class="stem" top="120" left="265" bottom="160" right="267">
    <outlinks/>
  </node>
</score-notation-graph>
"""
        with open(xml_path, "w", encoding="utf-8") as f:
            f.write(xml_content)
        print(f"[MUNG] Created sample MuNG XML graph at '{xml_path}'.")
        return xml_path

    def parse_mung_xml_to_note_events(self, xml_path: str) -> List[NoteEvent]:
        """
        Parses MuNG XML graph topology, walks outlink edges, computes pitch from staff line
        vertical position, and resolves duration from stem/beam node connections.
        """
        print(f"[MUNG] Parsing MuNG graph structure from '{xml_path}'...")
        tree = ET.parse(xml_path)
        root = tree.getroot()

        nodes: Dict[int, Dict[str, Any]] = {}
        for node_elem in root.findall("node"):
            n_id = int(node_elem.get("id"))
            cls_name = node_elem.get("class")
            top = float(node_elem.get("top"))
            left = float(node_elem.get("left"))
            bottom = float(node_elem.get("bottom"))
            right = float(node_elem.get("right"))

            outlinks = []
            outlinks_elem = node_elem.find("outlinks")
            if outlinks_elem is not None:
                for link in outlinks_elem.findall("link"):
                    outlinks.append({
                        "target": int(link.get("target")),
                        "type": link.get("type")
                    })

            nodes[n_id] = {
                "id": n_id,
                "class": cls_name,
                "bbox": [top, left, bottom, right],
                "y_center": (top + bottom) / 2.0,
                "x_center": (left + right) / 2.0,
                "outlinks": outlinks
            }

        # Find Clef node context
        clef_type = "g-clef"
        for n in nodes.values():
            if "clef" in n["class"]:
                clef_type = n["class"]
                break

        # Map Accidental Outlinks to Noteheads
        accidental_map: Dict[int, str] = {}
        for n in nodes.values():
            if "accidental" in n["class"]:
                acc_type = n["class"]
                for link in n["outlinks"]:
                    accidental_map[link["target"]] = acc_type

        # Reconstruct Note Events from Notehead Nodes
        events: List[NoteEvent] = []
        current_beat = 0.0

        for n_id, node in sorted(nodes.items(), key=lambda x: x[1]["x_center"]):
            cls = node["class"]
            if "notehead" not in cls:
                continue

            y_center = node["y_center"]
            
            # Pitch Estimation based on Staff Position (reference y=160 as G4 line, step=10px)
            staff_step = int(round((y_center - 100.0) / 10.0))
            staff_step = max(0, min(len(self.DIATONIC_PITCHES_G_CLEF) - 1, staff_step))
            base_pitch = self.DIATONIC_PITCHES_G_CLEF[staff_step]

            # Apply accidental modifier if linked
            if n_id in accidental_map:
                acc = accidental_map[n_id]
                if "sharp" in acc:
                    base_pitch = base_pitch[0] + "#" + base_pitch[1:]
                elif "flat" in acc:
                    base_pitch = base_pitch[0] + "b" + base_pitch[1:]

            # Duration Estimation based on Notehead Type & Outlink Edges
            has_stem = any(l["type"] == "has-stem" for l in node["outlinks"])
            has_beam = any(l["type"] == "has-beam" for l in node["outlinks"])

            if "empty" in cls:
                dur_name = "half" if has_stem else "whole"
                q_len = 2.0 if has_stem else 4.0
            else:
                if has_beam:
                    dur_name = "eighth"
                    q_len = 0.5
                elif has_stem:
                    dur_name = "quarter"
                    q_len = 1.0
                else:
                    dur_name = "quarter"
                    q_len = 1.0

            event = NoteEvent(
                id=n_id,
                onset_beat=current_beat,
                pitch_name=base_pitch,
                duration_name=dur_name,
                quarter_length=q_len,
                clef_context=clef_type
            )
            events.append(event)
            current_beat += q_len

        print(f"[MUNG] Reconstructed {len(events)} musical note events from graph topology.")
        return events
