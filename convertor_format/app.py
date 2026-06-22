import streamlit as st
from PIL import Image, ImageOps
from io import BytesIO
from zipfile import ZipFile
from pathlib import Path
import re
from ui_language import tr


def clean_filename_part(text):
    text = text.strip()
    text = re.sub(r'[<>:"/\\|?*]', "_", text)
    text = re.sub(r"\s+", "_", text)
    text = re.sub(r"_+", "_", text)
    return text.strip("_")


def clean_separator(text):
    text = text.strip()
    if text == "":
        return ""
    text = re.sub(r'[<>:"/\\|?*]', "_", text)
    text = re.sub(r"\s+", "_", text)
    return text


def convert_image(img, output_format, quality=90, progressive=True):
    buffer = BytesIO()
    img = ImageOps.exif_transpose(img)

    if output_format in ["JPG", "JPEG"]:
        img = img.convert("RGB")
        img.save(
            buffer,
            format="JPEG",
            quality=quality,
            optimize=True,
            progressive=progressive
        )
        extension = "jpg"

    elif output_format == "WEBP":
        img.save(
            buffer,
            format="WEBP",
            quality=quality,
            method=6
        )
        extension = "webp"

    elif output_format == "PNG":
        img.save(
            buffer,
            format="PNG",
            optimize=True
        )
        extension = "png"

    buffer.seek(0)
    return buffer, extension


def run():
    st.subheader(tr("Image Format Converter", "Convertor format imagini"))

    with st.expander(tr("What this app does and how to use it", "Pentru ce se folosește și cum se utilizează"), expanded=False):
        st.markdown(tr("**Use:** Converts images between JPG, PNG and WEBP, including bulk conversion.", "**Utilizare:** Schimbă formatul imaginilor între JPG, PNG și WEBP, inclusiv pentru mai multe imagini odată."))
        st.markdown(tr("**Quick steps:**", "**Pași rapizi:**"))
        st.markdown(tr("1. Upload the images you want to convert.", "1. Încarcă imaginile pe care vrei să le convertești."))
        st.markdown(tr("2. Choose the output format and quality when available.", "2. Alege formatul final și calitatea, dacă este cazul."))
        st.markdown(tr("3. Download all converted images in a ZIP.", "3. Descarcă toate imaginile convertite într-un ZIP."))

    files = st.file_uploader(
        tr("Select images", "Selectează imaginile"),
        type=["jpg", "jpeg", "png", "webp"],
        accept_multiple_files=True
    )

    col1, col2 = st.columns(2)

    with col1:
        output_format = st.selectbox(
            tr("Output format", "Format output"),
            ["JPG", "PNG", "WEBP"]
        )

    with col2:
        keep_original_name = st.checkbox(
            tr("Keep original name", "Păstrează numele original"),
            value=True
        )

    quality = 90
    progressive = True

    if output_format in ["JPG", "WEBP"]:
        quality = st.slider(tr("Quality", "Calitate"), 1, 100, 90)

    if output_format == "JPG":
        progressive = st.checkbox(tr("Progressive JPG", "Progressive JPG"), value=True)

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

    show_details = st.checkbox(tr("Show image details", "Afișează detalii imagini"), value=False)

    if not files:
        st.info(tr("Upload images for conversion.", "Încarcă imaginile pentru conversie."))
        return

    rename_prefix = clean_filename_part(rename_prefix)
    rename_separator = clean_separator(rename_separator)

    if enable_rename and not rename_prefix:
        st.error(tr("Base name cannot be empty.", "Numele bază nu poate fi gol."))
        return

    zip_buffer = BytesIO()
    results = []

    total_original_kb = 0
    total_final_kb = 0

    with ZipFile(zip_buffer, "w") as zip_file:
        for i, file in enumerate(files, start=int(rename_start)):
            original_bytes = file.getvalue()
            original_size_kb = len(original_bytes) / 1024
            total_original_kb += original_size_kb

            img = Image.open(BytesIO(original_bytes))

            converted, extension = convert_image(
                img,
                output_format,
                quality,
                progressive
            )

            final_bytes = converted.getvalue()
            final_size_kb = len(final_bytes) / 1024
            total_final_kb += final_size_kb

            if enable_rename:
                output_name = f"{rename_prefix}{rename_separator}{i}.{extension}"
            elif keep_original_name:
                output_name = f"{Path(file.name).stem}.{extension}"
            else:
                output_name = f"{Path(file.name).stem}_convertit.{extension}"

            zip_file.writestr(output_name, final_bytes)

            reduction = 100 - ((final_size_kb / original_size_kb) * 100)

            results.append({
                "old_name": file.name,
                "new_name": output_name,
                "original_size": original_size_kb,
                "final_size": final_size_kb,
                "reduction": reduction,
                "old_format": Path(file.name).suffix.lower().replace(".", ""),
                "new_format": extension,
                "image": ImageOps.exif_transpose(img),
                "converted_bytes": final_bytes
            })

    zip_buffer.seek(0)

    st.divider()

    total_reduction = 100 - ((total_final_kb / total_original_kb) * 100)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(tr("Files", "Fișiere"), len(files))
    c2.metric(tr("Original total", "Total original"), f"{total_original_kb:.1f} KB")
    c3.metric(tr("Final total", "Total final"), f"{total_final_kb:.1f} KB")
    c4.metric("Diferență", f"{total_reduction:.1f}%")

    st.divider()

    for item in results:
        if show_details:
            with st.expander(f"{item['old_name']} → {item['new_name']}", expanded=False):
                c1, c2, c3, c4 = st.columns(4)
                c1.metric(tr("Original format", "Format original"), item["old_format"].upper())
                c2.metric(tr("Final format", "Format final"), item["new_format"].upper())
                c3.metric(tr("Original", "Original"), f"{item['original_size']:.1f} KB")
                c4.metric(tr("Final", "Final"), f"{item['final_size']:.1f} KB")

                st.image(item["image"], use_container_width=True)

                st.download_button(
                    tr("Download image", "Descarcă imaginea"),
                    data=item["converted_bytes"],
                    file_name=item["new_name"],
                    mime=f"image/{item['new_format']}",
                    key=item["new_name"]
                )
        else:
            st.write(
                f"{item['old_name']} → {item['new_name']} | "
                f"{item['old_format'].upper()} → {item['new_format'].upper()} | "
                f"{item['original_size']:.1f} KB → {item['final_size']:.1f} KB"
            )

    st.divider()

    st.download_button(
        tr("Download all converted images ZIP", "Descarcă toate imaginile convertite ZIP"),
        data=zip_buffer,
        file_name="imagini_convertite.zip",
        mime="application/zip"
    )
