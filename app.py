from flask import Flask, request, jsonify, render_template
import pandas as pd
import joblib
import os
from urllib.parse import quote as url_quote

app = Flask(__name__)

# Load the trained model
model = joblib.load('rfe_data_model.pkl')

# Define the prediction function
def predict_delivery_time(data):
    # Prepare the features for prediction
    X = pd.DataFrame(data, index=[0])  # Convert input into DataFrame
    features = ['actual_distance_to_destination', 'segment_osrm_time', 'od_duration_dirr_hour',
                'osrm_distance_time_ratio', 'distance_time_ratio']
    X = X[features]
    
    # Make the prediction
    prediction = model.predict(X)
    
    return prediction[0]

# REST API endpoint for prediction
@app.route('/predict', methods=['POST'])
def predict():
    if request.is_json:
        # Get the JSON data from the request
        data = request.get_json()
        prediction = predict_delivery_time(data)
        return jsonify({'predicted_delivery_time': prediction}), 200
    else:
        return jsonify({'error': 'Request must be in JSON format'}), 400

# Frontend to upload CSV or input data manually
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        if 'file' in request.files:
            # File upload logic
            file = request.files['file']
            if file and file.filename.endswith('.csv'):
                df = pd.read_csv(file)
                predictions = []
                for _, row in df.iterrows():
                    data = row.to_dict()  # Convert row to a dictionary
                    prediction = predict_delivery_time(data)
                    predictions.append(prediction)
                
                df['predicted_delivery_time'] = predictions
                return df.to_html(classes='table table-striped', index=False)

        elif request.form:
            # Handle manual input logic
            try:
                data = {
                    'actual_distance_to_destination': float(request.form['actual_distance_to_destination']),
                    'segment_osrm_time': float(request.form['segment_osrm_time']),
                    'od_duration_dirr_hour': float(request.form['od_duration_dirr_hour']),
                    'osrm_distance_time_ratio': float(request.form['osrm_distance_time_ratio']),
                    'distance_time_ratio': float(request.form['distance_time_ratio'])
                }
                prediction = predict_delivery_time(data)
                return render_template('index.html', prediction=prediction)
            except ValueError:
                return render_template('index.html', prediction="Invalid input data")

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
