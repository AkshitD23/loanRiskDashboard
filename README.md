# Calibrated Loan Risk Prediction Dashboard

A production-grade machine learning system designed to predict loan default risks with high precision. This project features a FastAPI backend for real-time inference and a modern React-based dashboard for risk visualization, historical analysis, and model threshold calibration.

## 🚀 Overview

The **Loan Risk Model** leverages a 47-feature dataset to identify high-risk loan applications. Unlike standard classifiers, this system uses **Calibrated Probabilities** (Isotonic/Platt scaling) to ensure that the predicted risk scores reflect real-world default frequencies. It includes an administrative suite for monitoring feature drift and adjusting decision thresholds dynamically.

## ✨ Key Features

- **Real-time Risk Inference**: Upload CSV files to get instant risk assessments for multiple loan applications.
- **Dynamic Threshold Calibration**: Adjust the risk tolerance threshold via the UI to see live updates on "High Risk" vs "Low Risk" classifications.
- **Historical Audit Trail**: Every batch prediction is saved to a SQLite database for future auditing and review.
- **Advanced ML Pipeline**:
  - Temporal validation to ensure stability across economic cycles.
  - Automated feature engineering (Empirical length encoding, FICO score processing).
  - Multi-level model fallback (Logistic Regression → Random Forest → Gradient Boosting).
- **Drift Monitoring**: Built-in support for Population Stability Index (PSI) and feature drift analysis. (Based on PRD specifications).
- **Glassmorphic UI**: A premium, responsive dashboard built with React and Tailwind CSS.

## 🛠️ Tech Stack

### Backend
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Machine Learning**: Scikit-Learn, Pandas, Joblib
- **Database**: SQLite
- **Environment**: Python 3.9+

### Frontend
- **Framework**: [React](https://reactjs.org/) + [Vite](https://vitejs.dev/)
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **Charts**: Recharts
- **State/Routing**: React Router

## 📂 Project Structure

```text
LoanRiskModel/
├── backend.py              # FastAPI application & endpoints
├── database.py             # SQLite DB schema and ORM logic
├── loan_pipeline.py        # ML Pipeline definition & Custom Transformers
├── loan_default_pipeline.pkl # serialized ML model
├── run_qa_tests.py         # End-to-end QA validation suite
├── prd.md                  # Project Requirements Document
├── venv/                   # Python virtual environment
└── frontend/               # React application
    ├── src/
    │   ├── components/     # UI Components (Layout, Cards, etc.)
    │   ├── pages/          # Dashboard, History, Detail pages
    │   └── assets/         # Static assets
    ├── tailwind.config.js
    └── package.json
```

## 🏁 Getting Started

### Prerequisites
- Python 3.9 or higher
- Node.js 18+ and npm

### Backend Setup
1. Navigate to the root directory.
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies (if a requirements.txt exists, else install manually):
   ```bash
   pip install fastapi uvicorn pandas joblib scikit-learn
   ```
4. Start the backend server:
   ```bash
   python backend.py
   ```
   The API will be available at `http://localhost:8000`.

### Frontend Setup
1. Navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
   The dashboard will be available at `http://localhost:5173`.

## 📈 Usage

1. **Dashboard**: Use the "Upload CSV" button to process a batch of loans. Adjust the "Risk Threshold" slider to refine the classification.
2. **History**: View previous batches and their overall risk distribution.
3. **Details**: Click on a specific transaction in History to see individual user risk scores and predictions.

## 🧠 ML Pipeline Details

The model is trained using a **Temporal Splitting** strategy to prevent data leakage from the future.
- **Success Gate**: 60% Precision / 60% Recall.
- **Scaling**: Robust handling of missing values via median/mode imputation and standard scaling.
- **Calibration**: Probabilities are calibrated using Isotonic or Platt scaling to provide reliable risk estimates.

---
*Created as part of the Calibrated Loan Risk Prediction Project.*
