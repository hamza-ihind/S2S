import os
from typing import List

def convert_pdf_to_images(pdf_path: str, output_dir: str, dpi: int = 300) -> List[str]:
    """
    Converts pages of a PDF score into high-resolution PNG image files.
    """
    os.makedirs(output_dir, exist_ok=True)
    image_paths = []

    try:
        import fitz  # PyMuPDF
        doc = fitz.open(pdf_path)
        
        # Render matrix for target DPI (72 DPI is base)
        zoom = dpi / 72.0
        mat = fitz.Matrix(zoom, zoom)

        for page_idx in range(len(doc)):
            page = doc.load_page(page_idx)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            
            img_filename = f"page_{page_idx + 1:03d}.png"
            img_path = os.path.join(output_dir, img_filename)
            pix.save(img_path)
            image_paths.append(img_path)

        doc.close()
    except Exception as e:
        raise RuntimeError(f"PDF page rendering failed: {str(e)}")

    return image_paths
