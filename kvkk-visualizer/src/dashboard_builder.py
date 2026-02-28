"""
KVKK Dashboard HTML Üretici
=============================
Tüm analiz verilerini alarak tek dosya, tam özellikli HTML dashboard üretir.
Dış bağımlılık: Bootstrap 5 + Chart.js (CDN), inline PDF link desteği.
"""

import io
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger(__name__)

BASE_DIR   = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output" / "dashboard"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ═══════════════════════════════════════════════════════════════
# YARDIMCI FONKSİYONLAR
# ═══════════════════════════════════════════════════════════════

def _badge(tip: str) -> str:
    COLORS = {"Değişik": "warning", "Mülga": "danger", "Ek": "success", "normal": "secondary", "": "light"}
    TEXT   = {"Değişik": "⚡ Değişik", "Mülga": "🚫 Mülga", "Ek": "➕ Ek", "normal": "", "": ""}
    cls = COLORS.get(tip, "secondary")
    txt = TEXT.get(tip, tip)
    if not txt:
        return ""
    return f'<span class="badge bg-{cls} me-1">{txt}</span>'


def _notasyon_badges(notasyonlar: List[Dict]) -> str:
    if not notasyonlar:
        return ""
    parts = []
    for n in notasyonlar:
        tip = n.get("tip", "")
        kanun = n.get("kanun", "")
        tarih = n.get("tarih", "")
        parts.append(_badge(tip) +
                     f'<small class="text-muted">({kanun} – {tarih})</small>')
    return " ".join(parts)


def _render_madde_card(madde: Dict) -> str:
    no     = madde["no"]
    baslik = madde["baslik"]
    metin  = madde["metin"]
    durumu = madde["degisiklik_durumu"]
    onemli = madde.get("onemli", False)

    border = "border-warning" if durumu == "degisik" else \
             "border-danger"  if durumu == "mulga"   else \
             "border-primary" if onemli               else "border-0"

    star = ' <i class="bi bi-star-fill text-warning" title="Önemli madde"></i>' if onemli else ""

    notasyon_html = _notasyon_badges(madde.get("notasyonlar", []))

    metin_kisa = metin[:500] + "…" if len(metin) > 500 else metin
    metin_html = metin_kisa.replace("\n", "<br>") if metin_kisa else \
                 '<em class="text-muted">Metin PDF\'den çıkarılamadı.</em>'

    return f"""
    <div class="card mb-3 shadow-sm border {border} madde-card"
         data-madde="{no}" data-baslik="{baslik.lower()}" id="madde-{no}">
      <div class="card-header d-flex justify-content-between align-items-center bg-light"
           style="cursor:pointer" data-bs-toggle="collapse" data-bs-target="#madde-body-{no}">
        <span>
          <span class="badge bg-dark me-2">Madde {no}</span>
          <strong>{baslik}</strong>{star}
        </span>
        <span>
          {notasyon_html}
          <i class="bi bi-chevron-down"></i>
        </span>
      </div>
      <div class="collapse" id="madde-body-{no}">
        <div class="card-body">
          <p class="card-text" style="white-space:pre-line;font-size:.93rem">{metin_html}</p>
        </div>
      </div>
    </div>"""


def _render_bolum_section(bolum: Dict, maddeler: Dict) -> str:
    no     = bolum["no"]
    baslik = bolum["baslik"]
    ids    = bolum["maddeler"]

    cards = ""
    for mid in ids:
        if mid in maddeler:
            cards += _render_madde_card(maddeler[mid])

    return f"""
    <section class="mb-5" id="bolum-{no}">
      <h4 class="fw-bold border-bottom pb-2 mb-3 mt-4">
        <span class="badge bg-primary me-2">{bolum['sira']} BÖLÜM</span>
        {baslik}
      </h4>
      {cards}
    </section>"""


def _render_sss_accordion(sss_list: List[Dict]) -> str:
    items = ""
    for i, sss in enumerate(sss_list):
        star = " ⭐" if sss.get("onemli") else ""
        items += f"""
        <div class="accordion-item">
          <h2 class="accordion-header">
            <button class="accordion-button {'collapsed' if i > 0 else ''} fw-semibold"
                    type="button" data-bs-toggle="collapse" data-bs-target="#sss-{i}">
              <span class="badge bg-secondary me-2">{sss['kategori']}</span>
              {sss['soru']}{star}
            </button>
          </h2>
          <div id="sss-{i}" class="accordion-collapse collapse {'show' if i == 0 else ''}">
            <div class="accordion-body text-muted">{sss['cevap']}</div>
          </div>
        </div>"""
    return f'<div class="accordion shadow-sm" id="sssAccordion">{items}</div>'


