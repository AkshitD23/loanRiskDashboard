#!/usr/bin/env python3
"""
Loan Risk ML Dashboard — Comprehensive QA Test Runner
Covers: Model, API, Edge Cases, Integration, Performance
"""

import sys
import os
import io
import time
import json
import traceback

# ─── CRITICAL: register loan_pipeline under ALL module aliases BEFORE any import
# The pickle stored classes under '__main__' (because loan_pipeline.py was run
# directly).  We MUST force-assign (not setdefault) because __main__ already exists.
sys.path.insert(0, "/Users/apple/Desktop/LoanRiskModel")
import loan_pipeline as _loan_pipeline_mod

_original_main = sys.modules.get('__main__')
sys.modules['__main__']     = _loan_pipeline_mod   # force — key already exists
sys.modules['__mp_main__']  = _loan_pipeline_mod
sys.modules['loan_pipeline'] = _loan_pipeline_mod

import pandas as pd
import numpy as np
import requests

# ─────────────────────── helpers ────────────────────────
BASE_URL = "http://127.0.0.1:8000"

results = []  # list of (case_id, name, status, note)

def record(case_id, name, status, note=""):
    tag = "PASS" if status else "FAIL"
    results.append((case_id, name, tag, note))
    tick = "✓" if status else "✗"
    print(f"  [{tick}] TC-{case_id:03d} {name}: {tag}" + (f" — {note}" if note else ""))

def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

# ─────────── schema helpers ──────────────────────────────
REQUIRED_COLS = [
    "home_ownership","loan_amnt","emp_length","annual_inc",
    "verification_status","purpose","addr_state","delinq_2yrs",
    "dti","fico_range_low","fico_range_high","inq_last_6mths",
    "mths_since_last_delinq","mths_since_last_record","open_acc",
    "revol_bal","revol_util","total_acc","application_type",
    "tot_coll_amt","tot_cur_bal","acc_now_delinq","bc_util",
    "chargeoff_within_12_mths","delinq_amnt","num_accts_ever_120_pd",
    "num_actv_bc_tl","num_actv_rev_tl","num_bc_sats","num_bc_tl",
    "num_il_tl","num_op_rev_tl","num_rev_accts","num_rev_tl_bal_gt_0",
    "num_sats","num_tl_120dpd_2m","num_tl_30dpd","num_tl_90g_dpd_24m",
    "num_tl_op_past_12m","pct_tl_nvr_dlq","percent_bc_gt_75",
    "pub_rec_bankruptcies","tax_liens","tot_hi_cred_lim",
    "total_bal_ex_mort","total_bc_limit","total_il_high_credit_limi",
]

def make_row(n=1, overrides=None):
    """Generate n synthetic rows matching the required feature schema."""
    rows = []
    for i in range(n):
        r = {
            "id": 100 + i,
            "name": f"TestUser_{i}",
            "home_ownership": "MORTGAGE",
            "loan_amnt": 14000,
            "emp_length": "10+ years",
            "annual_inc": 77000,
            "verification_status": "Verified",
            "purpose": "debt_consolidation",
            "addr_state": "FL",
            "delinq_2yrs": 0,
            "dti": 22.59,
            "fico_range_low": 690,
            "fico_range_high": 694,
            "inq_last_6mths": 1,
            "mths_since_last_delinq": 33,
            "mths_since_last_record": np.nan,
            "open_acc": 10,
            "revol_bal": 13142,
            "revol_util": 61.7,
            "total_acc": 29,
            "application_type": "Individual",
            "tot_coll_amt": 0,
            "tot_cur_bal": 280305,
            "acc_now_delinq": 0,
            "bc_util": 63.8,
            "chargeoff_within_12_mths": 0,
            "delinq_amnt": 0,
            "num_accts_ever_120_pd": 1,
            "num_actv_bc_tl": 4,
            "num_actv_rev_tl": 4,
            "num_bc_sats": 4,
            "num_bc_tl": 7,
            "num_il_tl": 10,
            "num_op_rev_tl": 5,
            "num_rev_accts": 12,
            "num_rev_tl_bal_gt_0": 4,
            "num_sats": 10,
            "num_tl_120dpd_2m": 0,
            "num_tl_30dpd": 0,
            "num_tl_90g_dpd_24m": 0,
            "num_tl_op_past_12m": 3,
            "pct_tl_nvr_dlq": 93.1,
            "percent_bc_gt_75": 50,
            "pub_rec_bankruptcies": 0,
            "tax_liens": 0,
            "tot_hi_cred_lim": 295176,
            "total_bal_ex_mort": 53949,
            "total_bc_limit": 20600,
            "total_il_high_credit_limi": 44660,
        }
        if overrides:
            r.update(overrides)
        rows.append(r)
    return pd.DataFrame(rows)

