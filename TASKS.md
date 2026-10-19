# Candidate briefing — Client Churn Reduction (100 minutes)

**Client:** A digital subscription platform has noticed rising churn. The COO wants a data-driven way to identify at-risk customers and prioritize a retention campaign. Your deliverable is a working data-preparation and ML workflow, plus a business recommendation. Use the two historical CSVs for model development; the two **live** CSVs represent current users with no known outcome.

The files `data/customers_history.csv`, `data/events_history.csv`, `data/customers_live.csv`, and `data/events_live.csv` are fictional and generated for this exercise. Read them with `pd.read_csv`. Work in `assessment/solution.py`. You may add helper functions but **do not change the public function names or parameter lists**. Functions must not modify their input DataFrames.

### Stage 1 — Clean the activity log (18 min; Pandas)
`clean_events(events: pd.DataFrame) -> pd.DataFrame`

Raw columns: `event_id`, `customer_id`, `event_date`, `minutes_spent`, `pages_viewed`.

1. Create a copy. Coerce `event_date` to datetime; invalid dates are removed.
2. Coerce `minutes_spent` and `pages_viewed` to numeric; **remove negative values**, and remove rows with nonnumeric or missing `pages_viewed`.
3. Fill missing/nonnumeric `minutes_spent` with **0** (after discarding negative numeric values).
4. Remove rows with missing/empty `customer_id` or `event_id` (trim leading/trailing whitespace on customer IDs and event IDs).
5. Keep **last** record by `event_id` in original input order after invalid row removal.
6. Return just the five original columns, no missing values, unique event IDs, with datetime `event_date`. Keep `pages_viewed` numeric. Row ordering is not graded.

Run: `python -m pytest -q tests/test_01_clean.py`

### Stage 2 — Customer features (25 min; Pandas)
`build_features(customers: pd.DataFrame, events_clean: pd.DataFrame) -> pd.DataFrame`

Customers have `customer_id`, `age`, `tenure_days`, `plan_type`, `country`, `support_tickets`, and historical customers additionally have `churned` (0/1). Each customer appears once. Preserve **all** customers, even those with zero events.

Return one row per customer with the original customer columns plus EXACTLY:
- `sessions`: number of valid events
- `active_days`: number of different calendar dates with a valid event
- `total_minutes`: sum of `minutes_spent`
- `avg_pages`: mean `pages_viewed` across the customer's valid events

For a customer with no events, all four engineered features must be 0. Do not include events belonging to unknown customers. Do not modify inputs. Preserve `churned` only when present in `customers`.

Run: `python -m pytest -q tests/test_02_features.py`

### Stage 3 — NumPy vectorization (12 min; NumPy)
`inactivity_score(features: pd.DataFrame) -> np.ndarray`

Define a **vectorized** numeric risk proxy:

`0.60 / (1 + sessions) + 0.30 * (1 - clip(active_days / 15, 0, 1)) + 0.10 * clip(support_tickets / 5, 0, 1)`

Return a flat NumPy array of floats (not a Series), one item per input row, in original order. Do not use Python `for` loops, `iterrows` or `apply`. Zero events + zero support tickets should produce `0.90`. Treat negative input values as invalid (raise `ValueError`). Input columns are assumed present and non-null.

Run: `python -m pytest -q tests/test_03_numpy.py`

### Stage 4 — Predict churn (30 min; scikit-learn)
#### A. `train_model(features: pd.DataFrame)`
Input is historical customer features (from Stage 2) with `inactivity_score` attached as a column (Stage 3), and `churned` as target.

1. Use only `MODEL_NUMERIC` and `MODEL_CATEGORICAL`, defined in `solution.py`. In particular, **never** use `customer_id` or `churned` as features.
2. Split **80% train / 20% test**, `random_state=42`, stratified by `churned`.
3. Build and fit an **sklearn Pipeline** with **ColumnTransformer**:
   - Numeric: `SimpleImputer(strategy='median')`, followed by `StandardScaler`.
   - Categoricals: `SimpleImputer(strategy='most_frequent')`, followed by `OneHotEncoder(handle_unknown='ignore')`.
   - Classifier: `LogisticRegression(max_iter=1000, random_state=42)` (no balancing required).
4. Only fit imputation, scaling, encoding, and the model on training data. Keep the test split untouched.
5. Return exactly the tuple `(fitted_pipeline, X_test, y_test)`.

#### B. `evaluate_model(model, X_test, y_test) -> dict`
Calculate predictions at threshold **0.50** and return exactly four float keys:
`roc_auc`, `precision`, `recall`, `f1`.

ROC-AUC must be computed from **probabilities**, not hard class predictions. Set `zero_division=0` where appropriate. In guided mode, inspect the confusion matrix too (not graded).

Run: `python -m pytest -q tests/test_04_model.py`

### Stage 5 — Make a client decision (15 min; Pandas, NumPy, sklearn)
`prioritize_customers(model, live_features, budget=600., outreach_cost=12., retention_value=140., retention_uplift=0.30) -> pd.DataFrame`

The current/live cohort has no `churned` label. The model should provide `predict_proba` for the *churned=1* class.

Expected **net value per contacted customer**:
`p(churn) * retention_uplift * retention_value - outreach_cost`

Return DataFrame with exactly `customer_id`, `churn_probability`, `expected_net_value`.
- Filter out customers with expected net value **<=0**.
- Sort by expected net value descending, breaking exact ties by `customer_id` ascending.
- Campaign budget is a hard limit. You can contact at most `floor(budget/outreach_cost)` customers (no fractional contact). If `outreach_cost<=0`, raise `ValueError`. If `budget<=0`, return an empty table with the three specified columns.
- Do not modify inputs. Do not use `churned` or `customer_id` to generate predictions.

Run: `python -m pytest -q tests/test_05_business.py`

### Final oral / written mini-case (in `ANSWERS.md`)
1. When does ROC-AUC help more than accuracy for this problem? What does it miss?
2. What is *data leakage*, and what leakage risk would you check in event timestamps relative to churn?
3. Would you deploy this campaign immediately? What is one experiment that could establish incremental business value?

**Evaluation:** coding correctness 65%, sound ML process 20%, commercial reasoning 15%. Scores and timing are **our training rubric**, not official BCG X criteria.
