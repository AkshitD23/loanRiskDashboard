import pandas as pd
import numpy as np
import joblib
import re

from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import FunctionTransformer, StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, precision_recall_curve
from sklearn.model_selection import train_test_split


class EmpLengthTransformer(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        X_out = pd.DataFrame(X).copy()
        for col in X_out.columns:
            X_out[col] = X_out[col].astype(str).apply(self._parse_emp_length)
        return X_out

    def _parse_emp_length(self, val):
        if pd.isna(val) or val == 'nan' or val == 'n/a':
            return np.nan
        val = val.lower()
        if '< 1' in val:
            return 0
        match = re.search(r'\d+', val)
        if match:
             return int(match.group())
        return np.nan


class FicoTransformer(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        # We assume X has exactly two columns: low and high
        X_out = pd.DataFrame(X)
        fico_score = (X_out.iloc[:, 0] + X_out.iloc[:, 1]) / 2.0
        return pd.DataFrame(fico_score, columns=['fico_score'])


def build_preprocessor(df, exclude_cols):
    cols = df.columns.tolist()
    
    # Identify subsets based on columns available
    log_features = [
        'loan_amnt', 'annual_inc', 'revol_bal', 'tot_cur_bal', 
        'tot_hi_cred_lim', 'total_bal_ex_mort', 'total_bc_limit', 'total_il_high_credit_limi'
    ]
    log_features = [col for col in log_features if col in cols]
    
    fico_features = ['fico_range_low', 'fico_range_high']
    fico_features = [col for col in fico_features if col in cols]
    
    emp_features = ['emp_length']
    emp_features = [col for col in emp_features if col in cols]
    
    handled_cols = set(exclude_cols + log_features + fico_features + emp_features)
    
    # Basic numeric and categorical features
    num_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    cat_cols = df.select_dtypes(include=['object', 'category', 'bool']).columns.tolist()
    
    # Filter out highly cardinal categorical features to prevent OOM during OneHotEncoding
    cat_cols = [col for col in cat_cols if df[col].nunique() < 100]
    
    reg_num_cols = [col for col in num_cols if col not in handled_cols]
    reg_cat_cols = [col for col in cat_cols if col not in handled_cols]
    
    # 1. log_pipeline
    log_pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('log1p', FunctionTransformer(np.log1p, validate=False)),
        ('scaler', StandardScaler())
    ])

    # 2. num_pipeline
    num_pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])

    # 3. cat_pipeline
    cat_pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='most_frequent')),
        # handle_unknown skips unseen string classes cleanly
        ('ohe', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])

    # 4. emp_pipeline
    emp_pipeline = Pipeline([
        ('emp_transform', EmpLengthTransformer()),
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])

    # 5. fico_pipeline
    fico_pipeline = Pipeline([
        ('fico_transform', FicoTransformer()),
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    
    # Gather mapped columns
    transformers = []
    if log_features:
        transformers.append(('log', log_pipeline, log_features))
    if reg_num_cols:
        transformers.append(('num', num_pipeline, reg_num_cols))
    if reg_cat_cols:
        transformers.append(('cat', cat_pipeline, reg_cat_cols))
    if emp_features:
        transformers.append(('emp', emp_pipeline, emp_features))
    if len(fico_features) == 2:
        transformers.append(('fico', fico_pipeline, fico_features))
        
    preprocessor = ColumnTransformer(transformers=transformers, remainder='drop')
    return preprocessor

    
def select_model(X_train_prep, y_train, X_test_prep, y_test):
    # Models to test in specified order
    models = [
        ('LogisticRegression', LogisticRegression(max_iter=1000, random_state=42)),
        ('RandomForest', RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)),
        ('GradientBoosting', GradientBoostingClassifier(random_state=42))
    ]
    
    best_model_name = None
    best_model = None
    best_threshold = 0.5
    best_match_val = -1
    model_fallback = None
    model_fallback_name = None
    fallback_threshold = 0.5
    
    for name, model in models:
        print(f"Training {name}...")
        model.fit(X_train_prep, y_train)
        y_pred_proba = model.predict_proba(X_test_prep)[:, 1]
        
        precisions, recalls, thresholds = precision_recall_curve(y_test, y_pred_proba)
        
        # Find where precision and recall intersect (are closest)
        abs_diff = np.abs(precisions[:-1] - recalls[:-1])
        idx = np.argmin(abs_diff)
        
        match_prec = precisions[idx]
        match_rec = recalls[idx]
        match_thresh = thresholds[idx]
        
        print(f"{name} -> Intersect Threshold: {match_thresh:.4f}, Precision: {match_prec:.4f}, Recall: {match_rec:.4f}")
        
        # Track best intersection model as a fallback
        if match_rec > best_match_val:
            best_match_val = match_rec
            model_fallback = model
            model_fallback_name = name
            fallback_threshold = match_thresh
            
        # Standard acceptance criteria matching (>= 30%)
        if match_prec >= 0.3 and match_rec >= 0.3:
            best_model_name = name
            best_model = model
            best_threshold = match_thresh
            break
            
    if best_model is None:
        print(f"No model met the 0.3 metrics. Falling back to {model_fallback_name} (Intersection: {best_match_val:.4f})")
        best_model = model_fallback
        best_model_name = model_fallback_name
        best_threshold = fallback_threshold
        
    print(f"Selected Model: {best_model_name} with Threshold: {best_threshold:.4f}")
    return best_model, best_threshold


def evaluate_model(y_test, y_pred_proba, threshold):
    y_pred = (y_pred_proba >= threshold).astype(int)
    metrics = {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred),
        'recall': recall_score(y_test, y_pred),
        'f1': f1_score(y_test, y_pred),
        'roc_auc': roc_auc_score(y_test, y_pred_proba)
    }
    return metrics