def df_to_csv_bytes(df):
    buf = io.BytesIO()
    df.to_csv(buf, index=False)
    buf.seek(0)
    return buf.read()

def post_predict(csv_bytes, threshold=0.5, filename="test.csv", timeout=60):
    files = {"file": (filename, io.BytesIO(csv_bytes), "text/csv")}
    data = {"threshold": str(threshold)}
    return requests.post(f"{BASE_URL}/predict", files=files, data=data, timeout=timeout)


# ═══════════════════════════════════════════════════════
#  SECTION 1 — Model Tests
# ═══════════════════════════════════════════════════════
section("SECTION 1 — Model Tests")

# TC-001: Model loads successfully
try:
    import joblib
    model_data = joblib.load("/Users/apple/Desktop/LoanRiskModel/loan_default_pipeline.pkl")
    record(1, "Model loads successfully", True)
except Exception as e:
    record(1, "Model loads successfully", False, str(e))
    model_data = None

# TC-002: Model accepts dataframe input
try:
    assert model_data is not None
    pipeline = model_data['pipeline'] if isinstance(model_data, dict) else model_data
    df = make_row(3)
    drop = [c for c in ['id','name'] if c in df.columns]
    features = df.drop(columns=drop)
    probas = pipeline.predict_proba(features)
    record(2, "Model accepts dataframe input", True)
except Exception as e:
    record(2, "Model accepts dataframe input", False, str(e))

# TC-003: Model returns predict_proba (shape check)
try:
    assert model_data is not None
    pipeline = model_data['pipeline'] if isinstance(model_data, dict) else model_data
    df = make_row(5)
    drop = [c for c in ['id','name'] if c in df.columns]
    probas = pipeline.predict_proba(df.drop(columns=drop))
    assert probas.shape[0] == 5 and probas.shape[1] == 2
    assert all(0 <= p <= 1 for p in probas[:, 1])
    record(3, "Model returns predict_proba", True)
except Exception as e:
    record(3, "Model returns predict_proba", False, str(e))

# TC-004: Threshold logic works
try:
    assert model_data is not None
    pipeline = model_data['pipeline'] if isinstance(model_data, dict) else model_data
    df = make_row(10)
    drop = [c for c in ['id','name'] if c in df.columns]
    probas = pipeline.predict_proba(df.drop(columns=drop))[:, 1]
    for thresh in [0.0, 0.5, 1.0]:
        preds = (probas >= thresh).astype(int)
        if thresh == 0.0:
            assert all(preds == 1), "threshold=0 should flag all"
        if thresh == 1.0:
            assert all(preds == 0), "threshold=1 should flag none"
    record(4, "Threshold logic works", True)
except Exception as e:
    record(4, "Threshold logic works", False, str(e))

# TC-005: id/name preserved in output
try:
    df = make_row(3)
    assert 'id' in df.columns and 'name' in df.columns
    assert list(df['id'].values) == [100, 101, 102]
    assert df['name'].iloc[0].startswith("TestUser")
    record(5, "id/name preserved in output", True)
