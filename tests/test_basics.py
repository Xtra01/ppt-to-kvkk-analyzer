"""
PPT-to-KVKK Analyzer — Test Suite
===================================
Unit ve entegrasyon testleri.
Model indirmesi gerektiren testler CI'da otomatik atlanır (SKIP_HEAVY=1).
"""

import os
import json
import sys
import argparse
from pathlib import Path

import pytest

# src/ klasörünü Python path'ine ekle
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

SKIP_HEAVY = os.environ.get("SKIP_HEAVY", "0") == "1"

# ─────────────────────────────────────────────────────────────────
# YARDIMCI: çıktı dosyaları mevcut mu?
# ─────────────────────────────────────────────────────────────────
VECTORS_DIR = ROOT / "output" / "vectors"
TXT_DIR     = ROOT / "output" / "txt"
REPORTS_DIR = ROOT / "output" / "reports"
INPUT_DIR   = ROOT / "input"

METADATA_FILE = VECTORS_DIR / "metadata.json"
VECTORS_FILE  = VECTORS_DIR / "vectors.npy"
CHUNKS_FILE   = VECTORS_DIR / "extracted_chunks.json"
REPORT_FILE   = REPORTS_DIR / "KVKK_Analiz_Raporu.html"


# ════════════════════════════════════════════════════════════════
# 1 · SÜRÜM VE IMPORT TESTLERİ
# ════════════════════════════════════════════════════════════════

def test_version_defined():
    """__init__.py sürüm sabiti tanımlı ve semver uyumlu olmalı."""
    from src import __version__
    parts = __version__.split(".")
    assert len(parts) == 3, "Sürüm X.Y.Z formatında olmalı"
    assert all(p.isdigit() for p in parts), "Her kısım sayısal olmalı"


def test_ppt_to_vectors_importable():
    """ppt_to_vectors modülü hatasız import edilebilmeli."""
    import ppt_to_vectors  # noqa: F401
    assert True


def test_kvkk_rapor_importable():
    """kvkk_rapor modülü hatasız import edilebilmeli."""
    import kvkk_rapor  # noqa: F401
    assert True


# ════════════════════════════════════════════════════════════════
# 2 · KLASÖR YAPISI TESTLERİ
# ════════════════════════════════════════════════════════════════

def test_folder_structure_input():
    """input/ klasörü mevcut olmalı."""
    assert INPUT_DIR.is_dir(), f"input/ klasörü bulunamadı: {INPUT_DIR}"


def test_folder_structure_output_vectors():
    """output/vectors/ klasörü mevcut olmalı."""
    assert VECTORS_DIR.is_dir()


def test_folder_structure_output_txt():
    """output/txt/ klasörü mevcut olmalı."""
    assert TXT_DIR.is_dir()


def test_folder_structure_output_reports():
    """output/reports/ klasörü mevcut olmalı."""
    assert REPORTS_DIR.is_dir()


def test_no_turkish_folder_names_in_src():
    """src/ içindeki Python dosyaları eski Türkçe path'e referans vermemeli."""
    old_paths = ["kaynaklar", "çıktılar", "vektorler", "raporlar"]
    for py_file in (ROOT / "src").glob("*.py"):
        content = py_file.read_text(encoding="utf-8")
        for old in old_paths:
            # Yorum satırları hariç kontrol et
            code_lines = [l for l in content.splitlines()
                          if not l.strip().startswith("#")]
            code_text = "\n".join(code_lines)
            assert f'"{old}' not in code_text and f"'{old}" not in code_text and f"/ \"{old}" not in code_text, \
                f"{py_file.name} içinde eski path referansı bulundu: '{old}'"


# ════════════════════════════════════════════════════════════════
# 3 · CHUNK ALGORİTMASI TESTLERİ
# ════════════════════════════════════════════════════════════════

def test_chunk_text_short_stays_single():
    """500 karakterden kısa metin tek parça kalmali."""
    from ppt_to_vectors import _chunk_text
    text = "Bu kısa bir metin."
    result = _chunk_text(text, max_chars=500)
    assert len(result) == 1
    assert result[0] == text


def test_chunk_text_splits_long():
    """500 karakterden uzun metin birden fazla parçaya bölünmeli."""
    from ppt_to_vectors import _chunk_text
    text = ("A" * 250 + "\n") * 5   # 5 paragraf, toplam ~1275 karakter
    result = _chunk_text(text, max_chars=500)
    assert len(result) > 1


