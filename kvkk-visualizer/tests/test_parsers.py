"""
KVKK Görselleştirici — Test Suite
====================================
PDF dosyalarına gerek kalmadan çalışan birim testler.
"""

import sys
import json
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

ROOT    = Path(__file__).resolve().parent.parent.parent
PDF_DIR = ROOT / "KVKK"
PDFS_EXIST = all((PDF_DIR / f).exists() for f in [
    "kvkk 1.5.6698.pdf", "sorularla-verbis.pdf",
    "veri-sorumlulari-sicil-bilgi-sistemi-kilavuzu.pdf",
])


# ════════════════════════════════════════════════════════════════
# 1 · IMPORT TESTLERİ
# ════════════════════════════════════════════════════════════════

def test_pdf_extractor_importable():
    import pdf_extractor  # noqa
    assert True

def test_law_parser_importable():
    import law_parser  # noqa
    assert True

def test_verbis_parser_importable():
    import verbis_parser  # noqa
    assert True

def test_dashboard_builder_importable():
    import dashboard_builder  # noqa
    assert True

def test_version_defined():
    from src import __version__
    parts = __version__.split(".")
    assert len(parts) == 3
    assert all(p.isdigit() for p in parts)


# ════════════════════════════════════════════════════════════════
# 2 · KANUN PARSER UNIT TESTLERİ
# ════════════════════════════════════════════════════════════════

def test_parse_law_with_empty_pages():
    """Boş sayfa listesiyle parse_law hata vermemeli."""
    from law_parser import parse_law
    result = parse_law([])
    assert "meta" in result
    assert "bolumler" in result
    assert "maddeler" in result
    assert "degisiklikler" in result


def test_parse_law_returns_expected_bolumler():
    """7 bölüm tanımlı olmalı."""
    from law_parser import parse_law
    result = parse_law([])
    assert len(result["bolumler"]) == 7


def test_parse_law_meta_fields():
    """Meta alanları kanun numarasını içermeli."""
    from law_parser import parse_law
    result = parse_law([])
    meta = result["meta"]
    assert meta["kanun_no"] == "6698"
    assert "madde_sayisi" in meta
    assert "bolum_sayisi" in meta


def test_parse_law_important_madde_flags():
    """Önemli maddeler işaretli olmalı."""
    from law_parser import parse_law, ONEMLI_MADDELER
    result = parse_law([])
    for no in ONEMLI_MADDELER:
        assert result["maddeler"][no]["onemli"] is True


def test_parse_law_degisik_maddeler():
    """7499 değişikliğine uğrayan maddeler 'degisik' olarak işaretlenmeli."""
    from law_parser import parse_law, DEGISIK_MADDELER
    result = parse_law([])
    for no in DEGISIK_MADDELER:
        assert result["maddeler"][no]["degisiklik_durumu"] == "degisik"


def test_parse_law_bolum_madde_coverage():
    """Her bölümün madde listesi boş olmamalı."""
    from law_parser import parse_law
    result = parse_law([])
    for bolum in result["bolumler"]:
        assert len(bolum["maddeler"]) > 0, f"Bölüm {bolum['no']} boş"


def test_parse_law_idari_cezalar():
    """İdari ceza haritası üst/alt sınır bilgisi içermeli."""
    from law_parser import parse_law
    result = parse_law([])
    cezalar = result["idari_cezalar"]
    assert len(cezalar) > 0
    for eylem, c in cezalar.items():
        assert "alt" in c and "ust" in c
        assert c["ust"] > c["alt"], f"{eylem}: üst < alt sınır!"


def test_parse_law_real_text():
    """Gerçek kanun metni parse edildiğinde madde 1 bulunmalı."""
    from law_parser import parse_law
    fake_pages = [{"page_no": 1, "text": "MADDE 1- (1) Bu Kanunun amacı…\nMADDE 2- (1) Bu Kanun hükümleri…"}]
    result = parse_law(fake_pages)
    assert 1 in result["maddeler"]
    assert result["maddeler"][1]["baslik"] == "Amaç"


def test_notasyon_regex_in_law():
    """Değişiklik notasyonu metinde doğru bulunmalı."""
    from law_parser import NOTASYON_RE
    text = "MADDE 9- (Değişik:2/3/2024-7499/34 md.) Kişisel veriler…"
    m = NOTASYON_RE.search(text)
    assert m is not None
    assert m.group("tip") == "Değişik"
    assert m.group("kanun") == "7499"


def test_find_bolum_helper():
    """_find_bolum madde 6'yı doğru bölüme atamalı."""
    from law_parser import _find_bolum, BOLUM_MAP
    bolum_no = _find_bolum(6)
    assert 6 in BOLUM_MAP[bolum_no]["maddeler"]


