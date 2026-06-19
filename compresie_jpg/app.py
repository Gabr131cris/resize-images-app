import streamlit as st
from PIL import Image
from io import BytesIO
from zipfile import ZipFile


def compress_to_target(img, target_kb):
    quality = 95

    while quality >= 5:
        buffer = BytesIO()

        img.convert("RGB").save(
            buffer,
            format="JPEG",
            quality=quality,
            optimize=True,
            progressive=True
        )

        size_kb = len(buffer.getvalue()) / 1024

        if size_kb <= target_kb:
            return buffer, quality, size_kb

        quality -= 5

    return buffer, quality, size_kb


def run():

    st.subheader("Compresie JPG după mărime")

    target_kb = st.number_input(
        "Mărime maximă fișier (KB)",
        min_value=10,
        value=300
    )

    files = st.file_uploader(
        "Selectează imagini",
        type=["jpg", "jpeg", "png", "webp"],
        accept_multiple_files=True
    )

    if not files:
        return

    zip_buffer = BytesIO()

    with ZipFile(zip_buffer, "w") as zip_file:

        for file in files:

            img = Image.open(file)

            compressed, quality, final_size = compress_to_target(
                img,
                target_kb
            )

            output_name = (
                file.name.rsplit(".", 1)[0]
                + "_compressed.jpg"
            )

            zip_file.writestr(
                output_name,
                compressed.getvalue()
            )

            st.write(
                f"{file.name} → "
                f"{final_size:.1f} KB "
                f"(quality {quality})"
            )

    zip_buffer.seek(0)

    st.download_button(
        "Descarcă ZIP",
        zip_buffer,
        "imagini_compresate.zip",
        "application/zip"
    )