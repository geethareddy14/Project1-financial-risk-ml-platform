# Project1-financial-risk-ml-platform

## 🧰 Tech Stack

- **Programming:** Python  
- **ML & AI:** XGBoost, PyTorch, TensorFlow, Scikit-learn  
- **GenAI:** LangChain, OpenAI GPT, Hugging Face, FAISS  
- **MLOps:** MLflow, Docker, Kubernetes  
- **Data:** Pandas, NumPy, PySpark  
- **Cloud:** AWS (S3, SageMaker, EC2)  
- **APIs:** FastAPI, Flask

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


## 🧠 Model Training (Local Demo)
```bash
pip install pyspark pandas scikit-learn

python ml_training/export_gold_to_csv.py
# Copy the generated part-*.csv from out/gold/risk_features_csv/ into:
# out/gold/risk_features.csv

python ml_training/train_model.py

## ⚡ Inference

### Batch scoring
```bash
python inference/batch_scoring/batch_score.py

pip install -r requirements.txt
uvicorn inference.real_time_api.app:app --reload



## ✅ Data Quality (Demo)
```bash
python data_quality/basic_checks.py

## 📈 Results (Demo)
- Generated account-level risk features used for binary fraud prediction
- Achieved stable model training with end-to-end reproducibility
- Designed batch and real-time inference patterns used in financial systems