def train_pipeline(filepath='lending_accepted.csv'):
    print(f"Loading dataset from {filepath}...")
    df = pd.read_csv(filepath, low_memory=False, nrows=50000)
    
    target = 'loan_status'
    
    required_features = "id,name,home_ownership,loan_amnt,emp_length,annual_inc,verification_status,purpose,addr_state,delinq_2yrs,dti,fico_range_low,fico_range_high,inq_last_6mths,mths_since_last_delinq,mths_since_last_record,open_acc,revol_bal,revol_util,total_acc,application_type,tot_coll_amt,tot_cur_bal,acc_now_delinq,bc_util,chargeoff_within_12_mths,delinq_amnt,num_accts_ever_120_pd,num_actv_bc_tl,num_actv_rev_tl,num_bc_sats,num_bc_tl,num_il_tl,num_op_rev_tl,num_rev_accts,num_rev_tl_bal_gt_0,num_sats,num_tl_120dpd_2m,num_tl_30dpd,num_tl_90g_dpd_24m,num_tl_op_past_12m,pct_tl_nvr_dlq,percent_bc_gt_75,pub_rec_bankruptcies,tax_liens,tot_hi_cred_lim,total_bal_ex_mort,total_bc_limit,total_il_high_credit_limi".split(',')
    
    # Retain strictly the distinct binary classes for standard lending modeling
    df = df[df[target].isin(['Fully Paid', 'Charged Off'])].copy()
    df[target] = (df[target] == 'Charged Off').astype(int)
    
    # Filter dataset to only required features + target
    cols_to_keep = [col for col in required_features + [target] if col in df.columns]
    df = df[cols_to_keep].copy()
    
    non_training = ['id', 'name']
    
    # Exclude logic before training (non-training are excluded as features)
    X = df.drop(columns=[target] + [c for c in non_training if c in df.columns], errors='ignore')
    y = df[target]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    print("Building preprocessor...")
    preprocessor = build_preprocessor(X_train, exclude_cols=[])
    
    print("Preprocessing data...")
    X_train_prep = preprocessor.fit_transform(X_train)
    X_test_prep = preprocessor.transform(X_test)
    
    print("Selecting and training model based on recall and precision metrics...")
    best_model, best_threshold = select_model(X_train_prep, y_train, X_test_prep, y_test)
    
    print("Evaluating final model...")
    y_pred_proba = best_model.predict_proba(X_test_prep)[:, 1]
    
    metrics = evaluate_model(y_test, y_pred_proba, best_threshold)
    print("Final Model Evaluation Metrics:")
    for k, v in metrics.items():
        print(f"  {k}: {v:.4f}")
        
    print("Saving the final ColumnTransformer+Model pipeline...")
    final_pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('model', best_model)
    ])
    joblib.dump({'pipeline': final_pipeline, 'threshold': best_threshold}, 'loan_default_pipeline.pkl')
    print("Pipeline and threshold saved to loan_default_pipeline.pkl")


def predict(df, threshold=None):
    """
    Inference function that adds predictions and probabilities.
    Returns: id, name, probability, prediction.
    """
    try:
        data = joblib.load('loan_default_pipeline.pkl')
        if isinstance(data, dict):
            pipeline = data['pipeline']
            default_thresh = data['threshold']
        else:
            pipeline = data
            default_thresh = 0.5
    except Exception as e:
        raise RuntimeError("Could not load the pipeline. Did you run the training step to generate 'loan_default_pipeline.pkl'?") from e
    
    used_thresh = threshold if threshold is not None else default_thresh
    
    prob = pipeline.predict_proba(df)[:, 1]
    pred = (prob >= used_thresh).astype(int)
    
    # Retrieve required non-training output cols safely
    result = pd.DataFrame()
    if 'id' in df.columns:
        result['id'] = df['id']
    if 'name' in df.columns:
        result['name'] = df['name']
        
    result['probability'] = prob
    result['prediction'] = pred
    
    return result

if __name__ == '__main__':
    train_pipeline()
    
    # Example inference:
    # new_data = pd.read_csv('lending_accepted.csv').head(10)
    # preds = predict(new_data, threshold=0.5)
    # print(preds)
