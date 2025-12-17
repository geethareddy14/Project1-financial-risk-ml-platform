# Project1-financial-risk-ml-platform

## ▶️ Quick Start (Local Demo)
```bash
pip install pyspark
python data_processing/bronze/bronze_ingest.py

## ▶️ Pipeline Run Order (Local Demo)
```bash
pip install pyspark

python data_processing/bronze/bronze_ingest.py
python data_processing/silver/silver_clean.py
python data_processing/gold/gold_features.py


