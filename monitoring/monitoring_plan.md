# Monitoring Plan (Production)

## What we monitor
### Data Quality (upstream)
- Null rate / missing critical fields
- Schema drift (new/removed columns, type changes)
- Outlier detection (amount spikes, unusual MCC distribution)

### Model Performance (downstream)
- Prediction distribution shift (risk_score drift)
- AUC / precision / recall (when labels arrive)
- Calibration stability
- Alerting thresholds for risk_flag spikes

## Where to log
- Batch: metrics logged per run (Airflow task + artifact store)
- Streaming: metrics logged per micro-batch and aggregated hourly

## Alerts
- Slack / PagerDuty alerts for:
  - schema drift
  - data quality failures
  - risk_score distribution drift > threshold