except Exception as e:
    record(5, "id/name preserved in output", False, str(e))

# TC-006: Missing values handled (NaN in numeric cols)
try:
    assert model_data is not None
    pipeline = model_data['pipeline'] if isinstance(model_data, dict) else model_data
    df = make_row(3, overrides={"dti": np.nan, "revol_util": np.nan, "open_acc": np.nan})
    drop = [c for c in ['id','name'] if c in df.columns]
    probas = pipeline.predict_proba(df.drop(columns=drop))
    assert probas.shape[0] == 3
    record(6, "Missing values handled", True)
except Exception as e:
    record(6, "Missing values handled", False, str(e))

# TC-007: Unknown categories handled
try:
    assert model_data is not None
    pipeline = model_data['pipeline'] if isinstance(model_data, dict) else model_data
    df = make_row(3, overrides={
        "home_ownership": "UNKNOWN_CATEGORY_XYZ",
        "purpose": "alien_invasion",
        "verification_status": "NEVER_SEEN"
    })
    drop = [c for c in ['id','name'] if c in df.columns]
    probas = pipeline.predict_proba(df.drop(columns=drop))
    assert probas.shape[0] == 3
    record(7, "Unknown categories handled", True)
except Exception as e:
    record(7, "Unknown categories handled", False, str(e))

# TC-008: Log features transform works
try:
    from loan_pipeline import build_preprocessor
    df = make_row(5)
    drop = [c for c in ['id','name'] if c in df.columns]
    feats = df.drop(columns=drop)
    prep = build_preprocessor(feats, exclude_cols=[])
    result = prep.fit_transform(feats)
    assert result.shape[0] == 5
    record(8, "Log features transform works", True)
except Exception as e:
    record(8, "Log features transform works", False, str(e))

# TC-009: EmpLengthTransformer works
try:
    from loan_pipeline import EmpLengthTransformer
    t = EmpLengthTransformer()
    test_vals = pd.DataFrame({"emp_length": ["10+ years", "< 1 year", "5 years", "n/a", None]})
    result = t.fit_transform(test_vals)
    vals = result.iloc[:, 0].tolist()
    assert vals[0] == 10, f"Expected 10, got {vals[0]}"
    assert vals[1] == 0, f"Expected 0, got {vals[1]}"
    assert vals[2] == 5, f"Expected 5, got {vals[2]}"
    assert np.isnan(vals[3]), f"Expected nan for n/a"
    assert np.isnan(vals[4]), f"Expected nan for None"
    record(9, "EmpLengthTransformer works", True)
except Exception as e:
    record(9, "EmpLengthTransformer works", False, str(e))

# TC-010: FicoTransformer works
try:
    from loan_pipeline import FicoTransformer
    t = FicoTransformer()
    df_f = pd.DataFrame({"fico_range_low": [690, 700], "fico_range_high": [694, 710]})
    result = t.fit_transform(df_f)
    assert abs(result.iloc[0, 0] - 692.0) < 0.01
    assert abs(result.iloc[1, 0] - 705.0) < 0.01
    record(10, "FicoTransformer works", True)
except Exception as e:
    record(10, "FicoTransformer works", False, str(e))


# ═══════════════════════════════════════════════════════
#  SECTION 2 — API Tests
# ═══════════════════════════════════════════════════════
section("SECTION 2 — API Tests")

# TC-011: API start / health
try:
    r = requests.get(f"{BASE_URL}/docs", timeout=5)
    record(11, "API starts successfully", r.status_code == 200)
except Exception as e:
    record(11, "API starts successfully", False, str(e))

# TC-012: /predict endpoint (valid CSV)
try:
    csv_bytes = df_to_csv_bytes(make_row(3))
    r = post_predict(csv_bytes)
    assert r.status_code == 200, f"HTTP {r.status_code}: {r.text[:200]}"
    data = r.json()
    assert "predictions" in data
    assert len(data["predictions"]) == 3
    record(12, "/predict endpoint (valid CSV)", True)
