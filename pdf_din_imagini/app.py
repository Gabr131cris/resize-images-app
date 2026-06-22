import streamlit as st
from PIL import Image, ImageOps, ImageEnhance, ImageFilter
from io import BytesIO
from pathlib import Path
from ui_language import tr


def process_scan_effect(img, mode, contrast, sharpness, threshold):
    img = ImageOps.exif_transpose(img).convert("RGB")

    if mode == "Color normal":
        return img

    if mode == "Alb-negru / Grayscale":
        img = ImageOps.grayscale(img)
        img = ImageOps.autocontrast(img)
        img = ImageEnhance.Contrast(img).enhance(contrast)
        img = ImageEnhance.Sharpness(img).enhance(sharpness)
        return img.convert("RGB")

    if mode == "Scan document alb-negru":
        img = ImageOps.grayscale(img)
        img = ImageOps.autocontrast(img)
        img = ImageEnhance.Contrast(img).enhance(contrast)
        img = ImageEnhance.Sharpness(img).enhance(sharpness)
        img = img.point(lambda p: 255 if p > threshold else 0)
        return img.convert("RGB")

    if mode == "Scan document gri":
        img = ImageOps.grayscale(img)
        img = ImageOps.autocontrast(img)
        img = ImageEnhance.Contrast(img).enhance(contrast)
        img = ImageEnhance.Sharpness(img).enhance(sharpness)
        img = img.filter(ImageFilter.SHARPEN)
        return img.convert("RGB")

    return img


def fit_to_page(img, page_size, margin):
    page_w, page_h = page_size
    usable_w = page_w - margin * 2
    usable_h = page_h - margin * 2

    img_copy = img.copy()
    img_copy.thumbnail((usable_w, usable_h), Image.LANCZOS)

    page = Image.new("RGB", (page_w, page_h), "white")
    x = (page_w - img_copy.width) // 2
    y = (page_h - img_copy.height) // 2
    page.paste(img_copy, (x, y))

    return page


def run():
    st.subheader(tr("Images to PDF / Scanner", "PDF din imagini / Scanner"))

    with st.expander(tr("What this app does and how to use it", "Pentru ce se folosește și cum se utilizează"), expanded=False):
        st.markdown(tr("**Use:** Turns images into a PDF and applies useful document-scan effects.", "**Utilizare:** Transformă imagini în PDF și aplică efecte utile pentru documente scanate."))
        st.markdown(tr("**Quick steps:**", "**Pași rapizi:**"))
        st.markdown(tr("1. Upload images in the desired PDF page order.", "1. Încarcă imaginile în ordinea dorită pentru paginile PDF."))
        st.markdown(tr("2. Choose page size, DPI and processing mode.", "2. Alege formatul paginii, DPI-ul și modul de procesare."))
        st.markdown(tr("3. Preview if needed, then download the PDF.", "3. Verifică preview-ul dacă vrei, apoi descarcă PDF-ul."))

    with st.expander("Pentru ce se folosește și cum se utilizează", expanded=False):
        st.markdown("**Utilizare:** Transformă imagini în PDF și aplică efecte utile pentru documente scanate.")
        st.markdown("**Pași rapizi:**")
        st.markdown("1. Încarcă imaginile în ordinea dorită pentru paginile PDF.")
        st.markdown("2. Alege formatul paginii, DPI-ul și modul de procesare.")
        st.markdown("3. Verifică preview-ul dacă vrei, apoi descarcă PDF-ul.")

    files = st.file_uploader(
        tr("Select images", "Selectează imaginile"),
        type=["jpg", "jpeg", "png", "webp"],
        accept_multiple_files=True
    )

    page_preset = st.selectbox(
        tr("PDF page format", "Format pagină PDF"),
        [
            "A4 vertical",
            "A4 landscape",
            "Letter vertical",
            "Păstrează dimensiunea imaginii"
        ]
    )

    dpi = st.selectbox(tr("PDF DPI", "DPI PDF"), [72, 150, 200, 300], index=2)

    scan_mode = st.selectbox(
        tr("Image processing mode", "Mod procesare imagine"),
        [
            "Color normal",
            "Alb-negru / Grayscale",
            "Scan document alb-negru",
            "Scan document gri"
        ]
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        contrast = st.slider(tr("Contrast", "Contrast"), 0.5, 3.0, 1.5, 0.1)

    with col2:
        sharpness = st.slider(tr("Sharpness", "Claritate"), 0.5, 3.0, 1.4, 0.1)

    with col3:
        threshold = st.slider(tr("Black-white threshold", "Prag alb-negru"), 0, 255, 170)

    margin = st.slider(tr("Page margin px", "Margine pagină px"), 0, 200, 40)

    output_name = st.text_input(tr("PDF name", "Nume PDF"), value="document_scanat")

    show_preview = st.checkbox(tr("Show page preview", "Afișează preview pagini"), value=False)

    if not files:
        st.info(tr("Upload images for PDF.", "Încarcă imaginile pentru PDF."))
        return

    page_sizes = {
        "A4 vertical": (int(8.27 * dpi), int(11.69 * dpi)),
        "A4 landscape": (int(11.69 * dpi), int(8.27 * dpi)),
        "Letter vertical": (int(8.5 * dpi), int(11 * dpi)),
    }

    pages = []

    for file in files:
        img = Image.open(file)
        processed = process_scan_effect(
            img,
            scan_mode,
            contrast,
            sharpness,
            threshold
        )

        if page_preset == "Păstrează dimensiunea imaginii":
            page = processed.convert("RGB")
        else:
            page = fit_to_page(
                processed,
                page_sizes[page_preset],
                margin
            )

        pages.append({
            "name": file.name,
            "image": page
        })

    st.divider()

    c1, c2 = st.columns(2)
    c1.metric("Imagini", len(files))
    c2.metric(tr("PDF pages", "Pagini PDF"), len(pages))

    if show_preview:
        with st.expander(tr("PDF page preview", "Preview pagini PDF"), expanded=True):
            for page in pages:
                st.write(page["name"])
                st.image(page["image"], use_container_width=True)

    pdf_buffer = BytesIO()

    first_page = pages[0]["image"]
    other_pages = [p["image"] for p in pages[1:]]

    first_page.save(
        pdf_buffer,
        format="PDF",
        save_all=True,
        append_images=other_pages,
        resolution=dpi
    )

    pdf_buffer.seek(0)

    if not output_name.strip():
        output_name = "document_scanat"

    output_name = Path(output_name).stem + ".pdf"

    st.download_button(
        tr("Download PDF", "Descarcă PDF"),
        data=pdf_buffer,
        file_name=output_name,
        mime="application/pdf"
    )