# ════════════════════════════════════════════════════════════════
# 3 · VERBİS PARSER UNIT TESTLERİ
# ════════════════════════════════════════════════════════════════

def test_verbis_kayit_adimlari_count():
    """6 kayıt adımı tanımlı olmalı."""
    from verbis_parser import KAYIT_ADIMLARI
    assert len(KAYIT_ADIMLARI) == 6

def test_verbis_kayit_adimlari_structure():
    """Her adım zorunlu alanlara sahip olmalı."""
    from verbis_parser import KAYIT_ADIMLARI
    required = {"adim", "baslik", "aciklama", "gereksinimler", "ikon", "renk", "sure"}
    for adim in KAYIT_ADIMLARI:
        assert required.issubset(adim.keys()), f"Adım {adim.get('adim')}: eksik alan"
        assert adim["adim"] >= 1
        assert len(adim["gereksinimler"]) > 0

def test_verbis_kayit_order():
    """Adımlar sıralı 1–6 olmalı."""
    from verbis_parser import KAYIT_ADIMLARI
    assert [a["adim"] for a in KAYIT_ADIMLARI] == list(range(1, 7))

def test_verbis_sss_not_empty():
    """SSS listesi boş olmamalı."""
    from verbis_parser import VERBIS_SSS
    assert len(VERBIS_SSS) >= 5

def test_verbis_sss_structure():
    """Her SSS girişi soru, cevap ve kategori içermeli."""
    from verbis_parser import VERBIS_SSS
    for s in VERBIS_SSS:
        assert "soru"     in s and len(s["soru"])   > 5
        assert "cevap"    in s and len(s["cevap"])  > 10
        assert "kategori" in s and len(s["kategori"]) > 0

def test_verbis_sss_has_important():
    """En az bir önemli SSS bulunmalı."""
    from verbis_parser import VERBIS_SSS
    assert any(s.get("onemli") for s in VERBIS_SSS)

def test_verbis_stats_structure():
    """VERBİS istatistikleri işleme hacmi ve hukuki dayanak içermeli."""
    from verbis_parser import VERBIS_STATS
    assert "islem_hacimleri"  in VERBIS_STATS
    assert "hukuki_dayanaklar" in VERBIS_STATS
    assert sum(VERBIS_STATS["islem_hacimleri"].values())  == 100
    assert sum(VERBIS_STATS["hukuki_dayanaklar"].values()) == 100

def test_parse_verbis_qa_structure():
    """parse_verbis_qa doğru anahtar yapısı döndürmeli."""
    from verbis_parser import parse_verbis_qa
    result = parse_verbis_qa([{"page_no": 1, "text": "Test"}])
    assert "sss"            in result
    assert "kategoriler"    in result
    assert "kayit_adimlari" in result
    assert "stats"          in result

def test_parse_verbis_guide_structure():
    """parse_verbis_guide doğru anahtar yapısı döndürmeli."""
    from verbis_parser import parse_verbis_guide
    result = parse_verbis_guide([{"page_no": 1, "text": "Test"}])
    assert "sistem_ozellikleri" in result
    assert len(result["sistem_ozellikleri"]) > 0


# ════════════════════════════════════════════════════════════════
# 4 · DASHBOARD BUILDER UNIT TESTLERİ
# ════════════════════════════════════════════════════════════════

def _make_minimal_law():
    from law_parser import parse_law
    return parse_law([{"page_no": 1, "text": "MADDE 1- Amaç maddesi metni burada."}])

def _make_minimal_verbis():
    from verbis_parser import parse_verbis_qa
    return parse_verbis_qa([{"page_no": 1, "text": ""}])

def _make_minimal_guide():
    from verbis_parser import parse_verbis_guide
    return parse_verbis_guide([{"page_no": 1, "text": ""}])


def test_build_dashboard_returns_html():
    """build_dashboard geçerli HTML döndürmeli."""
    from dashboard_builder import build_dashboard
    html = build_dashboard(_make_minimal_law(), _make_minimal_verbis(), _make_minimal_guide())
    assert "<!DOCTYPE html>" in html
    assert "<html" in html
    assert "KVKK" in html

def test_build_dashboard_has_tabs():
    """Dashboard 5 sekme içermeli."""
    from dashboard_builder import build_dashboard
    html = build_dashboard(_make_minimal_law(), _make_minimal_verbis(), _make_minimal_guide())
    assert "tab-kanun"        in html
    assert "tab-verbis"       in html
    assert "tab-sss"          in html
    assert "tab-stats"        in html
    assert "tab-degisiklik"   in html

def test_build_dashboard_has_chartjs():
    """Chart.js CDN linki mevcut olmalı."""
    from dashboard_builder import build_dashboard
    html = build_dashboard(_make_minimal_law(), _make_minimal_verbis(), _make_minimal_guide())
    assert "chart.js" in html.lower()

