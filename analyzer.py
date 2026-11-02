from io import BytesIO

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

MAX_ROWS = 20_000
PREVIEW_ROWS = 5_000
MAX_ANOMALY_COLUMNS = 5


class AnalysisError(ValueError):
    pass


def analyze_csv_bytes(data: bytes) -> dict:
    try:
        df = pd.read_csv(BytesIO(data), encoding="utf-8-sig")
    except UnicodeDecodeError as exc:
        raise AnalysisError("UTF-8 인코딩 CSV만 지원합니다. 파일 인코딩을 확인해주세요.") from exc
    except (pd.errors.EmptyDataError, pd.errors.ParserError, ValueError) as exc:
        raise AnalysisError("비어 있거나 손상된 CSV 파일입니다. 구분자와 열 구조를 확인해주세요.") from exc
    if df.shape[0] > MAX_ROWS:
        raise AnalysisError(f"데이터 행 수는 최대 {MAX_ROWS:,}행까지 허용됩니다.")
    if df.shape[1] == 0:
        raise AnalysisError("컬럼이 없는 CSV 파일입니다.")

    numeric = df.select_dtypes(include=[np.number]).columns.tolist()
    missing = []
    for column in df.columns:
        count = int(df[column].isna().sum())
        missing.append({"column": str(column), "count": count,
                        "ratio": round(count / len(df) * 100, 2) if len(df) else 0})
    stats = []
    for column in numeric:
        series = df[column].dropna()
        stats.append({"column": str(column), "mean": _number(series.mean()),
                      "median": _number(series.median()), "min": _number(series.min()),
                      "max": _number(series.max())})

    anomaly = {"available": bool(numeric), "columns": numeric[:MAX_ANOMALY_COLUMNS],
               "count": 0, "ratio": 0, "message": None}
    if numeric:
        selected = numeric[:MAX_ANOMALY_COLUMNS]
        work = df[selected].replace([np.inf, -np.inf], np.nan).dropna()
        if len(work) >= 2:
            model = IsolationForest(contamination="auto", random_state=42, n_jobs=1)
            labels = model.fit_predict(work)
            count = int((labels == -1).sum())
            anomaly.update(count=count, ratio=round(count / len(work) * 100, 2))
        else:
            anomaly["message"] = "이상치 탐지에 필요한 결측치 없는 행이 2개 미만입니다."
    else:
        anomaly["message"] = "수치형 컬럼이 없어 이상치 탐지를 건너뛰었습니다."

    preview = df.head(PREVIEW_ROWS).astype(object).where(pd.notna(df.head(PREVIEW_ROWS)), None)
    return {"rows": int(len(df)), "columns": int(len(df.columns)),
            "column_types": [{"column": str(c), "dtype": str(df[c].dtype)} for c in df.columns],
            "missing": missing, "duplicates": int(df.duplicated().sum()),
            "numeric_stats": stats, "anomalies": anomaly,
            "preview": {"columns": [str(c) for c in df.columns], "rows": preview.to_dict(orient="records")}}


def _number(value):
    return None if pd.isna(value) else round(float(value), 6)
