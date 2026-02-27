"""
KVKK Değişiklik Analiz ve Raporlama Aracı
==========================================
PPT verilerini işleyerek KVKK kanun maddelerindeki değişiklikleri
resmi kaynaklarla karşılaştırır ve zengin HTML rapor üretir.

Kullanım:
    python kvkk_rapor.py            # Raporu oluştur (sadece yerel veri)
    python kvkk_rapor.py --online   # Resmi mevzuat.gov.tr verisini çek
    python kvkk_rapor.py --çıktı rapor.html  # Özel dosya adı
"""

# ═══════════════════════════════════════════════════════════════════
# 0 · IMPORTS
# ═══════════════════════════════════════════════════════════════════
__version__ = "1.2.0"

import re, json, sys, io, time, string, argparse, logging, textwrap
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import List, Dict, Tuple, Optional

# Windows konsolunda UTF-8 karakterleri düzgün yazdır
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s",
                    datefmt="%H:%M:%S")
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════
# 1 · DİZİN AYARLARI
# ═══════════════════════════════════════════════════════════════════
BASE_DIR      = Path(__file__).resolve().parent.parent
VEKTORLER_DIR = BASE_DIR / "çıktılar" / "vektorler"
TXT_DIR       = BASE_DIR / "çıktılar" / "txt"
RAPORLAR_DIR  = BASE_DIR / "çıktılar" / "raporlar"

