import os
import io
from PIL import Image
import pytesseract
try:
    import fitz
except ImportError:
    fitz = None

class OCR:
    SUPPORTED = (".txt", ".pdf", ".jpg", ".jpeg", ".png")

    def __init__(self, lang="pol", tesseract_cmd=r'C:\Program Files\Tesseract-OCR\tesseract.exe', min_native_chars=20, dpi=300):
        self.lang = lang
        self.min_native_chars = min_native_chars
        self.dpi = dpi
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    def extract(self, path):
        ext = os.path.splitext(path)[1].lower()
        if ext == ".txt":
            return self._read_txt(path)
        elif ext == ".pdf":
            return self._read_pdf(path)
        elif ext in (".jpg", ".jpeg", ".png"):
            return self._read_image(path)
        raise ValueError(f"nieobsługiwany format pliku: {ext or '(brak rozszerzenia)'}")

    def _read_txt(self, path):
        for encoding in ("utf-8", "cp1250", "latin-2"):
            try:
                with open(path, "r", encoding=encoding) as f:
                    return f.read()
            except (UnicodeDecodeError, LookupError):
                continue
        with open(path, "rb") as f:
            return f.read().decode("utf-8", errors="ignore")

    def _read_pdf(self, path):
        if fitz is None:
            raise RuntimeError(
                "brak biblioteki PyMuPDF - zainstaluj przez: pip install pymupdf"
            )
        parts = []
        pdf = fitz.open(path)
        try:
            for page in pdf:
                native_text = page.get_text().strip()
                if len(native_text) >= self.min_native_chars:
                    parts.append(native_text)
                else:
                    # brak warstwy tekstowej -> to skan, rób OCR na obrazie strony
                    pix = page.get_pixmap(dpi=self.dpi)
                    img = Image.open(io.BytesIO(pix.tobytes("png")))
                    parts.append(self._ocr_image(img))
        finally:
            pdf.close()
        return "\n".join(parts)

    # -- obrazy ----------------------------------------------------------
    def _read_image(self, path):
        return self._ocr_image(Image.open(path))

    def _ocr_image(self, img):
        img = self._preprocess(img)
        return pytesseract.image_to_string(img, lang=self.lang)

    @staticmethod
    def _preprocess(img):
        img = img.convert("L")
        w, h = img.size
        if max(w, h) < 1500:
            scale = 1500 / max(w, h)
            img = img.resize((round(w * scale), round(h * scale)), Image.LANCZOS)
        return img