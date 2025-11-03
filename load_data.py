# load_data.py
"""
Load CSV (data/claims.csv), compute fraud_score, and save to SQLite (db/claims.db).
Columns expected in CSV header (case-insensitive):
Patient ID, Age, Gender, Date Admitted, Date Discharged, Diagnosis, Amount Billed, Fraud Type
"""
import pandas as pd
import sqlite3
from pathlib import Path
from datetime import timedelta

CSV_PATH = Path("data/claims.csv")
DB_PATH = Path("db/claims.db")



# Tunable constants
HIGH_AGE_THRESHOLD = 80
LONG_STAY_DAYS = 7  # days considered unusually long
MAX_FREQ_PENALTY = 5

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    # normalize header names to snake_case keys
    df = df.rename(columns=lambda c: c.strip().lower().replace(" ", "_"))
    return df


def compute_scores(df: pd.DataFrame) -> pd.DataFrame:
    df = normalize_columns(df)

    # Ensure core columns exist
    for col in ("patient_id","amount_billed","diagnosis","date_admitted","date_discharged","age"):
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    # Clean and coerce types
    df['amount_billed'] = pd.to_numeric(df['amount_billed'], errors='coerce').fillna(0.0)
    df['age'] = pd.to_numeric(df['age'], errors='coerce').fillna(0).astype(int)
    df['date_admitted'] = pd.to_datetime(df['date_admitted'], errors='coerce')
    df['date_discharged'] = pd.to_datetime(df['date_discharged'], errors='coerce')
    df['diagnosis'] = df['diagnosis'].astype(str)

    # compute length of stay in days (at least 0)
    df['length_of_stay'] = (df['date_discharged'] - df['date_admitted']).dt.days.clip(lower=0).fillna(0).astype(int)

    # avg billed by diagnosis (peer baseline)
    avg_by_diag = df.groupby('diagnosis')['amount_billed'].mean().rename('avg_billed')
    df = df.join(avg_by_diag, on='diagnosis')

    # base ratio relative to peers for same diagnosis
    # avoid divide-by-zero by replacing zero averages with 1
    df['avg_billed_safe'] = df['avg_billed'].replace({0: 1.0})
    df['base_ratio'] = df['amount_billed'] / df['avg_billed_safe']

    # Age risk factor: extreme ages sometimes more vulnerable -- small multiplier
    df['age_risk'] = df['age'].apply(lambda a: 1.2 if a >= HIGH_AGE_THRESHOLD else 1.0)

    # Length-of-stay penalty: unusually long stays increase suspicion modestly
    df['stay_penalty'] = 1 + (df['length_of_stay'] / LONG_STAY_DAYS).clip(0, MAX_FREQ_PENALTY)

    # Frequency: count of claims for same patient in last 60 days (sliding window)
    df = df.sort_values(by=["patient_id", "date_admitted"])

    # Compute time-based claim counts (fallback if too few dates)
    if "date_admitted" in df.columns:
        try:
            df["claims_last_60d"] = (
                df.groupby("patient_id")["date_admitted"]
                .rolling("60D", on="date_admitted")
                .count()
                .reset_index(level=0, drop=True)
            )
        except Exception:
            # Fallback if rolling with time fails
            df["claims_last_60d"] = (
                df.groupby("patient_id")["date_admitted"].transform("count")
            )
    else:
        df["claims_last_60d"] = 0
        
    df['freq_penalty'] = 1 + (df['claims_last_60d'] / 5).clip(0, MAX_FREQ_PENALTY)

    # Raw score
    # df['raw_score'] = df['base_ratio'] * df['age_risk'] * df['stay_penalty'] * df['freq_penalty']
    df['raw_score'] = df['base_ratio'] * df['age_risk'] * df['stay_penalty'] * df['freq_penalty']

    # Scale raw_score to 0-100. Use median base_ratio as baseline scaling factor to reduce skew.
    median_base = df['base_ratio'].replace([float('inf'), float('-inf')], 0).median()
    baseline = 1 + (median_base if pd.notna(median_base) else 1.0)
    df['fraud_score'] = (100 * (df['raw_score'] / baseline)).clip(0, 100).round().astype(int)



    # Keep human-friendly column names for DB
    out = df[[
        'patient_id','age','gender','date_admitted','date_discharged',
        'diagnosis','amount_billed','length_of_stay','age_risk', 'stay_penalty'
        ,'fraud_score'
    ]].copy()

    # Rename to DB-friendly names (no spaces)
    out.columns = [
        'patient_id','age','gender','date_admitted','date_discharged',
        'diagnosis','amount_billed','length_of_stay', 'age_risk', 'stay_penalty'
        ,'fraud_score'
    ]
    return out


def write_db(df: pd.DataFrame, db_path: Path):
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    df.to_sql('claims', conn, if_exists='replace', index=False)
    conn.close()
    print(f"Wrote {len(df)} claims to {db_path}")

def main():
    if not CSV_PATH.exists():
        raise SystemExit(f"Missing CSV at {CSV_PATH}. Place your file at that path.")
    print("Loading CSV...")
    df = pd.read_csv(CSV_PATH)
    print("Computing fraud scores...")
    out = compute_scores(df)
    print("Writing to SQLite...")
    write_db(out, DB_PATH)
    print("Done.")

if __name__ == '__main__':
    main()
