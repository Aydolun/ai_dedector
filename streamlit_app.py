import html
import math
import re
from collections import Counter
from urllib.parse import urlparse

import numpy as np
import pandas as pd
import streamlit as st
import trafilatura


st.set_page_config(
    page_title="Metin Diligence Analizörü",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)


st.markdown(
    """
<style>
    :root {
        --bg: #f7f8fb;
        --card: #ffffff;
        --border: #e5e7eb;
        --text: #0f172a;
        --muted: #64748b;
        --accent: #6366f1;
        --accent-soft: #eef2ff;
        --good: #16a34a;
        --good-soft: #f0fdf4;
        --warn: #d97706;
        --warn-soft: #fffbeb;
        --bad: #dc2626;
        --bad-soft: #fef2f2;
    }

    .main > div {
        padding-top: 1.2rem;
    }

    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        line-height: 1.1;
        margin-bottom: 0.35rem;
        letter-spacing: -0.02em;
        background: linear-gradient(90deg, #6366f1, #8b5cf6, #0ea5e9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero-subtitle {
        color: var(--muted);
        font-size: 0.98rem;
        margin-bottom: 1.4rem;
    }

    .surface {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 1.15rem 1.2rem;
        box-shadow: 0 6px 24px rgba(15, 23, 42, 0.04);
    }

    .score-card {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 1.1rem 1rem 1.2rem 1rem;
        text-align: center;
        box-shadow: 0 6px 24px rgba(15, 23, 42, 0.04);
        min-height: 230px;
        position: relative;
        overflow: hidden;
    }

    .score-card::before {
        content: "";
        position: absolute;
        left: 0;
        right: 0;
        top: 0;
        height: 4px;
    }

    .score-card.ai::before {
        background: linear-gradient(90deg, #6366f1, #8b5cf6);
    }

    .score-card.repeat::before {
        background: linear-gradient(90deg, #f59e0b, #ef4444);
    }

    .score-card.original::before {
        background: linear-gradient(90deg, #22c55e, #06b6d4);
    }

    .score-label {
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--muted);
        font-size: 0.72rem;
        font-weight: 700;
        margin-bottom: 0.55rem;
    }

    .score-ring-wrap {
        position: relative;
        width: 124px;
        height: 124px;
        margin: 0.3rem auto 0.75rem auto;
    }

    .score-ring-wrap svg {
        transform: rotate(-90deg);
    }

    .ring-center {
        position: absolute;
        inset: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.8rem;
        font-weight: 800;
    }

    .score-desc {
        color: var(--muted);
        font-size: 0.86rem;
        line-height: 1.45;
    }

    .mini-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 0.8rem;
    }

    .mini-stat {
        min-width: 0;
    }

    .mini-stat-value {
        font-size: 1.12rem;
        font-weight: 800;
        line-height: 1.2;
        color: var(--text);
    }

    .mini-stat-label {
        font-size: 0.74rem;
        color: var(--muted);
        margin-top: 0.15rem;
    }

    .section-title {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--muted);
        font-weight: 800;
        margin-bottom: 0.8rem;
    }

    .chip-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.45rem;
        margin-top: 0.85rem;
    }

    .chip {
        display: inline-block;
        padding: 0.35rem 0.7rem;
        border-radius: 999px;
        font-size: 0.73rem;
        font-weight: 700;
        line-height: 1;
        border: 1px solid var(--border);
    }

    .chip-risk {
        background: var(--bad-soft);
        color: var(--bad);
        border-color: transparent;
    }

    .chip-warn {
        background: var(--warn-soft);
        color: var(--warn);
        border-color: transparent;
    }

    .chip-safe {
        background: var(--good-soft);
        color: var(--good);
        border-color: transparent;
    }

    .gauge-list {
        display: flex;
        flex-direction: column;
        gap: 0.65rem;
    }

    .gauge-row {
        display: grid;
        grid-template-columns: 92px 1fr 42px;
        align-items: center;
        gap: 0.6rem;
    }

    .gauge-name {
        font-size: 0.8rem;
        color: var(--muted);
    }

    .gauge-track {
        height: 9px;
        border-radius: 999px;
        background: #e5e7eb;
        overflow: hidden;
    }

    .gauge-fill {
        height: 100%;
        border-radius: 999px;
    }

    .gauge-value {
        font-size: 0.78rem;
        font-weight: 800;
        text-align: right;
    }

    .finding-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.8rem;
        padding: 0.7rem 0;
        border-bottom: 1px solid #eef2f7;
    }

    .finding-row:last-child {
        border-bottom: none;
    }

    .finding-text {
        font-size: 0.9rem;
        color: var(--muted);
    }

    .badge {
        display: inline-block;
        padding: 0.28rem 0.62rem;
        border-radius: 999px;
        font-size: 0.7rem;
        font-weight: 800;
        letter-spacing: 0.03em;
        text-transform: uppercase;
        white-space: nowrap;
    }

    .badge-ai { background: var(--warn-soft); color: var(--warn); }
    .badge-repeat { background: var(--bad-soft); color: var(--bad); }
    .badge-clean { background: var(--good-soft); color: var(--good); }
    .badge-cliche { background: #fff7d6; color: #b45309; }
    .badge-semantic { background: #eef2ff; color: #4f46e5; }

    .repeat-box {
        background: #fafafa;
        border: 1px solid #eceff3;
        border-radius: 14px;
        padding: 0.9rem 1rem;
        margin-bottom: 0.65rem;
    }

    .repeat-score {
        font-size: 0.8rem;
        font-weight: 800;
        margin-bottom: 0.45rem;
    }

    .repeat-text {
        font-size: 0.88rem;
        color: var(--muted);
        line-height: 1.55;
        margin: 0.15rem 0;
    }

    .pill-wrap {
        display: flex;
        flex-wrap: wrap;
        gap: 0.45rem;
    }

    .pill {
        display: inline-block;
        padding: 0.38rem 0.72rem;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 600;
        line-height: 1;
    }

    .pill-cliche {
        background: #fff7d6;
        color: #b45309;
    }

    .pill-trigram {
        background: #fee2e2;
        color: #b91c1c;
    }

    .full-text-box {
        padding: 1rem 1.05rem;
        border: 1px solid var(--border);
        border-radius: 16px;
        background: #fcfcfd;
        white-space: pre-wrap;
        word-break: break-word;
        line-height: 1.85;
        color: var(--muted);
        font-size: 0.93rem;
    }
</style>
""",
    unsafe_allow_html=True,
)