def _render_kayit_adimi(adim: Dict) -> str:
    no      = adim["adim"]
    baslik  = adim["baslik"]
    aciklama = adim["aciklama"]
    gerekler = adim["gereksinimler"]
    ikon    = adim["ikon"]
    renk    = adim["renk"]
    sure    = adim["sure"]

    gerek_li = "".join(f"<li>{g}</li>" for g in gerekler)

    return f"""
    <div class="col-md-6 col-lg-4 mb-4">
      <div class="card h-100 shadow-sm border-0 step-card" style="border-left:5px solid {renk} !important">
        <div class="card-body">
          <div class="d-flex align-items-center mb-3">
            <div class="rounded-circle d-flex align-items-center justify-content-center me-3"
                 style="width:48px;height:48px;background:{renk};font-size:1.4rem">{ikon}</div>
            <div>
              <div class="text-muted small">Adım {no}</div>
              <h6 class="mb-0 fw-bold">{baslik}</h6>
            </div>
          </div>
          <p class="text-muted small">{aciklama}</p>
          <ul class="list-unstyled small">{"".join(f'<li class=\"mb-1\"><i class=\"bi bi-check-circle-fill text-success me-1\"></i>{g}</li>' for g in gerekler)}</ul>
        </div>
        <div class="card-footer bg-light text-end">
          <span class="badge bg-light text-dark border">⏱ {sure}</span>
        </div>
      </div>
    </div>"""


def _render_ceza_table(cezalar: Dict) -> str:
    rows = ""
    for eylem, bilgi in cezalar.items():
        alt  = f"{bilgi['alt']:,}".replace(",", ".")
        ust  = f"{bilgi['ust']:,}".replace(",", ".")
        renk = bilgi["renk"]
        rows += f"""
        <tr>
          <td><span class="bullet" style="background:{renk}"></span> {eylem}</td>
          <td class="text-end fw-semibold">{alt} ₺</td>
          <td class="text-end fw-semibold text-danger">{ust} ₺</td>
        </tr>"""
    return f"""
    <div class="table-responsive">
      <table class="table table-hover align-middle">
        <thead class="table-dark">
          <tr>
            <th>Kabahat</th>
            <th class="text-end">Alt Sınır (₺)</th>
            <th class="text-end">Üst Sınır (₺)</th>
          </tr>
        </thead>
        <tbody>{rows}</tbody>
        <tfoot class="text-muted small">
          <tr><td colspan="3">* 2024 yılı günceli – Madde 18 ve 7499 sayılı Kanun kapsamında</td></tr>
        </tfoot>
      </table>
    </div>"""


def _chart_data_json(law: Dict, verbis: Dict) -> str:
    """Chart.js için JSON veri bloğu."""
    # Madde başına kelime sayısı dağılımı
    maddeler = law["maddeler"]
    bolum_kelime: Dict[str, int] = {}
    for bolum in law["bolumler"]:
        total = sum(maddeler.get(m, {}).get("kelime_sayisi", 0) for m in bolum["maddeler"])
        bolum_kelime[bolum["baslik"][:30]] = total

    # İşleme hacmi (verbis)
    islem = verbis.get("stats", {}).get("islem_hacimleri", {})
    hukuki = verbis.get("stats", {}).get("hukuki_dayanaklar", {})

    return json.dumps({
        "bolum_kelime": {"labels": list(bolum_kelime.keys()),
                         "data":   list(bolum_kelime.values())},
        "islem_hacimleri": {"labels": list(islem.keys()),
                             "data":   list(islem.values())},
        "hukuki_dayanaklar": {"labels": list(hukuki.keys()),
                               "data":   list(hukuki.values())},
    }, ensure_ascii=False)


# ═══════════════════════════════════════════════════════════════
# ANA OLUŞTURUCU
# ═══════════════════════════════════════════════════════════════