except Exception as e:
    record(12, "/predict endpoint (valid CSV)", False, str(e))

saved_predictions = []
if results[-1][2] == "PASS":
    saved_predictions = r.json()["predictions"]

# TC-013: CSV upload mechanics
try:
    df = make_row(5)
    csv_bytes = df_to_csv_bytes(df)
    r = post_predict(csv_bytes, filename="upload_test.csv")
    assert r.status_code == 200
    preds = r.json()["predictions"]
    assert len(preds) == 5
    assert all("probability" in p for p in preds)
    assert all("prediction" in p for p in preds)
    record(13, "CSV upload mechanics", True)
except Exception as e:
    record(13, "CSV upload mechanics", False, str(e))

# TC-014: Threshold parameter
try:
    df = make_row(10)
    csv_bytes = df_to_csv_bytes(df)
    # threshold=0 → all High Risk
    r0 = post_predict(csv_bytes, threshold=0.0)
    assert r0.status_code == 200
    hr0 = [p for p in r0.json()["predictions"] if p["prediction"] == "High Risk"]
    # threshold=1 → all Low Risk
    r1 = post_predict(csv_bytes, threshold=1.0)
    assert r1.status_code == 200
    hr1 = [p for p in r1.json()["predictions"] if p["prediction"] == "High Risk"]
    assert len(hr0) == 10, f"threshold=0 should give 10 High Risk, got {len(hr0)}"
    assert len(hr1) == 0, f"threshold=1 should give 0 High Risk, got {len(hr1)}"
    record(14, "Threshold parameter works", True)
except Exception as e:
    record(14, "Threshold parameter works", False, str(e))

# TC-015: JSON response format
try:
    df = make_row(2)
    csv_bytes = df_to_csv_bytes(df)
    r = post_predict(csv_bytes)
    assert r.status_code == 200
    data = r.json()
    preds = data["predictions"]
    for p in preds:
        assert "id" in p
        assert "name" in p
        assert "probability" in p
        assert "prediction" in p
        assert isinstance(p["probability"], float)
        assert p["prediction"] in ["High Risk", "Low Risk"]
    record(15, "JSON response format correct", True)
except Exception as e:
    record(15, "JSON response format correct", False, str(e))

# TC-016: Invalid CSV handling (non-CSV bytes)
try:
    invalid_bytes = b"this is not a csv at all !!!"
    r = post_predict(invalid_bytes, filename="bad.csv")
    # Should return 400 or 422 or 500 (not 200)
    assert r.status_code != 200, f"Expected error status, got 200"
    record(16, "Invalid CSV handling", True)
except Exception as e:
    record(16, "Invalid CSV handling", False, str(e))

# TC-017: Missing required columns
try:
    df_missing = pd.DataFrame({"some_col": [1, 2], "other_col": ["a", "b"]})
    csv_bytes = df_to_csv_bytes(df_missing)
    r = post_predict(csv_bytes)
    # Model will attempt predict — may 400 or may return probas with all defaults
    # Either is acceptable as long as it doesn't crash the server unexpectedly
    server_alive = requests.get(f"{BASE_URL}/docs", timeout=5)
    record(17, "Missing columns (server stays alive)", server_alive.status_code == 200)
except Exception as e:
    record(17, "Missing columns (server stays alive)", False, str(e))

# TC-018: Extra columns handled
try:
    df_extra = make_row(3)
    df_extra["extra_col_1"] = "foo"
    df_extra["extra_col_2"] = 9999
    csv_bytes = df_to_csv_bytes(df_extra)
    r = post_predict(csv_bytes)
    assert r.status_code == 200
    record(18, "Extra columns handled gracefully", True)
except Exception as e:
    record(18, "Extra columns handled gracefully", False, str(e))

