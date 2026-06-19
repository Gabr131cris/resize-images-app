Problema e aici: `return text.strip("_")` șterge separatorul `_`. Înlocuiește complet `rename/app.py` cu acesta:

```python
import streamlit as st
from io import BytesIO
from zipfile import ZipFile
from pathlib import Path
import re


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
    st.subheader("Rename imagini în serie")

    files = st.file_uploader(
        "Selectează imaginile",
        type=["jpg", "jpeg", "png", "webp"],
        accept_multiple_files=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        prefix = st.text_input("Nume bază", value="Poza_pisica")

    with col2:
        start_number = st.number_input(
            "Începe numerotarea de la",
            min_value=1,
            value=1,
            step=1
        )

    with col3:
        separator = st.text_input("Separator", value="_")

    keep_original_extension = st.checkbox(
        "Păstrează extensia originală",
        value=True
    )

    show_preview = st.checkbox(
        "Afișează preview nume",
        value=True
    )

    if not files:
        st.info("Încarcă imaginile pentru redenumire.")
        return

    prefix = clean_filename_part(prefix)
    separator = clean_separator(separator)

    if not prefix:
        st.error("Numele bază nu poate fi gol.")
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
    c1.metric("Fișiere", len(renamed_files))
    c2.metric("Primul nume", renamed_files[0]["new"])

    if show_preview:
        with st.expander("Preview redenumire", expanded=True):
            for item in renamed_files:
                st.write(f"{item['old']} → **{item['new']}**")

    st.download_button(
        "Descarcă imaginile redenumite ZIP",
        data=zip_buffer,
        file_name="imagini_redenumite.zip",
        mime="application/zip"
    )

