# Dataset V3 — event-window relabelling

This directory is independent from the original dataset and deployment projects.
It relabels existing F1-F4 recordings so that baseline and recovery windows are
Healthy and only inferred event windows are F1-F4.

Files:

- `event_label_manifest_v3.csv`: auditable source of inferred label intervals.
- `build_dataset_v3.py`: creates the master and ML-ready datasets.
- `master_features_relabelled_v3.csv`: all source feature windows plus V3 labels.
- `ml_dataset_v3.csv`: finite 40-feature rows ready for training.
- `train_model_v3.py`: 3-fold group-aware reference-model training.

Run from the PDM_V1 root:

```bash
python dataset_v3/build_dataset_v3.py
python dataset_v3/train_model_v3.py
```
