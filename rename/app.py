import streamlit as st
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


def run():
    st.subheader(tr("Bulk Image Rename", "Rename imagini în serie"))

    with st.expander(tr("What this app does and how to use it", "Pentru ce se folosește și cum se utilizează"), expanded=False):
        st.markdown(tr("**Use:** Quickly renames multiple images with prefix, separator and automatic numbering.", "**Utilizare:** Redenumește rapid multe imagini cu prefix, separator și numerotare automată."))
        st.markdown(tr("**Quick steps:**", "**Pași rapizi:**"))
        st.markdown(tr("1. Upload the images you want to rename.", "1. Încarcă imaginile pe care vrei să le redenumești."))
        st.markdown(tr("2. Set the base name, separator and start number.", "2. Setează numele de bază, separatorul și numărul de start."))
        st.markdown(tr("3. Review the preview and download the ZIP with new names.", "3. Verifică preview-ul și descarcă ZIP-ul cu numele noi."))

    files = st.file_uploader(
        tr("Select images", "Selectează imaginile"),
        type=["jpg", "jpeg", "png", "webp"],
        accept_multiple_files=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        prefix = st.text_input(tr("Base name", "Nume bază"), value="Poza_pisica")

    with col2:
        start_number = st.number_input(
            tr("Start numbering from", "Începe numerotarea de la"),
            min_value=1,
            value=1,
            step=1
        )

    with col3:
        separator = st.text_input(tr("Separator", "Separator"), value="-")

    keep_original_extension = st.checkbox(
        tr("Keep original extension", "Păstrează extensia originală"),
        value=True
    )

    show_preview = st.checkbox(
        tr("Show name preview", "Afișează preview nume"),
        value=True
    )

    if not files:
        st.info(tr("Upload images for renaming.", "Încarcă imaginile pentru redenumire."))
        return

    prefix = clean_filename_part(prefix)
    separator = clean_separator(separator)

    if not prefix:
        st.error(tr("Base name cannot be empty.", "Numele bază nu poate fi gol."))
        return

    zip_buffer = BytesIO()
    renamed_files = []

    with ZipFile(zip_buffer, "w") as zip_file:
        for index, file in enumerate(files, start=int(start_number)):
            old_name = file.name

            if keep_original_extension:
                extension = Path(old_name).suffix.lower()
            else:
                extension = ".jpg"

            new_name = f"{prefix}{separator}{index}{extension}"

            zip_file.writestr(new_name, file.getvalue())

            renamed_files.append({
                "old": old_name,
                "new": new_name
            })

    zip_buffer.seek(0)

    st.divider()

    c1, c2 = st.columns(2)
    c1.metric(tr("Files", "Fișiere"), len(renamed_files))
    c2.metric(tr("First name", "Primul nume"), renamed_files[0]["new"])

    if show_preview:
        with st.expander(tr("Rename preview", "Preview redenumire"), expanded=True):
            for item in renamed_files:
                st.write(f"{item['old']} → **{item['new']}**")

    st.download_button(
        tr("Download renamed images ZIP", "Descarcă imaginile redenumite ZIP"),
        data=zip_buffer,
        file_name="imagini_redenumite.zip",
        mime="application/zip"
    )