TR_CLICHES = [
    "sonuç olarak",
    "bu bağlamda",
    "öte yandan",
    "vurgulamak gerekirse",
    "dikkat edilmesi gereken",
    "şunu belirtmek gerekir",
    "genel itibarıyla",
    "göz ardı edilmemelidir",
    "bu doğrultuda",
    "önemle vurgulanmalıdır",
]

EN_CLICHES = [
    "furthermore",
    "moreover",
    "additionally",
    "it is worth noting",
    "in conclusion",
    "that being said",
    "on the other hand",
    "needless to say",
    "first and foremost",
    "last but not least",
]

PASSIVE_TR = [
    r"\b\w+(?:edildi|ıldı|ildi|uldu|üldü)\b",
    r"\b\w+(?:nıldı|nildi|nuldu|nüldü)\b",
    r"\b(?:yapıldı|olundu|sağlandı|kullanıldı|açıklandı|değerlendirildi|belirtildi)\b",
]

TYPO_PATTERNS = [r"—", r"–", r"…", r"[“”]", r"[‘’]"]

STOPWORDS_TR = {
    "bir",
    "ve",
    "veya",
    "ile",
    "de",
    "da",
    "ki",
    "mi",
    "mı",
    "mu",
    "mü",
    "bu",
    "şu",
    "o",
    "için",
    "gibi",
    "kadar",
    "daha",
    "en",
    "çok",
    "az",
    "pek",
    "ama",
    "fakat",
    "ancak",
    "çünkü",
    "eğer",
    "yani",
    "hem",
    "ya",
    "ise",
    "olarak",
    "üzere",
    "diye",
    "göre",
    "rağmen",
    "başka",
    "sadece",
    "yalnız",
    "elbette",
    "belki",
    "bence",
    "bana",
    "sana",
    "ona",
    "bize",
    "benden",
    "senden",
    "ondan",
    "bizim",
    "senin",
    "onun",
    "beni",
    "seni",
    "onu",
    "bizi",
    "sizi",
    "burada",
    "orada",
    "nerede",
    "nereye",
    "neden",
    "niçin",
    "nasıl",
    "hangi",
    "kim",
    "ne",
    "kaç",
    "her",
    "hiç",
    "bazı",
    "bazen",
    "birçok",
    "birkaç",
    "tüm",
    "hepsi",
    "herkes",
    "şey",
    "şeyler",
    "şimdi",
    "sonra",
    "önce",
    "zaten",
    "artık",
    "henüz",
    "hâlâ",
    "yine",
    "sanki",
    "madem",
    "meğer",
    "halbuki",
    "oysa",
    "niye",
    "nedeniyle",
    "dolayı",
    "nedenle",
    "kendi",
    "kendisi",
    "kendini",
    "kendine",
    "ben",
    "sen",
    "biz",
    "siz",
    "onlar",
    "olan",
    "oldu",
    "olduğu",
    "olduğunu",
    "olacak",
    "olabilir",
    "olması",
    "olup",
    "olur",
    "olursa",
    "olmadı",
    "olmak",
    "olmayan",
    "değil",
    "var",
    "yok",
}

STOPWORDS_EN = {
    "the",
    "a",
    "an",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "have",
    "has",
    "had",
    "do",
    "does",
    "did",
    "will",
    "would",
    "could",
    "should",
    "may",
    "might",
    "shall",
    "can",
    "to",
    "of",
    "in",
    "for",
    "on",
    "with",
    "at",
    "by",
    "from",
    "as",
    "into",
    "during",
    "before",
    "after",
    "above",
    "below",
    "between",
    "out",
    "off",
    "over",
    "under",
    "again",
    "then",
    "once",
    "here",
    "there",
    "when",
    "where",
    "why",
    "how",
    "all",
    "both",
    "each",
    "few",
    "more",
    "most",
    "other",
    "some",
    "such",
    "no",
    "nor",
    "not",
    "only",
    "own",
    "same",
    "so",
    "than",
    "too",
    "very",
    "just",
    "because",
    "but",
    "and",
    "or",
    "if",
    "while",
    "about",
    "up",
    "that",
    "this",
    "these",
    "those",
    "it",
    "its",
    "i",
    "me",
    "my",
    "we",
    "our",
    "you",
    "your",
    "he",
    "him",
    "his",
    "she",
    "her",
    "they",
    "them",
    "their",
    "what",
    "which",
    "who",
    "whom",
    "am",
}

ABBREVIATIONS = [
    "dr",
    "prof",
    "doç",
    "av",
    "müh",
    "mim",
    "alb",
    "bşk",
    "gen",
    "vs",
    "vb",
    "yk",
    "sgk",
    "tc",
    "tl",
    "usd",
    "eur",
    "gb",
    "mb",
    "tb",
    "dk",
    "sn",
    "gr",
    "kg",
    "cm",
    "mm",
    "km",
    "no",
    "nr",
    "say",
    "sf",
]

