# Proyek Analisis Data: E-Commerce Public Dataset ✨

## Deskripsi Proyek
Proyek ini merupakan analisis data pada E-Commerce Public Dataset untuk memenuhi submission Dicoding kelas "Belajar Analisis Data dengan Python". Analisis mencakup Data Wrangling, Exploratory Data Analysis (EDA), Visualisasi Data, dan Analisis Lanjutan (RFM Analysis).

## Pertanyaan Bisnis
1. Bagaimana tren jumlah pesanan dan total pendapatan (revenue) per bulan selama periode September 2016 hingga Agustus 2018?
2. Bagaimana distribusi segmentasi pelanggan berdasarkan analisis RFM (Recency, Frequency, Monetary)?
3. Bagaimana distribusi geografis pelanggan dan kontribusi pendapatan per state di Brasil?

## Struktur Direktori
```
submission
├───dashboard
│   ├───main_data.csv
│   └───dashboard.py
├───data
│   ├───customers_dataset.csv
│   ├───geolocation_dataset.csv
│   ├───orders_dataset.csv
│   ├───order_items_dataset.csv
│   ├───order_payments_dataset.csv
│   ├───order_reviews_dataset.csv
│   ├───products_dataset.csv
│   ├───product_category_name_translation.csv
│   └───sellers_dataset.csv
├───notebook.ipynb
├───README.md
├───requirements.txt
└───url.txt
```

## Setup Environment - Anaconda
```
conda create --name main-ds python=3.9
conda activate main-ds
pip install -r requirements.txt
```

## Setup Environment - Shell/Terminal
```
mkdir proyek_analisis_data
cd proyek_analisis_data
pipenv install
pipenv shell
pip install -r requirements.txt
```

## Run Streamlit App
```
cd dashboard
streamlit run dashboard.py
```
