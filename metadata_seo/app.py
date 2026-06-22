import csv
import re
from io import BytesIO, StringIO
from pathlib import Path
from zipfile import ZipFile

import streamlit as st
from PIL import Image, ImageOps
from ui_language import tr


STOP_WORDS = {
    "si", "și", "cu", "de", "din", "la", "in", "în", "pe", "pentru", "sau",
    "un", "o", "al", "a", "ale", "ai", "este", "sunt", "prin", "blat"
}

DEFAULT_BENEFITS = [
    "design modern",
    "aspect elegant",
    "calitate premium",
    "potrivit pentru locuințe și spații HoReCa",
]


def clean_text(text):
    text = re.sub(r"\s+", " ", text or "").strip()
    return text


def clean_filename_part(text):
    text = clean_text(text).lower()
    replacements = {
        "ă": "a", "â": "a", "î": "i", "ș": "s", "ş": "s", "ț": "t", "ţ": "t",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-") or "imagine-produs"


def split_product_terms(product_title):
    words = re.findall(r"[\wăâîșşțţ]+", product_title.lower())
    terms = []
    for word in words:
        if len(word) < 3 or word in STOP_WORDS:
            continue
        if word not in terms:
            terms.append(word)
    return terms


def build_meta_title(product_title, suffix):
    product_title = clean_text(product_title)
    suffix = clean_text(suffix)
    if suffix and suffix.lower() not in product_title.lower():
        title = f"{product_title} – {suffix}"
    else:
        title = product_title
    return title[:70].rstrip(" –,-")


def build_meta_description(product_title, benefits, call_to_action):
    product_title = clean_text(product_title)
    benefits = [clean_text(item) for item in benefits if clean_text(item)]
    call_to_action = clean_text(call_to_action)

    if benefits:
        benefit_text = ", ".join(benefits[:3])
        description = f"{product_title} cu {benefit_text}. {call_to_action}"
    else:
        description = f"{product_title}. {call_to_action}"

    return description[:160].rstrip(" ,.-") + ("." if not description[:160].rstrip().endswith((".", "!", "?")) else "")


def build_keywords(product_title, category, extra_keywords):
    product_title = clean_text(product_title)
    category = clean_text(category)
    base_terms = split_product_terms(product_title)

    keywords = []
    candidates = [
        product_title.lower(),
        category.lower(),
        f"{category} {product_title}".lower() if category else "",
    ]

    for term in base_terms:
        candidates.extend([
            term,
            f"{category} {term}".strip().lower(),
        ])

    candidates.extend([item.strip().lower() for item in extra_keywords.split(",")])

    for candidate in candidates:
        candidate = clean_text(candidate)
        if candidate and candidate not in keywords:
            keywords.append(candidate)

    return ", ".join(keywords[:18])


def build_product_tags(product_title, category, extra_tags):
    tags = []
    candidates = [category, product_title]
    candidates.extend(split_product_terms(product_title))
    candidates.extend(extra_tags.split(","))

    for candidate in candidates:
        candidate = clean_text(candidate).lower()
        if candidate and candidate not in tags:
            tags.append(candidate)

    return ", ".join(tags[:16])


def generate_metadata(product_title, category, title_suffix, benefits, call_to_action, extra_keywords, extra_tags):
    return {
        "meta_title": build_meta_title(product_title, title_suffix),
        "meta_description": build_meta_description(product_title, benefits, call_to_action),
        "meta_keywords": build_keywords(product_title, category, extra_keywords),
        "product_tags": build_product_tags(product_title, category, extra_tags),
    }


def remove_image_metadata(image_file, output_format, quality):
    original_name = Path(image_file.name)
    img = Image.open(image_file)
    img = ImageOps.exif_transpose(img)

    buffer = BytesIO()
    if output_format == tr("Keep original format", "Păstrează formatul original"):
        suffix = original_name.suffix.lower().replace(".", "")
        output_format = "JPEG" if suffix in ["jpg", "jpeg"] else suffix.upper()
    elif output_format == "JPG":
        output_format = "JPEG"

    if output_format in ["JPEG", "WEBP"]:
        img = img.convert("RGB")
        img.save(buffer, format=output_format, quality=quality, optimize=True)
    else:
        img.save(buffer, format="PNG", optimize=True)

    buffer.seek(0)
    extension = "jpg" if output_format == "JPEG" else output_format.lower()
    return buffer.getvalue(), extension


def build_csv(metadata, product_title):
    output = StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=[
            "product_title",
            "meta_title",
            "meta_description",
            "meta_keywords",
            "product_tags",
        ],
    )
    writer.writeheader()
    writer.writerow({"product_title": product_title, **metadata})
    return output.getvalue().encode("utf-8-sig")


