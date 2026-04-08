---
title: İçerik Kalitesi ve Özgünlük Analizi
emoji: 🧠
colorFrom: indigo
colorTo: purple
sdk: docker
python_version: "3.11"
app_file: streamlit_app.py
app_port: 8501
pinned: false
license: mit
---

# İçerik Kalitesi ve Özgünlük Analizi

Bir web sitesi URL'si girin. Uygulama sayfadaki ana metni çıkarıp yapay zekâ sinyalleri, tekrar örüntüleri, anlamsal benzerlik ve genel özgünlük yapısını Türkçe Streamlit arayüzünde analiz etsin.

## Özellikler

- **URL tabanlı analiz**: `trafilatura` ile ana metni backend tarafında çıkarır
- **Yapay zeka sinyalleri**: klişe ifade, tipografik karakter, pasif yapı, liste ve başlık yoğunluğu
- **Tekrar analizi**: kelime bazlı tekrar, anlamsal tekrar ve trigram tekrarları
- **İçerik kalitesi**: TTR, burstiness, yapı skoru, sözcük zenginliği ve analiz güveni
- **Profesyonel arayüz**: skor kartları, tablolar, grafikler, kısa özet ve tam metin görünümü
- **TXT rapor indirme**: analiz sonucunu dışa aktarır

## Çalıştırma

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Deploy

Streamlit Community Cloud için ana dosya:

```text
streamlit_app.py
```

Hugging Face Spaces üzerinde ise uygulama Docker içinde Streamlit olarak çalıştırılır.
