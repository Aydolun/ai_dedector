import streamlit as st
import trafilatura
import re
import numpy as np
import pandas as pd
from collections import Counter
import math

# ============================================================
# SAYFA YAPILANDIRMASI
# ============================================================
st.set_page_config(
    page_title="İçerik Analiz Uzmanı",
    page_icon="📊",
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
    .score-card {
        padding: 1.5rem;
        border-radius: 16px;
        margin: 0.8rem 0;
        text-align: center;
    }
    .score-high {
        background: linear-gradient(135deg, #f0fdf4, #dcfce7);
        border: 2px solid #86efac;
    }
    .score-mid {
        background: linear-gradient(135deg, #fffbeb, #fef3c7);
        border: 2px solid #fcd34d;
    }
    .score-low {
        background: linear-gradient(135deg, #fef2f2, #fee2e2);
        border: 2px solid #fca5a5;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 600;
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0.3rem 0;
    }
    .metric-desc {
        font-size: 0.85rem;
        color: #9ca3af;
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
    "hem",
    "de",
    "da",
    "ki",
    "mi",
    "mı",
    "mu",
    "mü",
    "ile",
    "ve",
    "veya",
    "ya",
    "yahut",
    "ama",
    "fakat",
    "çünkü",
    "çünki",
    "madem",
    "meğer",
    "meğerse",
    "ne",
    "nasıl",
    "nere",
    "neden",
    "niçin",
    "niye",
    "hangi",
    "kim",
    "kaç",
    "ne",
    "hangi",
    "bu",
    "şu",
    "o",
    "bunlar",
    "şunlar",
    "onlar",
    "ben",
    "sen",
    "biz",
    "siz",
    "kendim",
    "kendin",
    "kendi",
    "kendimiz",
    "kendiniz",
    "bana",
    "sana",
    "ona",
    "bize",
    "size",
    "benden",
    "senden",
    "ondan",
    "bizden",
    "sizden",
    "beni",
    "seni",
    "onu",
    "bizi",
    "sizi",
    "bizim",
    "senin",
    "onun",
}

# ============================================================
# YAYGIN TÜRKÇE YAZIM HATALARI
# ============================================================
SPELLING_RULES = [
    (r"\bherşey\b", "her şey", "Doğru yazımı: her şey (ayrı)"),
    (r"\bhersey\b", "her şey", "Doğru yazımı: her şey"),
    (r"\bbugun\b", "bugün", "Doğru yazımı: bugün"),
    (r"\byarin\b", "yarın", "Doğru yazımı: yarın"),
    (r"\byanlız\b", "yalnız", "Doğru yazımı: yalnız"),
    (r"\byalnış\b", "yanlış", "Doğru yazımı: yanlış"),
    (r"\byalniz\b", "yalnız", "Doğru yazımı: yalnız"),
    (r"\bcok\b", "çok", "Doğru yazımı: çok"),
    (r"\bguzel\b", "güzel", "Doğru yazımı: güzel"),
    (r"\byapıcam\b", "yapacağım", "Doğru yazımı: yapacağım"),
    (r"\bedicem\b", "edeceğim", "Doğru yazımı: edeceğim"),
    (r"\bapacık\b", "apaçık", "Doğru yazımı: apaçık"),
    (r"\bherhâlde\b", "herhalde", "Doğru yazımı: herhalde"),
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
    (r"\bögretmen\b", "öğretmen", "Doğru yazımı: öğretmen"),
    (r"\bıngilizce\b", "İngilizce", "Doğru yazımı: İngilizce"),
    (r"\bingilizce\b", "İngilizce", "Doğru yazımı: İngilizce"),
    (r"\balmanca\b", "Almanca", "Doğru yazımı: Almanca"),
    (r"\bfransızca\b", "Fransızca", "Doğru yazımı: Fransızca"),
    (r"\btürkçe\b", "Türkçe", "Doğru yazımı: Türkçe"),
    (r"\barapça\b", "Arapça", "Doğru yazımı: Arapça"),
    (r"\bistanbul\b", "İstanbul", "Doğru yazımı: İstanbul"),
    (r"\bankara\b", "Ankara", "Doğru yazımı: Ankara"),
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
            return None, "Sayfadan yeterli metin içeriği çıkarılamadı."
        return text.strip(), None
    except Exception as e:
        return None, f"Scraping sırasında bir hata oluştu: {str(e)}"


def get_sentences(text):
    """Metni cümlelere böler."""
    sentences = re.split(r"[.!?]+", text)
    return [s.strip() for s in sentences if s.strip() and len(s.strip()) > 5]


def get_words(text, include_stopwords=True):
    """Metni kelimelere böler."""
    cleaned = re.sub(r"[^\w\s]", "", text.lower())
    words = cleaned.split()
    if not include_stopwords:
        words = [w for w in words if w not in TURKISH_STOPWORDS and len(w) > 2]
    return words


def get_paragraphs(text):
    """Metni paragraflara böler."""
    paragraphs = text.split("\n\n")
    return [p.strip() for p in paragraphs if p.strip() and len(p.strip()) > 20]


# ============================================================
# ANALİZ 1: KELİME ÇEŞİTLİLİĞİ (Lexical Diversity)
# ============================================================
def analyze_lexical_diversity(text):
    """
    Metnin kelime çeşitliliğini analiz eder.
    TTR (Type-Token Ratio), MTLD (Measure of Textual Lexical Diversity)
    """
    words = get_words(text, include_stopwords=False)
    total_tokens = len(words)

    if total_tokens == 0:
        return {"error": "Yeterli kelime bulunamadı"}

    unique_types = len(set(words))

    # TTR: Tip-Token Oranı (1'e yakın = zengin kelime dağarcığı)
    ttr = unique_types / total_tokens

    # Kelime tekrar oranı
    word_counts = Counter(words)
    repeated_words = {w: c for w, c in word_counts.items() if c > 1}
    repeated_count = sum(repeated_words.values())
    repetition_rate = (repeated_count / total_tokens) * 100

    # En çok tekrar eden kelimeler
    top_repeated = word_counts.most_common(20)

    # Hapax Legomena (sadece 1 kez geçen kelimeler)
    hapax = [w for w, c in word_counts.items() if c == 1]
    hapax_ratio = len(hapax) / total_tokens

    # Ortalama kelime tekrar sayısı
    avg_repetition = total_tokens / unique_types if unique_types > 0 else 0

    # Kelime uzunluk dağılımı
    word_lengths = [len(w) for w in words]
    avg_word_length = np.mean(word_lengths)
    std_word_length = np.std(word_lengths)

    # Çeşitlilik skoru (0-100)
    # TTR ağırlıklı ama metin uzunluğuna normalize edilmiş
    if total_tokens < 100:
        diversity_score = min(ttr * 100, 100)
    else:
        # Uzun metinlerde TTR doğal olarak düşer, MTLD benzeri yaklaşım
        diversity_score = min((ttr * 2 + hapax_ratio) * 30, 100)

    return {
        "total_tokens": total_tokens,
        "unique_types": unique_types,
        "ttr": round(ttr, 4),
        "repetition_rate": round(repetition_rate, 1),
        "top_repeated": top_repeated,
        "hapax_count": len(hapax),
        "hapax_ratio": round(hapax_ratio, 4),
        "avg_repetition": round(avg_repetition, 2),
        "avg_word_length": round(avg_word_length, 2),
        "std_word_length": round(std_word_length, 2),
        "diversity_score": round(diversity_score, 1),
        "repeated_words": repeated_words,
    }


# ============================================================
# ANALİZ 2: CÜMLE ÇEŞİTLİLİĞİ VE YAPI
# ============================================================
def analyze_sentence_structure(text):
    """Cümle uzunluk dağılımı, çeşitlilik ve yapı analizi."""
    sentences = get_sentences(text)

    if len(sentences) < 3:
        return {"error": "Yeterli cümle bulunamadı"}

    # Cümle uzunlukları (kelime bazlı)
    sentence_lengths = [len(s.split()) for s in sentences]

    # İstatistikler
    mean_len = np.mean(sentence_lengths)
    std_len = np.std(sentence_lengths)
    median_len = np.median(sentence_lengths)
    min_len = min(sentence_lengths)
    max_len = max(sentence_lengths)
    range_len = max_len - min_len

    # Cümle uzunluk dağılımı
    length_distribution = Counter()
    for length in sentence_lengths:
        if length <= 5:
            length_distribution["Çok Kısa (1-5)"] += 1
        elif length <= 10:
            length_distribution["Kısa (6-10)"] += 1
        elif length <= 20:
            length_distribution["Orta (11-20)"] += 1
        elif length <= 30:
            length_distribution["Uzun (21-30)"] += 1
        else:
            length_distribution["Çok Uzun (30+)"] += 1

    # Cümle çeşitlilik skoru
    # Standart sapma ne kadar yüksekse cümleler o kadar çeşitli
    if std_len < 3:
        variety_score = 20
    elif std_len < 5:
        variety_score = 40
    elif std_len < 8:
        variety_score = 65
    elif std_len < 12:
        variety_score = 85
    else:
        variety_score = 100

    # En uzun ve en kısa cümleler
    longest_idx = sentence_lengths.index(max_len)
    shortest_idx = sentence_lengths.index(min_len)

    return {
        "sentence_count": len(sentences),
        "mean_length": round(mean_len, 1),
        "std_length": round(std_len, 2),
        "median_length": round(median_len, 1),
        "min_length": min_len,
        "max_length": max_len,
        "range_length": range_len,
        "length_distribution": dict(length_distribution),
        "variety_score": round(variety_score, 1),
        "longest_sentence": sentences[longest_idx][:200],
        "shortest_sentence": sentences[shortest_idx][:200],
        "sentence_lengths": sentence_lengths,
    }


# ============================================================
# ANALİZ 3: CÜMLE BENZERLİĞİ (TEKRAR EDEN FİKİRLER)
# ============================================================
def analyze_sentence_similarity(text):
    """
    Aynı veya çok benzer şeyleri söyleyen cümleleri tespit eder.
    N-gram overlap ve kelime kesişimi kullanır.
    """
    sentences = get_sentences(text)

    if len(sentences) < 3:
        return {"error": "Yeterli cümle bulunamadı"}

    # Her cümleyi kelime setine dönüştür (stopword hariç)
    sentence_word_sets = []
    for s in sentences:
        words = set(get_words(s, include_stopwords=False))
        sentence_word_sets.append(words)

    # İkili benzerlik hesapla (Jaccard similarity)
    similar_pairs = []
    n = len(sentences)

    for i in range(n):
        for j in range(i + 1, n):
            set_a = sentence_word_sets[i]
            set_b = sentence_word_sets[j]

            if len(set_a) == 0 or len(set_b) == 0:
                continue

            # Jaccard benzerliği
            intersection = len(set_a & set_b)
            union = len(set_a | set_b)
            jaccard = intersection / union if union > 0 else 0

            # Kelime kesişim oranı (daha hassas)
            overlap_ratio = (
                intersection / min(len(set_a), len(set_b))
                if min(len(set_a), len(set_b)) > 0
                else 0
            )

            # Ortak kelimeler
            common_words = set_a & set_b

            if jaccard >= 0.15 or overlap_ratio >= 0.3:
                similar_pairs.append(
                    {
                        "sentence_a": sentences[i][:150]
                        + ("..." if len(sentences[i]) > 150 else ""),
                        "sentence_b": sentences[j][:150]
                        + ("..." if len(sentences[j]) > 150 else ""),
                        "jaccard": round(jaccard, 3),
                        "overlap_ratio": round(overlap_ratio, 3),
                        "common_words": ", ".join(list(common_words)[:10]),
                        "common_count": len(common_words),
                    }
                )

    # Benzerliklere göre sırala
    similar_pairs.sort(key=lambda x: x["jaccard"], reverse=True)

    # Tekrar oranı
    total_pairs = n * (n - 1) // 2
    highly_similar = sum(1 for p in similar_pairs if p["jaccard"] >= 0.25)
    moderately_similar = sum(1 for p in similar_pairs if 0.15 <= p["jaccard"] < 0.25)

    # Benzersizlik skoru
    if total_pairs > 0:
        similarity_rate = len(similar_pairs) / total_pairs
        uniqueness_score = max(0, round((1 - similarity_rate) * 100, 1))
    else:
        uniqueness_score = 100

    return {
        "similar_pairs": similar_pairs[:30],  # En fazla 30 çift göster
        "total_similar_pairs": len(similar_pairs),
        "highly_similar": highly_similar,
        "moderately_similar": moderately_similar,
        "total_comparisons": total_pairs,
        "uniqueness_score": uniqueness_score,
    }


# ============================================================
# ANALİZ 4: İÇERİK YAPISI VE DERİNLİK
# ============================================================
def analyze_content_structure(text):
    """İçeriğin yapısal derinliğini ve organizasyonunu analiz eder."""
    paragraphs = get_paragraphs(text)
    sentences = get_sentences(text)
    words = get_words(text, include_stopwords=False)

    # Paragraf analizi
    paragraph_lengths = [len(p.split()) for p in paragraphs]
    avg_paragraph_length = np.mean(paragraph_lengths) if paragraph_lengths else 0
    std_paragraph_length = np.std(paragraph_lengths) if paragraph_lengths else 0

    # Başlık tespiti (kısa satırlar)
    lines = text.split("\n")
    potential_headings = [
        l.strip()
        for l in lines
        if 3 < len(l.strip()) < 60 and not l.strip().endswith((".", "!", "?", ","))
    ]

    # İçerik yoğunluğu
    total_chars = len(text)
    total_words = len(words)
    avg_word_length = np.mean([len(w) for w in words]) if words else 0

    # Yapı skoru
    structure_score = 0

    # Paragraf sayısı (ideal: 5-20 arası)
    if 5 <= len(paragraphs) <= 20:
        structure_score += 25
    elif len(paragraphs) > 20:
        structure_score += 20
    elif len(paragraphs) >= 3:
        structure_score += 15
    else:
        structure_score += 5

    # Paragraf uzunluk tutarlılığı
    if std_paragraph_length < avg_paragraph_length * 0.5:
        structure_score += 25
    elif std_paragraph_length < avg_paragraph_length:
        structure_score += 15
    else:
        structure_score += 5

    # Başlık varlığı
    if len(potential_headings) >= 2:
        structure_score += 25
    elif len(potential_headings) >= 1:
        structure_score += 15
    else:
        structure_score += 5

    # İçerik uzunluğu
    if total_words >= 500:
        structure_score += 25
    elif total_words >= 200:
        structure_score += 20
    elif total_words >= 100:
        structure_score += 10
    else:
        structure_score += 5

    return {
        "paragraph_count": len(paragraphs),
        "avg_paragraph_length": round(avg_paragraph_length, 1),
        "std_paragraph_length": round(std_paragraph_length, 1),
        "potential_headings": potential_headings[:10],
        "heading_count": len(potential_headings),
        "total_chars": total_chars,
        "total_words": total_words,
        "avg_word_length": round(avg_word_length, 2),
        "structure_score": min(structure_score, 100),
        "paragraph_lengths": paragraph_lengths,
    }


# ============================================================
# ANALİZ 5: OKUNABİLİRLİK
# ============================================================
def analyze_readability(text):
    """Metnin okunabilirlik seviyesini hesaplar."""
    sentences = get_sentences(text)
    words = get_words(text, include_stopwords=False)

    if len(sentences) < 2 or len(words) < 10:
        return {"error": "Yeterli veri yok"}

    avg_sentence_length = len(words) / len(sentences)
    avg_word_length = np.mean([len(w) for w in words])

    # Uzun kelime oranı (7+ karakter)
    long_words = [w for w in words if len(w) >= 7]
    long_word_ratio = len(long_words) / len(words)

    # Okunabilirlik skoru
    # Kısa cümle + kısa kelimeler = daha okunabilir
    readability_score = 100

    # Cümle uzunluğu cezası
    if avg_sentence_length > 25:
        readability_score -= 30
    elif avg_sentence_length > 20:
        readability_score -= 15
    elif avg_sentence_length > 15:
        readability_score -= 5

    # Kelime uzunluğu cezası
    if avg_word_length > 7:
        readability_score -= 25
    elif avg_word_length > 6:
        readability_score -= 15
    elif avg_word_length > 5:
        readability_score -= 5

    # Uzun kelime oranı cezası
    if long_word_ratio > 0.4:
        readability_score -= 20
    elif long_word_ratio > 0.3:
        readability_score -= 10

    readability_score = max(0, readability_score)

    # Seviye belirleme
    if readability_score >= 80:
        level = "Kolay"
        level_desc = "Genel okuyucu kitlesi için rahatça okunabilir."
    elif readability_score >= 60:
        level = "Orta"
        level_desc = "Orta eğitim seviyesindeki okuyucular için uygun."
    elif readability_score >= 40:
        level = "Zor"
        level_desc = "Akademik veya teknik dil içeriyor."
    else:
        level = "Çok Zor"
        level_desc = "Ağır terminoloji ve uzun cümleler içeriyor."

    return {
        "avg_sentence_length": round(avg_sentence_length, 1),
        "avg_word_length": round(avg_word_length, 2),
        "long_word_ratio": round(long_word_ratio, 3),
        "long_word_count": len(long_words),
        "readability_score": round(readability_score, 1),
        "level": level,
        "level_desc": level_desc,
    }


# ============================================================
# ANALİZ 6: YAZIM DENETİMİ
# ============================================================
def check_spelling(text):
    """Yerleşik Türkçe yazım kuralları ile yazım denetimi."""
    errors = []
    for pattern, correct, message in SPELLING_RULES:
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
# ANALİZ 7: KELİME DAĞILIM GRAFİĞİ
# ============================================================
def analyze_word_distribution(text):
    """Kelime frekans dağılımını detaylı analiz eder."""
    words = get_words(text, include_stopwords=False)
    word_counts = Counter(words)

    # Frekans dağılımı
    freq_values = list(word_counts.values())
    if freq_values:
        freq_mean = np.mean(freq_values)
        freq_std = np.std(freq_values)
        freq_median = np.median(freq_values)
    else:
        freq_mean = freq_std = freq_median = 0

    # Zipf analizi: En sık kelimelerin toplam içindeki payı
    total = sum(freq_values)
    top_5_share = (
        sum(c for _, c in word_counts.most_common(5)) / total * 100 if total > 0 else 0
    )
    top_10_share = (
        sum(c for _, c in word_counts.most_common(10)) / total * 100 if total > 0 else 0
    )
    top_20_share = (
        sum(c for _, c in word_counts.most_common(20)) / total * 100 if total > 0 else 0
    )

    # Tekrarlı kelime grupları
    repeated_2x = sum(1 for c in freq_values if c == 2)
    repeated_3x = sum(1 for c in freq_values if c == 3)
    repeated_5x_plus = sum(1 for c in freq_values if c >= 5)
    repeated_10x_plus = sum(1 for c in freq_values if c >= 10)

    return {
        "word_counts": word_counts,
        "freq_mean": round(freq_mean, 2),
        "freq_std": round(freq_std, 2),
        "freq_median": round(freq_median, 1),
        "top_5_share": round(top_5_share, 1),
        "top_10_share": round(top_10_share, 1),
        "top_20_share": round(top_20_share, 1),
        "repeated_2x": repeated_2x,
        "repeated_3x": repeated_3x,
        "repeated_5x_plus": repeated_5x_plus,
        "repeated_10x_plus": repeated_10x_plus,
    }


# ============================================================
# GENEL EMEK / ÇALIŞKANLIK SKORU
# ============================================================
def calculate_effort_score(lexical, sentence_sim, structure, readability):
    """
    İçeriğin ne kadar emek harcandığını gösteren bileşik skor.
    Kelime çeşitliliği + Cümle benzersizliği + Yapı + Okunabilirlik
    """
    lexical_score = lexical.get("diversity_score", 50)
    uniqueness_score = sentence_sim.get("uniqueness_score", 50)
    structure_score = structure.get("structure_score", 50)
    readability_score = readability.get("readability_score", 50)

    # Ağırlıklar: Çeşitlilik %30, Benzersizlik %30, Yapı %20, Okunabilirlik %20
    effort = (
        lexical_score * 0.30
        + uniqueness_score * 0.30
        + structure_score * 0.20
        + readability_score * 0.20
    )

    return round(effort, 1)


# ============================================================
# STREAMLIT UI
# ============================================================

st.markdown(
    '<div class="main-header">İçerik Analiz Uzmanı</div>', unsafe_allow_html=True
)
st.markdown(
    '<div class="sub-header">'
    "Bir web sitesi URL'si girin. İçeriğin kelime çeşitliliği, cümle benzerliği, "
    "yapısal derinliği ve yazım kalitesi detaylı olarak analiz edilsin."
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
            st.error(error)
        else:
            st.success(f"Sayfadan {len(text)} karakter metin çıkarıldı.")

            with st.spinner("Detaylı analizler çalıştırılıyor..."):
                lexical = analyze_lexical_diversity(text)
                sentence_struct = analyze_sentence_structure(text)
                sentence_sim = analyze_sentence_similarity(text)
                structure = analyze_content_structure(text)
                readability = analyze_readability(text)
                spelling_errors = check_spelling(text)
                word_dist = analyze_word_distribution(text)
                effort_score = calculate_effort_score(
                    lexical, sentence_sim, structure, readability
                )

            # ============================================================
            # GENEL EMEK SKORU
            # ============================================================
            st.subheader("Genel İçerik Kalite ve Emek Skoru")

            if effort_score >= 75:
                effort_class = "score-high"
                effort_emoji = "💎"
                effort_label = "Yüksek Kalite"
            elif effort_score >= 50:
                effort_class = "score-mid"
                effort_emoji = "📝"
                effort_label = "Orta Kalite"
            else:
                effort_class = "score-low"
                effort_emoji = "⚠️"
                effort_label = "Düşük Kalite"

            cols = st.columns(4)
            with cols[0]:
                st.markdown(
                    f'<div class="score-card {effort_class}">'
                    f'<div class="metric-label">Emek Skoru</div>'
                    f'<div class="metric-value">{effort_score}</div>'
                    f'<div class="metric-desc">{effort_emoji} {effort_label}</div>'
                    f"</div>",
                    unsafe_allow_html=True,
                )
            with cols[1]:
                st.markdown(
                    f'<div class="score-card {"score-high" if lexical["diversity_score"] >= 60 else "score-mid" if lexical["diversity_score"] >= 40 else "score-low"}">'
                    f'<div class="metric-label">Kelime Çeşitliliği</div>'
                    f'<div class="metric-value">{lexical["diversity_score"]}</div>'
                    f'<div class="metric-desc">{lexical["unique_types"]} benzersiz kelime</div>'
                    f"</div>",
                    unsafe_allow_html=True,
                )
            with cols[2]:
                st.markdown(
                    f'<div class="score-card {"score-high" if sentence_sim["uniqueness_score"] >= 70 else "score-mid" if sentence_sim["uniqueness_score"] >= 50 else "score-low"}">'
                    f'<div class="metric-label">Cümle Benzersizliği</div>'
                    f'<div class="metric-value">{sentence_sim["uniqueness_score"]}</div>'
                    f'<div class="metric-desc">{sentence_sim["total_similar_pairs"]} benzer çift</div>'
                    f"</div>",
                    unsafe_allow_html=True,
                )
            with cols[3]:
                st.markdown(
                    f'<div class="score-card {"score-high" if structure["structure_score"] >= 60 else "score-mid" if structure["structure_score"] >= 40 else "score-low"}">'
                    f'<div class="metric-label">Yapısal Derinlik</div>'
                    f'<div class="metric-value">{structure["structure_score"]}</div>'
                    f'<div class="metric-desc">{structure["paragraph_count"]} paragraf</div>'
                    f"</div>",
                    unsafe_allow_html=True,
                )

            st.markdown("---")

            # ============================================================
            # SEKMELER
            # ============================================================
            tab1, tab2, tab3, tab4 = st.tabs(
                [
                    "Kelime Tekrar Analizi",
                    "Cümle Benzerliği",
                    "İçerik Yapısı",
                    "Yazım Denetimi",
                ]
            )

            # --------------------------------------------------------
            # SEKME 1: KELİME TEKRAR ANALİZİ
            # --------------------------------------------------------
            with tab1:
                st.subheader("Kelime Çeşitliliği ve Tekrarlar")

                # Temel metrikler
                m1, m2, m3, m4 = st.columns(4)
                with m1:
                    st.metric("Toplam Kelime", f"{lexical['total_tokens']:,}")
                with m2:
                    st.metric("Benzersiz Kelime", f"{lexical['unique_types']:,}")
                with m3:
                    st.metric("Tekrar Oranı", f"{lexical['repetition_rate']}%")
                with m4:
                    st.metric("Tür-Token Oranı", f"{lexical['ttr']}")

                st.markdown("---")

                # En çok tekrar eden kelimeler
                st.subheader("En Çok Tekrar Eden Kelimeler")

                if lexical["top_repeated"]:
                    # Grafik için DataFrame
                    top_15 = lexical["top_repeated"][:15]
                    freq_df = pd.DataFrame(top_15, columns=["Kelime", "Tekrar Sayısı"])
                    freq_df = freq_df.set_index("Kelime")

                    st.bar_chart(freq_df, horizontal=True, height=450)

                    st.markdown("---")

                    # Detaylı tablo
                    st.subheader("Tüm Tekrarlı Kelimeler")

                    all_repeated = [
                        (w, c) for w, c in lexical["repeated_words"].items() if c > 1
                    ]
                    all_repeated.sort(key=lambda x: x[1], reverse=True)

                    if all_repeated:
                        rep_df = pd.DataFrame(
                            all_repeated, columns=["Kelime", "Tekrar Sayısı"]
                        )
                        st.dataframe(
                            rep_df,
                            use_container_width=True,
                            hide_index=True,
                            height=400,
                        )

                st.markdown("---")

                # Zipf analizi
                st.subheader("Kelime Dağılımı (Zipf Analizi)")

                z1, z2, z3 = st.columns(3)
                with z1:
                    st.metric("En Sık 5 Kelimenin Payı", f"{word_dist['top_5_share']}%")
                with z2:
                    st.metric(
                        "En Sık 10 Kelimenin Payı", f"{word_dist['top_10_share']}%"
                    )
                with z3:
                    st.metric(
                        "En Sık 20 Kelimenin Payı", f"{word_dist['top_20_share']}%"
                    )

                st.markdown("---")

                # Tekrar sıklığı dağılımı
                st.subheader("Tekrar Sıklığı Dağılımı")

                d1, d2, d3, d4 = st.columns(4)
                with d1:
                    st.metric("Sadece 1 Keç", f"{lexical['hapax_count']:,}")
                with d2:
                    st.metric("2 Keç Tekrar", f"{word_dist['repeated_2x']:,}")
                with d3:
                    st.metric("3 Keç Tekrar", f"{word_dist['repeated_3x']:,}")
                with d4:
                    st.metric("5+ Keç Tekrar", f"{word_dist['repeated_5x_plus']:,}")

                st.info(
                    f"Ortalama bir kelime **{lexical['avg_repetition']}** kez tekrar ediyor. "
                    f"Toplam {lexical['hapax_count']} kelime sadece 1 kez geçiyor "
                    f"(Hapax Legomena). Bu, metnin kelime zenginliğinin bir göstergesidir."
                )

            # --------------------------------------------------------
            # SEKME 2: CÜMLE BENZERLİĞİ
            # --------------------------------------------------------
            with tab2:
                st.subheader("Cümle Benzerliği ve Tekrar Eden Fikirler")

                # Temel metrikler
                s1, s2, s3, s4 = st.columns(4)
                with s1:
                    st.metric("Toplam Cümle", f"{sentence_struct['sentence_count']}")
                with s2:
                    st.metric(
                        "Ort. Cümle Uzunluğu",
                        f"{sentence_struct['mean_length']} kelime",
                    )
                with s3:
                    st.metric(
                        "Benzer Cümle Çifti", f"{sentence_sim['total_similar_pairs']}"
                    )
                with s4:
                    st.metric(
                        "Benzersizlik Skoru", f"{sentence_sim['uniqueness_score']}%"
                    )

                st.markdown("---")

                # Cümle uzunluk dağılımı
                st.subheader("Cümle Uzunluk Dağılımı")

                dist_data = sentence_struct["length_distribution"]
                if dist_data:
                    dist_df = pd.DataFrame(
                        list(dist_data.items()), columns=["Aralık", "Cümle Sayısı"]
                    ).set_index("Aralık")
                    st.bar_chart(dist_df, horizontal=True, height=250)

                st.markdown("---")

                # Benzer cümle çiftleri
                st.subheader("Birbirine Benzer Cümle Çiftleri")

                if sentence_sim["similar_pairs"]:
                    for idx, pair in enumerate(sentence_sim["similar_pairs"][:15]):
                        similarity_pct = int(pair["jaccard"] * 100)
                        overlap_pct = int(pair["overlap_ratio"] * 100)

                        if similarity_pct >= 25:
                            badge = "🔴 Yüksek Benzerlik"
                        elif similarity_pct >= 15:
                            badge = "🟡 Orta Benzerlik"
                        else:
                            badge = "🟢 Düşük Benzerlik"

                        with st.container(border=True):
                            st.markdown(
                                f"**{badge}** — Benzerlik: %{similarity_pct} | Ortak Kelime: {pair['common_count']}"
                            )
                            col_a, col_b = st.columns(2)
                            with col_a:
                                st.caption(f"Cümle A: {pair['sentence_a']}")
                            with col_b:
                                st.caption(f"Cümle B: {pair['sentence_b']}")
                            st.caption(f"Ortak kelimeler: {pair['common_words']}")

                    if sentence_sim["total_similar_pairs"] > 15:
                        st.info(
                            f"Toplam {sentence_sim['total_similar_pairs']} benzer çift bulundu. "
                            f"En belirgin {min(15, sentence_sim['total_similar_pairs'])} çift yukarıda gösteriliyor."
                        )
                else:
                    st.success(
                        "Hiçbir cümle çifti arasında anlamlı benzerlik bulunamadı. İçerik oldukça benzersiz."
                    )

                st.markdown("---")

                # Cümle çeşitlilik skoru
                st.subheader("Cümle Çeşitliliği")
                st.info(
                    f"Cümle uzunluklarının standart sapması: **{sentence_struct['std_length']}**. "
                    f"Bu değer ne kadar yüksekse, cümleler o kadar çeşitli uzunluklarda demektir. "
                    f"Çeşitlilik skoru: **{sentence_struct['variety_score']}/100**"
                )

            # --------------------------------------------------------
            # SEKME 3: İÇERİK YAPISI
            # --------------------------------------------------------
            with tab3:
                st.subheader("İçerik Yapısı ve Derinlik")

                # Temel metrikler
                p1, p2, p3, p4 = st.columns(4)
                with p1:
                    st.metric("Paragraf Sayısı", structure["paragraph_count"])
                with p2:
                    st.metric(
                        "Ort. Paragraf Uzunluğu",
                        f"{structure['avg_paragraph_length']} kelime",
                    )
                with p3:
                    st.metric("Olası Başlık Sayısı", structure["heading_count"])
                with p4:
                    st.metric("Toplam Karakter", f"{structure['total_chars']:,}")

                st.markdown("---")

                # Paragraf uzunluk grafiği
                st.subheader("Paragraf Uzunluk Dağılımı")

                if structure["paragraph_lengths"]:
                    para_df = pd.DataFrame(
                        enumerate(structure["paragraph_lengths"], 1),
                        columns=["Paragraf", "Kelime Sayısı"],
                    ).set_index("Paragraf")
                    st.bar_chart(para_df, height=300)

                st.markdown("---")

                # Başlıklar
                if structure["potential_headings"]:
                    st.subheader("Tespit Edilen Olası Başlıklar")
                    for h in structure["potential_headings"][:10]:
                        st.markdown(f"- {h}")

                st.markdown("---")

                # Okunabilirlik
                st.subheader("Okunabilirlik Analizi")

                if "error" not in readability:
                    o1, o2, o3 = st.columns(3)
                    with o1:
                        st.metric(
                            "Ort. Cümle Uzunluğu",
                            f"{readability['avg_sentence_length']} kelime",
                        )
                    with o2:
                        st.metric(
                            "Ort. Kelime Uzunluğu",
                            f"{readability['avg_word_length']} karakter",
                        )
                    with o3:
                        st.metric(
                            "Uzun Kelime Oranı",
                            f"{readability['long_word_ratio'] * 100:.1f}%",
                        )

                    st.markdown("---")

                    # Okunabilirlik seviyesi
                    if readability["readability_score"] >= 80:
                        level_color = "🟢"
                    elif readability["readability_score"] >= 60:
                        level_color = "🟡"
                    elif readability["readability_score"] >= 40:
                        level_color = "🟠"
                    else:
                        level_color = "🔴"

                    st.markdown(f"""
                    **{level_color} Okunabilirlik Seviyesi: {readability["level"]}**

                    {readability["level_desc"]}

                    - Okunabilirlik Skoru: **{readability["readability_score"]}/100**
                    - Uzun kelime (7+ karakter) sayısı: **{readability["long_word_count"]}**
                    """)

            # --------------------------------------------------------
            # SEKME 4: YAZIM DENETİMİ
            # --------------------------------------------------------
            with tab4:
                st.subheader("Yazım ve Dilbilgisi Denetimi")

                if spelling_errors:
                    st.warning(
                        f"Toplam **{len(spelling_errors)}** adet hata/uyarı bulundu."
                    )

                    error_df = pd.DataFrame(spelling_errors)
                    st.dataframe(error_df, use_container_width=True, hide_index=True)
                else:
                    st.success("Yazım hatası bulunamadı.")

                    if structure["total_words"] >= 500:
                        st.info(
                            f"Bu kadar uzun bir metinde ({structure['total_words']} kelime) "
                            f"hiç yazım hatası bulunmaması dikkat çekici."
                        )

                st.markdown("---")

                # Metin önizleme
                st.subheader("Çekilen Metin Önizlemesi")
                preview_text = text[:500] + ("..." if len(text) > 500 else "")
                with st.expander("Metin Önizlemesini Göster", expanded=False):
                    st.text(preview_text)

# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.caption(
    "İçerik Analiz Uzmanı | Web kazıma: trafilatura | "
    "Analiz motoru: numpy, pandas | Arayüz: Streamlit"
)