def test_build_dashboard_has_bootstrap():
    """Bootstrap CDN linki mevcut olmalı."""
    from dashboard_builder import build_dashboard
    html = build_dashboard(_make_minimal_law(), _make_minimal_verbis(), _make_minimal_guide())
    assert "bootstrap" in html.lower()

def test_build_dashboard_contains_kanun_no():
    """Kanun numarası 6698 dashboardda yer almalı."""
    from dashboard_builder import build_dashboard
    html = build_dashboard(_make_minimal_law(), _make_minimal_verbis(), _make_minimal_guide())
    assert "6698" in html

def test_build_dashboard_contains_ceza_table():
    """İdari para cezası tablosu yer almalı."""
    from dashboard_builder import build_dashboard
    html = build_dashboard(_make_minimal_law(), _make_minimal_verbis(), _make_minimal_guide())
    assert "Kabahat" in html
    assert "Alt Sınır" in html

def test_build_dashboard_contains_verbis_steps():
    """VERBİS kayıt adımları dashboardda görünmeli."""
    from dashboard_builder import build_dashboard
    html = build_dashboard(_make_minimal_law(), _make_minimal_verbis(), _make_minimal_guide())
    assert "Adım 1" in html or "adim-1" in html or "step-card" in html

def test_build_and_save_creates_file(tmp_path):
    """build_and_save dosyayı oluşturmalı."""
    from dashboard_builder import build_and_save
    out = tmp_path / "test_dashboard.html"
    result = build_and_save(_make_minimal_law(), _make_minimal_verbis(), _make_minimal_guide(), out_path=out)
    assert result.exists()
    assert result.stat().st_size > 50_000  # en az 50KB

def test_chart_data_json_valid():
    """Chart JSON verisi geçerli JSON olmalı."""
    from dashboard_builder import _chart_data_json
    j = _chart_data_json(_make_minimal_law(), _make_minimal_verbis())
    d = json.loads(j)
    assert "bolum_kelime"      in d
    assert "islem_hacimleri"   in d
    assert "hukuki_dayanaklar" in d


# ════════════════════════════════════════════════════════════════
# 5 · PDF EXTRACTOR TESTLERİ (PDF varsa)
# ════════════════════════════════════════════════════════════════

@pytest.mark.skipif(not PDFS_EXIST, reason="KVKK PDF dosyaları bulunamadı")
def test_extract_law_pdf():
    """Kanun PDF'i 20+ sayfa içermeli."""
    from pdf_extractor import extract_pdf
    pages = extract_pdf("law")
    assert len(pages) >= 20
    assert all("page_no" in p and "text" in p for p in pages)

@pytest.mark.skipif(not PDFS_EXIST, reason="KVKK PDF dosyaları bulunamadı")
def test_extract_verbis_qa_pdf():
    """VERBİS Q&A PDF'i 55+ sayfa içermeli."""
    from pdf_extractor import extract_pdf
    pages = extract_pdf("verbis_qa")
    assert len(pages) >= 55

@pytest.mark.skipif(not PDFS_EXIST, reason="KVKK PDF dosyaları bulunamadı")
def test_extract_verbis_guide_pdf():
    """VERBİS Kılavuzu PDF'i 90+ sayfa içermeli."""
    from pdf_extractor import extract_pdf
    pages = extract_pdf("verbis_guide")
    assert len(pages) >= 90

@pytest.mark.skipif(not PDFS_EXIST, reason="KVKK PDF dosyaları bulunamadı")
def test_law_pdf_contains_madde():
    """Kanun PDF metni 'MADDE' kelimesini içermeli."""
    from pdf_extractor import extract_pdf, get_full_text
    pages = extract_pdf("law")
    full  = get_full_text(pages)
    assert "MADDE" in full
    assert "6698"  in full

@pytest.mark.skipif(not PDFS_EXIST, reason="KVKK PDF dosyaları bulunamadı")
def test_full_pipeline():
    """Uçtan uca: PDF → parse → dashboard HTML üretimi."""
    from pdf_extractor    import extract_all
    from law_parser       import parse_law
    from verbis_parser    import parse_verbis_qa, parse_verbis_guide
    from dashboard_builder import build_dashboard

    raw          = extract_all()
    law          = parse_law(raw["law"])
    verbis_qa    = parse_verbis_qa(raw["verbis_qa"])
    verbis_guide = parse_verbis_guide(raw["verbis_guide"])

    html = build_dashboard(law, verbis_qa, verbis_guide)
    assert len(html) > 50_000  # zengin içerik
    assert "Madde 9" in html     # değişikliğe uğramış madde
    assert "7499"    in html     # değiştiren kanun
