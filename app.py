from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os

from geotiff.shape_processing import Shapefile

# Load environment variables from .env or .flaskenv
load_dotenv()

app = Flask(__name__)

# Variable to store the data received from the JavaScript request
received_data = None

@app.route('/', methods=['GET'])
def home_page():
    return render_template('final.html')

@app.route('/api/data', methods=['POST'])
def show_data():
    global received_data
    if request.method == 'POST':
        try:
            received_data = request.get_json()
            app.logger.info(f"Received data is: {received_data}")  # Logging the received data
            return jsonify(received_data)
        except Exception as e:
            app.logger.error(f"Error processing JSON data: {e}")
            return jsonify({"error": "Invalid JSON format"}), 400
    return jsonify({"error": "Invalid request method"}), 405


@app.route('/result', methods=['GET', 'POST'])
def result():
    if received_data is None:
        return jsonify({"error": "No data received yet"}), 400
    drawn_json = received_data
    drawn_object = Shapefile(drawn_json)
    result = drawn_object.display_data()
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
