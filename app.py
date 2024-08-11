from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from geotiff.shape_processing import Shapefile

# Load environment variables from .env or .flaskenv
load_dotenv()

app = Flask(__name__)

# Variable to store the data received from the JavaScript request
received_data = None


# Get the absolute path to the database
cwd = os.getcwd()
database = os.path.join(cwd, 'static', 'data')
# print(database)

# Set up the database URI in the Flask app configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(database, 'SHAPEDATA.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create the SQLAlchemy object
db = SQLAlchemy(app)

# Define the Park model
class Park(db.Model):
    __tablename__ = 'SHAPE_INFO'  # Name of the table in the database
    # Define columns
    FID = db.Column(db.Integer, primary_key=True)  
    NAME = db.Column(db.String(50))
    SQMI = db.Column(db.Float)  
    FEATTYPE = db.Column(db.String(50))
    Shape__Are = db.Column(db.Float)  
    Shape__Len = db.Column(db.Float)
    POINT_X = db.Column(db.Float)
    POINT_Y = db.Column(db.Float)


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


@app.route('/getData/<int:fid>', methods=['GET'])
def get_data(fid):
    # Query the database for the given FID
    print(f"fid value as a paramter is : {fid}")
    park = Park.query.filter_by(FID=fid).first()
    print(f"park is : {park}")
    # Check if the park was found
    if park:
        # Convert the park data to a dictionary
        park_data = {
            'FID': park.FID,
            'NAME': park.NAME,
            'SQMI': park.SQMI,
            'FEATTYPE': park.FEATTYPE,
            'Shape__Area': park.Shape__Are,
            'Shape__Len': park.Shape__Len,
            'POINT_X': park.POINT_X,
            'POINT_Y': park.POINT_Y
        }
        return jsonify(park_data)
    else:
        return jsonify({'error': 'Data not found'}), 404


if __name__ == '__main__':
    app.run(debug=True)
