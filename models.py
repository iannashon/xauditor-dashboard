# models.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class Claim:
    ClaimID: str
    PatientID: str
    ProviderID: str
    ProviderType: str
    ProcedureCode: str
    ClaimCharge: float
    DaysInHospital: int
    fraud_score: int
    fraud_category: str