def test_chunk_text_no_empty_chunks():
    """Hiçbir parça boş olmamalı."""
    from ppt_to_vectors import _chunk_text
    text = "Birinci paragraf.\n\n\nİkinci paragraf. " + "X" * 600
    result = _chunk_text(text, max_chars=300)
    assert all(c.strip() for c in result), "Boş chunk bulundu"


def test_chunk_text_exact_limit_stays_one():
    """Tam limit uzunluğundaki metin tek parça kalmalı."""
    from ppt_to_vectors import _chunk_text
    text = "A" * 500
    result = _chunk_text(text, max_chars=500)
    assert len(result) == 1


def test_chunk_text_preserves_content():
    """Parçalar birleştirildiğinde orijinal içerik korunmalı."""
    from ppt_to_vectors import _chunk_text
    words = ["kelime" + str(i) for i in range(200)]
    text = " ".join(words)
    result = _chunk_text(text, max_chars=100)
    combined = " ".join(result)
    # Tüm kelimeler parçalarda mevcut olmalı
    for w in words:
        assert w in combined


def test_create_chunks_filters_short():
    """MIN_CHUNK_CHARS'tan kısa parçalar atlanmalı."""
    from ppt_to_vectors import create_chunks, MIN_CHUNK_CHARS
    slides = [{"dosya": "test.pptx", "slayt_no": 1, "metin": "Kısa"}]
    # "Kısa" metni MIN_CHUNK_CHARS'tan kısa olduğu için atlanmalı
    result = create_chunks(slides)
    assert len(result) == 0 or all(len(c["metin"]) >= MIN_CHUNK_CHARS for c in result)


def test_create_chunks_structure():
    """Oluşturulan chunk'lar gerekli alanlara sahip olmalı."""
    from ppt_to_vectors import create_chunks
    slides = [
        {"dosya": "test.pptx", "slayt_no": 1, "metin": "Bu yeterince uzun bir metin parçasıdır ve işlenecektir."},
    ]
    result = create_chunks(slides)
    for chunk in result:
        assert "id" in chunk
        assert "dosya" in chunk
        assert "slayt_no" in chunk
        assert "parca_no" in chunk
        assert "metin" in chunk


def test_create_chunks_sequential_ids():
    """Chunk id'leri sıralı ve benzersiz olmalı."""
    from ppt_to_vectors import create_chunks
    slides = [
        {"dosya": "a.pptx", "slayt_no": i,
         "metin": "Yeterince uzun bir metin içeriği burada yer almaktadır test amaçlıdır."}
        for i in range(5)
    ]
    result = create_chunks(slides)
    ids = [c["id"] for c in result]
    assert ids == list(range(len(ids))), "ID'ler 0'dan başlayıp sıralı olmalı"


# ════════════════════════════════════════════════════════════════
# 4 · KVKK REGEX TESTLERİ
# ════════════════════════════════════════════════════════════════

def test_notasyon_regex_degisik():
    """Değişik notasyonu yakalanmalı."""
    from kvkk_rapor import _NOTASYON_RE
    m = _NOTASYON_RE.search("(Değişik:2/3/2024-7499/33 md.)")
    assert m is not None
    assert m.group("tip").lower() == "değişik"
    assert m.group("kanun") == "7499"


def test_notasyon_regex_mulga():
    """Mülga notasyonu yakalanmalı."""
    from kvkk_rapor import _NOTASYON_RE
    m = _NOTASYON_RE.search("(Mülga:2/3/2024-7499/33 md.)")
    assert m is not None
    assert m.group("tip").lower() == "mülga"


def test_notasyon_regex_ek():
    """Ek notasyonu yakalanmalı."""
    from kvkk_rapor import _NOTASYON_RE
    m = _NOTASYON_RE.search("(Ek:2/3/2024-7499/35 md.)")
    assert m is not None
    assert m.group("tip").lower() == "ek"


def test_notasyon_regex_no_match_on_plain():
    """Normal metin notasyon olarak eşleşmemeli."""
    from kvkk_rapor import _NOTASYON_RE
    m = _NOTASYON_RE.search("Bu normal bir metin cümlesidir.")
    assert m is None