# ═══════════════════════════════════════════════════════════════════
# 2 · KVKK MADDE VERİ TABANI (Yerel Yedek)
#     Kaynak: 6698 sayılı Kanun + 7499 sayılı Değişiklik Kanunu
# ═══════════════════════════════════════════════════════════════════
KVKK_MADDELER: Dict[int, Dict] = {
    1: {
        "baslik": "Amaç",
        "ozet": "Kişisel verilerin işlenmesinde başta özel hayatın gizliliği olmak üzere kişilerin temel hak ve özgürlüklerini korumak.",
        "mevcut_metin": "Bu Kanunun amacı, kişisel verilerin işlenmesinde başta özel hayatın gizliliği olmak üzere kişilerin temel hak ve özgürlüklerini korumak ve kişisel verileri işleyen gerçek ve tüzel kişilerin yükümlülükleri ile uyacakları usul ve esasları düzenlemektir.",
        "degisiklik": None,
    },
    2: {
        "baslik": "Kapsam",
        "ozet": "Kişisel verileri işlenen gerçek kişiler ile bu verileri tamamen veya kısmen otomatik olan ya da herhangi bir veri kayıt sisteminin parçası olmak kaydıyla otomatik olmayan yollarla işleyen gerçek veya tüzel kişiler.",
        "mevcut_metin": "Bu Kanun hükümleri, kişisel verileri işlenen gerçek kişiler ile bu verileri tamamen veya kısmen otomatik olan ya da herhangi bir veri kayıt sisteminin parçası olmak kaydıyla otomatik olmayan yollarla işleyen gerçek ve tüzel kişiler hakkında uygulanır.",
        "degisiklik": None,
    },
    3: {
        "baslik": "Tanımlar",
        "ozet": "Açık rıza, anonim hâle getirme, ilgili kişi, kişisel veri, kişisel verilerin işlenmesi, kurul, kurum, veri işleyen, VERBİS, veri sorumlusu kavramları.",
        "mevcut_metin": "Bu Kanunda yer alan kavramların tanımları düzenlenmekte olup temel tanımlar şunlardır: Açık rıza: Belirli bir konuya ilişkin, bilgilendirilmeye dayanan ve özgür iradeyle açıklanan rıza. Kişisel veri: Kimliği belirli veya belirlenebilir gerçek kişiye ilişkin her türlü bilgi. Veri sorumlusu: Kişisel verilerin işleme amaçlarını ve vasıtalarını belirleyen, veri kayıt sisteminin kurulmasından ve yönetilmesinden sorumlu olan gerçek veya tüzel kişi.",
        "degisiklik": None,
    },
    4: {
        "baslik": "Kişisel Verilerin İşlenmesinde Genel İlkeler",
        "ozet": "Hukuka ve dürüstlük kurallarına uygun, doğru ve güncel, belirli açık ve meşru amaçlar, amaçla bağlantılı, ilgili ve ölçülü, ilgili mevzuatta öngörülen süre kadar muhafaza.",
        "mevcut_metin": "Kişisel veriler ancak bu Kanunda ve diğer kanunlarda öngörülen hallerde veya kişinin açık rızasıyla işlenebilir. a) Hukuka ve dürüstlük kurallarına uygun olma. b) Doğru ve gerektiğinde güncel olma. c) Belirli, açık ve meşru amaçlar için işlenme. ç) İşlendikleri amaçla bağlantılı, sınırlı ve ölçülü olma. d) İlgili mevzuatta öngörülen veya işlendikleri amaç için gerekli olan süre kadar muhafaza edilme.",
        "degisiklik": None,
    },
    5: {
        "baslik": "Kişisel Verilerin İşlenme Şartları",
        "ozet": "Açık rıza veya kanunda öngörülen şartlardan birinin varlığı gerekir.",
        "mevcut_metin": "Kişisel veriler ilgili kişinin açık rızası olmaksızın işlenemez. Aşağıdaki şartlardan birinin varlığı hâlinde, ilgili kişinin açık rızası aranmaksızın kişisel verilerinin işlenmesi mümkündür: a) Kanunlarda açıkça öngörülmesi. b) Fiili imkânsızlık nedeniyle rızasını açıklayamayacak durumda bulunan veya rızasına hukuki geçerlilik tanınmayan kişinin kendisinin ya da bir başkasının hayatı veya beden bütünlüğünün korunması için zorunlu olması. c) Bir sözleşmenin kurulması veya ifasıyla doğrudan doğruya ilgili olması kaydıyla, sözleşmenin taraflarına ait kişisel verilerin işlenmesinin gerekli olması. ç) Veri sorumlusunun hukuki yükümlülüğünü yerine getirebilmesi için zorunlu olması. d) İlgili kişinin kendisi tarafından alenileştirilmiş olması. e) Bir hakkın tesisi, kullanılması veya korunması için veri işlemenin zorunlu olması. f) İlgili kişinin temel hak ve özgürlüklerine zarar vermemek kaydıyla, veri sorumlusunun meşru menfaatleri için veri işlenmesinin zorunlu olması.",
        "degisiklik": None,
    },
    6: {
        "baslik": "Özel Nitelikli Kişisel Verilerin İşlenme Şartları",
        "ozet": "Irk, etnik köken, siyasi düşünce, felsefi inanç, din, mezhep, kılık kıyafet, vakıf üyeliği, sağlık, cinsel hayat, ceza mahkûmiyeti, biyometrik ve genetik veriler özel niteliklidir.",
        "mevcut_metin": "(1) Kişilerin ırkı, etnik kökeni, siyasi düşüncesi, felsefi inancı, dini, mezhebi veya diğer inançları, kılık ve kıyafeti, dernek, vakıf ya da sendika üyeliği, sağlığı, cinsel hayatı, ceza mahkûmiyeti ve güvenlik tedbirleriyle ilgili verileri ile biyometrik ve genetik verileri özel nitelikli kişisel veridir. (3) [7499 sonrası] Özel nitelikli kişisel verilerin işlenmesi yasaktır. Ancak belirli şartların varlığında (açık rıza, kanunda öngörülmesi, fiili imkânsızlık, alenileştirme, hak tesisi, sağlık hizmetleri, sosyal güvenlik yükümlülükleri, vakıf/dernek amaçları) işlenmesi mümkündür.",
        "degisiklik": {
            "kanun_no": "7499",
            "tarih": "12.03.2024",
            "resmi_gazete": "32487",
            "eski_metin": "(2) Özel nitelikli kişisel verilerin, ilgilinin açık rızası olmaksızın işlenmesi yasaktır. (3) Sağlık ve cinsel hayata ilişkin kişisel veriler ise ancak kamu sağlığının korunması, koruyucu hekimlik, tıbbi teşhis, tedavi ve bakım hizmetlerinin yürütülmesi amacıyla ve sır saklama yükümlülüğü altında bulunan kişiler tarafından işlenebilir. (Orijinal 2016 Hali – 6698 sayılı Kanun)",
            "yeni_metin": "(2) MÜLGA — 7499/33. md. ile yürürlükten kaldırıldı (2/3/2024). (3) [DEĞİŞİK 7499/33] Özel nitelikli kişisel verilerin işlenmesi yasaktır; ancak (a) açık rıza, (b) kanunda açıkça öngörülme, (c) fiili imkânsızlık, (ç) alenileştirme, (d) hak tesisi/korunması, (e) sağlık/tıbbi hizmetler (sır saklama yükümlülüğü altında), (f) sosyal güvenlik yükümlülükleri, (g) vakıf/dernek/sendika amaçlarıyla sınırlı olması halinde mümkündür.",
            "etki": "Kritik – Fıkra 2 kaldırıldı, fıkra 3 kapsamlı koşul listesiyle yeniden düzenlendi",
            "gdpr_uyum": "GDPR Madde 9 ile uyumlu — daha kapsamlı özel kategori veri işleme koşulları",
            "ppt_kanit": "PPT Slayt 19 – '(2) (Mülga:2/3/2024-7499/33 md.)' ve '(3) (Değişik:2/3/2024-7499/33 md.)' notasyonları",
        },
    },
    7: {
        "baslik": "Kişisel Verilerin Silinmesi, Yok Edilmesi veya Anonim Hâle Getirilmesi",
        "ozet": "Kişisel veriler, işlenmesini gerektiren sebeplerin ortadan kalkması hâlinde silinir, yok edilir veya anonim hâle getirilir.",
        "mevcut_metin": "Bu Kanun ve ilgili diğer kanun hükümlerine uygun olarak işlenmiş olmasına rağmen, işlenmesini gerektiren sebeplerin ortadan kalkması hâlinde kişisel veriler resen veya ilgili kişinin talebi üzerine veri sorumlusu tarafından silinir, yok edilir veya anonim hâle getirilir.",
        "degisiklik": None,
    },
    8: {
        "baslik": "Kişisel Verilerin Aktarılması",
        "ozet": "Kişisel veriler, işlenme şartları bulunmak kaydıyla üçüncü kişilere aktarılabilir.",
        "mevcut_metin": "Kişisel veriler; kişisel veri işleme şartlarından birinin bulunması kaydıyla ilgili kişinin açık rızası aranmaksızın üçüncü kişilere aktarılabilir.",
        "degisiklik": None,
    },
    9: {
        "baslik": "Kişisel Verilerin Yurt Dışına Aktarılması",
        "ozet": "2024 değişikliği ile yurt dışı aktarım rejimi köklü biçimde değiştirildi. Yeterlilik kararı, standart sözleşme ve bağlayıcı şirket kuralları yeni mekanizmalar olarak eklendi.",
        "mevcut_metin": "Kişisel veriler, yeterli korumaya sahip yabancı ülkelere aktarılabilir. Yeterli koruma bulunmaması halinde Türkiye'deki ve ilgili yabancı ülkedeki veri sorumlularının yeterli bir korumayı yazılı olarak taahhüt etmeleri ve Kurulun izninin bulunması kaydıyla kişisel veriler yurt dışına aktarılabilir.",
        "degisiklik": {
            "kanun_no": "7499",
            "tarih": "12.03.2024",
            "resmi_gazete": "32487",
            "eski_metin": "Kişisel veriler, yeterli korumaya sahip yabancı ülkelere aktarılabilir. Yeterli koruma bulunmaması halinde Türkiye'deki ve ilgili yabancı ülkedeki veri sorumlularının yeterli bir korumayı yazılı olarak taahhüt etmeleri ve Kurulun izninin bulunması kaydıyla kişisel veriler yurt dışına aktarılabilir. (Eski 2016 Hali)",
            "yeni_metin": "Kişisel veriler; (a) Yeterlilik kararı bulunması, (b) Uygun güvenceler kapsamında: standart sözleşmeler, bağlayıcı şirket kuralları, Kurul tarafından onaylanan sözleşme veya uluslararası koruma, ya da (c) Açık rıza veya belirli istisnalar dahilinde yurt dışına aktarılabilir. (7499 Sayılı Kanun Değişikliği - 2024)",
            "etki": "Kritik – Tüm yurt dışı aktarım mekanizmaları değişti",
            "gdpr_uyum": "GDPR Madde 44-49 ile uyumlu hale getirildi",
        },
    },
    10: {
        "baslik": "Veri Sorumlusunun Aydınlatma Yükümlülüğü",
        "ozet": "Kişisel verilerin elde edilmesi sırasında veri sorumlusu, ilgili kişiyi aydınlatmak zorundadır.",
        "mevcut_metin": "Kişisel verilerin elde edilmesi sırasında veri sorumlusu veya yetkilendirdiği kişi, ilgili kişilere belirli bilgileri vermek zorundadır: a) Veri sorumlusunun kimliği. b) Kişisel verilerin hangi amaçla işleneceği. c) İşlenen kişisel verilerin kimlere ve hangi amaçla aktarılabileceği. ç) Kişisel veri toplamanın yöntemi ve hukuki sebebi. d) İlgili kişinin kanundan doğan hakları.",
        "degisiklik": None,
    },
    11: {
        "baslik": "İlgili Kişinin Hakları",
        "ozet": "Bilgi talep etme, amaç ve kullanım bilgisi, aktarım bilgisi, düzeltme talep etme, silinme talep etme, işlemeye itiraz etme, zarar tazminatı.",
        "mevcut_metin": "Herkes, veri sorumlusuna başvurarak kendisiyle ilgili şu hakları kullanabilir: a) Kişisel veri işlenip işlenmediğini öğrenme. b) Kişisel verileri işlenmişse buna ilişkin bilgi talep etme. c) Kişisel verilerin işlenme amacını öğrenme. ç) Yurt içinde veya yurt dışında kişisel verilerin aktarıldığı üçüncü kişileri bilme. d) Kişisel verilerin eksik veya yanlış işlenmiş olması hâlinde bunların düzeltilmesini isteme. e) Kişisel verilerin silinmesini veya yok edilmesini isteme. f) İtiraz etme. g) Zararın giderilmesini talep etme.",
        "degisiklik": None,
    },
    12: {
        "baslik": "Veri Güvenliğine İlişkin Yükümlülükler",
        "ozet": "Veri sorumlusu, kişisel verilerin güvenliğini sağlamak amacıyla uygun güvenlik düzeyini temin etmeye yönelik teknik ve idari tedbirleri almak zorundadır.",
        "mevcut_metin": "Veri sorumlusu; a) Kişisel verilerin hukuka aykırı olarak işlenmesini önlemek, b) Kişisel verilere hukuka aykırı olarak erişilmesini önlemek, c) Kişisel verilerin muhafazasını sağlamak amacıyla uygun güvenlik düzeyini temin etmeye yönelik gerekli her türlü teknik ve idari tedbirleri almak zorundadır.",
        "degisiklik": None,
    },
    13: {
        "baslik": "Veri Sorumlusuna Başvuru",
        "ozet": "İlgili kişi, haklarını kullanmak için veri sorumlusuna başvurabilir. Veri sorumlusu 30 gün içinde yanıt vermek zorundadır.",
        "mevcut_metin": "İlgili kişi, bu Kanunun uygulanmasıyla ilgili taleplerini yazılı olarak veya Kurulun belirleyeceği diğer yöntemlerle veri sorumlusuna iletir. Veri sorumlusu, başvuruda yer alan talepleri, talebin niteliğine göre en kısa sürede ve en geç otuz gün içinde ücretsiz olarak sonuçlandırır.",
        "degisiklik": None,
    },
    17: {
        "baslik": "Suçlar",
        "ozet": "Kişisel verilerin hukuka aykırı ele geçirilmesi, yayılması ve silinmemesi suç teşkil eder. Türk Ceza Kanunu hükümleri uygulanır.",
        "mevcut_metin": "Kişisel verilere ilişkin suçlar bakımından 26/9/2004 tarihli ve 5237 sayılı Türk Ceza Kanununun 135 ila 140 ıncı madde hükümleri uygulanır. Bu Kanun kapsamındaki verilerle ilgili olarak bu Kanun hükümlerine aykırı olarak yapılan işlemler de aynı madde kapsamında değerlendirilir.",
        "degisiklik": None,
    },
    18: {
        "baslik": "Kabahatler",
        "ozet": "Aydınlatma yükümlülüğü, veri güvenliği, kurul kararlarına uyma ve VERBİS ihlalleri idari para cezası gerektirir.",
        "mevcut_metin": "Bu Kanunun 10 uncu maddesinde öngörülen aydınlatma yükümlülüğünü yerine getirmeyenler hakkında 9.182 TL'den 183.614 TL'ye kadar; 12 nci maddesi kapsamında veri güvenliğine ilişkin yükümlülükleri yerine getirmeyenler hakkında 45.909 TL'den 9.180.507 TL'ye kadar idari para cezası verilir.",
        "degisiklik": {
            "kanun_no": "7499",
            "tarih": "12.03.2024",
            "resmi_gazete": "32487",
            "eski_metin": "2016 tarihli orijinal Kanundaki ceza miktarları çok daha düşüktü ve yıllık yeniden değerleme katsayısı ile artırılmaktaydı.",
            "yeni_metin": "7499 sayılı Kanun ile ceza miktarları artırıldı ve ceza mekanizması yeniden yapılandırıldı. Cezalar alt ve üst sınır olarak belirlendi.",
            "etki": "Önemli – Ceza miktarları ve mekanizması değişti",
            "gdpr_uyum": "GDPR ceza yapısına kısmen yaklaştırıldı",
        },
    },
}

