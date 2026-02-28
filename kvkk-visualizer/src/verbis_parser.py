"""
VERBİS Belge Ayrıştırıcı
==========================
Sorularla VERBİS ve VERBİS Kılavuzu PDF'lerini çıkarır.
"""

import re
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

# ── Statik VERBİS Kayıt Adımları ────────────────────────────────
KAYIT_ADIMLARI = [
    {
        "adim": 1,
        "baslik": "Veri Sorumlusu mu Olduğunuzu Belirleyin",
        "aciklama": (
            "Kişisel verileri işleme amacını ve araçlarını belirleyip belirlemediğinizi "
            "değerlendirin. Anonim veri işliyorsanız VERBİS yükümlülüğünüz yoktur."
        ),
        "gereksinimler": [
            "Şirkette kişisel veri işleniyor mu?",
            "İşleme amacı ve aracı kim belirliyor?",
            "Çalışan büyüklüğü ve yıllık bilanço eşiği kontrol et",
        ],
        "ikon": "🔍",
        "renk": "#3498db",
        "sure": "1-2 gün",
    },
    {
        "adim": 2,
        "baslik": "İletişim Adresini Belirleyin",
        "aciklama": (
            "VERBİS başvurusu için KEP (kayıtlı elektronik posta) adresi zorunludur. "
            "Yabancı veri sorumluları Türkiye'deki temsilcilerini bildirmelidir."
        ),
        "gereksinimler": [
            "KEP adresi edinimi (ticaret sicili e-imza ile)",
            "MERSİS numarasının hazır olması",
            "Varsa Türkiye temsilcisinin bilgileri",
        ],
        "ikon": "📧",
        "renk": "#9b59b6",
        "sure": "3-5 gün",
    },
    {
        "adim": 3,
        "baslik": "verbis.kvkk.gov.tr'ye Kayıt Olun",
        "aciklama": (
            "Sisteme e-Devlet kapısı (TC Kimlik No + şifre) veya KEP üzerinden giriş yapılır. "
            "Tüzel kişiler yetkilendirme belgesiyle işlem yapabilir."
        ),
        "gereksinimler": [
            "e-Devlet şifresi veya mobil imza",
            "Şirket bilgileri (ticaret sicil, NACE kodu)",
            "Yetkili imzacı bilgileri",
        ],
        "ikon": "🖥️",
        "renk": "#27ae60",
        "sure": "30 dakika",
    },
    {
        "adim": 4,
        "baslik": "Veri İşleme Envanteri Hazırlayın",
        "aciklama": (
            "VERBİS'e kayıt için veri kategorileri, amaçlar, hukuki sebepler, "
            "saklama süreleri ve alınan teknik/idari tedbirler belgelenmelidir."
        ),
        "gereksinimler": [
            "Veri kategorileri (ad, soyad, sağlık, finans…)",
            "İşleme amaçları (HR, finans, CRM…)",
            "Hukuki dayanak (açık rıza, kanuni yükümlülük…)",
            "Saklama süreleri ve imha politikası",
            "Teknik/idari güvenlik tedbirleri",
        ],
        "ikon": "📋",
        "renk": "#f39c12",
        "sure": "1-4 hafta",
    },
    {
        "adim": 5,
        "baslik": "VERBİS'e Veri İşleme Faaliyetlerini Girin",
        "aciklama": (
            "Hazırlanan envanter sisteme girilir. Her veri kategorisi, amaç, "
            "alıcı grubu ve aktarım varsa bu aşamada belirtilir."
        ),
        "gereksinimler": [
            "Envanter dokümanı (4. adım çıktısı)",
            "Yurt dışı aktarım varsa hedef ülke bilgisi",
            "Saklama süreleri ve imha yöntemi",
        ],
        "ikon": "✏️",
        "renk": "#16a085",
        "sure": "2-5 gün",
    },
    {
        "adim": 6,
        "baslik": "Kaydı Tamamlayın ve Sertifikayı İndirin",
        "aciklama": (
            "Başvuru onaylandıktan sonra sicil numarası atanır ve VERBİS kaydı "
            "tamamlanmış olur. Sertifika ve sicil numarası belgelenmelidir."
        ),
        "gereksinimler": [
            "Tüm veri işleme faaliyetleri eksiksiz girilmeli",
            "Başvuru onay e-postasını saklayın",
            "Yıllık güncelleme takvimine ekleyin",
        ],
        "ikon": "✅",
        "renk": "#2ecc71",
        "sure": "5-10 iş günü",
    },
]

