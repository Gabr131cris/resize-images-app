# 🖼️ Image Tools App

Aplicație web/locală dezvoltată în **Python + Streamlit** pentru procesarea rapidă a imaginilor în bulk.

### 🌐 Demo Online

Poți testa aplicația aici:

**https://resize-images-app.streamlit.app/**

---

## 🚀 Funcții disponibile

### 📦 Compresie imagini

* Compresie JPG sub o dimensiune aleasă (ex: 300 KB)
* Păstrarea rezoluției originale
* Export bulk

### 📐 Redimensionare imagini

* Redimensionare după lățime și/sau înălțime
* Păstrarea proporțiilor
* Export JPG, PNG sau WEBP

### 📝 Rename imagini

* Redenumire în serie
* Numerotare automată
* Prefix personalizat
* Separator personalizat

### 🔄 Convertor formate

* JPG → PNG
* PNG → JPG
* WEBP → JPG
* WEBP → PNG
* Conversie bulk

### 🏷️ Watermark

* Watermark text
* Watermark logo
* Poziționare personalizată
* Control dimensiune, culoare și transparență
* Procesare bulk

### 📱 Social Media / Thumbnail Generator

Preset-uri pentru:

* Instagram Post (1:1)
* Instagram Portrait (4:5)
* Instagram Story (9:16)
* Instagram Reels
* TikTok
* Facebook Post
* Facebook Cover
* Marketplace
* YouTube Thumbnail
* Thumbnail 300px
* Thumbnail 600px
* Thumbnail 1200px
* Dimensiuni personalizate


### 🧾 Metadata / SEO produs

* Generare Meta Titlu, Meta Tag Descriere, Meta Tag Cuvinte Cheie și Etichete Produs
* Export CSV pentru copiere/import în magazin online
* Curățare EXIF/metadata din imagini
* Redenumire SEO automată pentru imaginile de produs

### 📄 PDF din imagini

* Conversie imagini în PDF
* Mod scanner document
* Alb-negru
* Grayscale
* Îmbunătățire contrast
* Îmbunătățire claritate

### 📦 Procesare Bulk

Toate uneltele permit procesarea simultană a mai multor imagini și exportarea rezultatelor într-un singur fișier ZIP sau PDF.

---

# 🔎 SEO aplicație

Aplicația include optimizări SEO pentru versiunea online:

* titlu de pagină optimizat pentru redimensionare, compresie, watermark și SEO imagini;
* meta description și meta keywords pentru funcțiile principale;
* canonical URL pentru demo-ul online;
* Open Graph și Twitter Card pentru distribuire pe social media;
* structured data `SoftwareApplication` cu lista funcțiilor aplicației;
* text introductiv vizibil în aplicație pentru motoarele de căutare;
* `robots.txt` și `sitemap.xml` în folderul `static/`.

## Verificare Google Search Console

Pentru Streamlit, fișierele din `static/` sunt servite la URL-uri de forma `/app/static/nume-fisier`, nu direct din rădăcina domeniului. De aceea, pentru verificarea Google este recomandată metoda **HTML tag**, iar aplicația include deja meta tag-ul `google-site-verification` în `<head>`. Fișierul HTML de verificare este păstrat și în repository ca fallback/documentație.


---

# 📂 Structura proiectului

```text
app/
├── google43a5607d9f9a5ae6.html
├── main.py
├── requirements.txt
├── .streamlit/
│   └── config.toml
├── static/
│   ├── google43a5607d9f9a5ae6.html
│   ├── robots.txt
│   └── sitemap.xml
│
├── compresie_jpg/
│   └── app.py
│
├── redimensionare/
│   └── app.py
│
├── rename/
│   └── app.py
│
├── convertor_format/
│   └── app.py
│
├── watermark/
│   └── app.py
│
├── crop_thumbnail/
│   └── app.py
│
├── metadata_seo/
│   └── app.py
│
└── pdf_din_imagini/
    └── app.py
```

---

# 💻 Instalare locală

Este necesar Python 3.10+.

## Instalare dependințe

```bash
pip install -r requirements.txt
```

sau

```bash
python -m pip install -r requirements.txt
```

---

# ▶️ Pornire aplicație

Din folderul proiectului:

```bash
streamlit run main.py
```

sau

```bash
python -m streamlit run main.py
```

Aplicația va porni local în browser.

---

# 📋 requirements.txt

```txt
streamlit
pillow
```

---

# ➕ Cum adaugi o aplicație nouă

Creează un folder nou:

```text
nume_aplicatie/
└── app.py
```

În fișierul `app.py` trebuie să existe funcția:

```python
def run():
    pass
```

Aplicația principală detectează automat toate folderele care conțin un fișier `app.py` și le adaugă în meniu fără modificări suplimentare.

---

# ☁️ Deploy Online

Aplicația poate fi hostată gratuit folosind Streamlit Community Cloud.

Pași:

1. Urcă proiectul pe GitHub
2. Conectează repository-ul la Streamlit Cloud
3. Selectează `main.py`
4. Deploy

Orice modificare trimisă pe GitHub este actualizată automat în versiunea online.

---

# ⚠️ Observații

* Pentru procesarea unui număr foarte mare de imagini este recomandată rularea locală.
* Platformele gratuite de hosting pot avea limitări de memorie și timp de execuție.
* Pentru mii de imagini este recomandată utilizarea aplicației pe propriul calculator.

---

# 📜 Licență

Acest proiect este oferit în scop educațional și poate fi modificat sau extins după necesități.