KVKK_DEGISIKLIKLER = [
    {
        "kanun_no": "7499",
        "tarih": "12.03.2024",
        "resmi_gazete": "32487",
        "baslik": "7499 Sayılı Kişisel Verilerin Korunması Kanunu ile Bazı Kanunlarda Değişiklik Yapılmasına Dair Kanun",
        "link": "https://www.resmigazete.gov.tr/eskiler/2024/03/20240312-1.htm",
        "etkilenen_maddeler": [6, 9, 18],
        "ozet": (
            "Madde 6 (Özel Nitelikli Veriler): Fıkra 2 mülga edildi; fıkra 3 kapsamlı koşul listesiyle yeniden düzenlendi. "
            "Madde 9 (Yurt Dışı Aktarım): Tüm aktarım mekanizmaları GDPR ile uyumlu biçimde kökten değiştirildi — "
            "yeterlilik kararı, standart sözleşme, bağlayıcı şirket kuralları eklendi. "
            "Madde 18 (Kabahatler): Yeni 50.000–1.000.000 TL para cezası bandı eklendi (bent d); "
            "idari para cezalarına idare mahkemesinde itiraz yolu açıldı (fıkra 3 eklendi). "
            "Geçici Madde 3 (Ek): Madde 9 eski halinin 1/9/2024'e kadar uygulanmaya devam edeceği hükmü getirildi."
        ),
    },
    {
        "kanun_no": "6698",
        "tarih": "07.04.2016",
        "resmi_gazete": "29677",
        "baslik": "Kişisel Verilerin Korunması Kanunu (Orijinal)",
        "link": "https://www.resmigazete.gov.tr/eskiler/2016/04/20160407-8.htm",
        "etkilenen_maddeler": list(range(1, 31)),
        "ozet": "Kanun yürürlüğe girdi. Kişisel verilerin korunması alanındaki temel yasal çerçeve belirlendi.",
    },
]


# ═══════════════════════════════════════════════════════════════════
# 3 · VERİ YÜKLEME
# ═══════════════════════════════════════════════════════════════════

