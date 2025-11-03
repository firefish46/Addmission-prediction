from flask import Flask, request, jsonify, render_template
import joblib
import pandas as pd
import numpy as np

app = Flask(__name__)

# Load the trained model and scaler
try:
    model = joblib.load('best_model.pkl')
    scaler = joblib.load('scaler.pkl')
    
    # --- FIX 1: Feature names must exactly match the keys in the incoming JSON data from the front-end. ---
    # The front-end is sending keys like 'gre_score', 'toefl_score', etc. (all lowercase/snake_case)
    numerical_features = [
        'gre_score', 
        'toefl_score', 
        'university_rating', 
        'sop', 
        'lor', 
        'cgpa', 
        'research'
    ]
    
    print("Model and Scaler loaded successfully.")
except Exception as e:
    print(f"Error loading model or scaler: {e}")
    model = None
    scaler = None

# --- API Endpoint for Prediction ---
@app.route('/predict_api', methods=['POST'])
def predict_api():
    if model is None or scaler is None:
        # Return error as JSON with appropriate status code
        return jsonify({'error': 'Model or scaler not loaded.'}), 500
        
    try:
        # Get JSON data from the request body
        data = request.get_json(force=True)
        
        # --- FIX 2: Create DataFrame using the correct, lowercased keys from the input data ---
        # The DataFrame must be created with the columns in the exact order the model expects.
        # We ensure the values are extracted in the correct order defined by numerical_features.
        input_values = [data[col] for col in numerical_features]
        input_df = pd.DataFrame([input_values], columns=numerical_features)
        
        # Scale the input data
        # Note: input_df[numerical_features] is now correct because the DataFrame columns match the list.
        input_scaled_array = scaler.transform(input_df[numerical_features])
        input_scaled = pd.DataFrame(input_scaled_array, columns=numerical_features)
        
        # Make prediction
        prediction = model.predict(input_scaled)
        
        # Convert NumPy float to standard Python float
        predicted_chance_python_float = float(prediction[0])
        
        # Clip the prediction to be between 0 and 1, as chances can't be negative or > 1
        predicted_chance_clipped = np.clip(predicted_chance_python_float, 0.0, 1.0)
        
        # Return the prediction as JSON
        return jsonify(
            predicted_chance=round(predicted_chance_clipped, 4)
        )

    except Exception as e:
        # Log the error for debugging
        print(f"Prediction API Error: {e}")
        # Return a JSON error message instead of an HTML page
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

# --- Web Interface Endpoint ---
@app.route('/')
def home():
    # Render the home page using the template
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    # This function is not used by the front-end (which uses /predict_api), but we should fix its logic too.
    if model is None or scaler is None:
        return render_template('index.html', prediction_text="Error: Model or scaler not loaded.")

    # Get data from the form
    # Note: request.form.get() uses the correct HTML field names (lowercased)
    features = [
        request.form.get('gre_score'),
        request.form.get('toefl_score'),
        request.form.get('university_rating'),
        request.form.get('sop'),
        request.form.get('lor'),
        request.form.get('cgpa'),
        request.form.get('research')
    ]
    
    try:
        # Convert to a single row DataFrame
        input_data = pd.DataFrame([np.array(features, dtype=float)], columns=numerical_features)
        
        # Scale and predict
        input_scaled_array = scaler.transform(input_data[numerical_features])
        input_scaled = pd.DataFrame(input_scaled_array, columns=numerical_features)
        
        prediction = model.predict(input_scaled)
        
        # Clip the prediction
        output = np.clip(prediction[0], 0.0, 1.0)
        
        return render_template('index.html', prediction_text=f'Predicted Chance of Admit: {round(output, 4)}')
    
    except Exception as e:
        return render_template('index.html', prediction_text=f'An error occurred: {e}')


if __name__ == "__main__":
    app.run(debug=True)
