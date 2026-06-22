import streamlit as st
from PIL import Image
from io import BytesIO
from zipfile import ZipFile
from pathlib import Path
from ui_language import tr


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
            return buffer, quality, size_kb, True

        quality -= 5

    return last_buffer, quality, last_size, False


def run():
    st.subheader(tr("JPG Compression by size", "Compresie JPG după mărime"))

    with st.expander(tr("What this app does and how to use it", "Pentru ce se folosește și cum se utilizează"), expanded=False):
        st.markdown(tr("**Use:** Reduces JPG images to a chosen maximum file size, useful for websites, marketplaces or email.", "**Utilizare:** Micșorează imaginile JPG până la o dimensiune maximă aleasă, util pentru site, marketplace sau email."))
        st.markdown(tr("**Quick steps:**", "**Pași rapizi:**"))
        st.markdown(tr("1. Upload one or more images.", "1. Încarcă una sau mai multe imagini."))
        st.markdown(tr("2. Choose the maximum size in KB and rename options if needed.", "2. Alege mărimea maximă în KB și opțiunile de redenumire, dacă ai nevoie."))
        st.markdown(tr("3. Review the results and download the ZIP archive.", "3. Verifică rezultatele și descarcă arhiva ZIP."))

    with st.expander("Pentru ce se folosește și cum se utilizează", expanded=False):
        st.markdown("**Utilizare:** Micșorează imaginile JPG până la o dimensiune maximă aleasă, util pentru site, marketplace sau email.")
        st.markdown("**Pași rapizi:**")
        st.markdown("1. Încarcă una sau mai multe imagini.")
        st.markdown("2. Alege mărimea maximă în KB și opțiunile de redenumire, dacă ai nevoie.")
        st.markdown("3. Verifică rezultatele și descarcă arhiva ZIP.")

    col1, col2 = st.columns(2)

    with col1:
        target_kb = st.number_input(
            tr("Maximum file size (KB)", "Mărime maximă fișier (KB)"),
            min_value=10,
            value=300,
            step=10
        )

    with col2:
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

    files = st.file_uploader(
        tr("Select images", "Selectează imagini"),
        type=["jpg", "jpeg", "png", "webp"],
        accept_multiple_files=True
    )

    if not files:
        st.info(tr("Upload one or more images.", "Încarcă una sau mai multe imagini."))
        return

    zip_buffer = BytesIO()
    total_original = 0
    total_final = 0

    results = []

    with ZipFile(zip_buffer, "w") as zip_file:
        for i, file in enumerate(files, start=int(rename_start)):
            original_size_kb = len(file.getvalue()) / 1024
            total_original += original_size_kb

            img = Image.open(file)

            compressed, quality, final_size, success = compress_to_target(
                img,
                target_kb,
                progressive
            )

            total_final += final_size

            reduction = 100 - ((final_size / original_size_kb) * 100)

            if enable_rename:
                output_name = f"{rename_prefix}{rename_separator}{i}.jpg"
            else:
                output_name = file.name.rsplit(".", 1)[0] + "_compressed.jpg"

            zip_file.writestr(output_name, compressed.getvalue())

            results.append({
                "old_name": file.name,
                "new_name": output_name,
                "original_size": original_size_kb,
                "final_size": final_size,
                "reduction": reduction,
                "quality": quality,
                "success": success,
                "image": img,
                "compressed": compressed.getvalue()
            })

    zip_buffer.seek(0)

    st.divider()

    total_reduction = 100 - ((total_final / total_original) * 100)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(tr("Files", "Fișiere"), len(files))
    c2.metric(tr("Original total", "Total original"), f"{total_original:.1f} KB")
    c3.metric(tr("Final total", "Total final"), f"{total_final:.1f} KB")
    c4.metric("Reducere totală", f"{total_reduction:.1f}%")

    st.divider()

    for item in results:
        status = "✅" if item["success"] else "⚠️"

        if show_details:
            with st.expander(f"{status} {item['old_name']} → {item['new_name']}", expanded=False):
                c1, c2, c3, c4 = st.columns(4)
                c1.metric(tr("Original", "Original"), f"{item['original_size']:.1f} KB")
                c2.metric(tr("Final", "Final"), f"{item['final_size']:.1f} KB")
                c3.metric(tr("Reduction", "Reducere"), f"{item['reduction']:.1f}%")
                c4.metric("Quality", item["quality"])

                col_a, col_b = st.columns(2)

                with col_a:
                    st.caption(tr("Original", "Original"))
                    st.image(item["image"], use_container_width=True)

                with col_b:
                    st.caption("Comprimat")
                    preview_img = Image.open(BytesIO(item["compressed"]))
                    st.image(preview_img, use_container_width=True)

                st.download_button(
                    tr("Download image", "Descarcă imaginea"),
                    data=item["compressed"],
                    file_name=item["new_name"],
                    mime="image/jpeg",
                    key=item["new_name"]
                )
        else:
            st.write(
                f"{status} {item['old_name']} → {item['new_name']} | "
                f"{item['original_size']:.1f} KB → {item['final_size']:.1f} KB | "
                f"quality {item['quality']}"
            )

    st.divider()

    st.download_button(
        "Descarcă toate imaginile ZIP",
        data=zip_buffer,
        file_name="imagini_compresate.zip",
        mime="application/zip"
    )