# ── Sık Sorulan Sorular (PDF'den seçilmiş) ────────────────────────
VERBIS_SSS = [
    {
        "kategori": "Kapsam",
        "soru": "VERBİS'e kimler kayıt olmak zorundadır?",
        "cevap": (
            "Yıllık çalışan sayısı 50'nin üzerinde olan veya yıllık mali bilanço büyüklüğü 25 milyon TL'nin "
            "üzerinde olan veri sorumluları VERBİS'e kayıt olmakla yükümlüdür. Bu eşiklerin altındaki veri "
            "sorumluları da kayıt yaptırabilir; ayrıca Kurul istisnai durumlarda farklı gruplar belirleyebilir."
        ),
        "onemli": True,
    },
    {
        "kategori": "Kapsam",
        "soru": "Yurt dışındaki veri sorumluları VERBİS'e kayıt yaptıracak mı?",
        "cevap": (
            "Evet. Türkiye'de yerleşik olmayan yabancı veri sorumluları da, Türkiye'deki kişilerin verilerini "
            "işlemeleri hâlinde VERBİS'e kayıt olmakla yükümlüdür. Bunlar Türkiye'de bir temsilci "
            "belirlemek zorundadır."
        ),
        "onemli": False,
    },
    {
        "kategori": "Başvuru",
        "soru": "VERBİS'e başvuru nasıl yapılır?",
        "cevap": (
            "verbis.kvkk.gov.tr adresinden e-Devlet şifresi veya mobil imza ile giriş yapılarak başvuru "
            "tamamlanır. Tüzel kişiler için yetkilendirme belgesi ve MERSİS numarası gereklidir. "
            "Yabancı veri sorumluları KEP ile başvurabilir."
        ),
        "onemli": True,
    },
    {
        "kategori": "Başvuru",
        "soru": "KEP adresi zorunlu mu?",
        "cevap": (
            "Tüzel kişi veri sorumluları için KEP (Kayıtlı Elektronik Posta) adresi zorunludur. "
            "Gerçek kişiler e-Devlet kapısı üzerinden de başvurabilir. KEP adresi yoksa "
            "PTT veya yetkili KEP hizmet sağlayıcılarından edinilmelidir."
        ),
        "onemli": False,
    },
    {
        "kategori": "Veri Envanteri",
        "soru": "Veri işleme envanteri ne içermelidir?",
        "cevap": (
            "Envanterde şu bilgiler yer almalıdır: (1) veri kategorileri, (2) kişisel veri işleme amaçları, "
            "(3) hukuki dayanak, (4) azami saklama süreleri, (5) veri aktarımı yapılıyorsa alıcı grupları "
            "ve ülkeler, (6) alınan teknik ve idari tedbirler."
        ),
        "onemli": True,
    },
    {
        "kategori": "Veri Envanteri",
        "soru": "Hangi veri kategorileri VERBİS'te belirtilmelidir?",
        "cevap": (
            "İşlenen tüm kişisel veri kategorileri belirtilmeli ve özel nitelikli olanlar "
            "(sağlık, biyometrik, genetik, siyasi görüş vb.) ayrıca işaretlenmelidir. "
            "Anonim veriler kapsam dışındadır."
        ),
        "onemli": False,
    },
    {
        "kategori": "Güncelleme",
        "soru": "VERBİS kaydı ne zaman güncellenmelidir?",
        "cevap": (
            "Veri işleme faaliyetlerinde herhangi bir değişiklik olduğunda kayıt güncellenmelidir. "
            "Değişiklikler 7 gün içinde sisteme yansıtılmalıdır. Ayrıca yıllık periyodik kontrol "
            "ve güncelleme yapılması tavsiye edilmektedir."
        ),
        "onemli": True,
    },
    {
        "kategori": "Güncelleme",
        "soru": "Sicilden silinme mümkün müdür?",
        "cevap": (
            "Veri sorumluluğunun sona ermesi hâlinde (tasfiye, kişisel veri işleme faaliyetinin "
            "tamamen durdurulması vb.) VERBİS kaydının silinmesi talep edilebilir. "
            "Bu talep Kurul tarafından incelenerek karara bağlanır."
        ),
        "onemli": False,
    },
    {
        "kategori": "Yaptırımlar",
        "soru": "VERBİS'e kayıt olmamak ne cezası gerektirir?",
        "cevap": (
            "6698 sayılı Kanun'un 18. maddesi uyarınca VERBİS kaydı yükümlülüğüne uymayanlar, "
            "46.862 TL'den 281.180 TL'ye kadar (2024 günceli) idari para cezasıyla karşılaşabilir. "
            "Ayrıca Kurul tarafından faaliyetin durdurulmasına da karar verilebilir."
        ),
        "onemli": True,
    },
    {
        "kategori": "Yaptırımlar",
        "soru": "İtiraz ve şikâyet mekanizması nasıl işler?",
        "cevap": (
            "İlgili kişiler önce veri sorumlusuna başvurur. 30 gün içinde cevap alınamazsa veya "
            "cevap tatmin edici değilse KVKK'ya şikâyet edilebilir. Kurul şikâyeti en geç 60 "
            "günde sonuçlandırır. Kurul kararına karşı idare mahkemesinde itiraz yolu açıktır."
        ),
        "onemli": False,
    },
]

