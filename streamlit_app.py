import streamlit as st
import trafilatura
import re
import numpy as np
import pandas as pd
from collections import Counter
import language_tool_python

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
</style>
""",
    unsafe_allow_html=True,
)

# ============================================================
# TÜRKÇE STOPWORD LİSTESİ (kelime frekans analizi için)
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
    "hangi",
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
# AI KLİŞE KALIPLARI (Türkçe AI metinlerinde sık kullanılanlar)
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
    """Metindeki AI klişe kalıplarını sayar ve frekanslarını hesaplar."""
    text_lower = text.lower()
    found_cliches = {}

    for cliche in AI_CLICHES:
        count = len(re.findall(re.escape(cliche), text_lower))
        if count > 0:
            found_cliches[cliche] = count

    return found_cliches


def analyze_burstiness(text):
    """
    Cümle uzunluklarının standart sapmasını hesaplar.
    Düşük sapma = Robotik/Tekdüze, Yüksek sapma = İnsansı/Çeşitli
    """
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


def calculate_ai_score(markdown_count, cliche_count, burstiness_std, word_count):
    """
    Markdown izleri, klişeler ve tekdüzelik analizine göre
    0-100 arası AI olma ihtimali skoru hesaplar.
    """
    if markdown_count == 0:
        md_score = 0
    elif markdown_count <= 3:
        md_score = 25
    elif markdown_count <= 8:
        md_score = 55
    else:
        md_score = 100

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

    final_score = (md_score * 0.25) + (cliche_score * 0.40) + (burst_score * 0.35)

    return {
        "total": round(final_score, 1),
        "markdown_score": md_score,
        "cliche_score": cliche_score,
        "burstiness_score": burst_score,
    }


def analyze_word_frequency(text):
    """Noktalama ve stopword temizleyerek en çok tekrar eden 10 kelimeyi bulur."""
    cleaned = re.sub(r"[^\w\s]", "", text.lower())
    words = cleaned.split()
    filtered_words = [w for w in words if w not in TURKISH_STOPWORDS and len(w) > 2]
    counter = Counter(filtered_words)
    top_10 = counter.most_common(10)
    return top_10, len(words), len(filtered_words)


def check_spelling(text):
    """language_tool_python ile Türkçe yazım denetimi yapar."""
    try:
        tool = language_tool_python.LanguageTool("tr-TR")
        matches = tool.check(text)
        return matches
    except Exception as e:
        st.error(f"Yazım denetimi sırasında bir hata oluştu: {str(e)}")
        return []


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
                ai_score = calculate_ai_score(
                    markdown_total,
                    sum(found_cliches.values()),
                    burstiness["std_dev"],
                    word_count_total,
                )
                top_words, total_words, filtered_words_count = analyze_word_frequency(
                    text
                )
                spelling_errors = check_spelling(text)

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

                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric(
                        "Markdown İzleri Skoru",
                        f"{ai_score['markdown_score']}%",
                        help="Ham kopyalama izleri (kalın, başlık, kod bloğu vb.)",
                    )
                with c2:
                    st.metric(
                        "Klişe Kalıp Skoru",
                        f"{ai_score['cliche_score']}%",
                        help="AI'ın sık kullandığı Türkçe kalıplar",
                    )
                with c3:
                    st.metric(
                        "Tekdüzelik (Burstiness) Skoru",
                        f"{ai_score['burstiness_score']}%",
                        help="Cümle uzunluk çeşitliliği (düşük = robotik)",
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
                        f"Toplam **{sum(found_cliches.values())}** adet AI klişe kalıbı bulundu. "
                        f"Bu kalıplar, yapay zeka modellerinin Türkçe metin üretirken "
                        f"sık kullandığı ifadelerdir."
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

                    error_data = []
                    for err in spelling_errors:
                        error_data.append(
                            {
                                "Hata": err.ruleId if err.ruleId else "Bilinmeyen",
                                "Konum": f"Karakter {err.offset}",
                                "Hatalı Metin": err.context[
                                    err.offsetInContext : err.offsetInContext
                                    + len(err.misspelling)
                                ]
                                if err.misspelling
                                else err.context,
                                "Öneriler": ", ".join(err.replacements[:5])
                                if err.replacements
                                else "Öneri yok",
                                "Açıklama": err.message[:100] if err.message else "",
                            }
                        )

                    error_df = pd.DataFrame(error_data)
                    st.dataframe(error_df, use_container_width=True, hide_index=True)
                else:
                    st.success("Yazım hatası bulunamadı.")

                    if word_count_total >= 500:
                        st.warning(
                            f"**Kusursuzluk Paradoksu:** Metin dilbilgisi açısından kusursuz. "
                            f"Bu kadar uzun bir metinde ({word_count_total} kelime) insani hataların "
                            f"hiç bulunmaması, metnin AI ile üretilmiş olma şüphesini artırabilir. "
                            f"İnsan yazarlar genellikle uzun metinlerde küçük yazım veya dilbilgisi "
                            f"hataları yaparlar."
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
    "Yazım denetimi: language-tool-python | "
    "Analiz: numpy, pandas | Arayüz: Streamlit"
)