SYNONYM_GROUPS = [
    ["gelişmek", "ilerlemek", "büyümek", "artmak", "yükselmek"],
    ["önemli", "kritik", "değerli", "kayda_değer"],
    ["büyük", "geniş", "kapsamlı", "devasa"],
    ["hız", "sürat", "çabukluk", "hızlı"],
    ["etki", "tesir", "etkilemek", "etkisi"],
    ["teknoloji", "teknik", "dijital", "teknolojik"],
    ["hayat", "yaşam", "günlük", "yaşantı"],
    ["gelecek", "ileride", "gelecekte", "ileriki"],
    ["alan", "sektör", "bölüm", "saha"],
    ["gerekli", "şart", "zorunlu", "lazım"],
    ["katkı", "fayda", "yarar", "avantaj"],
    ["sorun", "problem", "zorluk", "mesele"],
    ["çözüm", "çare", "yol", "çözümü"],
    ["artırmak", "güçlendirmek", "geliştirmek", "yükseltmek"],
    ["kullanmak", "yararlanmak", "faydalanmak", "uygulamak"],
    ["sağlamak", "sunmak", "temin", "oluşturmak"],
    ["göstermek", "belirtmek", "ortaya_koymak", "ifade_etmek"],
    ["yapmak", "gerçekleştirmek", "uygulamak", "üretmek"],
    ["düşünce", "fikir", "görüş", "yaklaşım"],
    ["insan", "birey", "kişi", "toplum"],
    ["world", "global", "international", "worldwide"],
    ["important", "significant", "critical", "vital"],
    ["increase", "grow", "rise", "expand"],
    ["impact", "effect", "influence", "affect"],
    ["use", "utilize", "employ", "apply"],
    ["show", "demonstrate", "indicate", "reveal"],
]

WORD_TO_GROUP = {
    word.lower(): idx for idx, group in enumerate(SYNONYM_GROUPS) for word in group
}


def clamp(value: float, min_value: float, max_value: float) -> float:
    return min(max_value, max(min_value, value))


def count_matches(text: str, pattern: str) -> int:
    return len(re.findall(pattern, text, flags=re.IGNORECASE))


def get_paragraphs(text: str) -> list[str]:
    return [
        paragraph.strip()
        for paragraph in re.split(r"\n{2,}", text)
        if paragraph.strip()
    ]


def get_words(text: str) -> list[str]:
    return re.findall(r"\b[\wçğıöşüÇĞİÖŞÜ]+\b", text.lower())


def detect_lang(text: str) -> str:
    words = get_words(text)
    tr_hits = sum(1 for word in words if re.search(r"[çğıöşü]", word))
    en_hits = sum(1 for word in words if word in STOPWORDS_EN)
    return "tr" if tr_hits >= en_hits else "en"


def get_words_filtered(text: str, lang: str) -> list[str]:
    stopwords = STOPWORDS_TR if lang == "tr" else STOPWORDS_EN
    return [word for word in get_words(text) if word not in stopwords and len(word) > 2]


def stem_tr(word: str) -> str:
    suffixes = [
        "maktadır",
        "mektedir",
        "larımız",
        "lerimiz",
        "larından",
        "lerinden",
        "larınız",
        "leriniz",
        "ları",
        "leri",
        "ımız",
        "imiz",
        "umuz",
        "ümüz",
        "ınız",
        "iniz",
        "unuz",
        "ünüz",
        "daki",
        "deki",
        "dan",
        "den",
        "tan",
        "ten",
        "dır",
        "dir",
        "dur",
        "dür",
        "tir",
        "tır",
        "tur",
        "tür",
        "iyor",
        "ıyor",
        "uyor",
        "üyor",
        "acak",
        "ecek",
        "miş",
        "mış",
        "muş",
        "müş",
        "mek",
        "mak",
        "lar",
        "ler",
        "lık",
        "lik",
        "luk",
        "lük",
        "cı",
        "ci",
        "cu",
        "cü",
        "çı",
        "çi",
        "çu",
        "çü",
        "lı",
        "li",
        "lu",
        "lü",
        "sız",
        "siz",
        "suz",
        "süz",
        "dan",
        "den",
        "ta",
        "te",
        "da",
        "de",
        "ın",
        "in",
        "un",
        "ün",
        "ı",
        "i",
        "u",
        "ü",
    ]
    stem = word
    for suffix in suffixes:
        if stem.endswith(suffix) and len(stem) > len(suffix) + 2:
            stem = stem[: -len(suffix)]
            break
    return stem


def stem_en(word: str) -> str:
    suffixes = [
        "ingly",
        "edly",
        "ments",
        "ment",
        "tion",
        "sion",
        "ings",
        "ness",
        "less",
        "able",
        "ible",
        "ing",
        "ers",
        "ies",
        "ied",
        "est",
        "ed",
        "es",
        "s",
    ]
    stem = word
    for suffix in suffixes:
        if stem.endswith(suffix) and len(stem) > len(suffix) + 2:
            stem = stem[: -len(suffix)]
            break
    return stem


def stem_token(word: str, lang: str) -> str:
    return stem_tr(word) if lang == "tr" else stem_en(word)


def get_semantic_vector(words: list[str], lang: str) -> Counter:
    vector = Counter()
    for word in words:
        stemmed = stem_token(word, lang)
        vector[stemmed] += 1
        group_id = WORD_TO_GROUP.get(word)
        if group_id is None:
            group_id = WORD_TO_GROUP.get(stemmed)
        if group_id is not None:
            vector[f"syn_{group_id}"] += 1
    return vector


def cosine_similarity(vec_a: Counter, vec_b: Counter) -> float:
    keys = set(vec_a) | set(vec_b)
    dot = sum(vec_a.get(key, 0) * vec_b.get(key, 0) for key in keys)
    mag_a = math.sqrt(sum(value * value for value in vec_a.values()))
    mag_b = math.sqrt(sum(value * value for value in vec_b.values()))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


def jaccard_similarity(set_a: set[str], set_b: set[str]) -> float:
    if not set_a and not set_b:
        return 0.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union else 0.0


