# metrics.py
from sklearn.metrics import precision_score, recall_score, silhouette_score
import numpy as np

# YOLO metrics
def compute_yolo_metrics(y_true, y_pred):
    """
    y_true and y_pred: list of labels per image
    Returns: precision, recall
    """
    if len(y_true) == 0 or len(y_pred) == 0:
        return 0.0, 0.0
    precision = precision_score(y_true, y_pred, average='weighted', zero_division=0)
    recall = recall_score(y_true, y_pred, average='weighted', zero_division=0)
    return round(precision, 3), round(recall, 3)

# K-Means metrics
def compute_kmeans_metrics(features, labels):
    """
    features: array-like RGB values per clothing item
    labels: cluster labels assigned by K-Means
    Returns: silhouette score
    """
    if len(set(labels)) <= 1 or len(features) < 2:
        return 0.0
    score = silhouette_score(features, labels)
    return round(score, 3)

# Example function for storing metrics
def save_metrics(metrics_dict, filepath="metrics/metrics.json"):
    import json
    import os
    os.makedirs("metrics", exist_ok=True)
    with open(filepath, "w") as f:
        json.dump(metrics_dict, f, indent=4)
