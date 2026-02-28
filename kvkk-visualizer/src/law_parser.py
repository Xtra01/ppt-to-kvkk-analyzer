"""
6698 Sayılı KVKK Kanun Ayrıştırıcı
=====================================
PDF metninden kanun maddelerini, bölümlerini ve değişiklik notasyonlarını çıkarır.
"""

import re
import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ── Regex Desenleri ──────────────────────────────────────────────
NOTASYON_RE = re.compile(
    r"\((?P<tip>Değişik|Mülga|Ek)\s*:\s*(?P<tarih>[^-\)]+?)-(?P<kanun>\d+)/(?P<fıkra>\d+)\s*md\.\)",
    re.IGNORECASE | re.UNICODE,
)

MADDE_SPLIT_RE = re.compile(r"(?=^MADDE\s+\d+[-–])", re.MULTILINE)
MADDE_NO_RE    = re.compile(r"^MADDE\s+(\d+)[-–]", re.MULTILINE)

BOLUM_RE = re.compile(
    r"^(BİRİNCİ|İKİNCİ|ÜÇÜNCÜ|DÖRDÜNCÜ|BEŞİNCİ|ALTINCI|YEDİNCİ)\s+BÖLÜM\s*\n(.+?)$",
    re.MULTILINE | re.IGNORECASE,
)

# ── Statik Meta Veriler ──────────────────────────────────────────
BOLUM_MAP = {
    1: {"sira": "BİRİNCİ", "baslik": "Amaç, Kapsam ve Tanımlar",                  "maddeler": list(range(1, 4))},
    2: {"sira": "İKİNCİ",  "baslik": "Kişisel Verilerin İşlenmesi",               "maddeler": list(range(4, 11))},
    3: {"sira": "ÜÇÜNCÜ",  "baslik": "Yükümlülükler",                             "maddeler": list(range(11, 15))},
    4: {"sira": "DÖRDÜNCÜ","baslik": "Başvuru, Şikâyet ve İtiraz",                "maddeler": list(range(15, 17))},
    5: {"sira": "BEŞİNCİ", "baslik": "Kişisel Verileri Koruma Kurumu",            "maddeler": list(range(17, 27))},
    6: {"sira": "ALTINCI",  "baslik": "Suçlar ve Kabahatler",                     "maddeler": [27, 28]},
    7: {"sira": "YEDİNCİ", "baslik": "Çeşitli ve Son Hükümler",                  "maddeler": list(range(29, 33))},
}

MADDE_BASLIKLAR: Dict[int, str] = {
    1:  "Amaç",
    2:  "Kapsam",
    3:  "Tanımlar",
    4:  "Genel İlkeler",
    5:  "Kişisel Verilerin İşlenme Şartları",
    6:  "Özel Nitelikli Kişisel Verilerin İşlenme Şartları",
    7:  "Kişisel Verilerin Silinmesi, Yok Edilmesi veya Anonim Hâle Getirilmesi",
    8:  "Kişisel Verilerin Aktarılması",
    9:  "Kişisel Verilerin Yurt Dışına Aktarılması",
    10: "Aydınlatma Yükümlülüğü",
    11: "İlgili Kişinin Hakları",
    12: "Veri Güvenliğine İlişkin Yükümlülükler",
    13: "İlgili Kişinin Başvuru Hakkı",
    14: "Kurula Şikâyet",
    15: "Kurulun İnceleme Usulü",
    16: "Veri Sorumluları Sicili (VERBİS)",
    17: "Suçlar",
    18: "Kabahatler (İdari Para Cezaları)",
    19: "Kurul",
    20: "Kurul Üyeliği",
    21: "Üyeliğin Sona Ermesi",
    22: "Kurul'un Görev ve Yetkileri",
    23: "Kurum Yapısı ve Bütçesi",
    24: "Başkan'ın Görev ve Yetkileri",
    25: "İkinci Başkan",
    26: "Ana Hizmet Birimleri",
    27: "Suçlara İlişkin Hükümler",
    28: "Kabahatlere İlişkin Hükümler",
    29: "Veri İşleme Şartlarına Geçiş",
    30: "Kurul Üyelerine İlişkin Geçiş",
    31: "Personele İlişkin Geçiş",
    32: "Yürürlükten Kaldırılan Hükümler",
}

# Önemli maddeler (anasayfada vurgulanan)
ONEMLI_MADDELER = {6, 9, 10, 11, 12, 16, 18}

# Değişikliğe uğrayan maddeler (7499 sayılı Kanun)
DEGISIK_MADDELER = {
    9:  {"tip": "Değişik", "kanun": "7499", "tarih": "2/3/2024", "aciklama": "Yurt dışı aktarım şartları yeniden düzenlendi"},
}
MULGA_MADDELER: Dict[int, Dict] = {}
EK_FIKRALAR = [
    {"madde": 6, "kanun": "7499", "tarih": "2/3/2024", "aciklama": "Ek fıkra: biyometrik ve genetik veri"},
    {"madde": 18, "kanun": "7499", "tarih": "2/3/2024", "aciklama": "İdari para cezası tavanları güncellendi"},
]

