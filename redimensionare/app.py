import streamlit as st
from PIL import Image, ImageOps
from io import BytesIO
from zipfile import ZipFile
from pathlib import Path
import re
from ui_language import tr


def clean_filename(text):
    text = text.strip()
    text = re.sub(r'[<>:"/\\|?*]', "_", text)
    text = re.sub(r"\s+", "_", text)
    text = re.sub(r"_+", "_", text)
    return text.strip("_")


def resize_image(img, width=None, height=None, keep_ratio=True):
    img = ImageOps.exif_transpose(img)
    original_width, original_height = img.size

    if keep_ratio:
        if width and not height:
            ratio = width / original_width
            height = int(original_height * ratio)
        elif height and not width:
            ratio = height / original_height
            width = int(original_width * ratio)
        elif width and height:
            new_img = img.copy()
            new_img.thumbnail((width, height), Image.LANCZOS)
            return new_img
        else:
            return img
    else:
        width = width or original_width
        height = height or original_height

    return img.resize((int(width), int(height)), Image.LANCZOS)


def image_to_bytes(img, image_format="JPEG", quality=90, progressive=True):
    buffer = BytesIO()

    if image_format == "JPEG":
        img = img.convert("RGB")
        img.save(
            buffer,
            format="JPEG",
            quality=quality,
            optimize=True,
            progressive=progressive
        )
    elif image_format == "WEBP":
        img.save(
            buffer,
            format="WEBP",
            quality=quality,
            method=6
        )
    else:
        img.save(buffer, format="PNG", optimize=True)

    buffer.seek(0)
    return buffer


