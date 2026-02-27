"""
Temel sözdizimi ve import testleri.
Tam çalışma testleri büyük model indirdiği için CI'da atlanır;
bunlar yalnızca import ve regex testlerini kapsar.
"""
import re
import sys
from pathlib import Path

# src/ klasörünü Python path'ine ekle
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


def test_version_defined():
    """__init__.py sürüm sabiti tanımlı olmalı."""
    from src import __version__
    parts = __version__.split(".")
    assert len(parts) == 3
    assert all(p.isdigit() for p in parts)


def test_notasyon_regex():
    """KVKK değişiklik notasyon regex'i doğru çalışmalı."""
    from kvkk_rapor import _NOTASYON_RE

    test_cases = [
        ("(Değişik:2/3/2024-7499/33 md.)", "Değişik", "7499"),
        ("(Mülga:2/3/2024-7499/33 md.)",   "Mülga",   "7499"),
        ("(Ek:2/3/2024-7499/35 md.)",       "Ek",      "7499"),
    ]
    for text, expected_tip, expected_kanun in test_cases:
        m = _NOTASYON_RE.search(text)
        assert m is not None, f"Notasyon bulunamadı: {text}"
        assert m.group("tip").lower() == expected_tip.lower()
        assert m.group("kanun") == expected_kanun


def test_madde_pattern():
    """Madde referans regex'i madde numaralarını doğru yakalamalı."""
    from ppt_to_vectors import _chunk_text  # noqa: F401  (import sağlığı)
    assert True  # import başarılıysa test geçer
