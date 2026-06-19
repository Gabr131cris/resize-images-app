import streamlit as st
from PIL import Image
from io import BytesIO
from zipfile import ZipFile


def resize_image(img, width=None, height=None, keep_ratio=True):
    original_width, original_height = img.size

    if keep_ratio:
        if width and not height:
            ratio = width / original_width
            height = int(original_height * ratio)
        elif height and not width:
            ratio = height / original_height
            width = int(original_width * ratio)
        elif width and height:
            img.thumbnail((width, height))
            return img
        else:
            return img
    else:
        if not width:
            width = original_width
        if not height:
            height = original_height

    return img.resize((int(width), int(height)), Image.LANCZOS)


def image_to_bytes(img, image_format="JPEG", quality=90):
    buffer = BytesIO()

    if image_format == "JPEG":
        img = img.convert("RGB")
        img.save(buffer, format="JPEG", quality=quality, optimize=True)
    else:
        img.save(buffer, format=image_format)

    buffer.seek(0)
    return buffer


def run():
    st.subheader("Redimensionare imagini")

    uploaded_files = st.file_uploader(
        "Alege una sau mai multe imagini",
        type=["jpg", "jpeg", "png", "webp"],
        accept_multiple_files=True
    )

    col1, col2 = st.columns(2)

    with col1:
        width = st.number_input("Lățime nouă px", min_value=0, value=1000, step=10)

    with col2:
        height = st.number_input("Înălțime nouă px", min_value=0, value=0, step=10)

    keep_ratio = st.checkbox("Păstrează proporțiile", value=True)

    output_format = st.selectbox("Format output", ["JPEG", "PNG", "WEBP"])

    quality = 90
    if output_format in ["JPEG", "WEBP"]:
        quality = st.slider("Calitate", 1, 100, 90)

    if not uploaded_files:
        st.info("Încarcă imagini ca să începi.")
        return

    zip_buffer = BytesIO()

    with ZipFile(zip_buffer, "w") as zip_file:
        for file in uploaded_files:
            img = Image.open(file)

            new_img = resize_image(
                img,
                width=width if width > 0 else None,
                height=height if height > 0 else None,
                keep_ratio=keep_ratio
            )

            img_bytes = image_to_bytes(new_img, output_format, quality)

            extension = output_format.lower()
            output_name = file.name.rsplit(".", 1)[0] + f"_redimensionat.{extension}"

            zip_file.writestr(output_name, img_bytes.getvalue())

            st.write(f"{file.name}: {img.size[0]}x{img.size[1]} → {new_img.size[0]}x{new_img.size[1]}")

    zip_buffer.seek(0)

    st.download_button(
        label="Descarcă imaginile redimensionate ZIP",
        data=zip_buffer,
        file_name="imagini_redimensionate.zip",
        mime="application/zip"
    )