# İdari para cezaları (Madde 18) – 2024 sonrası
IDARI_CEZA_MAP = {
    "Görev ve yetkilerin yerine getirilmemesi":          {"alt": 93_724, "ust": 281_180, "renk": "#e74c3c"},
    "Aydınlatma yükümlülüğünün yerine getirilmemesi":  {"alt": 46_862, "ust": 140_590, "renk": "#e67e22"},
    "Veri güvenliği tedbirlerinin alınmaması":           {"alt": 46_862, "ust": 281_180, "renk": "#e67e22"},
    "Kurul kararlarının yerine getirilmemesi":           {"alt": 93_724, "ust": 562_362, "renk": "#c0392b"},
    "VERBİS'e kayıt yükümlülüğüne uyulmaması":          {"alt": 46_862, "ust": 281_180, "renk": "#e67e22"},
}


def parse_law(pages: List[Dict]) -> Dict:
    """
    Kanun PDF sayfalarını ayrıştırır.

    Returns:
        {
          "meta": {...},
          "bolumler": [...],
          "maddeler": {madde_no: {...}},
          "degisiklikler": [...],
        }
    """
    full_text = "\n".join(p["text"] for p in pages)

    # ── Bölüm tespiti ──────────────────────────────────────────
    bolumler = []
    for bolum_no, bolum in BOLUM_MAP.items():
        bolumler.append({
            "no":      bolum_no,
            "sira":    bolum["sira"],
            "baslik":  bolum["baslik"],
            "maddeler": bolum["maddeler"],
        })

    # ── Madde ayrıştırma ───────────────────────────────────────
    maddeler: Dict[int, Dict] = {}
    segments = MADDE_SPLIT_RE.split(full_text)

    for seg in segments:
        seg = seg.strip()
        if not seg:
            continue
        m = MADDE_NO_RE.match(seg)
        if not m:
            continue
        no = int(m.group(1))

        # Değişiklik notasyonları
        notasyonlar = []
        for n in NOTASYON_RE.finditer(seg):
            notasyonlar.append({
                "tip":    n.group("tip"),
                "tarih":  n.group("tarih").strip(),
                "kanun":  n.group("kanun"),
            })

        # Üst düzey metin temizle
        temiz = NOTASYON_RE.sub("", seg).strip()
        # MADDE satırını kaldır
        temiz = re.sub(r"^MADDE\s+\d+[-–]\s*", "", temiz, flags=re.MULTILINE).strip()

        baslik = MADDE_BASLIKLAR.get(no, f"Madde {no}")
        bolum_no = _find_bolum(no)

        degisiklik_durumu = "normal"
        if no in DEGISIK_MADDELER:
            degisiklik_durumu = "degisik"
        elif no in MULGA_MADDELER:
            degisiklik_durumu = "mulga"

        maddeler[no] = {
            "no":                no,
            "baslik":            baslik,
            "bolum":             bolum_no,
            "metin":             temiz[:3000],
            "notasyonlar":       notasyonlar,
            "degisiklik_durumu": degisiklik_durumu,
            "onemli":            no in ONEMLI_MADDELER,
            "kelime_sayisi":     len(temiz.split()),
        }

    # Boşlukları doldur (PDF parse edemediğimiz maddeler için)
    for no, baslik in MADDE_BASLIKLAR.items():
        if no not in maddeler:
            maddeler[no] = {
                "no":                no,
                "baslik":            baslik,
                "bolum":             _find_bolum(no),
                "metin":             "",
                "notasyonlar":       [],
                "degisiklik_durumu": "degisik" if no in DEGISIK_MADDELER else "normal",
                "onemli":            no in ONEMLI_MADDELER,
                "kelime_sayisi":     0,
            }

    # ── Değişiklik özeti ───────────────────────────────────────
    degisiklikler = []
    for no, d in DEGISIK_MADDELER.items():
        degisiklikler.append({
            "madde_no":  no,
            "baslik":    MADDE_BASLIKLAR.get(no, f"Madde {no}"),
            "tip":       d["tip"],
            "kanun":     d["kanun"],
            "tarih":     d["tarih"],
            "aciklama":  d["aciklama"],
        })
    for e in EK_FIKRALAR:
        degisiklikler.append({
            "madde_no":  e["madde"],
            "baslik":    MADDE_BASLIKLAR.get(e["madde"], f"Madde {e['madde']}"),
            "tip":       "Ek",
            "kanun":     e["kanun"],
            "tarih":     e["tarih"],
            "aciklama":  e["aciklama"],
        })

    return {
        "meta": {
            "kanun_no":    "6698",
            "kabul":       "24/3/2016",
            "resmi_gazete":"7/4/2016 – 29677",
            "degistiren":  "7499 sayılı Kanun (2/3/2024)",
            "madde_sayisi": len(maddeler),
            "bolum_sayisi": len(bolumler),
        },
        "bolumler":     bolumler,
        "maddeler":     maddeler,
        "degisiklikler": degisiklikler,
        "idari_cezalar": IDARI_CEZA_MAP,
        "ek_fikralar":  EK_FIKRALAR,
    }


def _find_bolum(madde_no: int) -> int:
    for bolum_no, bolum in BOLUM_MAP.items():
        if madde_no in bolum["maddeler"]:
            return bolum_no
    return 7  # son bölüm
