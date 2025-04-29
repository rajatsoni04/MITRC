from flask import Flask, render_template, request
import joblib
import mysql.connector

# Load the scaler and KMeans model
scaler = joblib.load('minmax.joblib')
model = joblib.load('kmeans_model.joblib')

app = Flask(__name__)

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Daya@123",
        database="crop_recommendation"
    )

@app.route('/history')
def history():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM CropHistory ORDER BY id DESC")
        history_data = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('history.html', historical_data=history_data)
    except Exception as e:
        print("History error:", e)
        return render_template('history.html', historical_data=[])

# Mapping from cluster to crop name
cluster_to_crop = {
    0: 'blackgram', 1: 'apple', 2: 'rice', 3: 'watermelon', 4: 'pomegranate',
    5: 'chickpea', 6: 'cotton', 7: 'mango', 8: 'papaya', 9: 'kidneybeans',
    10: 'lentil', 11: 'coffee', 12: 'coconut', 13: 'banana', 14: 'mungbean',
    15: 'mothbeans', 16: 'jute', 17: 'maize', 18: 'grapes', 19: 'pigeonpeas',
    20: 'mothbeans', 21: 'grapes'
}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/project')
def project():
    return render_template('project.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        N = float(request.form['N'])
        P = float(request.form['P'])
        K = float(request.form['K'])
        temperature = float(request.form['temperature'])
        humidity = float(request.form['humidity'])
        ph = float(request.form['ph'])
        rainfall = float(request.form['rainfall'])

        input_data = [[N, P, K, temperature, humidity, ph, rainfall]]
        scaled_input = scaler.transform(input_data)
        # prediction = model.predict(scaled_input)[0]
        cluster = model.predict(scaled_input)[0]
        crop_name = cluster_to_crop.get(cluster, "Unknown crop")

        # Save to database
        conn = get_db_connection()
        cursor = conn.cursor()
        insert_query = """
            INSERT INTO CropHistory (N, P, K, temperature, humidity, ph, rainfall, label)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (N, P, K, temperature, humidity, ph, rainfall, crop_name))
        conn.commit()
        cursor.close()
        conn.close()

        return render_template('project.html', prediction=f"{crop_name}")

    except Exception as e:
        print("Prediction error:", e)
        return render_template('project.html', prediction="Error during prediction.")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=2525)
