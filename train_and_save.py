import joblib
import pandas as pd
import numpy
from sklearn.linear_model import LinearRegression # ... other imports
from sklearn.preprocessing import StandardScaler # Assuming you used a StandardScaler
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor # Assuming this is your best model

# ... (Load your data into X and y) ...
# X_train, X_val, X_test, y_train, y_val, y_test = train_test_split(...)

from sklearn.model_selection import train_test_split
import pandas as pd
from sklearn.preprocessing import StandardScaler
df = pd.read_csv('university_admission.csv')
#df = df.drop('Serial No.', axis=1)

# Separate features (X) and target (y)
X = df.drop('Chance_of_Admission', axis=1)
y = df['Chance_of_Admission']

# Split data into training (70%) and temporary (30%)
X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3, random_state=42)

# Split the temporary set into validation (20%) and testing (10%) sets
# 20% of original is 2/3 of temporary (0.2 / 0.3 = 2/3)
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=1/3, random_state=42)

print(f"Training set size: {X_train.shape[0]}")
print(f"Validation set size: {X_val.shape[0]}")
print(f"Testing set size: {X_test.shape[0]}")
print(f"Number of features: {X_train.shape[1]}")
# Fit the scaler on training data (Crucial!)
# Identify numerical features for scaling (excluding the target variable)
numerical_features = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
numerical_features.remove('Chance_of_Admission')

# Initialize & apply StandardScaler

scaler = StandardScaler()
df[numerical_features] = scaler.fit_transform(df[numerical_features])
X_train_scaled = scaler.fit_transform(X_train[numerical_features])
# Re-train the best model on the full training data (X_train_scaled, y_train)
best_model = XGBRegressor(random_state=42) # Assuming LGBM was best
best_model.fit(X_train_scaled, y_train)

# Save the best model and the scaler
joblib.dump(best_model, 'best_model.pkl')
joblib.dump(scaler, 'scaler.pkl')

print("Model and Scaler saved successfully!")