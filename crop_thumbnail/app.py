import streamlit as st
from PIL import Image, ImageOps
from io import BytesIO
from zipfile import ZipFile
from pathlib import Path
import re


PRESETS = {
    "Instagram Post 1:1 - 1080x1080": (1080, 1080),
    "Instagram Portrait 4:5 - 1080x1350": (1080, 1350),
    "Instagram Story/Reels 9:16 - 1080x1920": (1080, 1920),
    "TikTok 9:16 - 1080x1920": (1080, 1920),
    "Facebook Post 1:1 - 1200x1200": (1200, 1200),
    "Facebook Cover - 1640x924": (1640, 924),
    "Marketplace 1:1 - 1200x1200": (1200, 1200),
    "YouTube Thumbnail 16:9 - 1280x720": (1280, 720),
    "Thumbnail mic - 300x300": (300, 300),
    "Thumbnail mediu - 600x600": (600, 600),
    "Thumbnail mare - 1200x1200": (1200, 1200),
    "Custom": None,
}


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


def crop_position_to_anchor(position):
    anchors = {
        "Centru": (0.5, 0.5),
        "Sus": (0.5, 0.0),
        "Jos": (0.5, 1.0),
        "Stânga": (0.0, 0.5),
        "Dreapta": (1.0, 0.5),
        "Stânga sus": (0.0, 0.0),
        "Dreapta sus": (1.0, 0.0),
        "Stânga jos": (0.0, 1.0),
        "Dreapta jos": (1.0, 1.0),
    }
    return anchors.get(position, (0.5, 0.5))


def process_image(img, width, height, mode, position, bg_color):
    img = ImageOps.exif_transpose(img).convert("RGB")

    if mode == "Crop / umple formatul":
        return ImageOps.fit(
            img,
            (width, height),
            method=Image.LANCZOS,
            centering=crop_position_to_anchor(position)
        )

    resized = img.copy()
    resized.thumbnail((width, height), Image.LANCZOS)

    canvas = Image.new("RGB", (width, height), bg_color)
    x = (width - resized.width) // 2
    y = (height - resized.height) // 2
    canvas.paste(resized, (x, y))

    return canvas


def save_image(img, output_format, quality, progressive):
    buffer = BytesIO()

    if output_format == "JPG":
        img.save(
            buffer,
            format="JPEG",
            quality=quality,
            optimize=True,
            progressive=progressive
        )
        ext = "jpg"
        mime = "image/jpeg"

    elif output_format == "WEBP":
        img.save(
            buffer,
            format="WEBP",
            quality=quality,
            method=6
        )
        ext = "webp"
        mime = "image/webp"

    else:
        img.save(buffer, format="PNG", optimize=True)
        ext = "png"
        mime = "image/png"

    buffer.seek(0)
    return buffer, ext, mime


