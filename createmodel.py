import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
import joblib

# --- 1. Load Data and Preprocess ---
# Ensure 'Admission_Predict.csv' is in your working directory
try:
    df = pd.read_csv('university_admission.csv')
except FileNotFoundError:
    print("FATAL ERROR: 'Admission_Predict.csv' not found. Please download the dataset.")
    exit()

df.columns = df.columns.str.strip().str.replace(' ', '_')
#df = df.drop('Serial_No.', axis=1)

X = df.drop('Chance_of_Admission', axis=1)
y = df['Chance_of_Admission']

# Split data (necessary to fit scaler only on training data)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Initialize and fit the MinMaxScaler
scaler = MinMaxScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# --- 2. Train the Final Random Forest Regressor ---
rfr_model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
# Train on the full scaled training set
rfr_model.fit(X_train_scaled, y_train)

# --- 3. Save the Model and Scaler ---
# Save the trained model
joblib.dump(rfr_model, 'rfr_model.pkl')
print("✅ Trained Random Forest model saved to 'rfr_model.pkl'")

# Save the fitted scaler
joblib.dump(scaler, 'scaler.pkl')
print("✅ Fitted MinMaxScaler saved to 'scaler.pkl'")