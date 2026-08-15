# MUSCIMA++ Dataset Loader Scaffolding (Phase 2 Detection & Graph Reconstruction)
import os
import xml.etree.ElementTree as ET

class MUSCIMAPlusPlusLoader:
    """
    Scaffolding loader for the MUSCIMA++ dataset.
    Provides node graphs (CropObject annotations with staff-line locations and parent-child relationships).
    """
    def __init__(self, dataset_dir=None):
        self.dataset_dir = dataset_dir
        self.crop_objects = []
        if dataset_dir and os.path.exists(dataset_dir):
            self._parse_muscima_xmls()
        else:
            print(f"ℹ️ MUSCIMA++ dataset directory '{dataset_dir}' not populated yet (Scaffolding ready for Phase 2).")

    def _parse_muscima_xmls(self):
        for root_dir, _, files in os.walk(self.dataset_dir):
            for file in files:
                if file.endswith(".xml"):
                    xml_path = os.path.join(root_dir, file)
                    tree = ET.parse(xml_path)
                    for crop_obj in tree.getroot().findall(".//CropObject"):
                        self.crop_objects.append(crop_obj)
        print(f"✅ Loaded {len(self.crop_objects)} MUSCIMA++ CropObjects.")