def run():
    st.subheader("Crop / Social Media / Thumbnail Generator")

    with st.expander("Pentru ce se folosește și cum se utilizează", expanded=False):
        st.markdown("**Utilizare:** Pregătește imagini pentru social media, marketplace sau thumbnail-uri folosind dimensiuni presetate.")
        st.markdown("**Pași rapizi:**")
        st.markdown("1. Încarcă imaginile și alege presetul dorit.")
        st.markdown("2. Alege crop complet sau fit cu fundal.")
        st.markdown("3. Verifică preview-ul și descarcă ZIP-ul final.")

    files = st.file_uploader(
        "Selectează imaginile",
        type=["jpg", "jpeg", "png", "webp"],
        accept_multiple_files=True
    )

    preset = st.selectbox("Preset mărime", list(PRESETS.keys()))

    if preset == "Custom":
        col1, col2 = st.columns(2)
        with col1:
            width = st.number_input("Lățime px", min_value=1, value=1080, step=10)
        with col2:
            height = st.number_input("Înălțime px", min_value=1, value=1080, step=10)
    else:
        width, height = PRESETS[preset]
        st.info(f"Mărime selectată: {width}x{height}px")

    mode = st.radio(
        "Mod procesare",
        ["Crop / umple formatul", "Fit / păstrează toată imaginea"],
        horizontal=True
    )

    position = "Centru"
    bg_color = "#FFFFFF"

    if mode == "Crop / umple formatul":
        position = st.selectbox(
            "Zona importantă a imaginii",
            [
                "Centru",
                "Sus",
                "Jos",
                "Stânga",
                "Dreapta",
                "Stânga sus",
                "Dreapta sus",
                "Stânga jos",
                "Dreapta jos",
            ]
        )
    else:
        bg_color = st.color_picker("Culoare fundal pentru spațiile libere", "#FFFFFF")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        output_format = st.selectbox("Format output", ["JPG", "PNG", "WEBP"])

    with col2:
        show_details = st.checkbox("Afișează detalii imagini", value=False)

    quality = 90
    progressive = True

    if output_format in ["JPG", "WEBP"]:
        quality = st.slider("Calitate export", 1, 100, 90)

    if output_format == "JPG":
        progressive = st.checkbox("Progressive JPG", value=True)

    with st.expander("Opțional: redenumește imaginile la export", expanded=False):
        enable_rename = st.checkbox("Activează redenumire", value=False)
        rename_prefix = st.text_input("Nume bază", value="Imagine")
        rename_start = st.number_input(
            "Începe numerotarea de la",
            min_value=1,
            value=1,
            step=1
        )
        rename_separator = st.text_input("Separator", value="-")

    if not files:
        st.info("Încarcă imaginile pentru crop / thumbnail.")
        return

    rename_prefix = clean_filename_part(rename_prefix)
    rename_separator = clean_separator(rename_separator)

    if enable_rename and not rename_prefix:
        st.error("Numele bază nu poate fi gol.")
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
            original_dimensions = img.size

            final_img = process_image(
                img=img,
                width=int(width),
                height=int(height),
                mode=mode,
                position=position,
                bg_color=bg_color
            )

            final_buffer, ext, mime = save_image(
                final_img,
                output_format,
                quality,
                progressive
            )

            final_bytes = final_buffer.getvalue()
            final_size_kb = len(final_bytes) / 1024
            total_final_kb += final_size_kb

            if enable_rename:
                output_name = f"{rename_prefix}{rename_separator}{i}.{ext}"
            else:
                output_name = f"{Path(file.name).stem}_{width}x{height}.{ext}"

            zip_file.writestr(output_name, final_bytes)

            results.append({
                "old_name": file.name,
                "new_name": output_name,
                "original_size": original_size_kb,
                "final_size": final_size_kb,
                "original_dimensions": original_dimensions,
                "final_dimensions": final_img.size,
                "final_bytes": final_bytes,
                "mime": mime
            })

    zip_buffer.seek(0)

    st.divider()

    diff = 100 - ((total_final_kb / total_original_kb) * 100)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Fișiere", len(files))
    c2.metric("Total original", f"{total_original_kb:.1f} KB")
    c3.metric("Total final", f"{total_final_kb:.1f} KB")
    c4.metric("Diferență", f"{diff:.1f}%")

    st.divider()

    for item in results:
        if show_details:
            with st.expander(f"{item['old_name']} → {item['new_name']}", expanded=False):
                c1, c2, c3, c4 = st.columns(4)
                c1.metric(
                    "Original",
                    f"{item['original_dimensions'][0]}×{item['original_dimensions'][1]}"
                )
                c2.metric(
                    "Final",
                    f"{item['final_dimensions'][0]}×{item['final_dimensions'][1]}"
                )
                c3.metric("Size original", f"{item['original_size']:.1f} KB")
                c4.metric("Size final", f"{item['final_size']:.1f} KB")

                preview_img = Image.open(BytesIO(item["final_bytes"]))
                st.image(preview_img, use_container_width=True)

                st.download_button(
                    "Descarcă imaginea",
                    data=item["final_bytes"],
                    file_name=item["new_name"],
                    mime=item["mime"],
                    key=item["new_name"]
                )
        else:
            st.write(
                f"{item['old_name']} → {item['new_name']} | "
                f"{item['original_dimensions'][0]}×{item['original_dimensions'][1]} → "
                f"{item['final_dimensions'][0]}×{item['final_dimensions'][1]} | "
                f"{item['original_size']:.1f} KB → {item['final_size']:.1f} KB"
            )

    st.divider()

    st.download_button(
        "Descarcă toate imaginile ZIP",
        data=zip_buffer,
        file_name="imagini_crop_thumbnail.zip",
        mime="application/zip"
    )