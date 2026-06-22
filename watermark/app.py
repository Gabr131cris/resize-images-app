import streamlit as st
from PIL import Image, ImageOps, ImageDraw, ImageFont
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


def hex_to_rgba(hex_color, opacity):
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    a = int(255 * (opacity / 100))
    return (r, g, b, a)


def get_position(base_size, wm_size, position, margin_x, margin_y):
    bw, bh = base_size
    ww, wh = wm_size

    positions = {
        "Stânga sus": (margin_x, margin_y),
        "Centru sus": ((bw - ww) // 2, margin_y),
        "Dreapta sus": (bw - ww - margin_x, margin_y),
        "Stânga centru": (margin_x, (bh - wh) // 2),
        "Centru": ((bw - ww) // 2, (bh - wh) // 2),
        "Dreapta centru": (bw - ww - margin_x, (bh - wh) // 2),
        "Stânga jos": (margin_x, bh - wh - margin_y),
        "Centru jos": ((bw - ww) // 2, bh - wh - margin_y),
        "Dreapta jos": (bw - ww - margin_x, bh - wh - margin_y),
    }

    return positions.get(position, (margin_x, margin_y))


def create_text_watermark(text, font_size, color, opacity, padding, bg_enabled, bg_color, bg_opacity):
    font = ImageFont.truetype("arial.ttf", font_size) if Path("C:/Windows/Fonts/arial.ttf").exists() else ImageFont.load_default()

    temp = Image.new("RGBA", (10, 10), (0, 0, 0, 0))
    draw = ImageDraw.Draw(temp)
    bbox = draw.textbbox((0, 0), text, font=font)

    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    wm_w = text_w + padding * 2
    wm_h = text_h + padding * 2

    watermark = Image.new("RGBA", (wm_w, wm_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(watermark)

    if bg_enabled:
        draw.rounded_rectangle(
            (0, 0, wm_w, wm_h),
            radius=8,
            fill=hex_to_rgba(bg_color, bg_opacity)
        )

    draw.text(
        (padding, padding - bbox[1]),
        text,
        font=font,
        fill=hex_to_rgba(color, opacity)
    )

    return watermark


def prepare_logo_watermark(logo_file, width_percent, opacity):
    logo = Image.open(logo_file).convert("RGBA")
    logo = ImageOps.exif_transpose(logo)

    alpha = logo.getchannel("A")
    alpha = alpha.point(lambda p: int(p * (opacity / 100)))
    logo.putalpha(alpha)

    return logo, width_percent


def apply_watermark(
    img,
    watermark,
    position,
    margin_x,
    margin_y,
    logo_width_percent=None
):
    base = ImageOps.exif_transpose(img).convert("RGBA")
    bw, bh = base.size

    wm = watermark.copy()

    if logo_width_percent:
        new_w = int(bw * (logo_width_percent / 100))
        ratio = new_w / wm.size[0]
        new_h = int(wm.size[1] * ratio)
        wm = wm.resize((new_w, new_h), Image.LANCZOS)

    x, y = get_position(base.size, wm.size, position, margin_x, margin_y)
    base.alpha_composite(wm, (x, y))

    return base


def save_image(img, output_format, quality, progressive):
    buffer = BytesIO()

    if output_format == "JPG":
        img.convert("RGB").save(
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
        img.save(
            buffer,
            format="PNG",
            optimize=True
        )
        ext = "png"
        mime = "image/png"

    buffer.seek(0)
    return buffer, ext, mime


def run():
    st.subheader(tr("Image Watermark", tr("Image Watermark", "Watermark imagini")))

    with st.expander(tr("What this app does and how to use it", "Pentru ce se folosește și cum se utilizează"), expanded=False):
        st.markdown(tr("**Use:** Applies a text or logo watermark to multiple images at once.", "**Utilizare:** Aplică watermark text sau logo pe mai multe imagini odată."))
        st.markdown(tr("**Quick steps:**", "**Pași rapizi:**"))
        st.markdown(tr("1. Upload images and choose text or logo watermark.", "1. Încarcă imaginile și alege watermark text sau logo."))
        st.markdown(tr("2. Set position, size, opacity, margins and output format.", "2. Setează poziția, mărimea, opacitatea, marginile și formatul final."))
        st.markdown(tr("3. Review the results and download the ZIP with watermarked images.", "3. Verifică rezultatele și descarcă ZIP-ul cu imaginile marcate."))

    files = st.file_uploader(
        tr("Select images", "Selectează imaginile"),
        type=["jpg", "jpeg", "png", "webp"],
        accept_multiple_files=True
    )

    watermark_type = st.radio(
        tr("Watermark type", "Tip watermark"),
        ["Text", "Logo"],
        horizontal=True
    )

    st.divider()

    if watermark_type == "Text":
        text = st.text_input(tr("Watermark text", "Text watermark"), value="Watermark")

        col1, col2, col3 = st.columns(3)

        with col1:
            font_size = st.slider(tr("Text size", "Mărime text"), 8, 200, 48)

        with col2:
            text_color = st.color_picker(tr("Text color", "Culoare text"), "#FFFFFF")

        with col3:
            text_opacity = st.slider(tr("Text opacity", "Opacitate text"), 1, 100, 70)

        col4, col5 = st.columns(2)

        with col4:
            padding = st.slider(tr("Text background padding", "Spațiere fundal text"), 0, 80, 16)

        with col5:
            bg_enabled = st.checkbox(tr("Background under text", "Fundal sub text"), value=True)

        bg_color = "#000000"
        bg_opacity = 40

        if bg_enabled:
            col6, col7 = st.columns(2)
            with col6:
                bg_color = st.color_picker(tr("Background color", "Culoare fundal"), "#000000")
            with col7:
                bg_opacity = st.slider(tr("Background opacity", "Opacitate fundal"), 1, 100, 40)

        logo_file = None
        logo_width_percent = None

    else:
        logo_file = st.file_uploader(
            tr("Upload PNG/WebP/JPG logo", "Încarcă logo PNG/WebP/JPG"),
            type=["png", "webp", "jpg", "jpeg"],
            accept_multiple_files=False
        )

        col1, col2 = st.columns(2)

        with col1:
            logo_width_percent = st.slider(
                tr("Logo size (% of image width)", "Mărime logo (% din lățimea imaginii)"),
                1,
                80,
                15
            )

        with col2:
            logo_opacity = st.slider(tr("Logo opacity", "Opacitate logo"), 1, 100, 70)

        text = ""
        font_size = 48
        text_color = "#FFFFFF"
        text_opacity = 70
        padding = 16
        bg_enabled = False
        bg_color = "#000000"
        bg_opacity = 40

    st.divider()

    col_pos1, col_pos2, col_pos3 = st.columns(3)

    with col_pos1:
        position = st.selectbox(
            tr("Position", "Poziție"),
            [
                "Dreapta jos",
                "Stânga jos",
                "Centru jos",
                "Dreapta sus",
                "Stânga sus",
                "Centru sus",
                "Centru",
                "Stânga centru",
                "Dreapta centru",
            ]
        )

    with col_pos2:
        margin_x = st.slider(tr("Margin X", "Margine X"), 0, 500, 40)

    with col_pos3:
        margin_y = st.slider(tr("Margin Y", "Margine Y"), 0, 500, 40)

    st.divider()

    col_out1, col_out2 = st.columns(2)

    with col_out1:
        output_format = st.selectbox(tr("Output format", "Format output"), ["JPG", "PNG", "WEBP"])

    with col_out2:
        show_details = st.checkbox(tr("Show image details", "Afișează detalii imagini"), value=False)

    quality = 90
    progressive = True

    if output_format in ["JPG", "WEBP"]:
        quality = st.slider(tr("Export quality", "Calitate export"), 1, 100, 90)

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

    if not files:
        st.info(tr("Upload images for watermark.", "Încarcă imaginile pentru watermark."))
        return

    if watermark_type == "Text" and not text.strip():
        st.error(tr("Watermark text cannot be empty.", "Textul watermark nu poate fi gol."))
        return

    if watermark_type == "Logo" and not logo_file:
        st.error(tr("Upload a logo.", "Încarcă un logo."))
        return

    rename_prefix = clean_filename_part(rename_prefix)
    rename_separator = clean_separator(rename_separator)

    if enable_rename and not rename_prefix:
        st.error(tr("Base name cannot be empty.", "Numele bază nu poate fi gol."))
        return

    if watermark_type == "Text":
        watermark = create_text_watermark(
            text=text,
            font_size=font_size,
            color=text_color,
            opacity=text_opacity,
            padding=padding,
            bg_enabled=bg_enabled,
            bg_color=bg_color,
            bg_opacity=bg_opacity
        )
        logo_width = None
    else:
        watermark, logo_width = prepare_logo_watermark(
            logo_file,
            logo_width_percent,
            logo_opacity
        )

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

            final_img = apply_watermark(
                img=img,
                watermark=watermark,
                position=position,
                margin_x=margin_x,
                margin_y=margin_y,
                logo_width_percent=logo_width
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
                output_name = f"{Path(file.name).stem}_watermark.{ext}"

            zip_file.writestr(output_name, final_bytes)

            results.append({
                "old_name": file.name,
                "new_name": output_name,
                "original_size": original_size_kb,
                "final_size": final_size_kb,
                "final_bytes": final_bytes,
                "mime": mime
            })

    zip_buffer.seek(0)

    st.divider()

    total_diff = 100 - ((total_final_kb / total_original_kb) * 100)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(tr("Files", "Fișiere"), len(files))
    c2.metric(tr("Original total", "Total original"), f"{total_original_kb:.1f} KB")
    c3.metric(tr("Final total", "Total final"), f"{total_final_kb:.1f} KB")
    c4.metric("Diferență", f"{total_diff:.1f}%")

    if show_details:
        st.divider()

        for item in results:
            with st.expander(f"{item['old_name']} → {item['new_name']}", expanded=False):
                c1, c2 = st.columns(2)
                c1.metric(tr("Original", "Original"), f"{item['original_size']:.1f} KB")
                c2.metric(tr("Final", "Final"), f"{item['final_size']:.1f} KB")

                preview_img = Image.open(BytesIO(item["final_bytes"]))
                st.image(preview_img, use_container_width=True)

                st.download_button(
                    tr("Download image", "Descarcă imaginea"),
                    data=item["final_bytes"],
                    file_name=item["new_name"],
                    mime=item["mime"],
                    key=item["new_name"]
                )
    else:
        st.divider()
        for item in results:
            st.write(
                f"{item['old_name']} → {item['new_name']} | "
                f"{item['original_size']:.1f} KB → {item['final_size']:.1f} KB"
            )

    st.divider()

    st.download_button(
        "Descarcă toate imaginile cu watermark ZIP",
        data=zip_buffer,
        file_name="imagini_watermark.zip",
        mime="application/zip"
    )