def run():
    st.subheader(tr("Resize Images", "Redimensionare imagini"))

    with st.expander(tr("What this app does and how to use it", "Pentru ce se folosește și cum se utilizează"), expanded=False):
        st.markdown(tr("**Use:** Resizes images by width and/or height while keeping proportions when needed.", "**Utilizare:** Redimensionează imagini după lățime și/sau înălțime, cu păstrarea proporțiilor."))
        st.markdown(tr("**Quick steps:**", "**Pași rapizi:**"))
        st.markdown(tr("1. Upload images and set the desired width or height.", "1. Încarcă imaginile și setează lățimea sau înălțimea dorită."))
        st.markdown(tr("2. Choose format, quality and rename options if needed.", "2. Alege formatul, calitatea și redenumirea, dacă ai nevoie."))
        st.markdown(tr("3. Review details and download all images in a ZIP.", "3. Verifică detaliile și descarcă toate imaginile în ZIP."))

    with st.expander("Pentru ce se folosește și cum se utilizează", expanded=False):
        st.markdown("**Utilizare:** Redimensionează imagini după lățime și/sau înălțime, cu păstrarea proporțiilor.")
        st.markdown("**Pași rapizi:**")
        st.markdown("1. Încarcă imaginile și setează lățimea sau înălțimea dorită.")
        st.markdown("2. Alege formatul, calitatea și redenumirea, dacă ai nevoie.")
        st.markdown("3. Verifică detaliile și descarcă toate imaginile în ZIP.")

    col1, col2 = st.columns(2)

    with col1:
        width = st.number_input(tr("New width px", "Lățime nouă px"), min_value=0, value=1000, step=10)

    with col2:
        height = st.number_input(tr("New height px", "Înălțime nouă px"), min_value=0, value=0, step=10)

    keep_ratio = st.checkbox(tr("Keep proportions", "Păstrează proporțiile"), value=True)

    output_format = st.selectbox(tr("Output format", "Format output"), ["JPEG", "PNG", "WEBP"])

    quality = 90
    progressive = True

    if output_format in ["JPEG", "WEBP"]:
        quality = st.slider(tr("Quality", "Calitate"), 1, 100, 90)

    if output_format == "JPEG":
        progressive = st.checkbox(tr("Progressive JPEG", "Progressive JPEG"), value=True)

    show_details = st.checkbox(tr("Show image details", "Afișează detalii imagini"), value=False)

    with st.expander(tr("Optional: rename images on export", "Opțional: redenumește imaginile la export"), expanded=False):
        enable_rename = st.checkbox(tr("Enable renaming", "Activează redenumire"), value=False)
        rename_prefix = st.text_input(tr("Base name", "Nume bază"), value="Imagine")
        rename_start = st.number_input(
            tr("Start numbering from", "Începe numerotarea de la"),
            min_value=1,
            value=1,
            step=1
        )
        rename_separator = st.text_input(tr("Separator", "Separator"), value="-")

    uploaded_files = st.file_uploader(
        tr("Choose one or more images", "Alege una sau mai multe imagini"),
        type=["jpg", "jpeg", "png", "webp"],
        accept_multiple_files=True
    )

    if not uploaded_files:
        st.info(tr("Upload images to start.", "Încarcă imagini ca să începi."))
        return

    if width == 0 and height == 0:
        st.warning(tr("Set at least width or height.", "Setează cel puțin lățimea sau înălțimea."))
        return

    rename_prefix = clean_filename(rename_prefix)
    rename_separator = clean_filename(rename_separator)

    zip_buffer = BytesIO()
    results = []

    total_original_kb = 0
    total_final_kb = 0

    with ZipFile(zip_buffer, "w") as zip_file:
        for i, file in enumerate(uploaded_files, start=int(rename_start)):
            original_bytes = file.getvalue()
            original_size_kb = len(original_bytes) / 1024
            total_original_kb += original_size_kb

            img = Image.open(BytesIO(original_bytes))
            img = ImageOps.exif_transpose(img)

            new_img = resize_image(
                img,
                width=width if width > 0 else None,
                height=height if height > 0 else None,
                keep_ratio=keep_ratio
            )

            img_bytes = image_to_bytes(
                new_img,
                output_format,
                quality,
                progressive
            )

            final_size_kb = len(img_bytes.getvalue()) / 1024
            total_final_kb += final_size_kb

            extension = output_format.lower()

            if enable_rename:
                output_name = f"{rename_prefix}{rename_separator}{i}.{extension}"
            else:
                output_name = file.name.rsplit(".", 1)[0] + f"_redimensionat.{extension}"

            zip_file.writestr(output_name, img_bytes.getvalue())

            reduction = 100 - ((final_size_kb / original_size_kb) * 100)

            results.append({
                "old_name": file.name,
                "new_name": output_name,
                "original_size": original_size_kb,
                "final_size": final_size_kb,
                "reduction": reduction,
                "old_dimensions": img.size,
                "new_dimensions": new_img.size,
                "original_image": img,
                "new_image_bytes": img_bytes.getvalue(),
            })

    zip_buffer.seek(0)

    st.divider()

    total_reduction = 100 - ((total_final_kb / total_original_kb) * 100)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(tr("Files", "Fișiere"), len(uploaded_files))
    c2.metric(tr("Original total", "Total original"), f"{total_original_kb:.1f} KB")
    c3.metric(tr("Final total", "Total final"), f"{total_final_kb:.1f} KB")
    c4.metric("Reducere totală", f"{total_reduction:.1f}%")

    st.divider()

    for item in results:
        if show_details:
            with st.expander(f"{item['old_name']} → {item['new_name']}", expanded=False):
                c1, c2, c3, c4 = st.columns(4)
                c1.metric(
                    "Dimensiuni originale",
                    f"{item['old_dimensions'][0]}×{item['old_dimensions'][1]}"
                )
                c2.metric(
                    "Dimensiuni finale",
                    f"{item['new_dimensions'][0]}×{item['new_dimensions'][1]}"
                )
                c3.metric(tr("Original", "Original"), f"{item['original_size']:.1f} KB")
                c4.metric(tr("Final", "Final"), f"{item['final_size']:.1f} KB")

                col_a, col_b = st.columns(2)

                with col_a:
                    st.caption(tr("Original", "Original"))
                    st.image(item["original_image"], use_container_width=True)

                with col_b:
                    st.caption("Redimensionat")
                    preview_img = Image.open(BytesIO(item["new_image_bytes"]))
                    st.image(preview_img, use_container_width=True)

                st.download_button(
                    tr("Download image", "Descarcă imaginea"),
                    data=item["new_image_bytes"],
                    file_name=item["new_name"],
                    mime=f"image/{output_format.lower()}",
                    key=item["new_name"]
                )
        else:
            st.write(
                f"{item['old_name']} → {item['new_name']} | "
                f"{item['old_dimensions'][0]}×{item['old_dimensions'][1]} → "
                f"{item['new_dimensions'][0]}×{item['new_dimensions'][1]} | "
                f"{item['original_size']:.1f} KB → {item['final_size']:.1f} KB"
            )

    st.divider()

    st.download_button(
        label="Descarcă toate imaginile redimensionate ZIP",
        data=zip_buffer,
        file_name="imagini_redimensionate.zip",
        mime="application/zip"
    )
