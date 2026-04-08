---
title: Metin Diligence Analizörü
emoji: 🧠
colorFrom: indigo
colorTo: purple
sdk: streamlit
sdk_version: "1.40.2"
app_file: streamlit_app.py
pinned: false
license: mit
---

# Metin Diligence Analizörü

Bir web sitesi URL'si girin. Uygulama sayfadaki ana metni çıkarıp yapay zeka sinyalleri, tekrar örüntüleri, anlamsal benzerlik ve genel özgünlük yapısını Streamlit arayüzünde analiz etsin.

## Özellikler

- **URL tabanlı analiz**: `trafilatura` ile ana metni backend tarafında çıkarır
- **Yapay zeka sinyalleri**: klişe ifade, tipografik karakter, pasif yapı, liste ve başlık yoğunluğu
- **Tekrar analizi**: kelime bazlı tekrar, anlamsal tekrar ve trigram tekrarları
- **İçerik kalitesi**: TTR, burstiness, yapı skoru, lexical richness ve analiz güveni
- **Profesyonel arayüz**: skor kartları, tablolar, grafikler, kısa özet ve tam metin görünümü
- **TXT rapor indirme**: analiz sonucunu dışa aktarır

## Çalıştırma

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Deploy

Streamlit Community Cloud veya Hugging Face Spaces için ana dosya:

```text
streamlit_app.py
```

Bu repo artık sadece Streamlit sürümünü içerir.
