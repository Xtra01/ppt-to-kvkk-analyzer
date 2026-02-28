"""
PDF Metin Çıkarıcı
==================
KVKK klasöründeki PDF belgelerinden metin çıkarır ve JSON formatında önbelleğe alır.
Dosya boyutları büyük olduğundan önbellekleme performans için kritiktir.
"""

import json
import io
import sys
import logging
from pathlib import Path
from typing import Dict, List

# Windows konsolunda UTF-8
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger(__name__)

# ── Dizin Ayarları ───────────────────────────────────────────────
BASE_DIR  = Path(__file__).resolve().parent.parent          # kvkk-visualizer/
ROOT_DIR  = BASE_DIR.parent                                 # ppt to text/
PDF_DIR   = ROOT_DIR / "KVKK"                               # KVKK/*.pdf
CACHE_DIR = BASE_DIR / "output" / "cache"                   # önbellek JSON'ları

PDF_FILES = {
    "law":          "kvkk 1.5.6698.pdf",
    "verbis_qa":    "sorularla-verbis.pdf",
    "verbis_guide": "veri-sorumlulari-sicil-bilgi-sistemi-kilavuzu.pdf",
}


def extract_pdf(name: str, force: bool = False) -> List[Dict]:
    """
    PDF'den sayfa bazında metin çıkarır.

    Returns:
        [{"page_no": int, "text": str}, ...]
    """
    pdf_path  = PDF_DIR  / PDF_FILES[name]
    cache_path = CACHE_DIR / f"{name}_pages.json"

    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    if cache_path.exists() and not force:
        logger.info(f"  ← Önbellekten okunuyor: {name}")
        with open(cache_path, encoding="utf-8") as f:
            return json.load(f)

    if not pdf_path.exists():
        logger.error(f"PDF bulunamadı: {pdf_path}")
        return []

    logger.info(f"  → PDF okunuyor: {pdf_path.name}")
    import pdfplumber

    pages: List[Dict] = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            pages.append({
                "page_no": i,
                "text":    text.strip(),
            })

    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(pages, f, ensure_ascii=False, indent=2)

    logger.info(f"    ✓ {len(pages)} sayfa çıkarıldı → {cache_path.name}")
    return pages


def extract_all(force: bool = False) -> Dict[str, List[Dict]]:
    """Tüm PDF'leri çıkarır/önbellekten döndürür."""
    result = {}
    for name in PDF_FILES:
        result[name] = extract_pdf(name, force=force)
    return result


def get_full_text(pages: List[Dict]) -> str:
    """Sayfa listesini tek metin string'ine birleştirir."""
    return "\n\n".join(p["text"] for p in pages if p["text"])


if __name__ == "__main__":
    logger.info("Tüm PDF'ler çıkarılıyor…")
    data = extract_all()
    for name, pages in data.items():
        logger.info(f"  {name}: {len(pages)} sayfa")
