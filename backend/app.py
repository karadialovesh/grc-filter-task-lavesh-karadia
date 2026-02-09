from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field, validator
import sqlite3
import os
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

# CORS for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database Setup
DB_NAME = "risks.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS risks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset TEXT NOT NULL,
            threat TEXT NOT NULL,
            likelihood INTEGER NOT NULL,
            impact INTEGER NOT NULL,
            score INTEGER NOT NULL,
            level TEXT NOT NULL,
            compliance_hint TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Pydantic Models
class RiskCreate(BaseModel):
    asset: str
    threat: str
    likelihood: int
    impact: int

    @validator('likelihood', 'impact')
    def validate_range(cls, v):
        if not 1 <= v <= 5:
            # Re-check range to return specific error msg
            raise ValueError("Invalid range: Likelihood and Impact must be 1–5.")
        return v

class RiskResponse(RiskCreate):
    id: int
    score: int
    level: str
    compliance_hint: Optional[str] = None

# Helper Functions
def calculate_risk_level(score: int) -> str:
    if 1 <= score <= 5:
        return "Low"
    elif 6 <= score <= 12:
        return "Medium"
    elif 13 <= score <= 18:
        return "High"
    elif 19 <= score <= 25:
        return "Critical"
    return "Unknown"

def get_compliance_hint(level: str) -> str:
    if level == "High" or level == "Critical":
        return "Recommend NIST PR.AC-7: Rate Limiting"
    return ""

# API Endpoints
@app.get("/")
def health():
    return {"status": "ok"}


@app.post("/assess-risk", response_model=RiskResponse)
def assess_risk(risk: RiskCreate):
    # Extra check for HTTP 400 specifically
    if not (1 <= risk.likelihood <= 5 and 1 <= risk.impact <= 5):
         raise HTTPException(status_code=400, detail={"error": "Invalid range: Likelihood and Impact must be 1–5."})

    score = risk.likelihood * risk.impact
    level = calculate_risk_level(score)
    hint = get_compliance_hint(level)

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT INTO risks (asset, threat, likelihood, impact, score, level, compliance_hint)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (risk.asset, risk.threat, risk.likelihood, risk.impact, score, level, hint))
    risk_id = c.lastrowid
    conn.commit()
    conn.close()

    return {
        "id": risk_id,
        "asset": risk.asset,
        "threat": risk.threat,
        "likelihood": risk.likelihood,
        "impact": risk.impact,
        "score": score,
        "level": level,
        "compliance_hint": hint
    }

@app.get("/risks", response_model=List[RiskResponse])
def get_risks(level: Optional[str] = Query(None, description="Filter by risk level (Low, Medium, High, Critical)")):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    if level:
        c.execute("SELECT * FROM risks WHERE level = ?", (level,))
    else:
        c.execute("SELECT * FROM risks")
    
    rows = c.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
