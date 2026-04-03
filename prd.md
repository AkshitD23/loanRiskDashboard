Project: Calibrated Loan Risk Prediction Dashboard
Status: PRD Finalized | Version: 1.0 | Author: Project Manager (Gemini)

1. Executive Summary
The goal is to build a production-grade ML dashboard that predicts loan default risk using a 47-feature dataset. The system prioritizes temporal validation to ensure the model generalizes across economic cycles and includes an Admin suite for drift monitoring and threshold calibration.

2. Technical Stack

FastAPI (Python).

ML Library: Scikit-learn, Joblib, Pandas.

Inference Engine: Calibrated Classifier Pipeline (saved as model.joblib).

3. Data & ML Pipeline Specifications
3.1 Feature Schema (47 Input Features)
The model will ingest the following features, excluding ID and Name (metadata only):

ID, name, home_ownership, loan_amnt, emp_length, annual_inc, verification_status, purpose, addr_state, delinq_2yrs, dti, fico_range_low, fico_range_high, inq_last_6mths, mths_since_last_delinq, mths_since_last_record, open_acc, revol_bal, revol_util, total_acc, application_type, tot_coll_amt, tot_cur_bal, acc_now_delinq, bc_util, chargeoff_within_12_mths, delinq_amnt, num_accts_ever_120_pd, num_actv_bc_tl, num_actv_rev_tl, num_bc_sats, num_bc_tl, num_il_tl, num_op_rev_tl, num_rev_accts, num_rev_tl_bal_gt_0, num_sats, num_tl_120dpd_2m, num_tl_30dpd, num_tl_90g_dpd_24m, num_tl_op_past_12m, pct_tl_nvr_dlq, percent_bc_gt_75, pub_rec_bankruptcies, tax_liens, tot_hi_cred_lim, total_bal_ex_mort, total_bc_limit, total_il_high_credit_limit.
This id and name should be droped before training, they are only needed afterwards for the dashboard UI.

3.2 Training & Validation Logic
Temporal Splitting: Data sorted by issue_d. Partitioned chronologically: Training < Calibration < Testing.

Preprocessing: * Numerical: SimpleImputer (median) + Standard Scaler.

Categorical: SimpleImputer (most_frequent) + One-Hot Encoding.

Model Hierarchy (Success Gate: 60% Precision / 60% Recall):

Level 1: Logistic Regression + Calibration.

Level 2: Random Forest (if Level 1 fails).

Level 3: Gradient Boosting (if Level 2 fails).

Calibration: Use Isotonic or Platt scaling to ensure probability accuracy.

4. Functional Requirements & UI
Drift Monitoring: Visualizations for Population Stability Index (PSI) and feature drift over time.


5. Sample Data Row
101, L&T, MORTGAGE, 14000, 10+ years, 77000, Verified, debt_consolidation, FL, 0, 22.59, 690, 694, 1, 33, , 10, 13142, 61.7, 29, Individual, 0, 280305, 0, 63.8, 0, 0, 1, 4, 4, 4, 7, 10, 5, 12, 4, 10, 0, 0, 0, 3, 93.1, 50, 0, 0, 295176, 53949, 20600, 44660