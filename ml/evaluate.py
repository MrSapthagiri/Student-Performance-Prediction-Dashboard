"""
Model evaluation metrics for classification and regression.
"""

import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, mean_absolute_error, mean_squared_error, r2_score,
    classification_report
)


def evaluate_classifier(model, X_test, y_test, model_name, binary=False):
    """Evaluate a classification model and return metrics dict."""
    y_pred = model.predict(X_test)

    avg = 'binary' if binary else 'weighted'
    metrics = {
        "model": model_name,
        "accuracy": round(accuracy_score(y_test, y_pred), 4),
        "precision_weighted": round(precision_score(y_test, y_pred, average=avg, zero_division=0), 4),
        "recall_weighted": round(recall_score(y_test, y_pred, average=avg, zero_division=0), 4),
        "f1_weighted": round(f1_score(y_test, y_pred, average=avg, zero_division=0), 4),
    }

    # ROC-AUC
    try:
        if hasattr(model, 'predict_proba'):
            y_proba = model.predict_proba(X_test)
            if binary:
                metrics['roc_auc'] = round(roc_auc_score(y_test, y_proba[:, 1]), 4)
            else:
                metrics['roc_auc'] = round(
                    roc_auc_score(y_test, y_proba, multi_class='ovr', average='weighted'), 4
                )
        else:
            metrics['roc_auc'] = 0.0
    except Exception:
        metrics['roc_auc'] = 0.0

    return metrics


def evaluate_regressor(model, X_test, y_test, model_name):
    """Evaluate a regression model and return metrics dict."""
    y_pred = model.predict(X_test)

    metrics = {
        "model": model_name,
        "mae": round(mean_absolute_error(y_test, y_pred), 4),
        "rmse": round(np.sqrt(mean_squared_error(y_test, y_pred)), 4),
        "r2": round(r2_score(y_test, y_pred), 4),
    }

    return metrics
