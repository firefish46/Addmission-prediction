from flask import Flask, request, jsonify, render_template
import joblib
import pandas as pd
import numpy as np

app = Flask(__name__)

# Load the trained model and scaler
try:
    model = joblib.load('best_model.pkl')
    scaler = joblib.load('scaler.pkl')
    
    # --- FIX: Feature names MUST match the names the model was trained on (Mixed Case/Capitalized) ---
    numerical_features = [
        'GRE_Score', 
        'TOEFL_Score', 
        'University_Rating', 
        'SOP', 
        'LOR', 
        'CGPA', 
        'Research'
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
        data = request.get_json(force=True)
        
        # 1. Map incoming lowercase keys from the front-end to the model's expected capitalized keys.
        # This creates a dictionary with the correct feature names and values.
        mapped_data = {
            'GRE_Score': data.get('gre_score'),
            'TOEFL_Score': data.get('toefl_score'),
            'University_Rating': data.get('university_rating'),
            'SOP': data.get('sop'),
            'LOR': data.get('lor'),
            'CGPA': data.get('cgpa'),
            'Research': data.get('research')
        }
        
        # 2. Convert to DataFrame, ensuring columns are in the exact order the model expects.
        input_values = [mapped_data[col] for col in numerical_features]
        input_df = pd.DataFrame([input_values], columns=numerical_features)
        
        # 3. Scale the input data
        input_scaled_array = scaler.transform(input_df[numerical_features])
        input_scaled = pd.DataFrame(input_scaled_array, columns=numerical_features)
        
        # 4. Make prediction
        prediction = model.predict(input_scaled)
        
        # Convert NumPy float to standard Python float and clip the prediction
        predicted_chance_python_float = float(prediction[0])
        predicted_chance_clipped = np.clip(predicted_chance_python_float, 0.0, 1.0)
        
        # Return the prediction as JSON
        return jsonify(
            predicted_chance=round(predicted_chance_clipped, 4)
        )

    except Exception as e:
        # Log the error for debugging
        print(f"Prediction API Error: {e}")
        # Return a JSON error message
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

# --- Web Interface Endpoint ---
@app.route('/')
def home():
    # Render the home page using the template
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if model is None or scaler is None:
        return render_template('index.html', prediction_text="Error: Model or scaler not loaded.")

    # We must map the incoming lowercase form data keys to the model's expected keys
    try:
        mapped_data = {
            'GRE_Score': request.form.get('gre_score'),
            'TOEFL_Score': request.form.get('toefl_score'),
            'University_Rating': request.form.get('university_rating'),
            'SOP': request.form.get('sop'),
            'LOR': request.form.get('lor'),
            'CGPA': request.form.get('cgpa'),
            'Research': request.form.get('research')
        }
        
        input_values = [mapped_data[col] for col in numerical_features]
        input_data = pd.DataFrame([np.array(input_values, dtype=float)], columns=numerical_features)
        
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
    