def split_sentences(text: str) -> list[str]:
    sentences: list[str] = []
    for raw_line in re.split(r"\n+", text):
        line = raw_line.strip()
        if len(line) < 3:
            continue
        if line.startswith("#"):
            cleaned_heading = re.sub(r"^#+\s*", "", line).strip()
            if cleaned_heading:
                sentences.append(cleaned_heading)
            continue

        protected = re.sub(r"(\d)\.(\d)", r"\1<DOT>\2", line)
        for abbr in ABBREVIATIONS:
            protected = re.sub(
                rf"\b({re.escape(abbr)})\.", r"\1<ABBR>", protected, flags=re.IGNORECASE
            )
        protected = re.sub(r"\b([A-Za-zÇĞİÖŞÜçğıöşü])\.", r"\1<ABBR>", protected)
        protected = re.sub(
            r"https?://\S+",
            lambda match: match.group(0).replace(".", "<DOT>"),
            protected,
        )
        parts = re.split(r"(?<=[.!?])\s+", protected)
        for part in parts:
            sentence = part.replace("<DOT>", ".").replace("<ABBR>", ".").strip()
            if sentence:
                sentences.append(sentence)
    return sentences


def ring_svg(score: float, color: str, size: int = 124) -> str:
    radius = (size - 12) / 2
    circumference = 2 * math.pi * radius
    offset = circumference - (score / 100.0) * circumference
    return f"""
<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">
  <circle cx="{size / 2}" cy="{size / 2}" r="{radius}" fill="none" stroke="#e5e7eb" stroke-width="8"></circle>
  <circle cx="{size / 2}" cy="{size / 2}" r="{radius}" fill="none" stroke="{color}" stroke-width="8"
          stroke-linecap="round" stroke-dasharray="{circumference}" stroke-dashoffset="{offset}"></circle>
</svg>
"""


def score_color_hex(score: float) -> str:
    if score > 60:
        return "#dc2626"
    if score >= 30:
        return "#d97706"
    return "#16a34a"


def score_desc(score: float, kind: str) -> str:
    if kind == "ai":
        return (
            "Yüksek YZ olasılığı"
            if score > 60
            else "Orta seviye"
            if score >= 30
            else "Düşük olasılık"
        )
    if kind == "repeat":
        return (
            "Yüksek tekrar"
            if score > 60
            else "Orta tekrar"
            if score >= 30
            else "Az tekrar"
        )
    return (
        "Yüksek orijinallik"
        if score > 60
        else "Orta seviye"
        if score >= 30
        else "Düşük orijinallik"
    )


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_article(url: str) -> dict:
    downloaded = trafilatura.fetch_url(url)
    if not downloaded:
        raise ValueError("Sayfa indirilemedi. URL erişilebilir olmayabilir.")

    plain_text = trafilatura.extract(
        downloaded,
        include_comments=False,
        include_tables=True,
    )
    if not plain_text or len(plain_text.strip()) < 50:
        raise ValueError("Sayfadan yeterli metin çıkarılamadı.")

    try:
        markdown_text = trafilatura.extract(
            downloaded,
            include_comments=False,
            include_tables=True,
            output_format="markdown",
        )
    except Exception:
        markdown_text = plain_text

    return {
        "plain_text": plain_text.strip(),
        "structured_text": (markdown_text or plain_text).strip(),
    }