def run():
    st.subheader(tr("Product Metadata / SEO + EXIF cleanup", "Metadata / SEO produs + curățare EXIF"))

    with st.expander(tr("What this app does and how to use it", "Pentru ce se folosește și cum se utilizează"), expanded=False):
        st.markdown(tr("**Use:** Generates product SEO fields and can remove EXIF/metadata from images.", "**Utilizare:** Generează câmpuri SEO pentru produse și poate curăța imaginile de EXIF/metadata."))
        st.markdown(tr("**Quick steps:**", "**Pași rapizi:**"))
        st.markdown(tr("1. Enter the product title and fill in category / benefits.", "1. Scrie titlul orientativ al produsului și completează categoria / beneficiile."))
        st.markdown(tr("2. Adjust the generated fields if needed.", "2. Ajustează câmpurile generate dacă este nevoie."))
        st.markdown(tr("3. Download the SEO CSV or the ZIP with metadata-free images.", "3. Descarcă CSV-ul SEO sau ZIP-ul cu imaginile fără metadata."))

    st.info(tr(
        "Meta Title, Meta Description, Keywords and Product Tags are usually used in the store platform / page code, not directly on the image. Here you can generate them quickly and clean EXIF/metadata from images.",
        "Meta Titlu, Meta Descriere, Cuvinte Cheie și Etichete Produs se folosesc de obicei în platforma magazinului / codul paginii, nu direct pe imagine. Aici le poți genera rapid și poți curăța imaginile de EXIF/metadata."
    ))

    product_title = st.text_input(
        tr("Product title / draft title", "Titlu orientativ produs"),
        value="Masă Living Blat Ceramic DTW0801MC Bej",
    )

    col1, col2 = st.columns(2)
    with col1:
        category = st.text_input(tr("Category / product type", "Categorie / tip produs"), value="masă living")
        title_suffix = st.text_input(tr("Meta Title suffix", "Text pentru Meta Titlu"), value="Eleganță și rafinament în design")
    with col2:
        call_to_action = st.text_input(
            tr("Call to action for description", "Call to action pentru descriere"),
            value="Alege rafinamentul modern pentru casa ta!",
        )
        tone = st.selectbox(tr("Text style", "Stil text"), [tr("Commercial", "Comercial"), tr("Short", "Scurt"), tr("Premium", "Premium")])

    default_benefits = DEFAULT_BENEFITS.copy()
    if tone == tr("Short", "Scurt"):
        default_benefits = ["design modern", "ușor de integrat", "aspect elegant"]
    elif tone == tr("Premium", "Premium"):
        default_benefits = ["design rafinat", "finisaj premium", "prezență elegantă"]

    benefits_text = st.text_area(
        tr("Benefits / product details (one per line)", "Beneficii / detalii produs (câte unul pe linie)"),
        value="\n".join(default_benefits),
        height=110,
    )
    benefits = benefits_text.splitlines()

    col3, col4 = st.columns(2)
    with col3:
        extra_keywords = st.text_area(
            tr("Extra keywords, separated by comma", "Cuvinte cheie extra, separate prin virgulă"),
            value="mobilier dining elegant, masă design modern, masă ceramică bej",
            height=90,
        )
    with col4:
        extra_tags = st.text_area(
            tr("Extra tags, separated by comma", "Etichete extra, separate prin virgulă"),
            value="mobilier modern, masă ceramică, masă bej, horeca",
            height=90,
        )

    if not clean_text(product_title):
        st.error(tr("Product title cannot be empty.", "Titlul produsului nu poate fi gol."))
        return

    metadata = generate_metadata(
        product_title=product_title,
        category=category,
        title_suffix=title_suffix,
        benefits=benefits,
        call_to_action=call_to_action,
        extra_keywords=extra_keywords,
        extra_tags=extra_tags,
    )

    st.divider()
    st.markdown(tr("### Generated fields", "### Câmpuri generate"))

    meta_title = st.text_area(tr("Meta Title", "Meta Titlu"), value=metadata["meta_title"], height=80)
    meta_description = st.text_area(tr("Meta Tag Description", "Meta Tag Descriere"), value=metadata["meta_description"], height=120)
    meta_keywords = st.text_area(tr("Meta Tag Keywords", "Meta Tag Cuvinte Cheie"), value=metadata["meta_keywords"], height=120)
    product_tags = st.text_area(tr("Product Tags", "Etichete Produs"), value=metadata["product_tags"], height=100)

    final_metadata = {
        "meta_title": meta_title,
        "meta_description": meta_description,
        "meta_keywords": meta_keywords,
        "product_tags": product_tags,
    }

    csv_bytes = build_csv(final_metadata, clean_text(product_title))
    st.download_button(
        tr("Download SEO CSV", "Descarcă SEO CSV"),
        data=csv_bytes,
        file_name=f"seo_{clean_filename_part(product_title)}.csv",
        mime="text/csv",
    )

    st.divider()
    st.markdown(tr("### Optional: remove metadata / EXIF from images", "### Opțional: elimină metadata / EXIF din imagini"))

    files = st.file_uploader(
        tr("Select images for EXIF cleanup", "Selectează imaginile pentru curățare EXIF"),
        type=["jpg", "jpeg", "png", "webp"],
        accept_multiple_files=True,
    )

    col5, col6, col7 = st.columns(3)
    with col5:
        output_format = st.selectbox(tr("Cleaned image format", "Format imagine curățată"), [tr("Keep original format", "Păstrează formatul original"), "JPG", "PNG", "WEBP"])
    with col6:
        quality = st.slider(tr("JPG/WEBP quality", "Calitate JPG/WEBP"), 1, 100, 90)
    with col7:
        rename_images = st.checkbox(tr("SEO rename images", "Redenumește SEO imaginile"), value=True)

    if not files:
        st.info(tr("Upload images only if you want to remove EXIF/metadata.", "Încarcă imagini doar dacă vrei să elimini EXIF/metadata."))
        return

    zip_buffer = BytesIO()
    base_name = clean_filename_part(product_title)

    with ZipFile(zip_buffer, "w") as zip_file:
        zip_file.writestr(f"seo_{base_name}.csv", csv_bytes)
        for index, file in enumerate(files, start=1):
            cleaned_bytes, extension = remove_image_metadata(file, output_format, quality)
            if rename_images:
                output_name = f"{base_name}-{index}.{extension}"
            else:
                output_name = f"{Path(file.name).stem}_fara_metadata.{extension}"
            zip_file.writestr(output_name, cleaned_bytes)

    zip_buffer.seek(0)

    st.success(tr(f"Prepared {len(files)} images without EXIF/metadata and the SEO CSV file.", f"Am pregătit {len(files)} imagini fără EXIF/metadata și fișierul CSV SEO."))
    st.download_button(
        tr("Download ZIP with clean images + SEO CSV", "Descarcă ZIP imagini curate + SEO CSV"),
        data=zip_buffer,
        file_name=f"imagini_seo_{base_name}.zip",
        mime="application/zip",
    )