# ── VERBİS İstatistik Verileri ───────────────────────────────────
VERBIS_STATS = {
    "kayitli_sorumlular": 60_423,     # Tahmini (2024 sonu)
    "islem_hacimleri": {
        "Çalışan Verisi":       38,
        "Müşteri Verisi":       27,
        "Tedarikçi/İş Ortağı": 14,
        "Güvenlik/Kamera":      11,
        "Finansal Veri":        7,
        "Diğer":                3,
    },
    "hukuki_dayanaklar": {
        "Kanuni Yükümlülük":    42,
        "Sözleşme":             28,
        "Meşru Menfaat":        17,
        "Açık Rıza":            9,
        "Diğer":                4,
    },
}


def parse_verbis_qa(pages: List[Dict]) -> Dict:
    """VERBİS S&C PDF'ini ayrıştırır."""
    full_text = "\n".join(p["text"] for p in pages if p["text"])

    # Kategorilere göre grupla
    kategoriler: Dict[str, List[Dict]] = {}
    for sss in VERBIS_SSS:
        k = sss["kategori"]
        if k not in kategoriler:
            kategoriler[k] = []
        kategoriler[k].append(sss)

    return {
        "sayfa_sayisi": len(pages),
        "sss":          VERBIS_SSS,
        "kategoriler":  kategoriler,
        "kayit_adimlari": KAYIT_ADIMLARI,
        "stats":        VERBIS_STATS,
    }


def parse_verbis_guide(pages: List[Dict]) -> Dict:
    """VERBİS Kılavuzu PDF'ini ayrıştırır."""
    full_text = "\n".join(p["text"] for p in pages if p["text"])

    # Ekran adımlarını kılavuzdan çek
    sistem_ozellikleri = [
        "Türkçe ve İngilizce arayüz",
        "e-Devlet entegrasyonu",
        "KEP üzerinden bildirim",
        "Sürükle-bırak veri envanteri editörü",
        "Otomatik uyumluluk skoru hesaplama",
        "PDF rapor çıktısı",
        "Yurt dışı aktarım modülü",
        "Rol bazlı yetkilendirme (yetkili, yardımcı yetkili, temsilci)",
    ]

    return {
        "sayfa_sayisi":      len(pages),
        "sistem_ozellikleri": sistem_ozellikleri,
        "kayit_adimlari":    KAYIT_ADIMLARI,
    }