def analyze_text(plain_text: str, structured_text: str) -> dict:
    lang = detect_lang(plain_text)
    sentences = split_sentences(plain_text)
    paragraphs = get_paragraphs(plain_text)
    all_words = get_words(plain_text)
    filtered_words = get_words_filtered(plain_text, lang)
    all_cliches = TR_CLICHES if lang == "tr" else EN_CLICHES

    found_cliches: list[str] = []
    lowered = plain_text.lower()
    for phrase in all_cliches:
        hits = len(re.findall(re.escape(phrase), lowered, flags=re.IGNORECASE))
        found_cliches.extend([phrase] * hits)

    typo_count = sum(count_matches(plain_text, pattern) for pattern in TYPO_PATTERNS)
    passive_count = sum(count_matches(plain_text, pattern) for pattern in PASSIVE_TR)
    if lang == "en":
        passive_count += count_matches(
            plain_text, r"\b(?:was|were|is|are|been|being)\s+\w+(?:ed|en)\b"
        )

    structured_lines = structured_text.splitlines()
    list_lines = sum(
        bool(re.match(r"^\s*(?:[-*•]|\d+\.)\s", line)) for line in structured_lines
    )
    heading_lines = sum(
        bool(re.match(r"^\s*#{1,6}\s", line)) for line in structured_lines
    )

    sentence_lengths = [len(get_words(sentence)) for sentence in sentences] or [0]
    avg_sentence_length = mean(sentence_lengths)
    burstiness = (
        (np.std(sentence_lengths) / avg_sentence_length) if avg_sentence_length else 0.0
    )
    ttr = (len(set(all_words)) / len(all_words)) if all_words else 0.0

    punctuation_marks = re.findall(r"[,:;!?()\"'“”‘’—–…-]", plain_text)
    punctuation_variety = len(set(punctuation_marks))
    punctuation_density = (
        (len(re.findall(r"[,:;!?]", plain_text)) / len(all_words)) if all_words else 0.0
    )

    sentence_word_sets = [
        set(get_words_filtered(sentence, lang)) for sentence in sentences
    ]
    similar_pairs_jaccard = []
    semantic_pairs = []
    for i in range(len(sentences)):
        for j in range(i + 1, len(sentences)):
            jac = jaccard_similarity(sentence_word_sets[i], sentence_word_sets[j])
            if jac >= 0.55:
                similar_pairs_jaccard.append(
                    {"a": sentences[i], "b": sentences[j], "score": jac}
                )
                continue

            words_a = get_words_filtered(sentences[i], lang)
            words_b = get_words_filtered(sentences[j], lang)
            if len(words_a) < 2 or len(words_b) < 2:
                continue
            cos = cosine_similarity(
                get_semantic_vector(words_a, lang), get_semantic_vector(words_b, lang)
            )
            if cos >= 0.30 and jac < 0.55:
                semantic_pairs.append(
                    {"a": sentences[i], "b": sentences[j], "score": cos, "jac": jac}
                )

    similar_pairs_jaccard.sort(key=lambda item: item["score"], reverse=True)
    semantic_pairs.sort(key=lambda item: item["score"], reverse=True)
    all_similar_pairs = similar_pairs_jaccard + semantic_pairs

    trigram_counts: Counter[str] = Counter(
        " ".join(filtered_words[index : index + 3])
        for index in range(max(0, len(filtered_words) - 2))
    )
    repeated_trigrams = [
        (text, count) for text, count in trigram_counts.items() if count > 1
    ]
    repeated_trigrams.sort(key=lambda item: item[1], reverse=True)

    top_words = Counter(filtered_words).most_common(12)
    repeated_words = [
        (word, count)
        for word, count in Counter(filtered_words).most_common(20)
        if count > 1
    ]

    word_count = len(all_words)
    sentence_count = len(sentences)
    paragraph_count = len(paragraphs)
    cliche_density = (len(found_cliches) / word_count * 1000) if word_count else 0.0
    passive_density = (passive_count / word_count * 1000) if word_count else 0.0
    repetition_ratio = (
        (len(all_similar_pairs) / sentence_count) if sentence_count else 0.0
    )

    structure_score = clamp(
        paragraph_count * 6
        + heading_lines * 8
        + (12 if avg_sentence_length < 30 else 0)
        + (12 if punctuation_variety >= 4 else 0),
        0,
        100,
    )
    lexical_richness = clamp((ttr * 100) - max(0, repetition_ratio * 40), 0, 100)

    ai_score = 0.0
    ai_score += clamp(cliche_density * 7.5, 0, 24)
    ai_score += 16 if typo_count >= 3 else 7 if typo_count >= 1 else 0
    ai_score += 18 if burstiness < 0.36 else 10 if burstiness < 0.48 else 0
    ai_score += clamp(passive_density * 9, 0, 12)
    ai_score += 8 if list_lines >= 4 else 4 if list_lines >= 2 else 0
    ai_score += 8 if heading_lines >= 3 else 3 if heading_lines >= 1 else 0
    ai_score += 10 if ttr > 0.78 else 6 if ttr > 0.70 else 0
    ai_score += 7 if punctuation_variety <= 2 and avg_sentence_length > 10 else 0
    ai_score += 8 if repetition_ratio > 0.25 else 4 if repetition_ratio > 0.12 else 0
    ai_score = round(clamp(ai_score, 0, 100))

    repeat_score = 0.0
    repeat_score += min(len(similar_pairs_jaccard) * 14, 36)
    repeat_score += min(len(semantic_pairs) * 10, 26)
    repeat_score += min(max(0, len(repeated_trigrams) - 2) * 4, 20)
    repeat_score += (
        10 if repetition_ratio > 0.20 else 5 if repetition_ratio > 0.10 else 0
    )
    repeat_score = round(clamp(repeat_score, 0, 100))

    originality_score = round(
        clamp(
            35
            + lexical_richness * 0.35
            + structure_score * 0.25
            + min(burstiness * 80, 18)
            - repeat_score * 0.45
            - ai_score * 0.2,
            0,
            100,
        )
    )

    confidence_score = round(
        clamp(
            (word_count / 14) + (sentence_count * 2.4) + (paragraph_count * 4), 18, 98
        )
    )

    findings = []
    if found_cliches:
        findings.append(
            {
                "text": f"{len(found_cliches)} adet klişe ifade tespit edildi",
                "badge": "Klişe",
            }
        )
    if typo_count:
        findings.append(
            {
                "text": f"{typo_count} adet tipografik karakter kullanımı bulundu",
                "badge": "YZ İşareti",
            }
        )
    if burstiness < 0.45:
        findings.append(
            {
                "text": f"Cümle ritmi tekdüze görünüyor (burstiness: {burstiness:.2f})",
                "badge": "YZ İşareti",
            }
        )
    if passive_count:
        findings.append(
            {"text": f"{passive_count} adet pasif yapı bulundu", "badge": "YZ İşareti"}
        )
    if list_lines:
        findings.append(
            {"text": f"{list_lines} adet liste satırı bulundu", "badge": "YZ İşareti"}
        )
    if heading_lines:
        findings.append(
            {"text": f"{heading_lines} adet başlık satırı bulundu", "badge": "Temiz"}
        )
    if similar_pairs_jaccard:
        findings.append(
            {
                "text": f"{len(similar_pairs_jaccard)} adet kelime bazlı tekrar tespit edildi",
                "badge": "Tekrar",
            }
        )
    if semantic_pairs:
        findings.append(
            {
                "text": f"{len(semantic_pairs)} adet anlamsal tekrar bulundu",
                "badge": "Anlamsal",
            }
        )
    if repeated_trigrams:
        findings.append(
            {
                "text": f"{len(repeated_trigrams)} adet tekrar eden trigram bulundu",
                "badge": "Tekrar",
            }
        )
    if punctuation_variety <= 2:
        findings.append(
            {
                "text": "Noktalama çeşitliliği düşük, metin ritmi mekanik olabilir",
                "badge": "YZ İşareti",
            }
        )
    if paragraph_count:
        findings.append(
            {
                "text": f"{paragraph_count} paragraf üzerinden yapısal analiz üretildi",
                "badge": "Temiz",
            }
        )
    if not findings:
        findings.append(
            {"text": "Önemli bir risk veya tekrar sinyali bulunamadı", "badge": "Temiz"}
        )

    summary = (
        f"Metin {word_count} kelime, {sentence_count} cümle ve {paragraph_count} paragraftan oluşuyor. "
        f"Sözcük çeşitliliği %{ttr * 100:.1f}, ortalama cümle uzunluğu {avg_sentence_length:.1f} kelime ve yapısal kalite skoru {structure_score:.0f}/100 seviyesinde. "
    )
    if ai_score > 60:
        summary += "Yapay zeka sinyalleri güçlü: klişe yoğunluğu, düşük ritim çeşitliliği veya pasif yapı kullanımı dikkat çekiyor. "
    elif ai_score >= 30:
        summary += "Yapay zeka sinyalleri orta seviyede; bazı şüpheli örüntüler var ama tek başına kesin karar vermek doğru olmaz. "
    else:
        summary += (
            "Yapay zeka skoru düşük; metin ritmi ve yapısı daha doğal görünüyor. "
        )
    if repeat_score > 40:
        summary += f"Tekrar tarafında {len(similar_pairs_jaccard)} kelime bazlı, {len(semantic_pairs)} anlamsal tekrar ve {len(repeated_trigrams)} tekrar eden trigram öne çıkıyor. "
    summary += f"Analiz güveni {confidence_score}/100, genel orijinallik skoru ise {originality_score}/100 olarak hesaplandı."

    return {
        "lang": lang,
        "plain_text": plain_text,
        "structured_text": structured_text,
        "word_count": word_count,
        "sentence_count": sentence_count,
        "paragraph_count": paragraph_count,
        "avg_sentence_length": avg_sentence_length,
        "ttr": ttr,
        "burstiness": burstiness,
        "punctuation_variety": punctuation_variety,
        "punctuation_density": punctuation_density,
        "structure_score": structure_score,
        "lexical_richness": lexical_richness,
        "confidence_score": confidence_score,
        "ai_score": ai_score,
        "repeat_score": repeat_score,
        "originality_score": originality_score,
        "found_cliches": found_cliches,
        "typo_count": typo_count,
        "list_lines": list_lines,
        "heading_lines": heading_lines,
        "passive_count": passive_count,
        "similar_pairs_jaccard": similar_pairs_jaccard,
        "semantic_pairs": semantic_pairs,
        "all_similar_pairs": all_similar_pairs,
        "repeated_trigrams": repeated_trigrams,
        "repeated_words": repeated_words,
        "top_words": top_words,
        "sentence_lengths": sentence_lengths,
        "findings": findings,
        "summary": summary,
        "cliche_density": cliche_density,
        "passive_density": passive_density,
        "repetition_ratio": repetition_ratio,
    }


