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
    global received_data
    # print(f"the received data is : {received_data}")
    if  received_data == None or received_data['features'] == []:
        error  = 'Please draw the shape on map and try again.'
        received_data = None
        return render_template('final.html', error = error)
    drawn_json = received_data
    # print(f"drawn json is  : {drawn_json}")
    drawn_object = Shapefile(drawn_json)
    if drawn_json is not None:
        result = drawn_object.display_data()
    # print(f"result is : {result}")
    columns = ['FID','NAME','SQMI','TYPE','SHAPE AREA(sqm)', 'SHAPE PERI(m)']
    return render_template('final.html', result=result, columns=columns, drawn_json = drawn_json)

if __name__ == '__main__':
    app.run(debug=True)