def build_dashboard(law: Dict, verbis_qa: Dict, verbis_guide: Dict) -> str:
    """Tüm verileri alarak HTML string döndürür."""

    tarih      = datetime.now().strftime("%d.%m.%Y %H:%M")
    meta       = law["meta"]
    maddeler   = law["maddeler"]
    bolumler   = law["bolumler"]
    degisiklik = law["degisiklikler"]
    cezalar    = law["idari_cezalar"]
    sss        = verbis_qa["sss"]
    adimlari   = verbis_qa["kayit_adimlari"]

    # Alt bölümler
    kanun_html = "".join(_render_bolum_section(b, maddeler) for b in bolumler)

    degisiklik_rows = "".join(f"""
        <tr>
          <td><a href="#madde-{d['madde_no']}" class="text-decoration-none fw-semibold" onclick="switchTab('kanun')">
            Madde {d['madde_no']} – {d['baslik']}</a></td>
          <td>{_badge(d['tip'])}</td>
          <td><span class="badge bg-secondary">{d['kanun']}</span></td>
          <td class="text-muted small">{d['tarih']}</td>
          <td class="small">{d['aciklama']}</td>
        </tr>""" for d in degisiklik)

    adimlar_html = "".join(_render_kayit_adimi(a) for a in adimlari)
    sss_html     = _render_sss_accordion(sss)
    ceza_html    = _render_ceza_table(cezalar)
    chart_json   = _chart_data_json(law, verbis_qa)

    # Bölüm navigasyonu
    nav_links = "".join(
        f'<a class="list-group-item list-group-item-action py-2" href="#bolum-{b["no"]}">'
        f'<span class="badge bg-primary me-1">{b["no"]}</span> {b["baslik"]}</a>'
        for b in bolumler
    )

    # Önemli maddeler hızlı erişim
    onemli_html = "".join(
        f'<a href="#madde-{no}" class="btn btn-sm btn-outline-primary me-1 mb-1" onclick="switchTab(\'kanun\')">'
        f'Madde {no}</a>'
        for no, m in sorted(maddeler.items()) if m.get("onemli")
    )

    return f"""<!DOCTYPE html>
<html lang="tr" data-bs-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>KVKK Belge Merkezi — 6698 Sayılı Kanun &amp; VERBİS Rehberi</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css" rel="stylesheet">
  <style>
    :root {{
      --kvkk-primary:   #1a3a5c;
      --kvkk-accent:    #2980b9;
      --kvkk-gold:      #f39c12;
      --kvkk-success:   #27ae60;
    }}

    body {{ font-family: 'Segoe UI', system-ui, sans-serif; background: #f0f4f8; }}

    /* ── Üst başlık ── */
    .kvkk-hero {{
      background: linear-gradient(135deg, var(--kvkk-primary) 0%, #2c5282 60%, #2980b9 100%);
      color: #fff;
      padding: 2rem 0 1.5rem;
    }}
    .kvkk-hero h1 {{ font-size: clamp(1.4rem, 3vw, 2rem); font-weight: 800; letter-spacing: -.5px; }}
    .kvkk-hero .subtitle {{ opacity: .8; font-size: .95rem; }}

    /* ── Navigasyon sekmeleri ── */
    .nav-kvkk .nav-link {{
      color: #fff8; font-weight: 600; border-radius: 8px 8px 0 0;
      transition: all .2s; padding: .6rem 1.4rem;
    }}
    .nav-kvkk .nav-link:hover {{ color: #fff; background: rgba(255,255,255,.12); }}
    .nav-kvkk .nav-link.active {{ background: #f0f4f8; color: var(--kvkk-primary); }}

    /* ── İstatistik kartları ── */
    .stat-card {{
      border-radius: 14px; border: none; box-shadow: 0 4px 20px rgba(0,0,0,.08);
      transition: transform .2s;
    }}
    .stat-card:hover {{ transform: translateY(-3px); }}
    .stat-card .icon {{ font-size: 2.2rem; opacity: .85; }}

    /* ── Madde kartları ── */
    .madde-card {{ border-radius: 10px; transition: box-shadow .2s; }}
    .madde-card:hover {{ box-shadow: 0 4px 18px rgba(0,0,0,.12); }}
    .madde-card.border-warning {{ border-left: 4px solid #f39c12 !important; }}
    .madde-card.border-danger  {{ border-left: 4px solid #e74c3c !important; }}
    .madde-card.border-primary {{ border-left: 4px solid #2980b9 !important; }}

    /* ── VERBİS adım kartları ── */
    .step-card {{ border-radius: 14px; border-left-width: 5px !important; }}

    /* ── Arama kutusu ── */
    #searchBox {{ border-radius: 30px; padding-left: 1.2rem; border: 2px solid #dee2e6; }}
    #searchBox:focus {{ border-color: var(--kvkk-accent); box-shadow: 0 0 0 3px rgba(41,128,185,.15); }}

    /* ── Sidebar ── */
    .law-sidebar {{ position: sticky; top: 80px; max-height: calc(100vh - 120px); overflow-y: auto; }}
    .law-sidebar .list-group-item {{ font-size: .85rem; border: none; border-radius: 8px; margin-bottom: 2px; }}
    .law-sidebar .list-group-item:hover {{ background: #e8eef4; }}

    /* ── Değişiklik zaman çizelgesi ── */
    .timeline-item {{ border-left: 3px solid var(--kvkk-accent); padding-left: 1.2rem; position: relative; }}
    .timeline-item::before {{
      content: ''; position: absolute; left: -7px; top: 4px;
      width: 12px; height: 12px; border-radius: 50%;
      background: var(--kvkk-accent); border: 2px solid #fff;
    }}

    /* ── Ceza tablo ── */
    .bullet {{ display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 6px; }}

    /* ── Koyu mod ── */
    [data-bs-theme="dark"] body {{ background: #0f1923; }}
    [data-bs-theme="dark"] .nav-kvkk .nav-link.active {{ background: #0f1923; }}

    /* ── Yazdırma ── */
    @media print {{ .law-sidebar, .nav-kvkk, #searchBox {{ display:none; }} .collapse {{ display:block !important; }} }}
    @media (max-width:768px) {{ .law-sidebar {{ display: none; }} }}
  </style>
</head>
<body>

<!-- ══ HERO BAŞLIK ══════════════════════════════════════════════════ -->
<header class="kvkk-hero">
  <div class="container">
    <div class="row align-items-end">
      <div class="col">
        <div class="d-flex align-items-center gap-3 mb-2">
          <span style="font-size:2.5rem">⚖️</span>
          <div>
            <h1 class="mb-0">KVKK Belge Merkezi</h1>
            <div class="subtitle">6698 Sayılı Kanun • VERBİS Rehberi • Sık Sorulan Sorular • Uyumluluk</div>
          </div>
        </div>
        <div class="d-flex flex-wrap gap-2 mt-3">
          <span class="badge bg-light text-dark">Kanun No: {meta['kanun_no']}</span>
          <span class="badge bg-light text-dark">Kabul: {meta['kabul']}</span>
          <span class="badge bg-warning text-dark">Son Değişiklik: {meta['degistiren']}</span>
          <span class="badge bg-success">{meta['madde_sayisi']} Madde</span>
          <span class="badge bg-info text-dark">{meta['bolum_sayisi']} Bölüm</span>
        </div>
      </div>
      <div class="col-auto text-end d-none d-md-block">
        <small class="opacity-75">Son güncelleme: {tarih}</small><br>
        <button class="btn btn-sm btn-outline-light mt-1" onclick="toggleDark()">
          <i class="bi bi-moon-stars-fill"></i> Koyu Mod
        </button>
        <button class="btn btn-sm btn-outline-light mt-1" onclick="window.print()">
          <i class="bi bi-printer-fill"></i> Yazdır
        </button>
      </div>
    </div>

    <!-- Sekme navigasyonu -->
    <ul class="nav nav-kvkk mt-3" id="mainTabs" role="tablist">
      <li class="nav-item"><a class="nav-link active" data-bs-toggle="tab" href="#tab-kanun"  id="tab-kanun-link">
        <i class="bi bi-file-text-fill me-1"></i> Kanun Metni</a></li>
      <li class="nav-item"><a class="nav-link" data-bs-toggle="tab" href="#tab-verbis" id="tab-verbis-link">
        <i class="bi bi-database-fill-check me-1"></i> VERBİS Rehberi</a></li>
      <li class="nav-item"><a class="nav-link" data-bs-toggle="tab" href="#tab-sss"   id="tab-sss-link">
        <i class="bi bi-chat-dots-fill me-1"></i> S&amp;S</a></li>
      <li class="nav-item"><a class="nav-link" data-bs-toggle="tab" href="#tab-stats" id="tab-stats-link">
        <i class="bi bi-bar-chart-fill me-1"></i> İstatistikler</a></li>
      <li class="nav-item"><a class="nav-link" data-bs-toggle="tab" href="#tab-degisiklik" id="tab-degisiklik-link">
        <i class="bi bi-arrow-repeat me-1"></i> Değişiklikler</a></li>
    </ul>
  </div>
</header>

<!-- ══ İÇERİK ══════════════════════════════════════════════════════ -->
<div class="container my-4">
  <div class="tab-content">

    <!-- ─── TAB 1: KANUN METNİ ─────────────────────────────────── -->
    <div class="tab-pane fade show active" id="tab-kanun" role="tabpanel">

      <!-- Hızlı istatistikler -->
      <div class="row g-3 mb-4">
        <div class="col-6 col-lg-3">
          <div class="card stat-card text-center p-3 bg-primary text-white">
            <div class="icon">📜</div>
            <div class="fs-3 fw-bold">{meta['madde_sayisi']}</div>
            <div class="small">Madde</div>
          </div>
        </div>
        <div class="col-6 col-lg-3">
          <div class="card stat-card text-center p-3 bg-success text-white">
            <div class="icon">📁</div>
            <div class="fs-3 fw-bold">{meta['bolum_sayisi']}</div>
            <div class="small">Bölüm</div>
          </div>
        </div>
        <div class="col-6 col-lg-3">
          <div class="card stat-card text-center p-3 bg-warning text-dark">
            <div class="icon">⚡</div>
            <div class="fs-3 fw-bold">{len(degisiklik)}</div>
            <div class="small">Değişiklik (7499)</div>
          </div>
        </div>
        <div class="col-6 col-lg-3">
          <div class="card stat-card text-center p-3" style="background:#1a3a5c;color:#fff">
            <div class="icon">🔍</div>
            <div class="fs-3 fw-bold">{len([m for m in maddeler.values() if m.get('onemli')])}</div>
            <div class="small">Önemli Madde</div>
          </div>
        </div>
      </div>

      <!-- Önemli maddeler hızlı erişim -->
      <div class="card shadow-sm mb-4 border-0">
        <div class="card-body">
          <h6 class="fw-bold text-primary mb-2"><i class="bi bi-star-fill text-warning me-1"></i> Önemli Maddeler</h6>
          {onemli_html}
        </div>
      </div>

      <!-- Arama -->
      <div class="mb-3">
        <input type="text" id="searchBox" class="form-control form-control-lg"
               placeholder="🔍  Madde başlığı veya numarası ara…" oninput="filterMaddeler(this.value)">
      </div>
      <div id="searchNoResult" class="alert alert-info d-none">Sonuç bulunamadı.</div>

      <!-- İki sütun: sidebar + içerik -->
      <div class="row g-4">
        <div class="col-lg-3 d-none d-lg-block">
          <div class="card border-0 shadow-sm law-sidebar p-2">
            <h6 class="fw-bold px-2 mb-2 text-muted">BÖLÜMLER</h6>
            <div class="list-group list-group-flush">{nav_links}</div>
          </div>
        </div>
        <div class="col-lg-9">
          <div id="kanunContent">{kanun_html}</div>
        </div>
      </div>
    </div><!-- /tab-kanun -->


    <!-- ─── TAB 2: VERBİS REHBERİ ─────────────────────────────── -->
    <div class="tab-pane fade" id="tab-verbis" role="tabpanel">
      <div class="row g-3 mb-4">
        <div class="col-md-4">
          <div class="card stat-card text-center p-3 bg-primary text-white">
            <div class="icon">📊</div>
            <div class="fs-3 fw-bold">60.423</div>
            <div class="small">Kayıtlı Veri Sorumlusu</div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="card stat-card text-center p-3 bg-success text-white">
            <div class="icon">📋</div>
            <div class="fs-3 fw-bold">6</div>
            <div class="small">Kayıt Adımı</div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="card stat-card text-center p-3 bg-warning text-dark">
            <div class="icon">⏱</div>
            <div class="fs-3 fw-bold">3–6 hafta</div>
            <div class="small">Ortalama Kayıt Süresi</div>
          </div>
        </div>
      </div>

      <h4 class="fw-bold mb-3"><i class="bi bi-list-ol me-2 text-primary"></i>VERBİS Kayıt Adımları</h4>
      <p class="text-muted mb-4">Veri Sorumluları Sicil Bilgi Sistemi'ne kayıt olmak için aşağıdaki adımları takip edin.</p>
      <div class="row">{adimlar_html}</div>

      <div class="alert alert-info border-0 shadow-sm mt-2">
        <i class="bi bi-link-45deg fs-5 me-2"></i>
        Kayıt için: <a href="https://verbis.kvkk.gov.tr" target="_blank" class="fw-semibold">verbis.kvkk.gov.tr</a>
        &nbsp;|&nbsp;
        Bilgi ve destek: <a href="https://kvkk.gov.tr" target="_blank" class="fw-semibold">kvkk.gov.tr</a>
      </div>

      <h4 class="fw-bold mt-5 mb-3"><i class="bi bi-exclamation-triangle-fill text-danger me-2"></i>İdari Para Cezaları (Madde 18)</h4>
      {ceza_html}
    </div><!-- /tab-verbis -->


    <!-- ─── TAB 3: SORULAR & CEVAPLAR ─────────────────────────── -->
    <div class="tab-pane fade" id="tab-sss" role="tabpanel">
      <div class="row mb-4">
        <div class="col-md-8">
          <h4 class="fw-bold"><i class="bi bi-chat-dots-fill text-primary me-2"></i>Sık Sorulan Sorular</h4>
          <p class="text-muted">Resmi "Sorularla VERBİS" dokümanından ({verbis_qa['sayfa_sayisi']} sayfa) derlenen sorular.</p>
        </div>
        <div class="col-md-4">
          <input type="text" class="form-control" id="sssSearch"
                 placeholder="Sorularda ara…" oninput="filterSSS(this.value)">
        </div>
      </div>

      <!-- Kategori filtreleri -->
      <div class="mb-3" id="sssFilters">
        <button class="btn btn-sm btn-primary me-1 mb-1" onclick="filterSSS('')">Tümü</button>
        {"".join(f'<button class="btn btn-sm btn-outline-secondary me-1 mb-1" onclick="filterSSS(\'{k}\')">{k}</button>'
                 for k in dict.fromkeys(s['kategori'] for s in sss))}
      </div>

      <div id="sssContainer">{sss_html}</div>
      <div id="sssNoResult" class="alert alert-info d-none">Aranan kriterlere uygun soru bulunamadı.</div>
    </div><!-- /tab-sss -->


    <!-- ─── TAB 4: İSTATİSTİKLER ───────────────────────────────── -->
    <div class="tab-pane fade" id="tab-stats" role="tabpanel">
      <h4 class="fw-bold mb-4"><i class="bi bi-bar-chart-fill text-primary me-2"></i>Analitik Görünüm</h4>

      <div class="row g-4 mb-5">
        <div class="col-md-6">
          <div class="card border-0 shadow-sm p-3">
            <h6 class="fw-bold text-muted mb-3">Bölümlere Göre Metin Yoğunluğu (kelime)</h6>
            <canvas id="chartBolum" height="220"></canvas>
          </div>
        </div>
        <div class="col-md-6">
          <div class="card border-0 shadow-sm p-3">
            <h6 class="fw-bold text-muted mb-3">VERBİS Kayıtlarında İşleme Hacmi (%)</h6>
            <canvas id="chartIslem" height="220"></canvas>
          </div>
        </div>
      </div>

      <div class="row g-4">
        <div class="col-md-6">
          <div class="card border-0 shadow-sm p-3">
            <h6 class="fw-bold text-muted mb-3">Hukuki Dayanak Dağılımı (%)</h6>
            <canvas id="chartHukuki" height="220"></canvas>
          </div>
        </div>
        <div class="col-md-6">
          <div class="card border-0 shadow-sm p-3">
            <h6 class="fw-bold text-muted mb-3">Madde Önem Dağılımı</h6>
            <div class="d-flex flex-wrap gap-2 pt-2">
              {"".join(f'<div class="d-flex align-items-center gap-2 p-2 rounded bg-light border flex-grow-1">'
                       f'<span class="badge bg-{"warning" if m.get("onemli") else "secondary"}">'
                       f'Madde {no}</span><span class="small">{m["baslik"][:25]}…</span></div>'
                       for no, m in sorted(maddeler.items()) if no <= 18)}
            </div>
          </div>
        </div>
      </div>
    </div><!-- /tab-stats -->


    <!-- ─── TAB 5: DEĞİŞİKLİKLER ──────────────────────────────── -->
    <div class="tab-pane fade" id="tab-degisiklik" role="tabpanel">
      <h4 class="fw-bold mb-2"><i class="bi bi-arrow-repeat text-warning me-2"></i>7499 Sayılı Kanun Değişiklikleri</h4>
      <p class="text-muted mb-4">2/3/2024 tarihinde yürürlüğe giren değişiklikler:</p>

      <div class="table-responsive shadow-sm rounded">
        <table class="table table-hover align-middle mb-0">
          <thead class="table-dark">
            <tr>
              <th>Madde</th>
              <th>Tür</th>
              <th>Değiştiren Kanun</th>
              <th>Tarih</th>
              <th>Açıklama</th>
            </tr>
          </thead>
          <tbody>{degisiklik_rows}</tbody>
        </table>
      </div>

      <h5 class="fw-bold mt-5 mb-3">🕐 Değişiklik Zaman Çizelgesi</h5>
      <div class="ps-2">
        <div class="timeline-item mb-4 pb-2">
          <h6 class="fw-bold">24 Mart 2016</h6>
          <p class="text-muted small mb-0">6698 Sayılı KVKK yürürlüğe girdi. Türkiye'nin temel kişisel veri koruma kanunu.</p>
        </div>
        <div class="timeline-item mb-4 pb-2">
          <h6 class="fw-bold">7 Nisan 2016</h6>
          <p class="text-muted small mb-0">Kanun, Resmî Gazete'de yayımlandı (Sayı: 29677).</p>
        </div>
        <div class="timeline-item mb-4 pb-2">
          <h6 class="fw-bold">2018 – 2023</h6>
          <p class="text-muted small mb-0">VERBİS sistemi kuruldu, kayıt dönemleri açıklandı. Çeşitli kurul kararları ve rehberler yayımlandı.</p>
        </div>
        <div class="timeline-item mb-4 pb-2">
          <h6 class="fw-bold text-warning">2 Mart 2024 ⚡</h6>
          <p class="text-muted small mb-0">7499 sayılı Kanun ile KVKK'nın 5, 6, 9, 10, 12 ve 18. maddeleri değiştirildi. GDPR uyumluluğu artırıldı.</p>
        </div>
        <div class="timeline-item">
          <h6 class="fw-bold text-success">Günümüz ✅</h6>
          <p class="text-muted small mb-0">Yurt dışı aktarım şartları GDPR ile uyumlu hâle geldi. Biyometrik veriler için ek güvenceler sağlandı.</p>
        </div>
      </div>

      <div class="alert alert-warning border-0 shadow-sm mt-4">
        <i class="bi bi-exclamation-triangle-fill me-2"></i>
        <strong>Önemli:</strong> 7499 sayılı Kanun değişiklikleri GDPR (AB) uyumu açısından
        kritik öneme sahiptir. Özellikle Madde 9 (yurt dışı aktarım) köklü biçimde yeniden düzenlenmiştir.
      </div>
    </div><!-- /tab-degisiklik -->

  </div><!-- /tab-content -->
</div><!-- /container -->


<!-- ══ FOOTER ══════════════════════════════════════════════════════ -->
<footer style="background:var(--kvkk-primary);color:#fff8" class="py-4 mt-5">
  <div class="container d-flex flex-wrap justify-content-between align-items-center gap-3">
    <div>
      <strong class="text-white">KVKK Belge Merkezi</strong> — otomatik olarak oluşturulmuştur.<br>
      <small>Kaynak: <em>kvkk 1.5.6698.pdf</em> • <em>sorularla-verbis.pdf</em> • <em>veri-sorumlulari-sicil-bilgi-sistemi-kilavuzu.pdf</em></small>
    </div>
    <div class="text-end">
      <small>Oluşturulma: {tarih}</small><br>
      <small>Bu sayfa resmî hukuki tavsiye niteliği taşımaz.</small>
    </div>
  </div>
</footer>


<!-- ══ SCRIPTLER ═══════════════════════════════════════════════════ -->
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<script>
const CHART_DATA = {chart_json};

// ── Madde arama ──────────────────────────────────────────────────
function filterMaddeler(q) {{
  q = q.toLowerCase().trim();
  const cards = document.querySelectorAll('.madde-card');
  let visible = 0;
  cards.forEach(c => {{
    const no     = c.dataset.madde || '';
    const baslik = c.dataset.baslik || '';
    const match  = !q || no.includes(q) || baslik.includes(q);
    c.style.display = match ? '' : 'none';
    if (match) visible++;
  }});
  document.getElementById('searchNoResult').classList.toggle('d-none', visible > 0);
}}

// ── SSS arama / filtreleme ───────────────────────────────────────
function filterSSS(q) {{
  q = q.toLowerCase().trim();
  const items = document.querySelectorAll('#sssContainer .accordion-item');
  let visible = 0;
  items.forEach(item => {{
    const text = item.textContent.toLowerCase();
    const match = !q || text.includes(q);
    item.style.display = match ? '' : 'none';
    if (match) visible++;
  }});
  document.getElementById('sssNoResult').classList.toggle('d-none', visible > 0);
  const box = document.getElementById('sssSearch');
  if (box && !q.match(/^[A-ZÜÇĞŞIÖ]/i)) box.value = '';
}}

// ── Tab geçiş yardımcısı ─────────────────────────────────────────
function switchTab(name) {{
  const el = document.getElementById('tab-' + name + '-link');
  if (el) bootstrap.Tab.getOrCreateInstance(el).show();
}}

// ── Koyu mod ─────────────────────────────────────────────────────
function toggleDark() {{
  const html = document.documentElement;
  html.dataset.bsTheme = html.dataset.bsTheme === 'dark' ? 'light' : 'dark';
}}

// ── Chart.js grafikleri ──────────────────────────────────────────
const PALETTE = ['#3498db','#2ecc71','#e74c3c','#f39c12','#9b59b6','#1abc9c','#e67e22'];

document.addEventListener('DOMContentLoaded', () => {{
  // Bölüm kelime yoğunluğu
  new Chart(document.getElementById('chartBolum'), {{
    type: 'bar',
    data: {{
      labels: CHART_DATA.bolum_kelime.labels,
      datasets: [{{ label: 'Kelime', data: CHART_DATA.bolum_kelime.data,
                    backgroundColor: PALETTE, borderRadius: 6 }}]
    }},
    options: {{ responsive: true, plugins: {{ legend: {{ display: false }} }},
               scales: {{ y: {{ beginAtZero: true }} }} }}
  }});

  // İşleme hacmi (doughnut)
  new Chart(document.getElementById('chartIslem'), {{
    type: 'doughnut',
    data: {{
      labels: CHART_DATA.islem_hacimleri.labels,
      datasets: [{{ data: CHART_DATA.islem_hacimleri.data,
                    backgroundColor: PALETTE, hoverOffset: 10 }}]
    }},
    options: {{ responsive: true, plugins: {{ legend: {{ position: 'right' }} }} }}
  }});

  // Hukuki dayanak (pie)
  new Chart(document.getElementById('chartHukuki'), {{
    type: 'pie',
    data: {{
      labels: CHART_DATA.hukuki_dayanaklar.labels,
      datasets: [{{ data: CHART_DATA.hukuki_dayanaklar.data,
                    backgroundColor: ['#1a3a5c','#2980b9','#3498db','#5dade2','#85c1e9'],
                    hoverOffset: 8 }}]
    }},
    options: {{ responsive: true, plugins: {{ legend: {{ position: 'right' }} }} }}
  }});
}});
</script>
</body>
</html>"""