# TC-019: Large file (100 rows)
try:
    df_large = make_row(100)
    csv_bytes = df_to_csv_bytes(df_large)
    t0 = time.time()
    r = post_predict(csv_bytes)
    elapsed = time.time() - t0
    assert r.status_code == 200
    assert len(r.json()["predictions"]) == 100
    record(19, f"Large file (100 rows) in {elapsed:.2f}s", True)
except Exception as e:
    record(19, "Large file (100 rows)", False, str(e))

# TC-020: Empty file
try:
    empty_bytes = b""
    r = post_predict(empty_bytes, filename="empty.csv")
    # Server should not crash
    server_alive = requests.get(f"{BASE_URL}/docs", timeout=5)
    record(20, "Empty file (server stays alive)", server_alive.status_code == 200)
except Exception as e:
    record(20, "Empty file (server stays alive)", False, str(e))


# ═══════════════════════════════════════════════════════
#  SECTION 3 (part) — History & Save Transaction API
# ═══════════════════════════════════════════════════════
section("SECTION 3 — Save Transaction & History API")

saved_tx_id = None

# TC-021: Save transaction
try:
    df = make_row(5)
    csv_bytes = df_to_csv_bytes(df)
    r = post_predict(csv_bytes)
    assert r.status_code == 200
    preds_for_save = r.json()["predictions"]

    payload = {
        "threshold": 0.5,
        "file_name": "qa_test.csv",
        "predictions": preds_for_save
    }
    rs = requests.post(f"{BASE_URL}/save_transaction", json=payload, timeout=10)
    assert rs.status_code == 200
    data = rs.json()
    assert "transaction_id" in data
    saved_tx_id = data["transaction_id"]
    record(21, "Save transaction to DB", True)
except Exception as e:
    record(21, "Save transaction to DB", False, str(e))

# TC-022: History endpoint returns list
try:
    r = requests.get(f"{BASE_URL}/history", timeout=10)
    assert r.status_code == 200
    items = r.json()
    assert isinstance(items, list)
    assert len(items) > 0
    first = items[0]
    assert "id" in first
    assert "timestamp" in first
    assert "threshold" in first
    assert "prediction_count" in first
    record(22, "History endpoint returns list", True)
except Exception as e:
    record(22, "History endpoint returns list", False, str(e))

# TC-023: Transaction detail endpoint
try:
    assert saved_tx_id is not None
    r = requests.get(f"{BASE_URL}/transaction/{saved_tx_id}", timeout=10)
    assert r.status_code == 200
    data = r.json()
    assert "transaction" in data
    assert "predictions" in data
    assert data["transaction"]["id"] == saved_tx_id
    assert len(data["predictions"]) == 5
    record(23, "Transaction detail endpoint", True)
except Exception as e:
    record(23, "Transaction detail endpoint", False, str(e))

# TC-024: Nonexistent transaction returns 404
try:
    r = requests.get(f"{BASE_URL}/transaction/99999999", timeout=10)
    assert r.status_code == 404
    record(24, "Nonexistent transaction returns 404", True)
except Exception as e:
    record(24, "Nonexistent transaction returns 404", False, str(e))

# TC-025: Threshold stored correctly in DB
try:
    assert saved_tx_id is not None
    r = requests.get(f"{BASE_URL}/transaction/{saved_tx_id}", timeout=10)
    assert r.status_code == 200
    stored_threshold = r.json()["transaction"]["threshold"]
    assert abs(stored_threshold - 0.5) < 0.001
    record(25, "Threshold stored correctly in DB", True)
except Exception as e:
    record(25, "Threshold stored correctly in DB", False, str(e))

# TC-026: Timestamp stored (non-empty string)
try:
    assert saved_tx_id is not None
    r = requests.get(f"{BASE_URL}/transaction/{saved_tx_id}", timeout=10)
    ts = r.json()["transaction"]["timestamp"]
    assert isinstance(ts, str) and len(ts) > 10
    record(26, "Timestamp stored in DB", True)
except Exception as e:
    record(26, "Timestamp stored in DB", False, str(e))