def render_score_card(title: str, score: float, description: str, css_class: str):
    color = score_color_hex(score)
    html_block = f"""
    <div class="score-card {css_class}">
        <div class="score-label">{title}</div>
        <div class="score-ring-wrap">
            {ring_svg(score, color)}
            <div class="ring-center" style="color:{color};">{int(round(score))}</div>
        </div>
        <div class="score-desc">{description}</div>
    </div>
    """
    st.markdown(html_block, unsafe_allow_html=True)


def render_gauges(items: list[dict]):
    rows = []
    for item in items:
        rows.append(
            f"""
            <div class="gauge-row">
                <div class="gauge-name">{item["label"]}</div>
                <div class="gauge-track"><div class="gauge-fill" style="width:{item["pct"]}%;background:{item["color"]};"></div></div>
                <div class="gauge-value">{item["value"]}</div>
            </div>
            """
        )
    st.markdown(
        f"<div class='gauge-list'>{''.join(rows)}</div>", unsafe_allow_html=True
    )


def render_findings(findings: list[dict]):
    badge_map = {
        "YZ İşareti": "badge-ai",
        "Tekrar": "badge-repeat",
        "Temiz": "badge-clean",
        "Klişe": "badge-cliche",
        "Anlamsal": "badge-semantic",
    }
    rows = []
    for finding in findings:
        badge_class = badge_map.get(finding["badge"], "badge-clean")
        rows.append(
            f"""
            <div class="finding-row">
                <div class="finding-text">{html.escape(finding["text"])}</div>
                <div class="badge {badge_class}">{finding["badge"]}</div>
            </div>
            """
        )
    st.markdown("".join(rows), unsafe_allow_html=True)


