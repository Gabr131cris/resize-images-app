import streamlit as st
from PIL import Image
from io import BytesIO
from zipfile import ZipFile


def compress_to_target(img, target_kb, progressive=True):
    quality = 95
    last_buffer = None
    last_size = 0

    while quality >= 5:
        buffer = BytesIO()

        img.convert("RGB").save(
            buffer,
            format="JPEG",
            quality=quality,
            optimize=True,
            progressive=progressive
        )

        size_kb = len(buffer.getvalue()) / 1024
        last_buffer = buffer
        last_size = size_kb

        if size_kb <= target_kb:
            return buffer, quality, size_kb

        quality -= 5

    return last_buffer, quality, last_size


def run():
    st.subheader("Compresie JPG după mărime")

    col1, col2 = st.columns(2)

    with col1:
        target_kb = st.number_input(
            "Mărime maximă fișier (KB)",
            min_value=10,
            value=300,
            step=10
        )

    with col2:
        progressive = st.checkbox("Progressive JPEG", value=True)

    files = st.file_uploader(
        "Selectează imagini",
        type=["jpg", "jpeg", "png", "webp"],
        accept_multiple_files=True
    )

    if not files:
        st.info("Încarcă una sau mai multe imagini.")
        return

    zip_buffer = BytesIO()

    with ZipFile(zip_buffer, "w") as zip_file:
        for file in files:
            original_size_kb = len(file.getvalue()) / 1024
            img = Image.open(file)

            compressed, quality, final_size = compress_to_target(
                img,
                target_kb,
                progressive
            )

            reduction = 100 - ((final_size / original_size_kb) * 100)

            output_name = file.name.rsplit(".", 1)[0] + "_compressed.jpg"

            zip_file.writestr(output_name, compressed.getvalue())

            st.divider()
            st.write(f"### {file.name}")

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Original", f"{original_size_kb:.1f} KB")
            c2.metric("Final", f"{final_size:.1f} KB")
            c3.metric("Reducere", f"{reduction:.1f}%")
            c4.metric("Quality", quality)

            col_a, col_b = st.columns(2)

            with col_a:
                st.caption("Original")
                st.image(img, use_container_width=True)

            with col_b:
                st.caption("Comprimat")
                preview_img = Image.open(BytesIO(compressed.getvalue()))
                st.image(preview_img, use_container_width=True)

            st.download_button(
                "Descarcă imaginea",
                data=compressed.getvalue(),
                file_name=output_name,
                mime="image/jpeg",
                key=output_name
            )

    zip_buffer.seek(0)

    st.divider()

    st.download_button(
        "Descarcă toate imaginile ZIP",
        zip_buffer,
        "imagini_compresate.zip",
        "application/zip"
    )