## Fraud Likelihood Score Heuristic

My fraud scoring algorithm is rule-based and designed to be transparent and explainable. It uses four key heuristics to estimate the likelihood of fraud for each claim:

1. **Charge Ratio** — Compares each claim’s billed amount to the average amount for the same diagnosis.
→ Claims that are significantly higher than the typical charge receive higher scores.

1. **Patient Frequency** — Flags patients who have multiple claims within a short period (60 days).
→ Frequent claims may indicate potential overuse or duplication.

1. **Hospital Stay Duration** — Penalizes claims with unusually long hospital stays relative to the diagnosis.
→ Extended stays can signal inflated billing or unnecessary care.

1. **High-Cost Procedures** — Identifies claims that fall within the top 5% of billed amounts across all records.
→ These high-cost outliers are weighted more heavily in the final fraud score.
## AI Prompt Journal

Most Effective Prompts:

1. **Prompt**: "Create a Flask application structure for a healthcare fraud dashboard with SQLite database, including data ingestion from CSV, fraud scoring algorithm, and two main views: dashboard overview and claims review page with search functionality."
   
   **Use**: Generated the initial application skeleton and database setup.

2. **Prompt**: "Design a comprehensive but simple fraud scoring heuristic that doesn't use machine learning. It should consider multiple factors like charge amounts compared to averages, provider claim frequency, and unusual patterns. Return a Python function that calculates scores from 0-100
   
   **Use**: Created the multi-factor fraud scoring algorithm.

3. **Prompt**: "Create a responsive HTML template using Bootstrap for a claims review table with pagination, search filtering by procedure code and provider type, and visual risk indicators using colored badges."
   
   **Use**: Built the claims review interface with search and pagination.

4. **Prompt**: "Generate a unit test for the fraud scoring function that tests edge cases like extremely high charges, normal claims, and boundary conditions for score categorization."
   
   **Use**: Created testing suite for the fraud detection logic.


5. **Prompt**: "Compare Flask vs FastAPI for building this dashboard, considering development speed, documentation quality, and deployment simplicity for a time-constrained prototype."
   
   **Use**: Made architectural decision to use Flask for rapid prototyping.




## Architectural Decision:

**Prompt**: "Compare using Postgres vs SQLite for a small MVP claims auditing web app that will be developed and deployed within 8 hours. Highlight deployment, complexity, and when to prefer one over the other."

Summary of decision:

1. SQLite chosen for MVP: zero-config, file-based, simple to seed from CSV, and easy to deploy on Replit/Vercel serverless container or simple VM. For the 8-hour prototyping constraint, SQLite reduces setup time dramatically.

2. Postgres tradeoffs: preferred for production (concurrency, robustness, analytics), but requires managed DB or extra infrastructure and increases setup time.

# NHIS Claims Auditor - Setup Guide
Got it! Here’s the **How to run** section exactly as you can **copy and paste** into your Markdown file:

---

## How to run

1. Clone the repository or copy the project files to your local machine.

2. Create and activate a Python virtual environment (optional but recommended):

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Prepare the database:

   * Run the provided script or commands to create the SQLite database.
   * Seed it with sample data from CSV files using the data ingestion scripts.

5. Run the Flask application:

   ```bash
   flask run
   ```

6. Open your browser and navigate to:

   ```
   http://localhost:5000
   ```



## How to run load_data.py

This script loads claims data from a CSV file (`data/claims.csv`), computes fraud scores, and saves the processed data to a SQLite database (`db/claims.db`).

### Steps to run:

1. Make sure you have your CSV file placed at `data/claims.csv`.

2. Ensure you have Python installed along with required dependencies (`pandas`).

3. Run the script from the project root directory:

   ```bash
   python load_data.py
