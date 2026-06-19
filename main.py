import streamlit as st
from pathlib import Path
import importlib.util

BASE_DIR = Path(__file__).parent

st.set_page_config(page_title="App Tools", layout="wide")
st.title("App Tools")

apps = []

for folder in BASE_DIR.iterdir():
    if folder.is_dir() and (folder / "app.py").exists():
        apps.append(folder)

apps = sorted(apps, key=lambda x: x.name.lower())

if not apps:
    st.warning("Nu există aplicații. Creează un folder cu fișier app.py în el.")
    st.stop()

app_names = [folder.name.replace("_", " ").title() for folder in apps]

selected_name = st.sidebar.selectbox("Alege aplicația", app_names)
selected_folder = apps[app_names.index(selected_name)]

st.header(selected_name)

app_file = selected_folder / "app.py"

spec = importlib.util.spec_from_file_location("selected_app", app_file)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

if hasattr(module, "run"):
    module.run()
else:
    st.error(f"Fișierul {app_file} trebuie să aibă o funcție run().")