# tests/test_compute_scores.py
import pandas as pd
from load_data import compute_scores

def test_high_charge_gets_higher_score():
    df = pd.DataFrame([
        {'Patient ID':'p1','Age':30,'Gender':'F','Date Admitted':'2024-01-01','Date Discharged':'2024-01-02','Diagnosis':'X','Amount Billed':1000,'Fraud Type':'No Fraud'},
        {'Patient ID':'p2','Age':40,'Gender':'M','Date Admitted':'2024-01-02','Date Discharged':'2024-01-02','Diagnosis':'X','Amount Billed':100,'Fraud Type':'No Fraud'},
    ])
    out = compute_scores(df)
    s1 = int(out.loc[out['patient_id']=='p1','fraud_score'].iloc[0])
    s2 = int(out.loc[out['patient_id']=='p2','fraud_score'].iloc[0])
    assert 0 <= s1 <= 100
    assert 0 <= s2 <= 100
    assert s1 > s2
