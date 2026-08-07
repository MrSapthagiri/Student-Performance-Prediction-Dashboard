from pathlib import Path
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]


def export_predictions_to_excel(history: list[dict], output_path: str | None = None) -> str:
    df = pd.DataFrame(history)
    output_file = output_path or str(ROOT_DIR / "exports" / "prediction_report.xlsx")
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(output_file, index=False)
    return output_file


def get_project_root() -> Path:
    return ROOT_DIR
