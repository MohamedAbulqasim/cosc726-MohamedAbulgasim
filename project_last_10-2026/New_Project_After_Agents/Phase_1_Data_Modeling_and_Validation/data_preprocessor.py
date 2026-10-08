"""
Phase 1: Data Preprocessor and Biological Validator
Handles:
- Biological zero replacement (Glucose, BloodPressure, SkinThickness, Insulin, BMI)
- Strict train-test separation before fitting transformers (No data leakage)
- Median imputation and standard scaling
- Clinical risk feature engineering based on ADA standards
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

PHYSIOLOGICAL_ZERO_COLS = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']
FEATURE_COLUMNS = [
    'Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness',
    'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age'
]

class ClinicalDataPreprocessor:
    def __init__(self):
        self.imputer = SimpleImputer(strategy='median')
        self.scaler = StandardScaler()
        self.is_fitted = False
        self.feature_names = FEATURE_COLUMNS.copy()
        self.engineered_feature_names = [
            'Insulin_Glucose_Ratio', 'High_Risk_Age', 'Obesity_Flag', 'Pedigree_Risk'
        ]
        self.all_feature_names = self.feature_names + self.engineered_feature_names

    def engineer_features(self, df_features: pd.DataFrame) -> pd.DataFrame:
        """Derives clinically meaningful biomarker features."""
        df_eng = df_features.copy()
        
        # 1. Insulin to Glucose Ratio (Surrogate indicator for insulin resistance)
        df_eng['Insulin_Glucose_Ratio'] = df_eng['Insulin'] / (df_eng['Glucose'] + 1e-5)
        
        # 2. ADA Age Risk (Age >= 45 is a recognized standard risk threshold)
        df_eng['High_Risk_Age'] = (df_eng['Age'] >= 45).astype(float)
        
        # 3. Obesity Flag (BMI >= 30.0 indicates clinical obesity)
        df_eng['Obesity_Flag'] = (df_eng['BMI'] >= 30.0).astype(float)
        
        # 4. Genetic Pedigree High Risk (Pedigree > 0.5)
        df_eng['Pedigree_Risk'] = (df_eng['DiabetesPedigreeFunction'] >= 0.5).astype(float)
        
        return df_eng

    def fit(self, X: pd.DataFrame):
        """Fits imputer and scaler on training data only."""
        X_copy = X[FEATURE_COLUMNS].copy()
        # Replace impossible biological zeros with NaN
        for col in PHYSIOLOGICAL_ZERO_COLS:
            X_copy[col] = X_copy[col].replace(0, np.nan)

        imputed_array = self.imputer.fit_transform(X_copy)
        df_imputed = pd.DataFrame(imputed_array, columns=FEATURE_COLUMNS, index=X.index)
        
        df_engineered = self.engineer_features(df_imputed)
        self.scaler.fit(df_engineered)
        self.is_fitted = True
        return self

    def transform(self, X: pd.DataFrame) -> np.ndarray:
        """Transforms data using fitted parameters."""
        if not self.is_fitted:
            raise ValueError("Preprocessor has not been fitted yet!")
        
        X_copy = X[FEATURE_COLUMNS].copy()
        for col in PHYSIOLOGICAL_ZERO_COLS:
            X_copy[col] = X_copy[col].replace(0, np.nan)

        imputed_array = self.imputer.transform(X_copy)
        df_imputed = pd.DataFrame(imputed_array, columns=FEATURE_COLUMNS, index=X.index)
        df_engineered = self.engineer_features(df_imputed)
        scaled_array = self.scaler.transform(df_engineered)
        return scaled_array

    def fit_transform(self, X: pd.DataFrame) -> np.ndarray:
        return self.fit(X).transform(X)

    def save(self, filepath: str):
        joblib.dump(self, filepath)

    @classmethod
    def load(cls, filepath: str) -> 'ClinicalDataPreprocessor':
        return joblib.load(filepath)

def load_and_split_dataset(csv_path: str, test_size: float = 0.2, random_state: int = 10):
    """Loads diabetes dataset and performs stratified train-test split."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset not found at: {csv_path}")
    
    df = pd.read_csv(csv_path)
    X = df[FEATURE_COLUMNS]
    y = df['Outcome']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    return X_train, X_test, y_train, y_test, df