def render_repeat_group(
    title: str, pairs: list[dict], color: str, score_key: str, label: str
):
    if not pairs:
        st.info(f"{title} için gösterilecek eşleşme bulunamadı.")
        return
    st.markdown(f"#### {title}")
    for pair in pairs[:20]:
        pct = round(pair[score_key] * 100)
        st.markdown(
            f"""
            <div class="repeat-box">
                <div class="repeat-score" style="color:{color};">%{pct} {label}</div>
                <div class="repeat-text"><em>{html.escape(pair["a"])}</em></div>
                <div class="repeat-text"><em>{html.escape(pair["b"])}</em></div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_pills(title: str, items: list[str], css_class: str):
    if not items:
        st.caption(f"{title}: işaret yok")
        return
    unique_items = list(dict.fromkeys(items))
    pills = "".join(
        f"<span class='pill {css_class}'>{html.escape(item)}</span>"
        for item in unique_items[:24]
    )
    st.markdown(f"**{title}**", unsafe_allow_html=False)
    st.markdown(f"<div class='pill-wrap'>{pills}</div>", unsafe_allow_html=True)


def copyable_report_text(result: dict, url: str) -> str:
    lines = [
        "=== METIN DILIGENCE ANALIZ RAPORU ===",
        "",
        f"Kaynak: {url}",
        f"Yapay Zeka Skoru: {result['ai_score']}/100",
        f"Tekrar Skoru: {result['repeat_score']}/100",
        f"Orijinallik Skoru: {result['originality_score']}/100",
        f"Analiz Guveni: {result['confidence_score']}/100",
        f"Yapi Skoru: {round(result['structure_score'])}/100",
        f"Lexical Richness: {round(result['lexical_richness'])}/100",
        "",
        f"Kelime: {result['word_count']} | Cumle: {result['sentence_count']} | Paragraf: {result['paragraph_count']} | TTR: %{result['ttr'] * 100:.1f}",
        "",
        "BULGULAR:",
    ]
    lines.extend(
        f"- [{finding['badge']}] {finding['text']}" for finding in result["findings"]
    )
    lines.extend(["", result["summary"]])
    return "\n".join(lines)


if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "analysis_url" not in st.session_state:
    st.session_state.analysis_url = ""


st.markdown(
    "<div class='hero-title'>Metin Diligence Analizörü</div>", unsafe_allow_html=True
)
st.markdown(
    "<div class='hero-subtitle'>Bir web sitesi URL'si girin. Sayfadaki ana metin backend üzerinden çekilsin, sonra yapay zeka sinyalleri, tekrar örüntüleri ve özgünlük yapısı daha gerçekçi heuristiklerle değerlendirilsin.</div>",
    unsafe_allow_html=True,
)


input_col, button_col = st.columns([5, 1])
with input_col:
    url = st.text_input(
        "URL", placeholder="https://ornek.com/makale", label_visibility="collapsed"
    )
with button_col:
    analyze_clicked = st.button("Analiz Et", use_container_width=True, type="primary")


if analyze_clicked:
    normalized_url = url.strip()
    parsed = urlparse(normalized_url)
    if not normalized_url or not parsed.scheme or not parsed.netloc:
        st.error("Geçerli bir URL girin.")
    else:
        with st.spinner("Sayfa çekiliyor ve analiz ediliyor..."):
            try:
                fetched = fetch_article(normalized_url)
                result = analyze_text(fetched["plain_text"], fetched["structured_text"])
                st.session_state.analysis_result = result
                st.session_state.analysis_url = normalized_url
            except Exception as exc:
                st.session_state.analysis_result = None
                st.error(f"Analiz sırasında hata oluştu: {exc}")


result = st.session_state.analysis_result
source_url = st.session_state.analysis_url

if result:
    st.caption(
        f"Kaynak: `{source_url}`  |  Kelime: `{result['word_count']}`  |  Cümle: `{result['sentence_count']}`  |  Paragraf: `{result['paragraph_count']}`  |  Dil: `{result['lang'].upper()}`"
    )

    hero_cols = st.columns(3)
    with hero_cols[0]:
        render_score_card(
            "Yapay Zeka Skoru",
            result["ai_score"],
            score_desc(result["ai_score"], "ai"),
            "ai",
        )
    with hero_cols[1]:
        render_score_card(
            "Tekrar Skoru",
            result["repeat_score"],
            score_desc(result["repeat_score"], "repeat"),
            "repeat",
        )
    with hero_cols[2]:
        render_score_card(
            "Orijinallik Skoru",
            result["originality_score"],
            score_desc(result["originality_score"], "original"),
            "original",
        )

    metric_cols = st.columns(4)
    metric_cols[0].metric("Kelime", f"{result['word_count']:,}")
    metric_cols[1].metric("Cümle", f"{result['sentence_count']:,}")
    metric_cols[2].metric("Sözcük Çeşitliliği", f"%{result['ttr'] * 100:.1f}")
    metric_cols[3].metric("Cümle Varyansı", f"{result['burstiness']:.2f}")

    overview_col, confidence_col = st.columns([1.4, 1])
    with overview_col:
        st.markdown(
            "<div class='surface'><div class='section-title'>Kaynak Görünümü</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
            <div class='mini-grid'>
                <div class='mini-stat'><div class='mini-stat-value'>{result["paragraph_count"]}</div><div class='mini-stat-label'>Paragraf</div></div>
                <div class='mini-stat'><div class='mini-stat-value'>{result["avg_sentence_length"]:.1f}</div><div class='mini-stat-label'>Ort. Cümle Uzunluğu</div></div>
                <div class='mini-stat'><div class='mini-stat-value'>{result["punctuation_variety"]}</div><div class='mini-stat-label'>Noktalama Çeşidi</div></div>
                <div class='mini-stat'><div class='mini-stat-value'>{round(result["lexical_richness"])}</div><div class='mini-stat-label'>Lexical Richness</div></div>
                <div class='mini-stat'><div class='mini-stat-value'>{len(result["similar_pairs_jaccard"])}</div><div class='mini-stat-label'>Kelime Tekrarı</div></div>
                <div class='mini-stat'><div class='mini-stat-value'>{len(result["semantic_pairs"])}</div><div class='mini-stat-label'>Anlamsal Tekrar</div></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        chips = []
        chips.append(
            (
                f"AI Risk {result['ai_score']}",
                "chip-risk"
                if result["ai_score"] > 60
                else "chip-warn"
                if result["ai_score"] >= 30
                else "chip-safe",
            )
        )
        chips.append(
            (
                f"Tekrar {result['repeat_score']}",
                "chip-risk"
                if result["repeat_score"] > 60
                else "chip-warn"
                if result["repeat_score"] >= 30
                else "chip-safe",
            )
        )
        chips.append(
            (
                f"Orijinallik {result['originality_score']}",
                "chip-safe"
                if result["originality_score"] >= 65
                else "chip-warn"
                if result["originality_score"] >= 40
                else "chip-risk",
            )
        )
        if result["repetition_ratio"] > 0.15:
            chips.append(("Yüksek tekrar oranı", "chip-risk"))
        if result["cliche_density"] > 2:
            chips.append(("Klişe yoğunluğu yüksek", "chip-warn"))
        if result["structure_score"] >= 55:
            chips.append(("Yapı tutarlı", "chip-safe"))
        chips_html = "".join(
            f"<span class='chip {css}'>{text}</span>" for text, css in chips
        )
        st.markdown(
            f"<div class='chip-row'>{chips_html}</div></div>", unsafe_allow_html=True
        )

    with confidence_col:
        confidence_color = score_color_hex(
            20
            if result["confidence_score"] >= 70
            else 45
            if result["confidence_score"] >= 50
            else 75
        )
        st.markdown(
            "<div class='surface'><div class='section-title'>Analiz Güveni</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
            <div style='display:flex;align-items:center;gap:1rem;'>
                <div style='font-size:2rem;font-weight:800;color:{confidence_color};min-width:64px;'>{result["confidence_score"]}</div>
                <div style='flex:1;'>
                    <div style='height:10px;background:#e5e7eb;border-radius:999px;overflow:hidden;'>
                        <div style='width:{result["confidence_score"]}%;height:100%;background:{confidence_color};border-radius:999px;'></div>
                    </div>
                    <div style='margin-top:0.65rem;font-size:0.85rem;color:#64748b;'>
                        {"Yeterli metin uzunluğu ve cümle sayısı sayesinde bu analiz yüksek güvenle üretildi." if result["confidence_score"] >= 80 else "Analiz yapılabilir seviyede veri var; sonuçlar yön gösterici olarak okunmalı." if result["confidence_score"] >= 60 else "Metin kısa veya parçalı olduğu için güven sınırlı."}
                    </div>
                </div>
            </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    tabs = st.tabs(["Özet", "Tekrarlar", "İşaretler", "Grafikler", "Tam Metin"])

    with tabs[0]:
        left, right = st.columns([1, 1])
        with left:
            with st.container(border=True):
                st.markdown("##### Detaylı Göstergeler")
                gauge_items = [
                    {
                        "label": "Klişeler",
                        "value": len(result["found_cliches"]),
                        "pct": 100
                        if len(result["found_cliches"]) >= 3
                        else 50
                        if len(result["found_cliches"]) >= 1
                        else 0,
                        "color": "#d97706",
                    },
                    {
                        "label": "Tipografik",
                        "value": result["typo_count"],
                        "pct": 100
                        if result["typo_count"] >= 3
                        else 40
                        if result["typo_count"] >= 1
                        else 0,
                        "color": "#6366f1",
                    },
                    {
                        "label": "Liste",
                        "value": result["list_lines"],
                        "pct": 100
                        if result["list_lines"] >= 4
                        else 33
                        if result["list_lines"] > 0
                        else 0,
                        "color": "#16a34a",
                    },
                    {
                        "label": "Pasif",
                        "value": result["passive_count"],
                        "pct": 100
                        if result["passive_count"] > 2
                        else 50
                        if result["passive_count"] > 0
                        else 0,
                        "color": "#dc2626",
                    },
                    {
                        "label": "Tekrar",
                        "value": len(result["all_similar_pairs"]),
                        "pct": min(len(result["all_similar_pairs"]) * 25, 100),
                        "color": "#dc2626",
                    },
                    {
                        "label": "Trigram",
                        "value": len(result["repeated_trigrams"]),
                        "pct": min(
                            max(0, len(result["repeated_trigrams"]) - 2) * 15, 100
                        ),
                        "color": "#b91c1c",
                    },
                    {
                        "label": "Yapı",
                        "value": round(result["structure_score"]),
                        "pct": result["structure_score"],
                        "color": "#16a34a",
                    },
                    {
                        "label": "Lexical",
                        "value": round(result["lexical_richness"]),
                        "pct": result["lexical_richness"],
                        "color": "#0f766e",
                    },
                ]
                render_gauges(gauge_items)
        with right:
            with st.container(border=True):
                st.markdown("##### Genel Rapor Özeti")
                st.write(result["summary"])

        with st.container(border=True):
            st.markdown("##### Tespit Edilen Bulgular")
            render_findings(result["findings"])

    with tabs[1]:
        left, right = st.columns(2)
        with left:
            render_repeat_group(
                "Aynı Kelimelerle Tekrar",
                result["similar_pairs_jaccard"],
                "#dc2626",
                "score",
                "Kelime Örtüşmesi",
            )
        with right:
            render_repeat_group(
                "Farklı Kelimelerle Aynı Anlam",
                result["semantic_pairs"],
                "#d97706",
                "score",
                "Anlamsal Benzerlik",
            )

    with tabs[2]:
        col_a, col_b = st.columns(2)
        with col_a:
            with st.container(border=True):
                render_pills("Klişe İfadeler", result["found_cliches"], "pill-cliche")
        with col_b:
            with st.container(border=True):
                render_pills(
                    "Tekrar Eden Trigramlar",
                    [
                        f"{text} ({count}x)"
                        for text, count in result["repeated_trigrams"]
                    ],
                    "pill-trigram",
                )

    with tabs[3]:
        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            length_buckets = {
                "1-5": 0,
                "6-10": 0,
                "11-20": 0,
                "21-35": 0,
                "35+": 0,
            }
            for length in result["sentence_lengths"]:
                if length <= 5:
                    length_buckets["1-5"] += 1
                elif length <= 10:
                    length_buckets["6-10"] += 1
                elif length <= 20:
                    length_buckets["11-20"] += 1
                elif length <= 35:
                    length_buckets["21-35"] += 1
                else:
                    length_buckets["35+"] += 1
            st.markdown("##### Cümle Uzunluk Dağılımı")
            st.bar_chart(
                pd.DataFrame(
                    {"Cümle Sayısı": list(length_buckets.values())},
                    index=list(length_buckets.keys()),
                )
            )

        with chart_col2:
            st.markdown("##### En Sık 12 Kelime")
            if result["top_words"]:
                top_word_df = pd.DataFrame(
                    result["top_words"], columns=["Kelime", "Tekrar"]
                ).set_index("Kelime")
                st.bar_chart(top_word_df)
            else:
                st.info("Grafik için yeterli kelime bulunamadı.")

        with st.container(border=True):
            st.markdown("##### En Çok Tekrar Eden Kelimeler")
            if result["repeated_words"]:
                repeated_word_df = pd.DataFrame(
                    result["repeated_words"], columns=["Kelime", "Tekrar"]
                )
                st.dataframe(
                    repeated_word_df, use_container_width=True, hide_index=True
                )
            else:
                st.info("Tekrar eden anlamlı kelime bulunamadı.")

    with tabs[4]:
        st.markdown("##### Çekilen Metin (Tamamı)")
        st.caption("Bu bölüm kırpılmadan çıkarılan metnin tamamını gösterir.")
        st.markdown(
            f"<div class='full-text-box'>{html.escape(result['plain_text'])}</div>",
            unsafe_allow_html=True,
        )

    report_text = copyable_report_text(result, source_url)
    st.download_button(
        "Raporu TXT olarak indir",
        data=report_text,
        file_name="metin-diligence-raporu.txt",
        mime="text/plain",
        use_container_width=True,
    )
