import json
import importlib.util
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

BASE_DIR = Path(__file__).parent
APP_URL = "https://resize-images-app.streamlit.app/"
PAGE_TITLE = "Image Tools App - Redimensionare, Compresie, Watermark și SEO Imagini"
META_DESCRIPTION = (
    "Aplicație online gratuită pentru redimensionare imagini, compresie JPG, conversie JPG PNG WEBP, "
    "watermark, redenumire poze, crop thumbnail social media, PDF din imagini și metadata SEO produs."
)
GOOGLE_SITE_VERIFICATIONS = [
    "google43a5607d9f9a5ae6",
    "D58qNq1QiMWQkpfNPLAoCDbbTmM5hb2N70Rm9hW0wMk",
]
META_KEYWORDS = [
    "redimensionare imagini online",
    "compresie jpg online",
    "convertor imagini jpg png webp",
    "watermark imagini",
    "redenumire poze bulk",
    "crop thumbnail social media",
    "pdf din imagini",
    "metadata seo produs",
    "curățare EXIF imagini",
    "optimizare imagini magazin online",
]


def inject_seo_tags():
    keywords = ", ".join(META_KEYWORDS)
    schema = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": "Image Tools App",
        "applicationCategory": "MultimediaApplication",
        "operatingSystem": "Web",
        "url": APP_URL,
        "description": META_DESCRIPTION,
        "inLanguage": "ro-RO",
        "offers": {
            "@type": "Offer",
            "price": "0",
            "priceCurrency": "RON",
        },
        "featureList": [
            "Redimensionare imagini în bulk",
            "Compresie JPG după dimensiune",
            "Conversie imagini JPG, PNG și WEBP",
            "Watermark text sau logo",
            "Redenumire imagini în serie",
            "Crop și thumbnail pentru social media",
            "PDF din imagini și mod scanner",
            "Generator Metadata SEO produs și curățare EXIF",
        ],
    }
    seo_payload = json.dumps({
        "title": PAGE_TITLE,
        "description": META_DESCRIPTION,
        "keywords": keywords,
        "url": APP_URL,
        "schema": schema,
        "googleVerifications": GOOGLE_SITE_VERIFICATIONS,
    })

    components.html(
        f"""
        <script>
        const seo = {seo_payload};
        const doc = window.parent.document;

        function upsertMeta(selector, attributes) {{
            let tag = doc.head.querySelector(selector);
            if (!tag) {{
                tag = doc.createElement('meta');
                doc.head.appendChild(tag);
            }}
            Object.entries(attributes).forEach(([key, value]) => tag.setAttribute(key, value));
        }}

        function upsertLink(selector, attributes) {{
            let tag = doc.head.querySelector(selector);
            if (!tag) {{
                tag = doc.createElement('link');
                doc.head.appendChild(tag);
            }}
            Object.entries(attributes).forEach(([key, value]) => tag.setAttribute(key, value));
        }}

        doc.title = seo.title;
        upsertMeta('meta[name="description"]', {{name: 'description', content: seo.description}});
        upsertMeta('meta[name="keywords"]', {{name: 'keywords', content: seo.keywords}});
        upsertMeta('meta[name="robots"]', {{name: 'robots', content: 'index, follow'}});
        seo.googleVerifications.forEach((token) => {{
            upsertMeta(
                `meta[name="google-site-verification"][content="${token}"]`,
                {{name: 'google-site-verification', content: token}}
            );
        }});
        upsertMeta('meta[property="og:title"]', {{property: 'og:title', content: seo.title}});
        upsertMeta('meta[property="og:description"]', {{property: 'og:description', content: seo.description}});
        upsertMeta('meta[property="og:type"]', {{property: 'og:type', content: 'website'}});
        upsertMeta('meta[property="og:url"]', {{property: 'og:url', content: seo.url}});
        upsertMeta('meta[property="og:locale"]', {{property: 'og:locale', content: 'ro_RO'}});
        upsertMeta('meta[name="twitter:card"]', {{name: 'twitter:card', content: 'summary'}});
        upsertMeta('meta[name="twitter:title"]', {{name: 'twitter:title', content: seo.title}});
        upsertMeta('meta[name="twitter:description"]', {{name: 'twitter:description', content: seo.description}});
        upsertLink('link[rel="canonical"]', {{rel: 'canonical', href: seo.url}});

        let schemaTag = doc.head.querySelector('script[data-image-tools-schema="software-application"]');
        if (!schemaTag) {{
            schemaTag = doc.createElement('script');
            schemaTag.type = 'application/ld+json';
            schemaTag.dataset.imageToolsSchema = 'software-application';
            doc.head.appendChild(schemaTag);
        }}
        schemaTag.textContent = JSON.stringify(seo.schema);
        </script>
        """,
        height=0,
    )


def show_seo_intro():
    st.caption(
        "Instrumente gratuite pentru imagini: redimensionare, compresie JPG, convertor JPG/PNG/WEBP, "
        "watermark, rename bulk, thumbnail social media, PDF din imagini și SEO pentru produse."
    )

    with st.expander("Ce poți face cu Image Tools App", expanded=False):
        st.markdown(
            """
            - Redimensionezi și comprimi imagini pentru site, magazin online sau social media.
            - Convertești poze între JPG, PNG și WEBP.
            - Aplici watermark text sau logo pe imagini în bulk.
            - Redenumești pozele SEO-friendly cu separator `-`.
            - Creezi thumbnail-uri pentru Instagram, TikTok, Facebook, Marketplace și YouTube.
            - Transformi imagini în PDF și poți simula un mod scanner.
            - Generezi metadata SEO pentru produse și cureți EXIF/metadata din imagini.
            """
        )


st.set_page_config(page_title=PAGE_TITLE, page_icon="🖼️", layout="wide")
inject_seo_tags()
st.title("Image Tools App")
show_seo_intro()

apps = []

for folder in BASE_DIR.iterdir():
    if folder.is_dir() and (folder / "app.py").exists():
        apps.append(folder)

apps = sorted(apps, key=lambda x: x.name.lower())

if not apps:
    st.warning("Nu există aplicații. Creează un folder cu fișier app.py în el.")
    st.stop()

app_names = [folder.name.replace("_", " ").title() for folder in apps]

selected_name = st.sidebar.radio("Alege aplicația", app_names)
selected_folder = apps[app_names.index(selected_name)]

st.header(selected_name)

app_file = selected_folder / "app.py"

spec = importlib.util.spec_from_file_location("selected_app", app_file)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

if hasattr(module, "run"):
    module.run()
else:
    st.error(f"Fișierul {app_file} trebuie să aibă o funcție run().")