def load_metadata() -> Dict:
    meta_path = VEKTORLER_DIR / "metadata.json"
    if not meta_path.exists():
        logger.error(f"metadata.json bulunamadı: {meta_path}")
        logger.error("Önce 'CALISTIR.bat' ile vektörleştirme yapın.")
        sys.exit(1)
    with open(meta_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    logger.info(f"Metadata yüklendi: {data['toplam_parca']} parça")
    return data


def load_txt_files() -> Dict[str, str]:
    """Her TXT dosyasını tam metin olarak yükler."""
    txt_files = {}
    if not TXT_DIR.exists():
        return txt_files
    for txt_file in sorted(TXT_DIR.glob("*.txt")):
        with open(txt_file, "r", encoding="utf-8") as f:
            txt_files[txt_file.stem] = f.read()
    return txt_files


# ───────────────────────────────────────────────────────────────────
# PPT'DEN OTOMATİK DEĞİŞİKLİK NOTASYONU ÇIKARICI
# ───────────────────────────────────────────────────────────────────
# Türk hukuk metinlerinde değişiklik notasyonları şu formatta gelir:
#   (Değişik:2/3/2024-7499/33 md.)  → madde/fıkra değişti
#   (Mülga:2/3/2024-7499/33 md.)   → madde/fıkra mülga edildi
#   (Ek:2/3/2024-7499/35 md.)      → madde/fıkra/bent eklendi
# ───────────────────────────────────────────────────────────────────
_NOTASYON_RE = re.compile(
    r"(\((?P<tip>Değişik|Mülga|Ek)\s*:\s*(?P<gun>\d+)/(?P<ay>\d+)/(?P<yil>\d{4})-(?P<kanun>\d+)/(?P<madde_ref>\d+)\s*md\.\))",
    re.IGNORECASE | re.UNICODE,
)
_MADDE_ONCESI_RE = re.compile(
    r"(?:GEÇİCİ\s+MADDE\s+\d+|MADDE\s+(\d+))\s*[-–]?\s*$",
    re.IGNORECASE | re.UNICODE | re.MULTILINE,
)
_FIKRA_BENT_RE = re.compile(
    r"^\s*(?:\((\d+)\)|([a-zçğışöü])\))",
    re.UNICODE,
)


def extract_ppt_change_annotations(txt_dir: Path) -> List[Dict]:
    """
    TXT çıktı dosyalarını satır satır tarar.
    Türk hukuk notasyonu ile işaretlenmiş değişiklik, mülga ve ek içeren
    her satırı tespit eder ve yapılandırılmış bir liste olarak döndürür.

    Döndürülen her kayıt:
    {
        "tip":        "Değişik" | "Mülga" | "Ek",
        "tarih":      "2/3/2024",
        "kanun_no":   "7499",
        "madde_ref":  "33",           # kanun içindeki madde numarası
        "kaynak_txt": "1- KVKK ...",  # dosya adı
        "slayt_no":   19,
        "baglantilar":["Madde 6"],    # bağlam incelemesiyle tahmin edilen KVKK maddesi
        "notasyon":   "(Mülga:...)",  # ham notasyon metni
        "satir":      "(2) (Mülga:2/3/2024-7499/33 md.)",  # tüm satır
        "onceki_satir": "...",        # bağlam: önceki satır
        "sonraki_satir": "...",       # bağlam: sonraki satır
    }
    """
    results: List[Dict] = []
    if not txt_dir.exists():
        return results

    slayt_header_re = re.compile(r"── Slayt (\d+) ─+")
    # KVKK madde arayıcı – önceki satırlarda geçen "MADDE X" bağlamını taşıyacağız
    madde_context_re = re.compile(r"MADDE\s+(\d+)", re.IGNORECASE)

    for txt_file in sorted(txt_dir.glob("*.txt")):
        dosya_adi = txt_file.stem
        lines = txt_file.read_text(encoding="utf-8").splitlines()

        current_slayt = 0
        current_madde_context: List[int] = []

        for idx, line in enumerate(lines):
            # Slayt numarasını güncelle
            slayt_m = slayt_header_re.search(line)
            if slayt_m:
                current_slayt = int(slayt_m.group(1))
                current_madde_context = []  # yeni slayt → bağlamı sıfırla
                continue

            # Satırda MADDE X görüldüyse bağlamı güncelle
            for mm in madde_context_re.finditer(line):
                mn = int(mm.group(1))
                if 1 <= mn <= 30 and mn not in current_madde_context:
                    current_madde_context.append(mn)
                    if len(current_madde_context) > 5:
                        current_madde_context.pop(0)

            # Notasyon var mı?
            for match in _NOTASYON_RE.finditer(line):
                tip      = match.group("tip").capitalize()
                tarih    = f"{match.group('gun')}/{match.group('ay')}/{match.group('yil')}"
                kanun    = match.group("kanun")
                mad_ref  = match.group("madde_ref")

                onceki  = lines[idx - 1].strip() if idx > 0 else ""
                sonraki = lines[idx + 1].strip() if idx < len(lines) - 1 else ""

                # Bağlam maddesi — geçerli slayttaki bilinen KVKK maddelerini listele
                baglantilar = [f"Madde {m}" for m in current_madde_context[-3:]] if current_madde_context else []

                results.append({
                    "tip":         tip,
                    "tarih":       tarih,
                    "kanun_no":    kanun,
                    "madde_ref":   mad_ref,
                    "kaynak_txt":  dosya_adi,
                    "slayt_no":    current_slayt,
                    "baglantilar": baglantilar,
                    "notasyon":    match.group(1),
                    "satir":       line.strip(),
                    "onceki_satir": onceki,
                    "sonraki_satir": sonraki,
                })

    logger.info(f"   → {len(results)} adet PPT değişiklik notasyonu tespit edildi")
    return results




# ═══════════════════════════════════════════════════════════════════
# 4 · MADDE REFERANS ÇIKARICI
# ═══════════════════════════════════════════════════════════════════

MADDE_PATTERN = re.compile(
    r"(?:madde|m\.)\s*(\d+)[^\d]",
    re.IGNORECASE | re.UNICODE
)
FIKRA_PATTERN = re.compile(
    r"(?:fıkra|f\.)\s*(\d+)",
    re.IGNORECASE | re.UNICODE
)
DEGISIKLIK_PATTERN = re.compile(
    r"(değişti|değişiklik|eski|yeni|güncellendi|revize|7499|2024|2023|2022|2021|2020|2019|2018|2017|2016)",
    re.IGNORECASE | re.UNICODE
)
ESKI_YENI_PATTERN = re.compile(
    r"(?:eski\s*hal[i:]?|eski\s*metin|önceki\s*hal|değişmeden\s*önceki)[^\n]{10,200}",
    re.IGNORECASE | re.UNICODE | re.DOTALL
)
YENI_HAL_PATTERN = re.compile(
    r"(?:yeni\s*hal[i:]?|yeni\s*metin|değişiklik\s*sonrası|güncel\s*hal)[^\n]{10,200}",
    re.IGNORECASE | re.UNICODE | re.DOTALL
)


def extract_article_mentions(chunks: List[Dict]) -> Dict[int, List[Dict]]:
    """Her KVKK maddesinin hangi slaytlarda geçtiğini çıkarır."""
    madde_map: Dict[int, List[Dict]] = defaultdict(list)

    for chunk in chunks:
        metin = chunk["metin"]
        found_maddeler = set()
        for m in MADDE_PATTERN.finditer(metin):
            num = int(m.group(1))
            if 1 <= num <= 30 and num not in found_maddeler:
                found_maddeler.add(num)
                has_change_signal = bool(DEGISIKLIK_PATTERN.search(metin))
                eski_hal = ESKI_YENI_PATTERN.search(metin)
                yeni_hal = YENI_HAL_PATTERN.search(metin)
                madde_map[num].append({
                    "dosya": chunk["dosya"],
                    "slayt_no": chunk["slayt_no"],
                    "metin_ozeti": metin[:250] + ("…" if len(metin) > 250 else ""),
                    "degisiklik_sinyali": has_change_signal,
                    "eski_hal_metni": eski_hal.group(0).strip() if eski_hal else None,
                    "yeni_hal_metni": yeni_hal.group(0).strip() if yeni_hal else None,
                })

    return dict(madde_map)


def compute_statistics(chunks: List[Dict], madde_map: Dict[int, List]) -> Dict:
    """Dosya bazlı istatistikleri hesaplar."""
    dosya_sayisi = defaultdict(int)
    for c in chunks:
        dosya_sayisi[c["dosya"]] += 1

    madde_frekans = {m: len(v) for m, v in madde_map.items()}
    en_cok_5 = sorted(madde_frekans.items(), key=lambda x: -x[1])[:5]

    degisiklik_sinyalli = {
        m: sum(1 for v in refs if v["degisiklik_sinyali"])
        for m, refs in madde_map.items()
    }

    return {
        "toplam_parca": len(chunks),
        "dosya_sayisi": dict(dosya_sayisi),
        "madde_frekans": madde_frekans,
        "en_cok_5": en_cok_5,
        "degisiklik_sinyalli": degisiklik_sinyalli,
        "toplam_degisiklik_sinyali": sum(degisiklik_sinyalli.values()),
    }


# ═══════════════════════════════════════════════════════════════════
# 5 · RESMİ MEVZUAT ÇEKİCİ (Online – İsteğe Bağlı)
# ═══════════════════════════════════════════════════════════════════

def fetch_official_law() -> Optional[str]:
    """mevzuat.gov.tr'den KVKK metnini çeker."""
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        logger.warning("requests/beautifulsoup4 eksik. pip install requests beautifulsoup4")
        return None

    url = ("https://www.mevzuat.gov.tr/mevzuat"
           "?MevzuatNo=6698&MevzuatTur=1&MevzuatTertip=5")
    try:
        r = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        content = soup.find("div", {"id": "MevzuatMetni"}) or soup.find("div", class_="mevzuat-metin")
        text = content.get_text(" ", strip=True) if content else r.text[:5000]
        logger.info(f"Resmi mevzuat çekildi ({len(text)} karakter)")
        return text
    except Exception as exc:
        logger.warning(f"Resmi mevzuat çekilemedi: {exc}")
        return None


# ═══════════════════════════════════════════════════════════════════
# 6 · PLOTLy JSON VERİSİ (HTML içine gömülecek)
# ═══════════════════════════════════════════════════════════════════

def build_chart_data(stats: Dict, madde_map: Dict) -> Dict:
    """Plotly için grafik verisi hazırlar."""
    # Madde frekans çubuğu
    sorted_maddeler = sorted(stats["madde_frekans"].items())
    bar_x = [f"Madde {m}" for m, _ in sorted_maddeler]
    bar_y = [cnt for _, cnt in sorted_maddeler]
    bar_colors = []
    for m, _ in sorted_maddeler:
        if m in KVKK_MADDELER and KVKK_MADDELER[m].get("degisiklik"):
            bar_colors.append("#e74c3c")  # Değişen maddeler kırmızı
        else:
            bar_colors.append("#3498db")  # Normal maddeler mavi

    # Dosya bazlı pasta grafik
    pie_labels = [d.replace(" KVKK Sertifika Programı.pptx", "").replace("- ", "") for d in stats["dosya_sayisi"]]
    pie_values = list(stats["dosya_sayisi"].values())

    # Değişiklik sinyal scatter
    degisiklik_x = [f"Madde {m}" for m in stats["degisiklik_sinyalli"]]
    degisiklik_y = list(stats["degisiklik_sinyalli"].values())

    return {
        "bar": {"x": bar_x, "y": bar_y, "colors": bar_colors},
        "pie": {"labels": pie_labels, "values": pie_values},
        "degisiklik": {"x": degisiklik_x, "y": degisiklik_y},
    }


# ═══════════════════════════════════════════════════════════════════
# 7 · HTML RAPOR OLUŞTURUCUSU
# ═══════════════════════════════════════════════════════════════════

def _render_madde_card(madde_no: int, madde: Dict, refs: List[Dict], stats: Dict) -> str:
    """Tek bir madde için HTML bölümü üretir."""
    degisiklik = madde.get("degisiklik")
    ref_count = len(refs)
    signal_count = sum(1 for r in refs if r["degisiklik_sinyali"])

    badge = ""
    if degisiklik:
        badge = '<span class="badge bg-danger ms-2">DEĞİŞTİ</span>'
    elif signal_count > 0:
        badge = f'<span class="badge bg-warning text-dark ms-2">{signal_count} değişiklik sinyali</span>'

    # Referans listesi (max 5 slayt göster)
    ref_rows = ""
    for ref in refs[:5]:
        dosya_kisa = ref["dosya"].replace(" KVKK Sertifika Programı.pptx", "").replace("- ", "")
        deg_icon = "🔄" if ref["degisiklik_sinyali"] else "📋"
        ref_rows += f"""
        <tr class="{'table-warning' if ref['degisiklik_sinyali'] else ''}">
            <td>{deg_icon}</td>
            <td><span class="badge bg-secondary">{dosya_kisa}</span></td>
            <td class="text-center">{ref['slayt_no']}</td>
            <td><small class="text-muted">{ref['metin_ozeti']}</small></td>
        </tr>"""
    if len(refs) > 5:
        ref_rows += f'<tr><td colspan="4" class="text-center text-muted"><em>… ve {len(refs)-5} slayt daha</em></td></tr>'

    # Değişiklik karşılaştırma bölümü
    karsilastirma = ""
    if degisiklik:
        karsilastirma = f"""
        <div class="mt-4">
            <h6 class="fw-bold text-danger">
                <i class="bi bi-exclamation-triangle-fill"></i>
                Kanun Değişikliği – {degisiklik['kanun_no']} ({degisiklik['tarih']})
            </h6>
            <p class="small text-muted mb-2">
                Resmî Gazete: <strong>{degisiklik['resmi_gazete']}</strong> |
                Etki: <strong>{degisiklik['etki']}</strong>
            </p>
            <div class="row">
                <div class="col-md-6">
                    <div class="card border-danger h-100">
                        <div class="card-header bg-danger text-white py-2">
                            <i class="bi bi-x-circle-fill"></i> ESKİ HAL (Önceki)
                        </div>
                        <div class="card-body bg-danger bg-opacity-10">
                            <p class="small mb-0">{degisiklik['eski_metin']}</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card border-success h-100">
                        <div class="card-header bg-success text-white py-2">
                            <i class="bi bi-check-circle-fill"></i> YENİ HAL (Güncel)
                        </div>
                        <div class="card-body bg-success bg-opacity-10">
                            <p class="small mb-0">{degisiklik['yeni_metin']}</p>
                        </div>
                    </div>
                </div>
            </div>
            <div class="alert alert-info mt-3 py-2 small">
                <i class="bi bi-link-45deg"></i>
                <strong>GDPR Uyumu:</strong> {degisiklik.get('gdpr_uyum', 'Belirtilmemiş')}
            </div>
            {('<div class="alert alert-warning mt-2 py-2 small"><i class="bi bi-cpu-fill"></i> <strong>PPT Kanıtı:</strong> ' + degisiklik["ppt_kanit"] + "</div>") if degisiklik.get("ppt_kanit") else ""}
        </div>"""

    return f"""
    <div class="card mb-4 shadow-sm {'border-danger' if degisiklik else ''}">
        <div class="card-header {'bg-danger text-white' if degisiklik else 'bg-primary text-white'}">
            <div class="d-flex justify-content-between align-items-center">
                <h5 class="mb-0">Madde {madde_no} – {madde['baslik']}{badge}</h5>
                <span class="badge bg-light text-dark">{ref_count} slayt atıfı</span>
            </div>
        </div>
        <div class="card-body">
            <div class="row mb-3">
                <div class="col-md-8">
                    <h6 class="text-secondary">📖 Özet</h6>
                    <p class="mb-2">{madde['ozet']}</p>
                    <h6 class="text-secondary mt-3">📜 Kanun Metni</h6>
                    <div class="p-3 bg-light border rounded small">{madde['mevcut_metin']}</div>
                </div>
                <div class="col-md-4">
                    <h6 class="text-secondary">📊 PPT'deki Atıflar</h6>
                    <div class="table-responsive">
                        <table class="table table-sm table-hover">
                            <thead class="table-light">
                                <tr>
                                    <th></th><th>Dosya</th><th>Slayt</th><th>Bağlam</th>
                                </tr>
                            </thead>
                            <tbody>{ref_rows}</tbody>
                        </table>
                    </div>
                </div>
            </div>
            {karsilastirma}
        </div>
    </div>"""


def _render_timeline() -> str:
    """Kanun değişiklikleri zaman çizelgesi."""
    items = ""
    for i, dg in enumerate(sorted(KVKK_DEGISIKLIKLER, key=lambda x: x["tarih"])):
        side = "left" if i % 2 == 0 else "right"
        etkilenen = ", ".join([f"Madde {m}" for m in dg["etkilenen_maddeler"][:5]])
        if len(dg["etkilenen_maddeler"]) > 5:
            etkilenen += " ve diğerleri"
        color = "#e74c3c" if dg["kanun_no"] != "6698" else "#3498db"
        items += f"""
        <div class="timeline-item {side}">
            <div class="timeline-content" style="border-left: 4px solid {color};">
                <div class="fw-bold" style="color:{color};">{dg['tarih']} – {dg['kanun_no']} Sayılı Kanun</div>
                <div class="small text-muted">RG: {dg['resmi_gazete']}</div>
                <p class="small mt-1 mb-1">{dg['ozet']}</p>
                <div class="small"><strong>Etkilenen:</strong> {etkilenen}</div>
                <a href="{dg['link']}" target="_blank" class="small">Resmî Gazete ↗</a>
            </div>
        </div>"""
    return items


def _render_comparison_table(madde_map: Dict) -> str:
    """Eski/Yeni karşılaştırma özet tablosu."""
    rows = ""
    for madde_no, madde in sorted(KVKK_MADDELER.items()):
        if madde.get("degisiklik"):
            dg = madde["degisiklik"]
            ppt_refs = len(madde_map.get(madde_no, []))
            rows += f"""
            <tr class="table-danger">
                <td class="fw-bold">Madde {madde_no}</td>
                <td>{madde['baslik']}</td>
                <td><span class="badge bg-danger">{dg['kanun_no']}</span></td>
                <td>{dg['tarih']}</td>
                <td><small>{dg['etki']}</small></td>
                <td class="text-center">{ppt_refs}</td>
            </tr>"""
    return rows


def _render_ppt_annotations(annotations: List[Dict]) -> str:
    """
    PPT'lerden otomatik çıkarılan değişiklik notasyonlarını
    güzel bir HTML bölümü olarak gösterir.
    """
    if not annotations:
        return '<div class="alert alert-secondary">PPT dosyalarında değişiklik notasyonu bulunamadı.</div>'

    tip_badge = {
        "Değişik": ("bg-warning text-dark", "bi-pencil-square", "DEĞİŞİK"),
        "Mülga":   ("bg-danger",            "bi-trash-fill",    "MÜLGA"),
        "Ek":      ("bg-success",           "bi-plus-circle-fill", "EK"),
    }

    # Kanun bazlı grupla
    by_kanun: Dict[str, List[Dict]] = defaultdict(list)
    for ann in annotations:
        by_kanun[ann["kanun_no"]].append(ann)

    html_parts = []
    for kanun_no in sorted(by_kanun.keys(), reverse=True):
        anns = by_kanun[kanun_no]
        rows = ""
        for ann in anns:
            badge_cls, icon, etiket = tip_badge.get(
                ann["tip"], ("bg-secondary", "bi-circle", ann["tip"])
            )
            baglanti_html = " ".join(
                f'<span class="badge bg-light text-dark border">{b}</span>'
                for b in ann["baglantilar"]
            ) or '<span class="text-muted small">—</span>'

            dosya_kisa = ann["kaynak_txt"].replace(" KVKK Sertifika Programı", "")
            satir_html = ann["satir"].replace("<", "&lt;").replace(">", "&gt;")
            onceki_html = ann["onceki_satir"].replace("<", "&lt;").replace(">", "&gt;")
            sonraki_html = ann["sonraki_satir"].replace("<", "&lt;").replace(">", "&gt;")

            rows += f"""
            <tr>
                <td class="text-center">
                    <span class="badge {badge_cls}">
                        <i class="bi {icon}"></i> {etiket}
                    </span>
                </td>
                <td class="text-center text-muted small">{ann['tarih']}</td>
                <td class="text-center">
                    <span class="badge bg-secondary">{dosya_kisa}</span>
                    <div class="small text-muted">Slayt {ann['slayt_no']}</div>
                </td>
                <td>{baglanti_html}</td>
                <td>
                    <div class="small font-monospace text-danger fw-bold">{satir_html}</div>
                    <div class="small text-muted mt-1">
                        <span class="me-2 text-secondary">↑</span>{onceki_html}
                    </div>
                    <div class="small text-muted">
                        <span class="me-2 text-secondary">↓</span>{sonraki_html}
                    </div>
                </td>
            </tr>"""

        kanun_tarih = anns[0]["tarih"] if anns else "—"
        html_parts.append(f"""
        <div class="card mb-4 shadow-sm border-warning">
            <div class="card-header bg-warning text-dark">
                <i class="bi bi-journal-code"></i>
                <strong>{kanun_no} Sayılı Kanun Değişiklikleri</strong>
                <span class="ms-2 badge bg-dark">{len(anns)} notasyon</span>
                <span class="ms-2 text-dark small">Tarih: {kanun_tarih}</span>
            </div>
            <div class="card-body p-0">
                <div class="alert alert-info m-3 py-2 small mb-0">
                    <i class="bi bi-cpu-fill"></i>
                    Bu notasyonlar PPT dosyalarının metinlerinden <strong>otomatik olarak tespit edilmiştir</strong>.
                    Her satır, slayt numarası ve bağlamıyla birlikte gösterilmektedir.
                </div>
                <div class="table-responsive">
                    <table class="table table-sm table-hover mb-0">
                        <thead class="table-dark">
                            <tr>
                                <th class="text-center">Tür</th>
                                <th class="text-center">Tarih</th>
                                <th class="text-center">Kaynak</th>
                                <th>KVKK Bağlamı</th>
                                <th>Slayt Metni (Bağlam)</th>
                            </tr>
                        </thead>
                        <tbody>{rows}</tbody>
                    </table>
                </div>
            </div>
        </div>""")

    return "\n".join(html_parts)


def build_html_report(meta: Dict, madde_map: Dict, stats: Dict, chart_data: Dict,
                      official_text: Optional[str] = None,
                      ppt_annotations: Optional[List[Dict]] = None) -> str:
    """Ana HTML raporunu üretir."""
    tarih = datetime.now().strftime("%d.%m.%Y %H:%M")
    toplam_parca = meta["toplam_parca"]
    toplam_dosya = len(stats["dosya_sayisi"])
    toplam_madde = len(madde_map)
    degisen_madde = sum(1 for m in KVKK_MADDELER.values() if m.get("degisiklik"))

    # İlk 5 madde kartı (değişenler önce)
    madde_cards_html = ""
    tum_maddeler = set(madde_map.keys()) | set(KVKK_MADDELER.keys())
    degisen_once = sorted(tum_maddeler,
                          key=lambda m: (0 if KVKK_MADDELER.get(m, {}).get("degisiklik") else 1, m))
    for madde_no in degisen_once:
        if madde_no in KVKK_MADDELER:
            refs = madde_map.get(madde_no, [])
            madde_cards_html += _render_madde_card(
                madde_no, KVKK_MADDELER[madde_no], refs, stats
            )

    # Zaman çizelgesi
    timeline_html = _render_timeline()

    # Karşılaştırma tablosu
    comparison_rows = _render_comparison_table(madde_map)

    # PPT notasyon bölümü
    ppt_ann_html = _render_ppt_annotations(ppt_annotations or [])

    # Plotly veri – JSON olarak göm
    chart_json = json.dumps(chart_data, ensure_ascii=False)

    official_section = ""
    if official_text:
        ozet = official_text[:1500].replace("<", "&lt;").replace(">", "&gt;")
        official_section = f"""
        <div class="card mb-4">
            <div class="card-header bg-info text-white">
                <i class="bi bi-globe"></i> Resmî Mevzuat.gov.tr Metni (Canlı Çekilen)
            </div>
            <div class="card-body"><pre class="small text-muted" style="white-space:pre-wrap;">{ozet}…</pre></div>
        </div>"""

    return f"""<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KVKK Değişiklik Analiz Raporu</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
    <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
    <style>
        body {{ font-family:'Segoe UI',sans-serif; background:#f8f9fa; }}
        h1,h2,h3,h4,h5,h6 {{ font-weight:600; }}
        .navbar-brand {{ font-size:1.3rem; font-weight:700; }}
        .stat-card {{ border-radius:12px; padding:1.5rem; color:#fff; text-align:center; }}
        .stat-card .num {{ font-size:2.5rem; font-weight:700; }}
        .stat-card .lbl {{ font-size:.85rem; opacity:.85; }}
        .timeline {{ position:relative; max-width:900px; margin:auto; padding:10px 0; }}
        .timeline::before {{ content:''; position:absolute; left:50%; top:0; bottom:0;
            width:3px; background:#dee2e6; transform:translateX(-50%); }}
        .timeline-item {{ width:45%; padding:12px; margin:12px 0; }}
        .timeline-item.left {{ margin-left:0; margin-right:auto; }}
        .timeline-item.right {{ margin-left:auto; margin-right:0; }}
        .timeline-content {{ background:#fff; border-radius:8px; padding:14px;
            box-shadow:0 2px 8px rgba(0,0,0,.08); }}
        .section-title {{ border-left:5px solid #0d6efd; padding-left:12px; margin:2rem 0 1rem; }}
        @media(max-width:600px) {{
            .timeline-item {{ width:100%; margin-left:0!important; }}
            .timeline::before {{ left:12px; }}
        }}
    </style>
</head>
<body>
<nav class="navbar navbar-dark bg-primary shadow-sm">
    <div class="container">
        <span class="navbar-brand">
            <i class="bi bi-shield-lock-fill"></i> KVKK Değişiklik Analiz Raporu
        </span>
        <span class="text-white-50 small">{tarih}</span>
    </div>
</nav>

<div class="container py-4">

    <!-- ÖZET KARTLAR -->
    <div class="row g-3 mb-5">
        <div class="col-6 col-md-3">
            <div class="stat-card" style="background:linear-gradient(135deg,#0d6efd,#0a58ca);">
                <div class="num">{toplam_dosya}</div>
                <div class="lbl">PPT Dosyası</div>
            </div>
        </div>
        <div class="col-6 col-md-3">
            <div class="stat-card" style="background:linear-gradient(135deg,#198754,#146c43);">
                <div class="num">{toplam_parca}</div>
                <div class="lbl">Metin Parçası</div>
            </div>
        </div>
        <div class="col-6 col-md-3">
            <div class="stat-card" style="background:linear-gradient(135deg,#6610f2,#520dc2);">
                <div class="num">{toplam_madde}</div>
                <div class="lbl">Tespit Edilen Madde</div>
            </div>
        </div>
        <div class="col-6 col-md-3">
            <div class="stat-card" style="background:linear-gradient(135deg,#dc3545,#b02a37);">
                <div class="num">{degisen_madde}</div>
                <div class="lbl">Değişen Madde</div>
            </div>
        </div>
    </div>

    <!-- GRAFİKLER -->
    <h3 class="section-title"><i class="bi bi-bar-chart-fill"></i> İstatistiksel Analiz</h3>
    <div class="row mb-5">
        <div class="col-md-7">
            <div class="card shadow-sm h-100">
                <div class="card-header">Madde Bazlı Atıf Sıklığı <span class="badge bg-danger ms-2">Kırmızı = Değişen Madde</span></div>
                <div class="card-body p-0"><div id="barChart" style="height:350px;"></div></div>
            </div>
        </div>
        <div class="col-md-5">
            <div class="card shadow-sm h-100">
                <div class="card-header">Kaynak PPT Dağılımı</div>
                <div class="card-body p-0"><div id="pieChart" style="height:350px;"></div></div>
            </div>
        </div>
    </div>
    <div class="row mb-5">
        <div class="col-12">
            <div class="card shadow-sm">
                <div class="card-header">Değişiklik Sinyali Taşıyan Slayt Sayısı (Madde Bazlı)</div>
                <div class="card-body p-0"><div id="degisiklikChart" style="height:280px;"></div></div>
            </div>
        </div>
    </div>

    <!-- DEĞİŞİKLİK KARŞILAŞTIRMa TABLOSU -->
    <h3 class="section-title"><i class="bi bi-table"></i> Değişiklik Özet Tablosu</h3>
    <div class="card shadow-sm mb-5">
        <div class="card-body p-0">
            <div class="table-responsive">
                <table class="table table-hover mb-0">
                    <thead class="table-dark">
                        <tr>
                            <th>Madde</th>
                            <th>Başlık</th>
                            <th>Değişiklik Kanunu</th>
                            <th>Tarih</th>
                            <th>Etki</th>
                            <th>PPT Atıfları</th>
                        </tr>
                    </thead>
                    <tbody>
                        {comparison_rows if comparison_rows else '<tr><td colspan="6" class="text-center text-muted py-3">Tespit edilen kanun değişikliği yok</td></tr>'}
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- PPT'DEN OTOMATİK TESPİT EDİLEN DEĞİŞİKLİK NOTASYONLARI -->
    <h3 class="section-title">
        <i class="bi bi-cpu-fill text-warning"></i>
        PPT'lerden Otomatik Tespit Edilen Değişiklik Notasyonları
    </h3>
    <div class="mb-3 alert alert-warning small py-2">
        <i class="bi bi-exclamation-triangle-fill"></i>
        Aşağıdaki notasyonlar, PPT dosyalarının slayt metinlerinden makine tarafından otomatik çıkarılmıştır.
        Türk hukuk mevzuatındaki standart <code>(Değişik:tarih-kanun/madde md.)</code>,
        <code>(Mülga:...)</code> ve <code>(Ek:...)</code> formatları aranmıştır.
    </div>
    {ppt_ann_html}

    <!-- ZAMAN ÇİZELGESİ -->
    <h3 class="section-title"><i class="bi bi-calendar3"></i> Kanun Değişiklik Zaman Çizelgesi</h3>
    <div class="card shadow-sm mb-5">
        <div class="card-body">
            <div class="timeline">
                {timeline_html}
            </div>
        </div>
    </div>

    <!-- MADDE DETAY KARTLARI -->
    <h3 class="section-title"><i class="bi bi-journal-text"></i> Madde Bazlı Detaylı Analiz</h3>
    <div class="mb-3 alert alert-info small py-2">
        <i class="bi bi-info-circle-fill"></i>
        <strong>Kırmızı çerçeveli kartlar</strong> değişikliğe uğramış maddeleri,
        <strong>turuncu rozetler</strong> PPT'lerde değişiklik sinyali tespit edilen bölümleri gösterir.
        Atıf bulunmayan ama önemli maddeler de dahil edilmiştir.
    </div>
    {madde_cards_html}

    {official_section}

    <!-- KAYNAKLAR -->
    <h3 class="section-title"><i class="bi bi-link-45deg"></i> Resmi Kaynaklar</h3>
    <div class="card shadow-sm mb-5">
        <div class="card-body">
            <ul class="list-group list-group-flush">
                <li class="list-group-item">
                    <i class="bi bi-file-text text-primary"></i>
                    <strong>6698 Sayılı KVKK:</strong>
                    <a href="https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=6698&MevzuatTur=1&MevzuatTertip=5"
                       target="_blank">mevzuat.gov.tr ↗</a>
                    &nbsp;|&nbsp;
                    <a href="https://www.resmigazete.gov.tr/eskiler/2016/04/20160407-8.htm"
                       target="_blank">Resmî Gazete 29677 ↗</a>
                </li>
                <li class="list-group-item">
                    <i class="bi bi-file-text text-danger"></i>
                    <strong>7499 Sayılı Değişiklik Kanunu (2024):</strong>
                    <a href="https://www.resmigazete.gov.tr/eskiler/2024/03/20240312-1.htm"
                       target="_blank">Resmî Gazete 32487 ↗</a>
                </li>
                <li class="list-group-item">
                    <i class="bi bi-shield-lock text-info"></i>
                    <strong>KVKK Kurumu:</strong>
                    <a href="https://www.kvkk.gov.tr" target="_blank">kvkk.gov.tr ↗</a>
                </li>
                <li class="list-group-item">
                    <i class="bi bi-globe text-success"></i>
                    <strong>VERBİS:</strong>
                    <a href="https://verbis.kvkk.gov.tr" target="_blank">verbis.kvkk.gov.tr ↗</a>
                </li>
            </ul>
        </div>
    </div>

    <footer class="text-center text-muted small py-4 border-top">
        <i class="bi bi-robot"></i> Bu rapor otomatik olarak oluşturulmuştur.
        Model: <code>{meta.get('model','—')}</code> |
        Kaynak: {toplam_dosya} PPTX → {toplam_parca} parça |
        Tarih: {tarih}
    </footer>

</div><!-- /container -->

<script>
const CHART = {chart_json};

// Bar Chart
Plotly.newPlot('barChart', [{{
    type: 'bar', x: CHART.bar.x, y: CHART.bar.y,
    marker: {{ color: CHART.bar.colors, line: {{color:'#fff', width:0.5}} }},
    hovertemplate: '%{{x}}: %{{y}} slayt atıfı<extra></extra>'
}}], {{
    margin:{{t:20,r:20,b:120,l:50}},
    paper_bgcolor:'#fff', plot_bgcolor:'#f8f9fa',
    xaxis:{{ tickangle:-45, tickfont:{{size:11}} }},
    yaxis:{{ title:'Atıf Sayısı' }}
}}, {{responsive:true, displayModeBar:false}});

// Pie Chart
Plotly.newPlot('pieChart', [{{
    type:'pie', labels: CHART.pie.labels, values: CHART.pie.values,
    hole:0.4, textinfo:'percent+label',
    hovertemplate:'%{{label}}: %{{value}} parça (%{{percent}})<extra></extra>'
}}], {{
    margin:{{t:20,r:20,b:20,l:20}}, paper_bgcolor:'#fff',
    showlegend:false
}}, {{responsive:true, displayModeBar:false}});

// Değişiklik Chart
Plotly.newPlot('degisiklikChart', [{{
    type:'bar', x: CHART.degisiklik.x, y: CHART.degisiklik.y,
    marker:{{ color:'#f39c12', opacity:0.85 }},
    hovertemplate:'%{{x}}: %{{y}} slayt değişiklik sinyali<extra></extra>'
}}], {{
    margin:{{t:20,r:20,b:100,l:50}},
    paper_bgcolor:'#fff', plot_bgcolor:'#f8f9fa',
    xaxis:{{ tickangle:-45 }}, yaxis:{{ title:'Sinyal Sayısı' }}
}}, {{responsive:true, displayModeBar:false}});
</script>
</body>
</html>"""


# ═══════════════════════════════════════════════════════════════════
# 8 · ANA FONKSİYON
# ═══════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="KVKK Değişiklik Analiz ve Raporlama Aracı",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
    python kvkk_rapor.py                    # Yerel verilerle rapor oluştur
    python kvkk_rapor.py --online           # + mevzuat.gov.tr'den canlı veri
    python kvkk_rapor.py --cikti ozet.html  # Özel çıktı adı
        """,
    )
    parser.add_argument("--online", action="store_true",
                        help="mevzuat.gov.tr'den canlı kanun metni çek")
    parser.add_argument("--cikti", type=str, default="KVKK_Analiz_Raporu.html",
                        help="Çıktı HTML dosyası adı")
    args = parser.parse_args()

    logger.info("━" * 55)
    logger.info("KVKK DEĞİŞİKLİK ANALİZ RAPORU OLUŞTURULUYOR")
    logger.info("━" * 55)

    # 1) Veri yükle
    logger.info("1/6 · Metadata yükleniyor…")
    meta = load_metadata()
    chunks = meta["chunks"]

    # 2) Madde referansları çıkar
    logger.info("2/6 · KVKK madde referansları çıkarılıyor…")
    madde_map = extract_article_mentions(chunks)
    logger.info(f"   → {len(madde_map)} farklı madde tespit edildi")

    # 3) İstatistikler
    logger.info("3/6 · İstatistikler hesaplanıyor…")
    stats = compute_statistics(chunks, madde_map)
    logger.info(f"   → En çok atıf: {stats['en_cok_5']}")

    # 4) Resmi mevzuat (opsiyonel)
    official_text = None
    if args.online:
        logger.info("4/6 · Resmî mevzuat.gov.tr verisi çekiliyor…")
        official_text = fetch_official_law()
    else:
        logger.info("4/6 · Online mod kapalı. Yerel veri tabanı kullanılıyor.")

    # 5) PPT dosyalarından değişiklik notasyonlarını çıkar
    logger.info("5/6 · PPT dosyalarından değişiklik notasyonları çıkarılıyor…")
    ppt_annotations = extract_ppt_change_annotations(TXT_DIR)
    by_tip = {}
    for ann in ppt_annotations:
        by_tip[ann["tip"]] = by_tip.get(ann["tip"], 0) + 1
    if by_tip:
        for tip, cnt in by_tip.items():
            logger.info(f"   → {tip}: {cnt} adet")

    # 6) HTML rapor
    logger.info("6/6 · HTML rapor oluşturuluyor…")
    chart_data = build_chart_data(stats, madde_map)
    html = build_html_report(meta, madde_map, stats, chart_data, official_text, ppt_annotations)

    RAPORLAR_DIR.mkdir(parents=True, exist_ok=True)
    rapor_path = RAPORLAR_DIR / args.cikti
    with open(rapor_path, "w", encoding="utf-8") as f:
        f.write(html)

    logger.info("━" * 55)
    logger.info(f"✓ RAPOR OLUŞTURULDU → {rapor_path}")
    logger.info(f"  Tarayıcıda açmak için çift tıklayın.")
    logger.info("━" * 55)


if __name__ == "__main__":
    main()
