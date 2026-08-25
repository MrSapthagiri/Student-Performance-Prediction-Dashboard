"""
Script to run the full ML training pipeline.
"""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from ml.train import run_training


if __name__ == "__main__":
    metadata = run_training()
    if metadata:
        print("\n📋 Training Summary:")
        print(f"   Best Risk Model:  {metadata['best_risk_model']}")
        print(f"   Best Score Model: {metadata['best_score_model']}")
        print(f"   Best Pass Model:  {metadata['best_pass_model']}")
        print(f"   Features Used:    {metadata['feature_count']}")
        print(f"   Dataset Size:     {metadata['dataset_size']}")
