import os
import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.tree import DecisionTreeClassifier

# Ensure directories exist
os.makedirs('models', exist_ok=True)

def train_heart_disease_model():
    print("Training Heart Disease Prediction model...")
    # Synthetic dataset generation
    np.random.seed(42)
    n_samples = 200
    
    # Features: Age, Sex, ChestPainType (0-3), RestingBP, Cholesterol, FastingBS (0,1), MaxHR, ExerciseAngina (0,1)
    age = np.random.randint(29, 80, size=n_samples)
    sex = np.random.randint(0, 2, size=n_samples)
    cp = np.random.randint(0, 4, size=n_samples)
    trestbps = np.random.randint(94, 200, size=n_samples)
    chol = np.random.randint(126, 564, size=n_samples)
    fbs = np.random.randint(0, 2, size=n_samples)
    thalach = np.random.randint(71, 202, size=n_samples)
    exang = np.random.randint(0, 2, size=n_samples)
    
    # Target: 0 (No Heart Disease), 1 (Heart Disease) based on some rough rules
    # Heart disease is more likely with high age, male, chest pain, high bp, high chol, low maxHR, and exercise angina.
    score = (age - 40)*0.1 + sex*1.5 + cp*1.2 + (trestbps - 120)*0.03 + (chol - 200)*0.01 + fbs*0.5 - (thalach - 150)*0.04 + exang*1.5 - 2.0
    target = (score > 0).astype(int)
    
    X = pd.DataFrame({
        'age': age,
        'sex': sex,
        'cp': cp,
        'trestbps': trestbps,
        'chol': chol,
        'fbs': fbs,
        'thalach': thalach,
        'exang': exang
    })
    y = target
    
    model = LogisticRegression(max_iter=1000)
    model.fit(X, y)
    
    joblib.dump(model, 'models/heart_disease_model.joblib')
    print("Heart Disease model saved successfully to models/heart_disease_model.joblib!")

def train_house_price_model():
    print("Training House Price Prediction model...")
    # Synthetic dataset generation
    np.random.seed(42)
    n_samples = 200
    
    # Features: Bedrooms, Bathrooms, SqFt, LotSize, YearBuilt
    bedrooms = np.random.randint(1, 6, size=n_samples)
    bathrooms = np.random.randint(1, 4, size=n_samples) + 0.5 * np.random.randint(0, 2, size=n_samples)
    sqft = np.random.randint(500, 5000, size=n_samples)
    lotsize = np.random.randint(1000, 20000, size=n_samples)
    year_built = np.random.randint(1950, 2024, size=n_samples)
    
    # Target: Price based on some rules + noise
    price = bedrooms * 50000 + bathrooms * 40000 + sqft * 150 + lotsize * 5 + (year_built - 1950) * 1000 + np.random.normal(0, 20000, size=n_samples)
    price = np.clip(price, 80000, None)
    
    X = pd.DataFrame({
        'bedrooms': bedrooms,
        'bathrooms': bathrooms,
        'sqft': sqft,
        'lotsize': lotsize,
        'year_built': year_built
    })
    y = price
    
    model = LinearRegression()
    model.fit(X, y)
    
    joblib.dump(model, 'models/house_price_model.joblib')
    print("House Price model saved successfully to models/house_price_model.joblib!")

def train_diabetes_model():
    print("Training Diabetes Prediction model...")
    # Synthetic dataset generation
    np.random.seed(42)
    n_samples = 200
    
    # Features: Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin, BMI, DiabetesPedigree, Age
    pregnancies = np.random.randint(0, 15, size=n_samples)
    glucose = np.random.randint(50, 200, size=n_samples)
    bp = np.random.randint(40, 120, size=n_samples)
    skin = np.random.randint(0, 99, size=n_samples)
    insulin = np.random.randint(0, 800, size=n_samples)
    bmi = np.random.uniform(15.0, 55.0, size=n_samples)
    pedigree = np.random.uniform(0.08, 2.42, size=n_samples)
    age = np.random.randint(21, 81, size=n_samples)
    
    # Target: 0 (No Diabetes), 1 (Diabetes) based on some rules
    score = pregnancies*0.2 + (glucose - 100)*0.05 + (bp - 80)*0.01 + bmi*0.1 + pedigree*1.5 + (age - 30)*0.02 - 4.5
    target = (score > 0).astype(int)
    
    X = pd.DataFrame({
        'pregnancies': pregnancies,
        'glucose': glucose,
        'bp': bp,
        'skin': skin,
        'insulin': insulin,
        'bmi': bmi,
        'pedigree': pedigree,
        'age': age
    })
    y = target
    
    model = DecisionTreeClassifier(max_depth=5, random_state=42)
    model.fit(X, y)
    
    joblib.dump(model, 'models/diabetes_model.joblib')
    print("Diabetes model saved successfully to models/diabetes_model.joblib!")

if __name__ == '__main__':
    train_heart_disease_model()
    train_house_price_model()
    train_diabetes_model()
    print("All dummy models trained and saved!")
