import os
from typing import List

def convert_pdf_to_images(pdf_path: str, output_dir: str, dpi: int = 300) -> List[str]:
    """
    Converts pages of a PDF score into high-resolution PNG image files.
    Tries PyMuPDF (fitz) first, falling back to pdf2image if fitz is unavailable.
    """
    os.makedirs(output_dir, exist_ok=True)
    image_paths = []
    errors = []

    # 1. Try PyMuPDF (fitz)
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(pdf_path)
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
        if image_paths:
            return image_paths
    except Exception as e:
        errors.append(f"PyMuPDF error: {str(e)}")

    # 2. Fallback to pdf2image
    try:
        from pdf2image import convert_from_path
        pages = convert_from_path(pdf_path, dpi=dpi)
        for page_idx, page in enumerate(pages):
            img_filename = f"page_{page_idx + 1:03d}.png"
            img_path = os.path.join(output_dir, img_filename)
            page.save(img_path, "PNG")
            image_paths.append(img_path)

        if image_paths:
            return image_paths
    except Exception as e:
        errors.append(f"pdf2image error: {str(e)}")

    raise RuntimeError(f"PDF page rendering failed: {'; '.join(errors)}")