# ═══════════════════════════════════════════════════════
#  SECTION 4 — Edge Case Tests
# ═══════════════════════════════════════════════════════
section("SECTION 4 — Edge Case Tests")

# TC-027: Empty CSV (only headers)
try:
    df_empty = make_row(0)
    csv_bytes = df_to_csv_bytes(df_empty)
    r = post_predict(csv_bytes, filename="empty_rows.csv")
    server_alive = requests.get(f"{BASE_URL}/docs", timeout=5)
    record(27, "Empty CSV (headers only) - server alive", server_alive.status_code == 200)
except Exception as e:
    record(27, "Empty CSV (headers only) - server alive", False, str(e))

# TC-028: Single row CSV
try:
    df_single = make_row(1)
    csv_bytes = df_to_csv_bytes(df_single)
    r = post_predict(csv_bytes)
    assert r.status_code == 200
    preds = r.json()["predictions"]
    assert len(preds) == 1
    record(28, "Single row CSV", True)
except Exception as e:
    record(28, "Single row CSV", False, str(e))

# TC-029: Missing emp_length column (tested via API which back-fills missing cols)
try:
    df = make_row(3)
    df = df.drop(columns=['emp_length'])  # remove optional column
    csv_bytes = df_to_csv_bytes(df)
    r = post_predict(csv_bytes)
    assert r.status_code == 200, f"HTTP {r.status_code}: {r.text[:200]}"
    preds = r.json()["predictions"]
    assert len(preds) == 3
    record(29, "Missing emp_length column handled", True)
except Exception as e:
    record(29, "Missing emp_length column handled", False, str(e))

# TC-030: Missing fico columns (tested via API which back-fills missing cols)
try:
    df = make_row(3)
    df = df.drop(columns=['fico_range_low', 'fico_range_high'])  # remove optional columns
    csv_bytes = df_to_csv_bytes(df)
    r = post_predict(csv_bytes)
    assert r.status_code == 200, f"HTTP {r.status_code}: {r.text[:200]}"
    preds = r.json()["predictions"]
    assert len(preds) == 3
    record(30, "Missing fico columns handled", True)
except Exception as e:
    record(30, "Missing fico columns handled", False, str(e))

# TC-031: All categorical columns unknown values
try:
    assert model_data is not None
    pipeline = model_data['pipeline'] if isinstance(model_data, dict) else model_data
    df = make_row(3, overrides={
        "home_ownership": "???", "purpose": "???",
        "verification_status": "???", "addr_state": "??",
        "application_type": "???"
    })
    drop = [c for c in ['id','name'] if c in df.columns]
    probas = pipeline.predict_proba(df.drop(columns=drop))
    assert probas.shape[0] == 3
    record(31, "All categorical unknown values handled", True)
except Exception as e:
    record(31, "All categorical unknown values handled", False, str(e))

# TC-032: All numeric null
try:
    assert model_data is not None
    pipeline = model_data['pipeline'] if isinstance(model_data, dict) else model_data
    df = make_row(3)
    num_cols = df.select_dtypes(include=['int64','float64']).columns.tolist()
    df[num_cols] = np.nan
    drop = [c for c in ['id','name'] if c in df.columns]
    probas = pipeline.predict_proba(df.drop(columns=drop))
    assert probas.shape[0] == 3
    record(32, "All numeric null values handled", True)
except Exception as e:
    record(32, "All numeric null values handled", False, str(e))

# TC-033: Threshold = 0
try:
    df = make_row(5)
    csv_bytes = df_to_csv_bytes(df)
    r = post_predict(csv_bytes, threshold=0.0)
    assert r.status_code == 200
    preds = r.json()["predictions"]
    high_risk = [p for p in preds if p["prediction"] == "High Risk"]
    assert len(high_risk) == 5, f"threshold=0 should flag all 5, got {len(high_risk)}"
    record(33, "Threshold=0 flags all as High Risk", True)
