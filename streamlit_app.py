import streamlit as st
import trafilatura
import re
import numpy as np
import pandas as pd
from collections import Counter

# ============================================================
# SAYFA YAPILANDIRMASI
# ============================================================
st.set_page_config(
    page_title="AI Site Dedektifi",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# CSS STİL AYARLARI
# ============================================================
st.markdown(
    """
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #6366f1, #8b5cf6, #a855f7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #6b7280;
        margin-bottom: 2rem;
    }
    .verdict-box {
        padding: 1.2rem 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        font-size: 1.1rem;
        font-weight: 600;
    }
    .verdict-ai {
        background: linear-gradient(135deg, #fef2f2, #fee2e2);
        border: 2px solid #fca5a5;
        color: #991b1b;
    }
    .verdict-maybe {
        background: linear-gradient(135deg, #fffbeb, #fef3c7);
        border: 2px solid #fcd34d;
        color: #92400e;
    }
    .verdict-human {
        background: linear-gradient(135deg, #f0fdf4, #dcfce7);
        border: 2px solid #86efac;
        color: #166534;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ============================================================
# TÜRKÇE STOPWORD LİSTESİ
# ============================================================
TURKISH_STOPWORDS = {
    "acaba",
    "altı",
    "ama",
    "ancak",
    "arada",
    "aslında",
    "ayrıca",
    "bana",
    "bazı",
    "belki",
    "ben",
    "benden",
    "beni",
    "benim",
    "beri",
    "beş",
    "bile",
    "bin",
    "bir",
    "birçok",
    "biri",
    "birkaç",
    "birkez",
    "birşey",
    "birşeyi",
    "biz",
    "bize",
    "bizden",
    "bizi",
    "bizim",
    "bu",
    "buna",
    "bunda",
    "bundan",
    "bunlar",
    "bunları",
    "bunların",
    "bunu",
    "bunun",
    "burada",
    "böyle",
    "böylece",
    "çok",
    "çünkü",
    "da",
    "daha",
    "dahi",
    "de",
    "defa",
    "değil",
    "diğer",
    "diye",
    "dokuz",
    "dolayı",
    "dört",
    "eğer",
    "en",
    "etmesi",
    "etti",
    "fakat",
    "falan",
    "felan",
    "gene",
    "gereği",
    "gibi",
    "göre",
    "halen",
    "hangi",
    "hani",
    "hariç",
    "hatta",
    "hem",
    "henüz",
    "hep",
    "hepsi",
    "her",
    "herhangi",
    "herkesin",
    "hiç",
    "için",
    "ile",
    "ilgili",
    "ise",
    "işte",
    "itibaren",
    "itibariyle",
    "kaç",
    "kadar",
    "karşın",
    "kendi",
    "kendilerine",
    "kendini",
    "kendisi",
    "kere",
    "kez",
    "ki",
    "kim",
    "kimden",
    "kime",
    "kimi",
    "kimse",
    "mı",
    "mi",
    "mu",
    "mü",
    "nasıl",
    "ne",
    "neden",
    "nedenle",
    "nerde",
    "nerede",
    "nereye",
    "niçin",
    "niye",
    "o",
    "olan",
    "olarak",
    "oldu",
    "olduğu",
    "olduğunu",
    "oldukça",
    "olmadı",
    "olmak",
    "olması",
    "olsun",
    "olup",
    "olur",
    "olursa",
    "on",
    "ona",
    "ondan",
    "onlar",
    "onlardan",
    "onları",
    "onların",
    "onu",
    "onun",
    "orada",
    "önce",
    "otuz",
    "oysa",
    "pek",
    "rağmen",
    "sana",
    "sanki",
    "sen",
    "senden",
    "seni",
    "senin",
    "siz",
    "sizden",
    "sizi",
    "sizin",
    "şey",
    "şeyi",
    "şeyler",
    "şöyle",
    "şu",
    "şuna",
    "şunda",
    "şundan",
    "şunları",
    "şunu",
    "tarafından",
    "trilyon",
    "tüm",
    "üç",
    "üzere",
    "var",
    "ve",
    "veya",
    "ya",
    "yani",
    "yapacak",
    "yapılan",
    "yapılması",
    "yapmak",
    "yaptı",
    "yaptığı",
    "yedi",
    "yerine",
    "yetmiş",
    "yine",
    "yirmi",
    "yoksa",
    "yüz",
    "zaten",
    "ait",
    "altında",
    "arasında",
    "açık",
    "adeta",
    "asla",
    "aynen",
    "az",
    "bunca",
    "civar",
    "çoğu",
    "çoğunlukla",
    "dair",
    "dek",
    "den",
    "dönük",
    "doğru",
    "elbet",
    "esnasında",
    "etrafında",
    "evvel",
    "gayet",
    "hakeza",
    "halbuki",
    "hangisi",
    "hani",
    "hariç",
    "hasebiyle",
    "haşa",
    "hatta",
    "hep",
    "hepsi",
    "her",
    "hiç",
    "için",
    "ile",
    "ilave",
    "ilk",
    "illa",
    "ilâ",
    "ise",
    "işte",
    "kadar",
    "karşı",
    "karşın",
    "kaynak",
    "kendi",
    "ki",
    "kim",
    "kimse",
    "madem",
    "mebni",
    "meğer",
    "meğerki",
    "meğerse",
    "mu",
    "mü",
    "nasıl",
    "ne",
    "neden",
    "nedeniyle",
    "nedenle",
    "nerde",
    "nerede",
    "nere",
    "nereden",
    "nereye",
    "neye",
    "niçin",
    "niye",
    "nitekim",
    "o",
    "olan",
    "olarak",
    "oldukça",
    "olmadıkça",
    "olmak",
    "olmamak",
    "olmayan",
    "olmaz",
    "olsa",
    "olsun",
    "olup",
    "olur",
    "olursa",
    "oluyor",
    "ona",
    "ancak",
    "denli",
    "doğru",
    "dair",
    "dek",
    "den",
    "derece",
    "dolayı",
    "dolayısıyla",
    "elbette",
    "ettiği",
    "ettiğini",
    "evvel",
    "gibi",
    "göre",
    "için",
    "ile",
    "ise",
    "kaç",
    "kadar",
    "karşı",
    "kaynak",
    "ki",
    "kim",
    "kimse",
    "madem",
    "meğer",
    "mi",
    "mı",
    "mu",
    "mü",
    "nasıl",
    "ne",
    "neden",
    "nerede",
    "niçin",
    "niye",
    "o",
    "olan",
    "olarak",
    "oldukça",
    "olmak",
    "olsa",
    "olsun",
    "olup",
    "olur",
    "ona",
    "ondan",
    "onlar",
    "onları",
    "onu",
    "onun",
    "önce",
    "otuz",
    "oysa",
    "pek",
    "rağmen",
    "sadece",
    "sanki",
    "sen",
    "siz",
    "şey",
    "şeyi",
    "şeyler",
    "şöyle",
    "şu",
    "şuna",
    "şunda",
    "şundan",
    "şunu",
    "tarafından",
    "trilyon",
    "tüm",
    "üç",
    "üzere",
    "var",
    "ve",
    "veya",
    "ya",
    "yani",
    "yapmak",
    "yaptı",
    "yedi",
    "yerine",
    "yetmiş",
    "yine",
    "yirmi",
    "yoksa",
    "yüz",
    "zaten",
    "ait",
    "altında",
    "arasında",
    "söyle",
    "şimdi",
    "şöyle",
    "böyle",
    "tüm",
    "her",
    "bütün",
    "diye",
    "gibi",
    "kadar",
    "sonra",
    "önce",
    "içinde",
    "üzerinde",
    "hakkında",
    "karşı",
    "yanında",
    "göre",
    "doğru",
    "başka",
    "sadece",
    "yalnız",
    "pek",
    "az",
    "çok",
    "daha",
    "en",
    "hayır",
    "evet",
    "tamam",
    "elbette",
    "belki",
    "galiba",
    "sanırım",
    "bence",
    "bize",
    "sana",
    "ona",
    "benden",
    "senden",
    "ondan",
    "bizim",
    "senin",
    "onun",
}

# ============================================================
# AI KLİŞE KALIPLARI
# ============================================================
AI_CLICHES = [
    "sonuç olarak",
    "özetle",
    "şunu belirtmekte fayda var",
    "bu bağlamda",
    "önemli bir rol oynar",
    "günümüz dünyasında",
    "unutmamak gerekir ki",
    "öne çıkmaktadır",
    "büyük önem arz etmektedir",
    "tartışılmaktadır",
    "göz önünde bulundurulmalıdır",
    "kapsamlı bir şekilde",
    "detaylı bir şekilde",
    "oldukça önemlidir",
    "büyük bir kısmı",
    "bu nedenle",
    "bu açıdan",
    "bu noktada",
    "diğer yandan",
    "her ne kadar",
    "aynı zamanda",
    "bir başka deyişle",
    "kısacası",
    "özetlemek gerekirse",
    "sonuç olarak söyleyebiliriz ki",
    "bu da gösteriyor ki",
    "yadsınamaz bir gerçektir ki",
    "şüphesiz ki",
    "kuşkusuz",
    "malumdur ki",
]

# ============================================================
# YAYGIN TÜRKÇE YAZIM HATALARI (Java gerektirmeyen kontrol)
# ============================================================
SPELLING_RULES = [
    # (regex_pattern, dogru_yazi, aciklama)
    (r"\bde\s+ki\b", "de ki", '"de" ve "ki" ayrı yazılmalı'),
    (r"\bda\s+ki\b", "da ki", '"da" ve "ki" ayrı yazılmalı'),
    (r"\bki\s+de\b", "ki de", '"ki" ve "de" ayrı yazılmalı'),
    (r"\bki\s+da\b", "ki da", '"ki" ve "da" ayrı yazılmalı'),
    (r"\bmi\s+de\b", "mi de", '"mi" ve "de" ayrı yazılmalı'),
    (r"\bmi\s+ki\b", "mi ki", '"mi" ve "ki" ayrı yazılmalı'),
    (r"\bherkez\b", "herkes", "Doğru yazımı: herkes"),
    (r"\bherkesin\b", "herkesin", None),
    (r"\bherşey\b", "her şey", "Doğru yazımı: her şey (ayrı)"),
    (r"\bhersey\b", "her şey", "Doğru yazımı: her şey"),
    (r"\bbugun\b", "bugün", "Doğru yazımı: bugün"),
    (r"\byarın\b", "yarın", None),
    (r"\byarin\b", "yarın", "Doğru yazımı: yarın"),
    (r"\bbugün\b", "bugün", None),
    (r"\bgüzel\b", "güzel", None),
    (r"\byanlız\b", "yalnız", "Doğru yazımı: yalnız"),
    (r"\byalnış\b", "yanlış", "Doğru yazımı: yanlış"),
    (r"\byalniz\b", "yalnız", "Doğru yazımı: yalnız (İngilizce klavye)"),
    (r"\bcok\b", "çok", "Doğru yazımı: çok"),
    (r"\bcoktan\b", "çoktan", None),
    (r"\bguzel\b", "güzel", "Doğru yazımı: güzel (İngilizce klavye)"),
    (r"\bsey\b", "şey", "Doğru yazımı: şey (bağımsız kelime olarak)"),
    (r"\bşey\b", "şey", None),
    (r"\bniye\b", "niye", None),
    (r"\bnicün\b", "niçün", None),
    (r"\byapıcam\b", "yapacağım", "Doğru yazımı: yapacağım"),
    (r"\bedicem\b", "edeceğim", "Doğru yazımı: edeceğim"),
    (r"\bapacık\b", "apaçık", "Doğru yazımı: apaçık"),
    (r"\bapçık\b", "apaçık", "Doğru yazımı: apaçık"),
    (r"\bherhalde\b", "herhalde", None),
    (r"\bherhâlde\b", "herhalde", "Doğru yazımı: herhalde"),
    (r"\bbi\b", "bir", '"bi" yerine "bir" yazılmalı (bağımsız kelime)'),
    (r"\bnapıcam\b", "ne yapacağım", "Doğru yazımı: ne yapacağım"),
    (r"\bnabıcam\b", "ne yapacağım", "Doğru yazımı: ne yapacağım"),
    (r"\bnapıyorsun\b", "ne yapıyorsun", "Doğru yazımı: ne yapıyorsun"),
    (r"\bgeliom\b", "geliyorum", "Doğru yazımı: geliyorum"),
    (r"\bgelcem\b", "geleceğim", "Doğru yazımı: geleceğim"),
    (r"\bgidcem\b", "gideceğim", "Doğru yazımı: gideceğim"),
    (r"\bbiliom\b", "biliyorum", "Doğru yazımı: biliyorum"),
    (r"\bistiom\b", "istiyorum", "Doğru yazımı: istiyorum"),
    (r"\balmıom\b", "almıyorum", "Doğru yazımı: almıyorum"),
    (r"\balmıyom\b", "almıyorum", "Doğru yazımı: almıyorum"),
    (r"\bdüşünüom\b", "düşünüyorum", "Doğru yazımı: düşünüyorum"),
    (r"\böğrencileri\b", "öğrencileri", None),
    (r"\bögretmen\b", "öğretmen", "Doğru yazımı: öğretmen"),
    (r"\bokul\b", "okul", None),
    (r"\bkitap\b", "kitap", None),
    (r"\bıngilizce\b", "İngilizce", "Doğru yazımı: İngilizce"),
    (r"\bingilizce\b", "İngilizce", "Doğru yazımı: İngilizce (büyük harf)"),
    (r"\balmanca\b", "Almanca", "Doğru yazımı: Almanca (büyük harf)"),
    (r"\bfransızca\b", "Fransızca", "Doğru yazımı: Fransızca (büyük harf)"),
    (r"\btürkçe\b", "Türkçe", "Doğru yazımı: Türkçe (büyük harf)"),
    (r"\barapça\b", "Arapça", "Doğru yazımı: Arapça (büyük harf)"),
    (r"\bistanbul\b", "İstanbul", "Doğru yazımı: İstanbul (büyük harf)"),
    (r"\bankara\b", "Ankara", "Doğru yazımı: Ankara (büyük harf)"),
    (r"\bızmır\b", "İzmir", "Doğru yazımı: İzmir"),
    (r"\bızmir\b", "İzmir", "Doğru yazımı: İzmir"),
]


# ============================================================
# YARDIMCI FONKSİYONLAR
# ============================================================


def scrape_url(url):
    """Verilen URL'den trafilatura ile temiz metin çıkarır."""
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded is None:
            return (
                None,
                "URL'den içerik alınamadı. Linkin geçerli ve erişilebilir olduğundan emin olun.",
            )
        text = trafilatura.extract(
            downloaded, include_comments=False, include_tables=True
        )
        if not text or len(text.strip()) < 50:
            return (
                None,
                "Sayfadan yeterli metin içeriği çıkarılamadı. Sayfa çok az metin içerebilir.",
            )
        return text.strip(), None
    except Exception as e:
        return None, f"Scraping sırasında bir hata oluştu: {str(e)}"


def detect_markdown_izleri(text):
    """Metindeki ham markdown formatlama izlerini tespit eder."""
    patterns = {
        "Kalın yazım (**text**)": r"\*\*.+?\*\*",
        "Altı çizili (__text__)": r"__.+?__",
        "Eğik yazı (*text*)": r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)",
        "Başlık (###)": r"#{1,6}\s",
        "Kod bloğu (```)": r"```[\s\S]*?```",
        "Satır içi kod (`text`)": r"`[^`]+`",
        "Madde işareti (- ile)": r"(?m)^\s*-\s",
        "Numaralı liste": r"(?m)^\s*\d+\.\s",
    }

    detections = {}
    total_count = 0
    for label, pattern in patterns.items():
        matches = re.findall(pattern, text)
        count = len(matches)
        detections[label] = count
        total_count += count

    return detections, total_count


def analyze_cliches(text):
    """Metindeki AI klişe kalıplarını sayar."""
    text_lower = text.lower()
    found_cliches = {}

    for cliche in AI_CLICHES:
        count = len(re.findall(re.escape(cliche), text_lower))
        if count > 0:
            found_cliches[cliche] = count

    return found_cliches


def analyze_burstiness(text):
    """Cümle uzunluklarının standart sapmasını hesaplar."""
    sentences = re.split(r"[.!?]+", text)
    sentences = [s.strip() for s in sentences if s.strip()]

    if len(sentences) < 3:
        return {
            "sentence_count": len(sentences),
            "std_dev": 0,
            "mean_length": 0,
            "label": "Yetersiz Veri",
            "description": "Analiz için yeterli cümle bulunamadı.",
        }

    word_counts = [len(s.split()) for s in sentences]

    std_dev = np.std(word_counts)
    mean_length = np.mean(word_counts)

    if std_dev < 3:
        label = "Robotik / Tekdüze"
        description = "Cümle uzunlukları çok benzer. Bu, AI tarafından üretilmiş metinlere özgü bir özelliktir."
    elif std_dev < 6:
        label = "Orta Seviye"
        description = (
            "Cümle uzunluklarında orta düzeyde çeşitlilik var. Kesin bir yargı zor."
        )
    else:
        label = "İnsansı / Çeşitli"
        description = "Cümle uzunlukları doğal çeşitlilik gösteriyor. Bu, insan yazımına özgü bir özelliktir."

    return {
        "sentence_count": len(sentences),
        "std_dev": round(float(std_dev), 2),
        "mean_length": round(float(mean_length), 1),
        "label": label,
        "description": description,
        "word_counts": word_counts,
    }


def calculate_ai_score(
    markdown_count, cliche_count, burstiness_std, word_count, spelling_error_count
):
    """
    Markdown izleri, klişeler, tekdüzelik ve yazım hatalarına göre
    0-100 arası AI olma ihtimali skoru hesaplar.
    """
    # Markdown skoru (0-100)
    if markdown_count == 0:
        md_score = 0
    elif markdown_count <= 3:
        md_score = 25
    elif markdown_count <= 8:
        md_score = 55
    else:
        md_score = 100

    # Klişe skoru (0-100)
    if cliche_count == 0:
        cliche_score = 0
    elif cliche_count <= 2:
        cliche_score = 20
    elif cliche_count <= 5:
        cliche_score = 50
    elif cliche_count <= 10:
        cliche_score = 75
    else:
        cliche_score = 100

    # Burstiness skoru (0-100) - düşük sapma = yüksek AI
    if burstiness_std < 2:
        burst_score = 90
    elif burstiness_std < 4:
        burst_score = 70
    elif burstiness_std < 6:
        burst_score = 45
    elif burstiness_std < 8:
        burst_score = 25
    else:
        burst_score = 10

    # Yazım hatası skoru (0-100) - çok az hata + uzun metin = AI şüphesi
    if word_count >= 500 and spelling_error_count == 0:
        spelling_score = 70
    elif word_count >= 300 and spelling_error_count <= 1:
        spelling_score = 50
    elif spelling_error_count == 0:
        spelling_score = 30
    else:
        spelling_score = 10

    # Ağırlıklı toplam: Markdown %20, Klişeler %35, Burstiness %30, Yazım %15
    final_score = (
        (md_score * 0.20)
        + (cliche_score * 0.35)
        + (burst_score * 0.30)
        + (spelling_score * 0.15)
    )

    return {
        "total": round(final_score, 1),
        "markdown_score": md_score,
        "cliche_score": cliche_score,
        "burstiness_score": burst_score,
        "spelling_score": spelling_score,
    }


def get_verdict(score):
    """AI skoruna göre net karar verir."""
    if score >= 70:
        return "AI", "Bu metin büyük olasılıkla yapay zeka tarafından üretilmiştir."
    elif score >= 40:
        return (
            "BELİRSİZ",
            "Bu metin hem AI hem insan tarafından üretilmiş olabilir. Kesin bir yargı için daha fazla analiz gerekir.",
        )
    else:
        return "İNSAN", "Bu metin büyük olasılıkla insan tarafından yazılmıştır."


def analyze_word_frequency(text):
    """Noktalama ve stopword temizleyerek en çok tekrar eden 10 kelimeyi bulur."""
    cleaned = re.sub(r"[^\w\s]", "", text.lower())
    words = cleaned.split()
    filtered_words = [w for w in words if w not in TURKISH_STOPWORDS and len(w) > 2]
    counter = Counter(filtered_words)
    top_10 = counter.most_common(10)
    return top_10, len(words), len(filtered_words)


def check_spelling_native(text):
    """
    Java gerektirmeyen yerleşik Türkçe yazım kontrolü.
    Yaygın hataları regex kurallarıyla tespit eder.
    """
    errors = []
    for pattern, correct, message in SPELLING_RULES:
        # message None ise bu bir "doğru" kelime, hata olarak sayma
        if message is None:
            continue
        matches = list(re.finditer(pattern, text, re.IGNORECASE))
        for match in matches:
            errors.append(
                {
                    "Hata": "Yazım",
                    "Konum": f"Karakter {match.start()}",
                    "Hatalı Metin": match.group(),
                    "Öneriler": correct,
                    "Açıklama": message,
                }
            )
    return errors


# ============================================================
# STREAMLIT UI
# ============================================================

st.markdown('<div class="main-header">AI Site Dedektifi</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">'
    "Bir web sitesi URL'si girin. Uygulama metni otomatik olarak çekip "
    "<strong>yapay zeka tarafından üretilmiş olma ihtimalini</strong> analiz etsin."
    "</div>",
    unsafe_allow_html=True,
)

url = st.text_input(
    "Web Sitesi URL'si",
    placeholder="https://ornek.com/makale",
    help="Analiz etmek istediğiniz web sayfasının tam URL'sini girin.",
)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    analyze_button = st.button("Analiz Et", type="primary", use_container_width=True)

# ============================================================
# ANALİZ İŞLEMİ
# ============================================================
if analyze_button:
    if not url:
        st.warning("Lütfen bir URL girin.")
    else:
        with st.spinner("Web sayfasından metin çıkarılıyor..."):
            text, error = scrape_url(url)

        if error:
            st.error(f"{error}")
        else:
            st.success(f"Sayfadan {len(text)} karakter metin çıkarıldı.")

            with st.spinner("AI analiz algoritmaları çalıştırılıyor..."):
                markdown_detections, markdown_total = detect_markdown_izleri(text)
                found_cliches = analyze_cliches(text)
                burstiness = analyze_burstiness(text)
                word_count_total = len(text.split())
                spelling_errors = check_spelling_native(text)
                ai_score = calculate_ai_score(
                    markdown_total,
                    sum(found_cliches.values()),
                    burstiness["std_dev"],
                    word_count_total,
                    len(spelling_errors),
                )
                top_words, total_words, filtered_words_count = analyze_word_frequency(
                    text
                )

                # Net karar
                verdict_type, verdict_text = get_verdict(ai_score["total"])

            # ============================================================
            # NET KARAR KUTUSU
            # ============================================================
            if verdict_type == "AI":
                verdict_class = "verdict-ai"
                verdict_icon = "🤖"
            elif verdict_type == "BELİRSİZ":
                verdict_class = "verdict-maybe"
                verdict_icon = "⚠️"
            else:
                verdict_class = "verdict-human"
                verdict_icon = "👤"

            st.markdown(
                f'<div class="verdict-box {verdict_class}">'
                f"{verdict_icon} KARAR: {verdict_type}<br>"
                f'<span style="font-weight:400;font-size:0.95rem;">{verdict_text}</span>'
                f"</div>",
                unsafe_allow_html=True,
            )

            # ============================================================
            # SONUÇLARI SEKMELERDE GÖSTER
            # ============================================================
            tab1, tab2, tab3 = st.tabs(
                ["Genel AI Skoru ve Tespitler", "Kelime Analizi", "Yazım Denetimi"]
            )

            # --------------------------------------------------------
            # SEKME 1: Genel AI Skoru ve Tespitler
            # --------------------------------------------------------
            with tab1:
                st.subheader("Yapay Zeka Olma İhtimali")

                if ai_score["total"] >= 70:
                    score_label = "Yüksek İhtimal"
                elif ai_score["total"] >= 40:
                    score_label = "Orta İhtimal"
                else:
                    score_label = "Düşük İhtimal"

                col_a, col_b = st.columns([1, 2])
                with col_a:
                    st.metric(
                        label="AI Skoru",
                        value=f"{ai_score['total']}%",
                        delta=score_label,
                    )
                with col_b:
                    st.progress(ai_score["total"] / 100)
                    st.caption(score_label)

                st.markdown("---")

                st.subheader("Alt Analiz Sonuçları")

                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    st.metric(
                        "Markdown İzleri",
                        f"{ai_score['markdown_score']}%",
                        help="Ham kopyalama izleri",
                    )
                with c2:
                    st.metric(
                        "Klişe Kalıplar",
                        f"{ai_score['cliche_score']}%",
                        help="AI Türkçe kalıpları",
                    )
                with c3:
                    st.metric(
                        "Tekdüzelik",
                        f"{ai_score['burstiness_score']}%",
                        help="Düşük = robotik",
                    )
                with c4:
                    st.metric(
                        "Yazım Temizliği",
                        f"{ai_score['spelling_score']}%",
                        help="Kusursuz = şüpheli",
                    )

                st.markdown("---")

                st.subheader("Markdown Tespit Detayları")
                if markdown_total > 0:
                    md_df = pd.DataFrame(
                        [(k, v) for k, v in markdown_detections.items() if v > 0],
                        columns=["İşaret Tipi", "Bulunan Sayı"],
                    )
                    st.dataframe(md_df, use_container_width=True, hide_index=True)
                    st.info(
                        f"Toplam **{markdown_total}** adet markdown izi bulundu. "
                        f"Bu, metnin bir AI aracından kopyalanmış olabileceğini düşündürüyor."
                    )
                else:
                    st.success("Herhangi bir markdown formatlama izi bulunamadı.")

                st.markdown("---")

                st.subheader("AI Klişe Kalıp Analizi")
                if found_cliches:
                    cliche_df = pd.DataFrame(
                        list(found_cliches.items()),
                        columns=["Klişe Kalıp", "Geçiş Sayısı"],
                    )
                    st.dataframe(cliche_df, use_container_width=True, hide_index=True)
                    st.warning(
                        f"Toplam **{sum(found_cliches.values())}** adet AI klişe kalıbı bulundu."
                    )
                else:
                    st.success("AI'ya özgü klişe kalıp bulunamadı.")

                st.markdown("---")

                st.subheader("Tekdüzelik (Burstiness) Analizi")
                st.markdown(f"""
                - **Toplam Cümle Sayısı:** {burstiness["sentence_count"]}
                - **Ortalama Cümle Uzunluğu:** {burstiness["mean_length"]} kelime
                - **Standart Sapma:** {burstiness["std_dev"]}
                - **Etiket:** {burstiness["label"]}
                """)
                st.info(burstiness["description"])

            # --------------------------------------------------------
            # SEKME 2: Kelime Analizi
            # --------------------------------------------------------
            with tab2:
                st.subheader("Kelime Frekans Analizi")

                col_x, col_y = st.columns(2)
                with col_x:
                    st.metric("Toplam Kelime Sayısı", f"{total_words:,}")
                with col_y:
                    st.metric(
                        "Anlamlı Kelime (Stopword Hariç)", f"{filtered_words_count:,}"
                    )

                if top_words:
                    freq_df = pd.DataFrame(top_words, columns=["Kelime", "Frekans"])
                    freq_df = freq_df.set_index("Kelime")

                    st.markdown("### En Çok Tekrar Eden 10 Kelime")
                    st.bar_chart(freq_df, horizontal=True, height=400)

                    st.dataframe(
                        freq_df.reset_index().rename(
                            columns={"Kelime": "Kelime", "Frekans": "Geçiş Sayısı"}
                        ),
                        use_container_width=True,
                        hide_index=True,
                    )
                else:
                    st.warning("Analiz edilecek yeterli kelime bulunamadı.")

            # --------------------------------------------------------
            # SEKME 3: Yazım Denetimi
            # --------------------------------------------------------
            with tab3:
                st.subheader("Yazım ve Dilbilgisi Denetimi")

                if spelling_errors:
                    st.warning(
                        f"Toplam **{len(spelling_errors)}** adet hata/uyarı bulundu."
                    )
                    error_df = pd.DataFrame(spelling_errors)
                    st.dataframe(error_df, use_container_width=True, hide_index=True)
                else:
                    st.success("Yazım hatası bulunamadı.")

                    if word_count_total >= 500:
                        st.warning(
                            f"**Kusursuzluk Paradoksu:** Metin dilbilgisi açısından kusursuz. "
                            f"Bu kadar uzun bir metinde ({word_count_total} kelime) insani hataların "
                            f"hiç bulunmaması, metnin AI ile üretilmiş olma şüphesini artırabilir."
                        )

                st.markdown("---")

                st.subheader("Çekilen Metin Önizlemesi")
                preview_text = text[:500] + ("..." if len(text) > 500 else "")
                with st.expander("Metin Önizlemesini Göster", expanded=False):
                    st.text(preview_text)

# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.caption(
    "AI Site Dedektifi | Web kazıma: trafilatura | "
    "Yazım denetimi: yerleşik kurallar | "
    "Analiz: numpy, pandas | Arayüz: Streamlit"
)
