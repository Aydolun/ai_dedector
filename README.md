---
title: AI Site Dedektifi
emoji: 🔍
colorFrom: indigo
colorTo: purple
sdk: streamlit
sdk_version: "1.40.2"
app_file: app.py
pinned: false
license: mit
---

# AI Site Dedektifi

Bir web sitesi URL'si girin, uygulama metni otomatik olarak çekip yapay zeka tarafından üretilmiş olma ihtimalini analiz etsin.

## Özellikler

- **Web Scraping**: trafilatura ile temiz metin çıkarma
- **Markdown Tespiti**: Kalın, başlık, kod bloğu gibi ham kopyalama izleri
- **AI Klişeleri**: Türkçe AI kalıplarının frekans analizi
- **Burstiness Analizi**: Cümle uzunluk çeşitliliği (robotik vs insansı)
- **Kelime Frekansı**: En çok tekrar eden kelimeler
- **Yazım Denetimi**: language-tool-python ile Türkçe yazım kontrolü

## Kurulum

```bash
pip install -r requirements.txt
streamlit run app.py
```