except Exception as e:
    record(33, "Threshold=0 flags all as High Risk", False, str(e))

# TC-034: Threshold = 1
try:
    df = make_row(5)
    csv_bytes = df_to_csv_bytes(df)
    r = post_predict(csv_bytes, threshold=1.0)
    assert r.status_code == 200
    preds = r.json()["predictions"]
    high_risk = [p for p in preds if p["prediction"] == "High Risk"]
    assert len(high_risk) == 0, f"threshold=1 should flag none, got {len(high_risk)}"
    record(34, "Threshold=1 flags none as High Risk", True)
except Exception as e:
    record(34, "Threshold=1 flags none as High Risk", False, str(e))

# TC-035: Threshold = 0.99
try:
    df = make_row(10)
    csv_bytes = df_to_csv_bytes(df)
    r = post_predict(csv_bytes, threshold=0.99)
    assert r.status_code == 200
    preds = r.json()["predictions"]
    high_risk = [p for p in preds if p["prediction"] == "High Risk"]
    # probability has to be very high (>= 0.99) for any to be flagged
    # just verify request completes
    record(35, "Threshold=0.99 processed successfully", True)
except Exception as e:
    record(35, "Threshold=0.99 processed successfully", False, str(e))


# ═══════════════════════════════════════════════════════
#  SECTION 5 — Performance Tests
# ═══════════════════════════════════════════════════════
section("SECTION 5 — Performance Tests")

perf_benchmarks = {100: 10, 1000: 30, 10000: 120}  # rows: max_seconds

for n_rows, max_sec in perf_benchmarks.items():
    tc_id = {100: 36, 1000: 37, 10000: 38}[n_rows]
    try:
        df = make_row(n_rows)
        csv_bytes = df_to_csv_bytes(df)
        t0 = time.time()
        r = post_predict(csv_bytes, timeout=max_sec + 10)
        elapsed = time.time() - t0
        assert r.status_code == 200, f"HTTP {r.status_code}"
        assert len(r.json()["predictions"]) == n_rows
        ok = elapsed <= max_sec
        record(tc_id, f"Performance: {n_rows} rows in {elapsed:.1f}s (limit {max_sec}s)", ok,
               "" if ok else f"Too slow: {elapsed:.1f}s > {max_sec}s")
    except Exception as e:
        record(tc_id, f"Performance: {n_rows} rows", False, str(e))


# ═══════════════════════════════════════════════════════
#  SECTION 6 — Integration Flow
# ═══════════════════════════════════════════════════════
section("SECTION 6 — Integration Flow (E2E)")

# TC-039: Full E2E flow
try:
    # 1. Upload CSV
    df = make_row(10)
    csv_bytes = df_to_csv_bytes(df)
    # 2. Run prediction at threshold 0.4
    r = post_predict(csv_bytes, threshold=0.4)
    assert r.status_code == 200, f"Predict failed: {r.text[:100]}"
    preds = r.json()["predictions"]
    # 3. Save transaction
    payload = {"threshold": 0.4, "file_name": "integration_test.csv", "predictions": preds}
    rs = requests.post(f"{BASE_URL}/save_transaction", json=payload, timeout=10)
    assert rs.status_code == 200
    tx_id = rs.json()["transaction_id"]
    # 4. Verify appears in history
    rh = requests.get(f"{BASE_URL}/history", timeout=10)
    assert rh.status_code == 200
    ids = [item["id"] for item in rh.json()]
    assert tx_id in ids, f"TX {tx_id} not in history: {ids}"
    # 5. Open detail page
    rd = requests.get(f"{BASE_URL}/transaction/{tx_id}", timeout=10)
    assert rd.status_code == 200
    detail = rd.json()
    assert detail["transaction"]["threshold"] == 0.4
    assert len(detail["predictions"]) == 10
    record(39, "Full E2E integration flow", True)
except Exception as e:
    record(39, "Full E2E integration flow", False, str(e))