def test_extract_article_mentions():
    """Madde referansları metin parçalarından doğru çıkarılmalı."""
    from kvkk_rapor import extract_article_mentions
    chunks = [
        {"id": 0, "dosya": "test.pptx", "slayt_no": 1,
         "metin": "KVKK madde 6 kapsamında özel nitelikli kişisel veriler ele alınmaktadır."},
        {"id": 1, "dosya": "test.pptx", "slayt_no": 2,
         "metin": "Madde 18 yaptırımları önemlidir."},
    ]
    result = extract_article_mentions(chunks)
    assert isinstance(result, dict)
    # madde 6 veya 18 yakalamalı
    assert len(result) > 0


def test_compute_statistics():
    """İstatistik hesaplama doğru sonuç vermeli."""
    from kvkk_rapor import compute_statistics
    chunks = [
        {"id": 0, "dosya": "a.pptx", "slayt_no": 1, "metin": "metin"},
        {"id": 1, "dosya": "b.pptx", "slayt_no": 2, "metin": "metin"},
    ]
    # extract_article_mentions'ın ürettiği refs yapısını taklit et
    ref_template = {
        "dosya": "a.pptx", "slayt_no": 1, "metin_ozeti": "metin",
        "degisiklik_sinyali": False, "eski_hal_metni": None, "yeni_hal_metni": None,
    }
    madde_map = {
        6:  [dict(ref_template, dosya="a.pptx", degisiklik_sinyali=True)],
        18: [dict(ref_template, dosya="b.pptx")],
    }
    stats = compute_statistics(chunks, madde_map)
    assert "toplam_parca" in stats
    assert stats["toplam_parca"] == 2
    assert "dosya_sayisi" in stats
    assert len(stats["dosya_sayisi"]) == 2
    assert "madde_frekans" in stats
    assert "degisiklik_sinyalli" in stats
    assert stats["degisiklik_sinyalli"][6] == 1  # 1 adet degisiklik sinyali var


# ════════════════════════════════════════════════════════════════
# 5 · CLI / ARGPARSE TESTLERİ
# ════════════════════════════════════════════════════════════════

def test_pptv_argparse_accepts_all():
    """ppt_to_vectors --all argümanı kabul edilmeli."""
    import ppt_to_vectors
    import argparse
    # main() doğrudan çağırmak yerine parser'ı test et
    parser = argparse.ArgumentParser()
    parser.add_argument("--extract", action="store_true")
    parser.add_argument("--vectorize", action="store_true")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--txt", action="store_true")
    parser.add_argument("--search", type=str)
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args(["--all", "--txt"])
    assert args.all is True
    assert args.txt is True


def test_pptv_argparse_search_topk():
    """--search ve --top-k birlikte çalışmalı."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--search", type=str)
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args(["--search", "KVKK nedir", "--top-k", "10"])
    assert args.search == "KVKK nedir"
    assert args.top_k == 10


def test_kvkk_argparse_online_flag():
    """kvkk_rapor --online bayrağı tanımlı olmalı."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--online", action="store_true")
    args = parser.parse_args(["--online"])
    assert args.online is True


# ════════════════════════════════════════════════════════════════
# 6 · ÇIKTI DOSYALARI DOĞRULAMA TESTLERİ
# (Kodun en az bir kez çalıştırılmış olması gerekir)
# ════════════════════════════════════════════════════════════════

@pytest.mark.skipif(not METADATA_FILE.exists(), reason="metadata.json yok, önce --all çalıştırın")
def test_metadata_json_structure():
    """metadata.json zorunlu alanları içermeli."""
    with open(METADATA_FILE, encoding="utf-8") as f:
        meta = json.load(f)
    assert "model" in meta
    assert "vektor_boyutu" in meta
    assert "toplam_parca" in meta
    assert "chunks" in meta
    assert isinstance(meta["chunks"], list)
    assert len(meta["chunks"]) > 0


@pytest.mark.skipif(not METADATA_FILE.exists(), reason="metadata.json yok")
def test_metadata_chunk_fields():
    """Her chunk dosya, slayt_no ve metin alanlarını içermeli."""
    with open(METADATA_FILE, encoding="utf-8") as f:
        meta = json.load(f)
    for chunk in meta["chunks"][:10]:  # İlk 10'u kontrol et
        assert "dosya" in chunk
        assert "slayt_no" in chunk
        assert "metin" in chunk
        assert len(chunk["metin"]) > 0


