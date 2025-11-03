# app.py
from flask import Flask, g, render_template, request, url_for, redirect
import sqlite3
from pathlib import Path
import math

DB_PATH = Path("db/claims.db")
PER_PAGE = 10

app = Flask(__name__)

def get_db():
    db = getattr(g, "_db", None)
    if db is None:
        if not DB_PATH.exists():
            raise RuntimeError("Database not found. Run load_data.py first.")
        db = sqlite3.connect(str(DB_PATH))
        db.row_factory = sqlite3.Row
        g._db = db
    return db

@app.teardown_appcontext
def close_db(exc):
    db = getattr(g, "_db", None)
    if db is not None:
        db.close()

@app.route("/")
def index():
    db = get_db()
    total_row = db.execute("SELECT COUNT(*) as cnt FROM claims").fetchone()
    total = total_row["cnt"] if total_row else 0
    avg_row = db.execute("SELECT AVG(amount_billed) as avg_amount FROM claims").fetchone()
    avg_amount = float(avg_row["avg_amount"]) if avg_row and avg_row["avg_amount"] is not None else 0.0
    high_row = db.execute("SELECT COUNT(*) as cnt FROM claims WHERE fraud_score > 75").fetchone()
    high_count = high_row["cnt"] if high_row else 0

    # distribution
    dist_rows = db.execute("""
        SELECT
          CASE
            WHEN fraud_score <= 25 THEN 'Low'
            WHEN fraud_score <= 75 THEN 'Medium'
            ELSE 'High'
          END as bucket,
          COUNT(*) as cnt
        FROM claims
        GROUP BY bucket
    """).fetchall()
    dist = {r["bucket"]: r["cnt"] for r in dist_rows}
    # ensure keys exist
    for k in ("Low","Medium","High"):
        dist.setdefault(k, 0)

    return render_template("index.html",
                           total=total,
                           avg_amount=avg_amount,
                           high_count=high_count,
                           dist=dist)

@app.route("/claims")
def claims():
    q = request.args.get("q", "").strip()
    page = max(1, int(request.args.get("page", 1)))
    offset = (page - 1) * PER_PAGE
    db = get_db()

    base_sql = "SELECT * FROM claims"
    params = []
    where = ""
    if q:
        # allow searching diagnosis or patient_id
        where = " WHERE diagnosis LIKE ? OR patient_id LIKE ?"
        params.extend([f"%{q}%", f"%{q}%"])

    count_sql = f"SELECT COUNT(*) as cnt FROM claims{where}"
    total = db.execute(count_sql, params).fetchone()["cnt"]

    sql = base_sql + where + " ORDER BY fraud_score DESC LIMIT ? OFFSET ?"
    params.extend([PER_PAGE, offset])
    rows = db.execute(sql, params).fetchall()

    total_pages = max(1, math.ceil(total / PER_PAGE))

    return render_template("claims.html",
                           claims=rows,
                           q=q,
                           page=page,
                           total_pages=total_pages,
                           total=total)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