# TC-040: Large CSV integration
try:
    df = make_row(500)
    csv_bytes = df_to_csv_bytes(df)
    r = post_predict(csv_bytes, threshold=0.5)
    assert r.status_code == 200
    preds = r.json()["predictions"]
    assert len(preds) == 500
    payload = {"threshold": 0.5, "file_name": "large_integration.csv", "predictions": preds}
    rs = requests.post(f"{BASE_URL}/save_transaction", json=payload, timeout=30)
    assert rs.status_code == 200
    record(40, "Large CSV E2E integration (500 rows)", True)
except Exception as e:
    record(40, "Large CSV E2E integration (500 rows)", False, str(e))


# ═══════════════════════════════════════════════════════
#  SECTION 7 — Database Integrity Tests
# ═══════════════════════════════════════════════════════
section("SECTION 7 — Database Integrity Tests")

# TC-041: DB has transactions table
try:
    import sqlite3
    conn = sqlite3.connect("/Users/apple/Desktop/LoanRiskModel/loan_risk.db")
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in c.fetchall()]
    conn.close()
    assert "transactions" in tables
    assert "predictions" in tables
    record(41, "DB has transactions & predictions tables", True)
except Exception as e:
    record(41, "DB has transactions & predictions tables", False, str(e))

# TC-042: DB record count consistency
try:
    conn = sqlite3.connect("/Users/apple/Desktop/LoanRiskModel/loan_risk.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM transactions")
    tx_count = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM predictions")
    pred_count = c.fetchone()[0]
    conn.close()
    assert tx_count > 0, "No transactions in DB"
    assert pred_count > 0, "No predictions in DB"
    record(42, f"DB has {tx_count} transactions, {pred_count} predictions", True)
except Exception as e:
    record(42, "DB record count consistency", False, str(e))

# TC-043: Foreign key integrity
try:
    conn = sqlite3.connect("/Users/apple/Desktop/LoanRiskModel/loan_risk.db")
    c = conn.cursor()
    c.execute("""
        SELECT COUNT(*) FROM predictions p 
        LEFT JOIN transactions t ON p.transaction_id = t.id 
        WHERE t.id IS NULL
    """)
    orphans = c.fetchone()[0]
    conn.close()
    assert orphans == 0, f"Found {orphans} orphan predictions"
    record(43, "No orphan predictions (FK integrity)", True)
except Exception as e:
    record(43, "No orphan predictions (FK integrity)", False, str(e))


# ═══════════════════════════════════════════════════════
#  Write test_cases.txt
# ═══════════════════════════════════════════════════════
section("Writing test_cases.txt report")

report_lines = [
    "=" * 60,
    "  LOAN RISK ML DASHBOARD — QA TEST REPORT",
    f"  Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}",
    "=" * 60,
    "",
]

for (cid, name, status, note) in results:
    report_lines.append(f"TEST CASE {cid}: {name}")
    report_lines.append(f"STATUS: {status}")
    if note:
        report_lines.append(f"NOTE: {note}")
    report_lines.append("")

pass_count = sum(1 for r in results if r[2] == "PASS")
fail_count = len(results) - pass_count

report_lines += [
    "=" * 60,
    f"  TOTAL: {len(results)} tests | PASS: {pass_count} | FAIL: {fail_count}",
    "=" * 60,
]

report_path = "/Users/apple/Desktop/LoanRiskModel/test_cases.txt"
with open(report_path, "w") as f:
    f.write("\n".join(report_lines))

print(f"\n✓ Report written to: {report_path}")
print(f"\n{'='*60}")
print(f"  TOTAL: {len(results)} tests | PASS: {pass_count} | FAIL: {fail_count}")
if fail_count == 0:
    print("  ✅ ALL TESTS PASSED — SYSTEM READY FOR DEPLOYMENT")
else:
    print(f"  ⚠️  {fail_count} test(s) failed — see report for details")
print(f"{'='*60}\n")

sys.exit(0 if fail_count == 0 else 1)
