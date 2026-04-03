from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Any, Dict
import pandas as pd
import joblib
import io
import uvicorn
from contextlib import asynccontextmanager

import database

import sys
import loan_pipeline

# ── Pickle compatibility fix ───────────────────────────────────────────────
# The pipeline was saved when loan_pipeline.py ran as __main__, so pickle
# stores EmpLengthTransformer / FicoTransformer under module='__main__'.
# We must register loan_pipeline under ALL aliases pickle might look for.
# setdefault() is NOT used for __main__ because that key already exists;
# we must force-assign it.  We save the original __main__ and restore after load.
_original_main = sys.modules.get('__main__')
sys.modules['__main__'] = loan_pipeline
sys.modules['__mp_main__'] = loan_pipeline
sys.modules['loan_pipeline'] = loan_pipeline

# Global variable to hold the model pipeline
model_data = None
model_pipeline = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global model_data, model_pipeline
    try:
        model_data = joblib.load("loan_default_pipeline.pkl")
        if isinstance(model_data, dict):
            model_pipeline = model_data.get('pipeline')
        else:
            model_pipeline = model_data
        print("Model loaded successfully.")
    except Exception as e:
        print(f"Error loading model: {e}")
        model_pipeline = None
    finally:
        # Restore the original __main__ so uvicorn internals keep working
        if _original_main is not None:
            sys.modules['__main__'] = _original_main
    
    # Initialize the DB schema
    database.init_db()
    
    yield
    # Clean up (if necessary)
    model_pipeline = None

app = FastAPI(title="Loan Risk Model API", lifespan=lifespan)

# Allow CORS for frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SaveTransactionRequest(BaseModel):
    threshold: float
    file_name: str
    predictions: List[Dict[str, Any]]

@app.post("/predict")
async def predict_loan_risk(
    file: UploadFile = File(...),
    threshold: float = Form(0.5)
):
    if model_pipeline is None:
        raise HTTPException(status_code=500, detail="Model is not loaded.")
        
    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
        
        # Store id and name if they exist, but drop them from inference
        results = []
        ids = df.get('id', df.get('member_id', pd.Series(range(len(df))))).fillna('Unknown')
        names = df.get('name', pd.Series(['Unknown User'] * len(df))).fillna('Unknown User')
        
        # Keep features exactly as expected by dropping 'id', 'name', 'member_id' if present but 
        # usually pipelines handle columns by names if pandas dataframe is passed.
        # However, to be safe, we'll try to predict with the original df as long as id/name don't interfere
        # Actually, the user asked to explicitly "drop id,name". Let's drop them.
        drop_cols = [c for c in ['id', 'name', 'member_id'] if c in df.columns]
        features = df.drop(columns=drop_cols)

        # ── Resilience: add any columns the pipeline expects but are missing ──
        # ColumnTransformer raises on missing columns; fill them with NaN so
        # the pipeline's own imputers handle them gracefully.
        try:
            fitted_cols = model_pipeline.named_steps['preprocessor'].feature_names_in_
            for col in fitted_cols:
                if col not in features.columns:
                    features[col] = float('nan')
        except AttributeError:
            pass  # older sklearn versions may not expose feature_names_in_

        # Obtain probabilities for class 1 (Assuming 1 is default/risk)
        probas = model_pipeline.predict_proba(features)
        
        # predict_proba returns array of shape (n_samples, n_classes). Assuming binary classification:
        # positive class probability is at index 1
        pos_probas = probas[:, 1] if probas.shape[1] > 1 else probas[:, 0]
        
        for i in range(len(df)):
            prob = float(pos_probas[i])
            pred_class = "High Risk" if prob >= threshold else "Low Risk"
            results.append({
                "id": str(ids.iloc[i]),
                "name": str(names.iloc[i]),
                "probability": prob,
                "prediction": pred_class
            })
            
        return {"predictions": results}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/save_transaction")
async def save_transaction(request: SaveTransactionRequest):
    try:
        transaction_id = database.save_transaction_to_db(
            threshold=request.threshold,
            file_name=request.file_name,
            predictions=request.predictions
        )
        return {"message": "Saved successfully", "transaction_id": transaction_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history")
async def get_history():
    try:
        return database.get_history_from_db()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/transaction/{transaction_id}")
async def get_transaction(transaction_id: int):
    try:
        result = database.get_transaction_details(transaction_id)
        if result is None:
            raise HTTPException(status_code=404, detail="Transaction not found")
        return result
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