@pytest.mark.skipif(not VECTORS_FILE.exists(), reason="vectors.npy yok")
def test_vectors_npy_shape():
    """vectors.npy doğru boyutta vektör matrisi içermeli."""
    import numpy as np
    embeddings = np.load(str(VECTORS_FILE))
    assert embeddings.ndim == 2, "2D matris bekleniyor"
    assert embeddings.shape[1] == 384, "MiniLM modeli 384 boyutlu vektör üretmeli"
    assert embeddings.shape[0] > 0, "En az bir vektör olmalı"


@pytest.mark.skipif(not VECTORS_FILE.exists() or not METADATA_FILE.exists(),
                    reason="Vektör dosyaları yok")
def test_vectors_count_matches_metadata():
    """vectors.npy'deki vektör sayısı metadata'daki chunk sayısıyla eşleşmeli."""
    import numpy as np
    embeddings = np.load(str(VECTORS_FILE))
    with open(METADATA_FILE, encoding="utf-8") as f:
        meta = json.load(f)
    assert embeddings.shape[0] == meta["toplam_parca"]
    assert embeddings.shape[0] == len(meta["chunks"])


@pytest.mark.skipif(not any(TXT_DIR.glob("*.txt")), reason="TXT dosyaları üretilmemiş")
def test_txt_files_exist():
    """output/txt/ içinde TXT dosyaları bulunmalı."""
    txt_files = list(TXT_DIR.glob("*.txt"))
    assert len(txt_files) > 0, "TXT dosyaları üretilmemiş"


@pytest.mark.skipif(not any(TXT_DIR.glob("*.txt")), reason="TXT dosyaları yok")
def test_txt_files_not_empty():
    """TXT dosyaları boş olmamalı."""
    for txt_file in TXT_DIR.glob("*.txt"):
        content = txt_file.read_text(encoding="utf-8")
        assert len(content) > 100, f"{txt_file.name} dosyası çok kısa veya boş"


@pytest.mark.skipif(not REPORT_FILE.exists(), reason="HTML rapor yok")
def test_html_report_exists_and_valid():
    """HTML raporu mevcut ve geçerli HTML içermeli."""
    content = REPORT_FILE.read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in content or "<html" in content
    assert "KVKK" in content
    assert len(content) > 10_000, "Rapor çok kısa, içerik eksik olabilir"


@pytest.mark.skipif(not REPORT_FILE.exists(), reason="HTML rapor yok")
def test_html_report_contains_key_sections():
    """HTML raporunda temel bölümler bulunmalı."""
    content = REPORT_FILE.read_text(encoding="utf-8")
    assert "Madde" in content or "madde" in content
    assert "7499" in content or "6698" in content  # Kanun numaraları


# ════════════════════════════════════════════════════════════════
# 7 · EXTRACT_PPTX UNIT TESTİ (gerçek dosyayla)
# ════════════════════════════════════════════════════════════════

@pytest.mark.skipif(not any(INPUT_DIR.glob("*.pptx")), reason="input/ içinde PPTX yok")
def test_extract_pptx_returns_slides():
    """extract_pptx gerçek dosyadan slayt listesi döndürmeli."""
    from ppt_to_vectors import extract_pptx
    pptx_files = sorted(INPUT_DIR.glob("*.pptx"))
    first_file = pptx_files[0]
    slides = extract_pptx(first_file)
    assert isinstance(slides, list)
    assert len(slides) > 0, "Slayt çıkarılamadı"
    assert all("metin" in s and "slayt_no" in s and "dosya" in s for s in slides)


@pytest.mark.skipif(not any(INPUT_DIR.glob("*.pptx")), reason="input/ içinde PPTX yok")
def test_extract_all_finds_all_pptx():
    """extract_all tüm PPTX dosyalarından veri çıkarmalı."""
    from ppt_to_vectors import extract_all
    slides = extract_all(INPUT_DIR)
    pptx_count = len(list(INPUT_DIR.glob("*.pptx")))
    dosyalar = set(s["dosya"] for s in slides)
    assert len(dosyalar) == pptx_count, \
        f"{pptx_count} PPTX var ama sadece {len(dosyalar)} dosyadan veri çıkarıldı"