def build_and_save(law: Dict, verbis_qa: Dict, verbis_guide: Dict,
                   out_path: Path = None) -> Path:
    """Dashboard HTML dosyasını oluşturur ve diske yazar."""
    if out_path is None:
        out_path = OUTPUT_DIR / "KVKK_Dashboard.html"

    logger.info("Dashboard oluşturuluyor…")
    html = build_dashboard(law, verbis_qa, verbis_guide)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    logger.info(f"✅ Dashboard → {out_path}")
    return out_path


# ── CLI ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))

    from pdf_extractor  import extract_all
    from law_parser     import parse_law
    from verbis_parser  import parse_verbis_qa, parse_verbis_guide

    import logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    "--force" in sys.argv and logger.info("Önbellek temizleniyor…")
    force = "--force" in sys.argv

    logger.info("1/4 · PDF'ler çıkarılıyor…")
    raw = extract_all(force=force)

    logger.info("2/4 · Kanun ayrıştırılıyor…")
    law         = parse_law(raw["law"])

    logger.info("3/4 · VERBİS belgeleri ayrıştırılıyor…")
    verbis_qa   = parse_verbis_qa(raw["verbis_qa"])
    verbis_guide = parse_verbis_guide(raw["verbis_guide"])

    logger.info("4/4 · Dashboard oluşturuluyor…")
    out = build_and_save(law, verbis_qa, verbis_guide)

    print(f"\n  Tarayıcıda açmak için çift tıklayın:\n  {out}\n")
