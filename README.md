# Image Tools App

Aplicație web/locală făcută în Python + Streamlit pentru procesare rapidă de imagini în bulk.
O poti testa aici : https://resize-images-app.streamlit.app/

## Funcții disponibile

- Compresie JPG sub o mărime aleasă, de exemplu sub 300 KB
- Redimensionare imagini
- Rename imagini în serie
- Convertor format: JPG, PNG, WEBP
- Watermark cu text sau logo
- Crop / social media presets / thumbnail generator
- PDF din imagini cu efecte de scanare
- Procesare bulk pentru mai multe imagini odată
- Download rezultat ca ZIP sau PDF

## Structură proiect

app/
├── main.py

├── requirements.txt

├── compresie_jpg/

│   └── app.py

├── redimensionare/

│   └── app.py

├── rename/

│   └── app.py

├── convertor_format/

│   └── app.py

├── watermark/

│   └── app.py

├── crop_thumbnail/

│   └── app.py

└── pdf_din_imagini/

    └── app.py


## Instalare locală

Ai nevoie de Python instalat.

Instalează librăriile:

pip install -r requirements.txt

sau:

python -m pip install -r requirements.txt
Pornire aplicație

Din folderul proiectului:

streamlit run main.py

sau:

python -m streamlit run main.py

Aplicația se va deschide în browser, local.

requirements.txt
streamlit
pillow

## Cum adaugi o aplicație nouă

Creezi un folder nou în proiect:

nume_aplicatie/

└── app.py

În app.py trebuie să existe funcția:

def run():
    ...

main.py detectează automat folderele care conțin app.py și le adaugă în meniu.

## Deploy online

Aplicația poate fi hostată gratuit pe Streamlit Community Cloud.

Pași:

Urcă proiectul pe GitHub
Intră pe Streamlit Community Cloud
Conectează repo-ul
Alege main.py ca fișier principal
Deploy
Observații

Pentru multe imagini sau fișiere foarte mari, este recomandată rularea locală pe PC, nu pe hosting gratuit.

Hosting-ul gratuit poate avea limitări de memorie și timp de procesare.